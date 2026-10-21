"""Market Scanner : découvre les marchés, détecte les incohérences, choisit la liste de surveillance."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from polymarket_agent.models import MarketInfo
from polymarket_agent.sources.polymarket_gamma import GammaClient, parse_market

log = logging.getLogger(__name__)


@dataclass
class ScanResult:
    markets: list[MarketInfo] = field(default_factory=list)
    watchlist: list[MarketInfo] = field(default_factory=list)
    excluded: dict[str, int] = field(default_factory=dict)


def classify(market: MarketInfo, now: datetime, cfg: dict) -> str:
    """Retourne '' si le marché est exploitable, sinon la raison d'exclusion."""
    if market.issues:
        return "données incohérentes"
    if not market.active or market.closed:
        return "inactif ou fermé"
    if not market.enable_order_book or not market.accepting_orders:
        return "carnet indisponible"
    end_min = now + timedelta(minutes=cfg["min_horizon_minutes"])
    end_max = now + timedelta(hours=cfg["max_horizon_hours"])
    if market.end_date is None or not (end_min <= market.end_date <= end_max):
        return "hors horizon"
    if market.liquidity < Decimal(str(cfg["min_liquidity"])):
        return "liquidité insuffisante"
    if market.volume_24h < Decimal(str(cfg["min_volume_24h"])):
        return "volume insuffisant"
    if market.spread is None or market.spread > Decimal(str(cfg["max_spread"])):
        return "écart achat/vente trop large"
    extreme = Decimal(str(cfg.get("max_favorite_price", 0.99)))
    if market.best_ask >= extreme or market.best_bid <= 1 - extreme:
        return "issue quasi certaine (match joué ou info déjà connue)"
    return ""


def _add_holding_markets(gamma: GammaClient, now: datetime, cfg: dict, result: ScanResult, seen: set[str]) -> None:
    """Marchés LONGS à récompense de détention (19/10/2026) : l'horizon normal (30 jours) les
    écartait tous (la plupart se règlent en 2027-2028), parking_politique ne pouvait rien acheter.
    `holding_pages` pages de plus, triées par volume, jusqu'à `holding_max_horizon_days` ; seuls
    les marchés éligibles à la récompense sont gardés, avec les mêmes filtres que les autres."""
    pages = int(cfg.get("holding_pages", 0) or 0)
    if pages <= 0:
        return
    days = float(cfg.get("holding_max_horizon_days", 900))
    long_cfg = dict(cfg, max_horizon_hours=days * 24)
    try:
        raw = gamma.list_markets(end_min=now + timedelta(hours=cfg["max_horizon_hours"]),
                                 end_max=now + timedelta(days=days), page_size=cfg["page_size"], max_pages=pages)
    except Exception as exc:  # noqa: BLE001 - un complément ne doit jamais bloquer le scan normal
        log.warning("scanner : marchés à récompense de détention indisponibles (%s)", exc)
        return
    for item in raw:
        market = parse_market(item)
        if market.market_id in seen or not market.holding_rewards:
            continue
        seen.add(market.market_id)
        market.exclusion = classify(market, now, long_cfg)
        market.eligible = not market.exclusion
        if market.exclusion:
            result.excluded[market.exclusion] = result.excluded.get(market.exclusion, 0) + 1
        result.markets.append(market)


