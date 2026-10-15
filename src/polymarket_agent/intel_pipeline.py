"""Assemble l'étape 5 pour le cycle : collecte → observations des 24 h → résumé par marché
→ (option) classement Gemini → caractéristiques attachées aux marchés surveillés."""

from __future__ import annotations

import logging
from datetime import datetime

from polymarket_agent.correlation import correlation_group
from polymarket_agent.data_collector import collect, load_recent
from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.models import MarketInfo
from polymarket_agent.social_intelligence import summarize
from polymarket_agent.sources.gemini import GeminiClassifier

log = logging.getLogger(__name__)


def make_collector(settings: dict, http: HttpClient, db, factories: dict | None = None):
    llm_cfg = settings.get("llm", {})
    gemini = (GeminiClassifier(http, llm_cfg.get("model", "gemini-2.5-flash"),
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
        for market in markets:
            market.intel = summarize(market.market_id, recent, now, down, stances)
            group = correlation_group(market)
            if group.startswith("crypto:"):
                market.crypto_quote = collection.crypto.get(group.split(":")[1])
        return status

    return run
