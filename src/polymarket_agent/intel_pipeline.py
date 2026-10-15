"""Assemble l'étape 5 pour le cycle : collecte → observations des 24 h → résumé par marché
→ (option) classement Gemini → caractéristiques attachées aux marchés surveillés."""

from __future__ import annotations

import logging
from datetime import datetime

from polymarket_agent.correlation import correlation_group
from polymarket_agent import resolution_sources, stance_eval
from polymarket_agent.data_collector import _due, collect, load_recent, with_retries
from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.models import MarketInfo
from polymarket_agent.social_intelligence import summarize
from polymarket_agent.sources.gemini import GeminiClassifier
from polymarket_agent.sources.polymarket_gamma import GammaClient

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
        # Avis classés PAR MARCHÉ : un même article peut être favorable à une question et
        # défavorable à une autre.
        stances: dict[str, dict[str, dict]] = {}
        status = dict(collection.status)
        if gemini is not None and gemini.available:
            busiest = sorted(markets, key=lambda m: -sum(1 for o in recent if m.market_id in o.market_ids))
            try:
                fresh_count = 0
                for market in busiest[: int(llm_cfg.get("markets_per_cycle", 2))]:
                    obs = [o for o in recent if market.market_id in o.market_ids and not o.duplicate_of]
                    if len(obs) < 2:
                        continue
                    # Seuls les textes jamais classés pour ce marché sont envoyés à Gemini.
                    known = db.get_stances(market.market_id, [o.external_id for o in obs]) if db else {}
                    new = [o for o in obs if o.external_id not in known]
                    fresh = gemini.classify(market.question, new, now) if new else {}
                    if db and fresh:
                        db.save_stances(market.market_id, fresh, now)
                    fresh_count += len(fresh)
                    stances[market.market_id] = dict(known, **fresh)
                total = sum(len(v) for v in stances.values())
                status["gemini"] = (f"ok ({fresh_count} nouveaux textes classés, {total} avis sur "
                                    f"{len(stances)} marchés)")
            except SourceUnavailable as exc:
                status["gemini"] = f"indisponible : {exc}"[:200]
        else:
            status["gemini"] = "désactivée (pas de clé GEMINI_API_KEY)"
        # Justesse de Gemini : ses avis comparés au résultat des marchés résolus (une fois par heure).
        if db is not None:
            ev = llm_cfg.get("evaluation", {})
            if _due(db, "justesse_gemini", float(ev.get("every_minutes", 60)), now):
                try:
                    get_market = (factories or {}).get("gamma_get_market") or GammaClient(
                        http, settings.get("sources", {}).get("polymarket_gamma", {}).get(
                            "base_url", "https://gamma-api.polymarket.com")).get_market
                    stance_eval.update_outcomes(db, get_market, now, int(ev.get("markets_per_run", 10)))
                except Exception as exc:  # noqa: BLE001 - une mesure de recherche ne bloque jamais le cycle
                    log.warning("justesse Gemini non mise à jour : %s", exc)
                db.set_source_run("justesse_gemini", now)
            status["justesse_gemini"] = stance_eval.status_text(stance_eval.score(db))
        # Source de résolution des marchés surveillés : archivée une fois par heure (chantier n°0).
        res_cfg = settings.get("sources", {}).get("sources_resolution", {})
        if db is not None and res_cfg.get("enabled", True):
            try:
                if _due(db, "sources_resolution", float(res_cfg.get("every_minutes", 60)), now):
                    resolution_sources.archive(db, markets, now)
                    db.set_source_run("sources_resolution", now)
                status["sources_resolution"] = resolution_sources.status_text(db)
            except Exception as exc:  # noqa: BLE001 - un inventaire ne bloque jamais le cycle
                status["sources_resolution"] = f"erreur : {type(exc).__name__}: {exc}"[:200]
        down = [n for n, s in status.items() if s.startswith("indisponible")]
        quotes = latest_quotes(recent)
        quotes.update(collection.crypto)  # les prix tout juste collectés priment
        for market in markets:
            market.intel = summarize(market.market_id, recent, now, down, stances.get(market.market_id, {}))
            group = correlation_group(market)
            if group.startswith("crypto:"):
                market.crypto_quote = quotes.get(group.split(":")[1])
        return status

    return run