def _add_tag_markets(gamma: GammaClient, now: datetime, cfg: dict, result: ScanResult, seen: set[str]) -> None:
    """Marchés d'une étiquette précise (21/10/2026) : les marchés « mentions » (étiquette 100343)
    ont peu de volume et n'entraient presque jamais dans les pages triées par volume ;
    mots_prononces (retenue sur le passé) ne voyait aucun marché. `tag_pages: {étiquette: pages}` ou
    `{étiquette: {pages, min_liquidity, ...}}` : filtres propres à l'étiquette (ces marchés ont
    rarement 1 000 $ de liquidité ; le carnet réel décide de toute façon de ce qui s'exécute)."""
    for tag, spec in (cfg.get("tag_pages") or {}).items():
        spec = dict(spec) if isinstance(spec, dict) else {"pages": spec}
        pages = int(spec.pop("pages", 0) or 0)
        if pages <= 0:
            continue
        tag_cfg = dict(cfg, **spec)
        try:
            raw = gamma.list_markets(end_min=now, end_max=now + timedelta(hours=cfg["max_horizon_hours"]),
                                     page_size=cfg["page_size"], max_pages=pages, tag_id=tag)
        except Exception as exc:  # noqa: BLE001 - un complément ne doit jamais bloquer le scan normal
            log.warning("scanner : marchés de l'étiquette %s indisponibles (%s)", tag, exc)
            continue
        for item in raw:
            market = parse_market(item)
            if market.market_id in seen:
                continue
            seen.add(market.market_id)
            market.exclusion = classify(market, now, tag_cfg)
            market.eligible = not market.exclusion
            if market.exclusion:
                result.excluded[market.exclusion] = result.excluded.get(market.exclusion, 0) + 1
            result.markets.append(market)


def _add_ended_markets(gamma: GammaClient, now: datetime, cfg: dict, result: ScanResult, seen: set[str]) -> None:
    """Marchés dont l'échéance vient de PASSER (20/10/2026, stratégie apres_echeance) : encore
    échangés en attendant la résolution officielle. `ended_pages` pages, échéance entre
    `ended_max_hours` et `ended_min_hours` heures dans le passé, mêmes filtres sinon."""
    pages = int(cfg.get("ended_pages", 0) or 0)
    if pages <= 0:
        return
    oldest, newest = float(cfg.get("ended_max_hours", 72)), float(cfg.get("ended_min_hours", 1))
    past_cfg = dict(cfg, min_horizon_minutes=-oldest * 60, max_horizon_hours=-newest)
    try:
        raw = gamma.list_markets(end_min=now - timedelta(hours=oldest), end_max=now - timedelta(hours=newest),
                                 page_size=cfg["page_size"], max_pages=pages)
    except Exception as exc:  # noqa: BLE001 - un complément ne doit jamais bloquer le scan normal
        log.warning("scanner : marchés échus indisponibles (%s)", exc)
        return
    for item in raw:
        market = parse_market(item)
        if market.market_id in seen:
            continue
        seen.add(market.market_id)
        market.exclusion = classify(market, now, past_cfg)
        market.eligible = not market.exclusion
        market.ended = True
        if market.exclusion:
            result.excluded[market.exclusion] = result.excluded.get(market.exclusion, 0) + 1
        result.markets.append(market)


def scan(gamma: GammaClient, now: datetime, cfg: dict) -> ScanResult:
    raw = gamma.list_markets(
        end_min=now + timedelta(minutes=cfg["min_horizon_minutes"]),
        end_max=now + timedelta(hours=cfg["max_horizon_hours"]),
        page_size=cfg["page_size"], max_pages=cfg["max_pages"],
    )
    result = ScanResult()
    seen: set[str] = set()
    for item in raw:
        market = parse_market(item)
        if market.market_id in seen:
            continue
        seen.add(market.market_id)
        market.exclusion = classify(market, now, cfg)
        market.eligible = not market.exclusion
        if market.exclusion:
            result.excluded[market.exclusion] = result.excluded.get(market.exclusion, 0) + 1
        result.markets.append(market)
    _add_holding_markets(gamma, now, cfg, result, seen)
    _add_tag_markets(gamma, now, cfg, result, seen)
    _add_ended_markets(gamma, now, cfg, result, seen)
    eligible = sorted((m for m in result.markets if m.eligible and not m.ended), key=lambda m: m.volume_24h, reverse=True)
    result.watchlist = eligible[: cfg["watchlist_size"]]
    log.info("scanner : %d marchés, %d exploitables, %d surveillés, exclusions %s",
             len(result.markets), len(eligible), len(result.watchlist), result.excluded)
    return result
