"""Assemble l'étape 5 pour le cycle : collecte → observations des 24 h → résumé par marché
→ (option) classement Gemini → caractéristiques attachées aux marchés surveillés."""

from __future__ import annotations

import logging
from datetime import datetime

from polymarket_agent.correlation import correlation_group
from polymarket_agent.data_collector import collect, load_recent, with_retries
from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.models import MarketInfo
from polymarket_agent.social_intelligence import summarize
from polymarket_agent.sources.gemini import GeminiClassifier

log = logging.getLogger(__name__)


def latest_quotes(observations) -> dict:
    """Dernier prix crypto connu par actif (la source n'est interrogée qu'une fois sur N cycles :
    entre deux, on réutilise le dernier prix enregistré ; la stratégie vérifie son âge)."""
    from polymarket_agent.sources.crypto_prices import CryptoQuote
    best = {}
    for o in observations:
        if o.source != "crypto_prices" or "asset" not in o.data or o.published_at is None:
            continue
        asset = o.data["asset"]
        if asset not in best or o.published_at > best[asset].as_of:
            best[asset] = CryptoQuote(asset, float(o.data["price"]), float(o.data["hourly_vol"]),
                                      o.published_at, o.domain)
    return best


def make_collector(settings: dict, http: HttpClient, db, factories: dict | None = None):
    llm_cfg = settings.get("llm", {})
    # Gemini peut mettre plus de 15 s à classer 20 textes : délai plus long, aucun nouvel essai ;
    # en cas de refus ou de lenteur, mieux vaut passer au modèle suivant.
    gemini_http = with_retries(http, llm_cfg.get("max_retries", 0), llm_cfg.get("timeout_seconds", 40))
    gemini = (GeminiClassifier(gemini_http, llm_cfg.get("model", "gemini-2.5-flash"),
                               int(llm_cfg.get("max_calls_per_day", 0)), db)
              if llm_cfg.get("enabled") else None)

    def run(markets: list[MarketInfo], now: datetime) -> dict[str, str]:
        collection = collect(settings, http, db, markets, now, factories)
        recent = load_recent(db, now) if db else collection.observations
        stances: dict[str, dict] = {}
        status = dict(collection.status)
        if gemini is not None and gemini.available:
            busiest = sorted(markets, key=lambda m: -sum(1 for o in recent if m.market_id in o.market_ids))
            try:
                for market in busiest[: int(llm_cfg.get("markets_per_cycle", 2))]:
                    obs = [o for o in recent if market.market_id in o.market_ids and not o.duplicate_of]
                    if len(obs) >= 2:
                        stances.update(gemini.classify(market.question, obs, now))
                status["gemini"] = f"ok ({len(stances)} textes classés)"
            except SourceUnavailable as exc:
                status["gemini"] = f"indisponible : {exc}"[:200]
        else:
            status["gemini"] = "désactivée (pas de clé GEMINI_API_KEY)"
        down = [n for n, s in status.items() if s.startswith("indisponible")]
        quotes = latest_quotes(recent)
        quotes.update(collection.crypto)  # les prix tout juste collectés priment
        for market in markets:
            market.intel = summarize(market.market_id, recent, now, down, stances)
            group = correlation_group(market)
            if group.startswith("crypto:"):
                market.crypto_quote = quotes.get(group.split(":")[1])
        return status

    return run
