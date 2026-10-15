"""Data Collector : interroge chaque source active, sans jamais bloquer le cycle.

- Chaque source est activable séparément (config/settings.yaml, `sources.*.enabled`) et a
  sa propre fréquence (`every_minutes`) : on économise les appels et on respecte les limites.
- Une source qui échoue est notée « indisponible » avec la raison ; les autres continuent
  (mode dégradé) et l'analyse est marquée partielle.
- Les observations sont dédoublonnées (empreinte + quasi-copies) et enregistrées en base.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from polymarket_agent.correlation import correlation_group
from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.models import MarketInfo
from polymarket_agent.observations import Observation, mark_duplicates
from polymarket_agent.social_intelligence import match, search_query
from polymarket_agent.sources.bluesky import BlueskySource
from polymarket_agent.sources.crypto_prices import CryptoPricesSource, CryptoQuote
from polymarket_agent.sources.gdelt import GdeltSource
from polymarket_agent.sources.google_news import GoogleNewsSource
from polymarket_agent.sources.polymarket_comments import CommentsSource
from polymarket_agent.sources.rss import RssSource

log = logging.getLogger(__name__)


@dataclass
class Collection:
    observations: list[Observation] = field(default_factory=list)
    status: dict[str, str] = field(default_factory=dict)  # source → ok / désactivée / indisponible…
    crypto: dict[str, CryptoQuote] = field(default_factory=dict)

    @property
    def sources_down(self) -> list[str]:
        return [name for name, state in self.status.items() if state.startswith("indisponible")]


def with_retries(http, max_retries, timeout=None):
    """Copie du client HTTP avec son propre nombre de nouveaux essais et, au besoin, son propre
    délai d'attente (None = inchangé)."""
    if (max_retries is None and timeout is None) or not hasattr(http, "max_retries"):
        return http
    clone = copy.copy(http)
    if max_retries is not None:
        clone.max_retries = int(max_retries)
    if timeout is not None:
        clone.timeout = float(timeout)
    return clone


def _due(db, name: str, every_minutes: float, now: datetime) -> bool:
    last = db.source_last_run(name) if db else None
    return last is None or now - last >= timedelta(minutes=every_minutes) - timedelta(seconds=30)


def load_recent(db, now: datetime, hours: int = 24) -> list[Observation]:
    """Observations des dernières `hours` heures (pour les volumes de mentions sur 24 h)."""
    import json

    from polymarket_agent.sources._util import parse_date
    out = []
    for r in db.recent_observations(now - timedelta(hours=hours)):
        out.append(Observation(
            source=r["source"], external_id=r["external_id"], published_at=parse_date(r["published_at"]),
            collected_at=parse_date(r["collected_at"]), url=r["url"] or "", title=r["title"] or "",
            text=r["text"] or "", author=r["author"] or "", domain=r["domain"] or "",
            engagement=r["engagement"] or 0, market_ids=json.loads(r["market_ids"] or "[]"),
            reliability=r["reliability"] or 0, uncertainty=r["uncertainty"] or "", kind=r["kind"] or "",
            sentiment=r["sentiment"] or 0, dup_key=r["dup_key"] or "", duplicate_of=r["duplicate_of"] or "",
            data=json.loads(r["data"] or "{}")))
    return out


def collect(settings: dict, http: HttpClient, db, markets: list[MarketInfo], now: datetime,
            factories: dict | None = None) -> Collection:
    """`factories` permet aux tests de remplacer une source par une fausse."""
    src = settings.get("sources", {})
    factories = factories or {}
    result = Collection()
    top = markets[: int(settings.get("collector", {}).get("markets_per_cycle", 5))]
    queries = [q for q in (search_query(m) for m in top) if q]
    assets = sorted({correlation_group(m).split(":")[1] for m in markets
                     if correlation_group(m).startswith("crypto:")} | {"btc", "eth"})

    def run(name: str, call) -> None:
        cfg = src.get(name, {})
        if not cfg.get("enabled"):
            result.status[name] = "désactivée"
            return
        if not _due(db, name, float(cfg.get("every_minutes", 5)), now):
            result.status[name] = "pas encore (fréquence)"
            return
        try:
            obs = call(cfg)
        except (SourceUnavailable, ValueError, KeyError, TypeError) as exc:
            result.status[name] = f"indisponible : {exc}"[:200]
            log.warning("source %s indisponible : %s", name, exc)
            if db:  # une source en panne attend sa fréquence normale avant de réessayer
                db.set_source_run(name, now)
            return
        result.observations += obs
        result.status[name] = f"ok ({len(obs)} observations)"
        if db:
            db.set_source_run(name, now)

    run("polymarket_comments", lambda cfg: factories.get("polymarket_comments", lambda: CommentsSource(
        http, src.get("polymarket_gamma", {}).get("base_url", "https://gamma-api.polymarket.com"),
        int(cfg.get("per_event", 20))))().fetch(sorted({m.event_id for m in top}), now))

    def crypto(cfg):
        source = factories.get("crypto_prices", lambda: CryptoPricesSource(http))()
        obs = source.fetch(assets, now)
        for o in obs:
            result.crypto[o.data["asset"]] = CryptoQuote(o.data["asset"], o.data["price"], o.data["hourly_vol"],
                                                         o.published_at, o.domain)
        return obs
    run("crypto_prices", crypto)
    run("gdelt", lambda cfg: factories.get("gdelt", lambda: GdeltSource(
        with_retries(http, cfg.get("max_retries")), cfg.get("timespan", "3h")))()
        .fetch(queries[: int(cfg.get("queries_per_run", 3))], now))
    run("google_news", lambda cfg: factories.get("google_news", lambda: GoogleNewsSource(
        per_query=int(cfg.get("per_query", 15))))().fetch(queries[: int(cfg.get("queries_per_run", 5))], now))
    rss_sources = []

    def rss(cfg):
        # Identifiant complet (settings → http.user_agent) : certains sites refusent l'identifiant court.
        source = factories.get("rss", lambda: RssSource(
            cfg.get("feeds", []), user_agent=settings.get("http", {}).get("user_agent", "polymarket-autonomous-lab")))()
        rss_sources.append(source)
        return source.fetch(now)
    run("rss", rss)
    failed = getattr(rss_sources[0], "failures", {}) if rss_sources else {}
    if failed and result.status.get("rss", "").startswith("ok"):
        names = {f["url"]: f.get("name", f["url"]) for f in src.get("rss", {}).get("feeds", [])}
        result.status["rss"] = (result.status["rss"][:-1] + f", {len(failed)} flux en échec : "
                                + ", ".join(sorted(names.get(u, u) for u in failed)) + ")")[:300]
    run("bluesky", lambda cfg: factories.get("bluesky", lambda: BlueskySource(http))()
        .fetch(queries[: int(cfg.get("queries_per_run", 3))], now))
    result.status["x_api"] = "désactivée (payante)"

    known = db.recent_dup_keys(now - timedelta(days=3)) if db else set()
    mark_duplicates(result.observations, known)
    match(result.observations, markets)
    if db:
        db.save_observations(result.observations)
    return result
