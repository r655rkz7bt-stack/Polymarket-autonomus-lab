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
from polymarket_agent.sources.weather import station_of

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


def latest_weather(observations, now: datetime, max_age_hours: float = 8) -> dict[str, dict]:
    """Par station : dernier relevé meteo_metar (ses données au premier niveau, avec `published_at`,
    format attendu par temperature_floor) et dernière prévision meteo_prevision (clé "prevision")."""
    from datetime import timedelta
    out: dict[str, dict] = {}
    seen: dict[tuple[str, str], datetime] = {}
    for o in observations:
        if o.source not in ("meteo_prevision", "meteo_metar") or o.published_at is None:
            continue
        if now - o.published_at > timedelta(hours=max_age_hours) or "station" not in o.data:
            continue
        key = (o.data["station"], o.source)
        if key in seen and seen[key] >= o.published_at:
            continue
        seen[key] = o.published_at
        entry = out.setdefault(o.data["station"], {})
        if o.source == "meteo_prevision":
            entry["prevision"] = dict(o.data, published_at=o.published_at)
        else:
            entry.update(o.data, published_at=o.published_at)
    return out


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
                # Budget de l'heure atteint : une pause voulue (appels étalés sur 24 h), pas une panne.
                status["gemini"] = (f"en pause : {exc}" if "budget" in str(exc) else f"indisponible : {exc}")[:200]
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
        weather = latest_weather(recent, now)
        down = [n for n, s in status.items() if s.startswith("indisponible")]
        quotes = latest_quotes(recent)
        quotes.update(collection.crypto)  # les prix tout juste collectés priment
        # Sport : score officiel et cotes des bookmakers de chaque marché « A vs. B » (sports_link.py).
        from polymarket_agent import sports_link
        linked = sports_link.attach(markets, recent)
        if linked:
            status["liaison_sport"] = f"ok ({linked} marchés reliés à leur match ou à leurs cotes)"
        # Vingt nouvelles pistes, lot B : prix de la même question ailleurs (references.py). Les
        # références tirées des instantanés de la base sont rattachées en amont, à TOUS les marchés
        # scannés (main, 21/10/2026) ; ici seulement le football à 3 issues (cotes du jour).
        from polymarket_agent import references
        try:
            status["references_football"] = f"ok ({references.attach_football(markets, recent)} marchés)"
        except Exception as exc:  # noqa: BLE001 - un rattachement ne bloque jamais le cycle
            status["references_football"] = f"erreur : {type(exc).__name__}: {exc}"[:200]
        for market in markets:
            market.intel = summarize(market.market_id, recent, now, down, stances.get(market.market_id, {}))
            # Météo de la station qui tranche le marché : relevé (temperature_floor) + prévision.
            station = station_of(market.resolution_source, market.description)
            market.weather = weather.get(station) if station else None
            group = correlation_group(market)
            if group.startswith("crypto:"):
                market.crypto_quote = quotes.get(group.split(":")[1])
        return status

    return run
