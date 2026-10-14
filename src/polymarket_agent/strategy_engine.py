"""Strategy Engine : les stratégies PROPOSENT, le contrôleur de sécurité décide.

Chaque stratégie a un identifiant, une version, une date de création, des
paramètres bornés (config/strategies.yaml) et un historique (base SQLite).
Étape 3 : une seule stratégie, la référence naïve « naive_favorite ».
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml

from polymarket_agent.fees import UnknownFees, taker_fee
from polymarket_agent.ledger import LedgerState
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.portfolio_manager import size_buy
from polymarket_agent.safety_controller import Proposal, RiskLimits

log = logging.getLogger(__name__)
ONE = Decimal("1")


class StrategyConfigError(Exception):
    pass


def make_op_id(bucket: str, strategy_id: str, version: str, token_id: str, side: str) -> str:
    """Identifiant déterministe : relancer le même cycle redonne le même identifiant,
    donc l'opération ne peut pas être comptabilisée deux fois."""
    raw = f"{bucket}|{strategy_id}|{version}|{token_id}|{side}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def load_params(spec: dict) -> dict[str, Decimal]:
    """Lit les paramètres et vérifie qu'ils restent dans leurs bornes."""
    params: dict[str, Decimal] = {}
    for name, item in (spec or {}).items():
        try:
            value, low, high = (Decimal(str(item[k])) for k in ("value", "min", "max"))
        except (KeyError, TypeError, ArithmeticError) as exc:
            raise StrategyConfigError(f"paramètre {name} mal formé") from exc
        if not (low <= value <= high):
            raise StrategyConfigError(f"paramètre {name}={value} hors des bornes [{low}, {high}]")
        params[name] = value
    return params


@dataclass
class StrategyOutput:
    proposals: list[Proposal] = field(default_factory=list)
    abstentions: dict[str, int] = field(default_factory=dict)

    def abstain(self, reason: str) -> None:
        self.abstentions[reason] = self.abstentions.get(reason, 0) + 1


class NaiveFavorite:
    """Référence naïve : acheter le favori (prix 0,80–0,95) d'un marché qui se résout bientôt.

    Probabilité estimée = milieu du carnet + biais a priori (NON calibré), avec un
    intervalle ± incertitude. L'avantage est calculé sur la borne basse, après frais,
    au prix exécutable (pas au dernier prix affiché).
    """

    strategy_id = "naive_favorite"
    required = ("min_ask", "max_ask", "bias", "uncertainty", "min_net_edge",
                "max_extra_ticks", "max_proposals_per_cycle")

    def __init__(self, version: str, created_at: str, params: dict[str, Decimal]):
        missing = [p for p in self.required if p not in params]
        if missing:
            raise StrategyConfigError(f"{self.strategy_id} : paramètres manquants {missing}")
        self.version = version
        self.created_at = created_at
        self.params = params

    def propose(self, watchlist: list[MarketInfo], books: dict[str, OrderBook],
                state: LedgerState, limits: RiskLimits, bucket: str,
                marks: dict[str, Decimal] | None = None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        min_edge = max(p["min_net_edge"], limits.min_net_edge_floor)
        candidates: list[tuple[Decimal, Proposal]] = []
        for market in watchlist:
            if not market.outcome_prices or len(market.token_ids) != 2:
                out.abstain("marché non binaire")
                continue
            idx = 0 if market.outcome_prices[0] >= market.outcome_prices[1] else 1
            token_id = market.token_ids[idx]
            if token_id in state.positions:
                out.abstain("position déjà ouverte")
                continue
            book = books.get(token_id)
            if book is None or book.best_ask is None or book.mid is None:
                out.abstain("carnet indisponible")
                continue
            ask = book.best_ask
            if not (p["min_ask"] <= ask <= p["max_ask"]):
                out.abstain("favori hors de la plage de prix")
                continue
            q = min(book.mid + p["bias"], Decimal("0.99"))
            low = q - p["uncertainty"]
            high = min(q + p["uncertainty"], Decimal("0.995"))
            best: tuple[Decimal, Decimal] | None = None  # (prix limite, coût par part)
            tick = book.tick_size
            try:
                for k in range(int(p["max_extra_ticks"]) + 1):
                    price = ask + tick * k
                    if price >= ONE:
                        break
                    cost_ps = price + taker_fee(ONE, price, market.fees)
                    if low - cost_ps >= min_edge:
                        best = (price, cost_ps)
            except UnknownFees:
                out.abstain("frais inconnus")
                continue
            if best is None:
                out.abstain("avantage net insuffisant")
                continue
            max_price, cost_ps = best
            shares = size_buy(state, limits, token_id=token_id, event_id=market.event_id,
                              prob_low=low, cost_per_share=cost_ps, marks=marks)
            if shares < max(market.min_order_size, book.min_order_size):
                out.abstain("taille autorisée trop faible")
                continue
            edge = low - cost_ps
            candidates.append((edge, Proposal(
                op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "BUY"),
                side="BUY", market_id=market.market_id, event_id=market.event_id,
                token_id=token_id, outcome=market.outcomes[idx], est_probability=q,
                prob_low=low, prob_high=high, max_price=max_price, shares=shares,
                net_edge=edge, sources=("polymarket_gamma", "polymarket_clob"),
                uncertainty=f"a priori non calibré ± {p['uncertainty']}",
                invalidation="prix du favori < 0,70 ou règles de résolution ambiguës",
                horizon_hours=Decimal(str(round(
                    max((market.end_date - book.fetched_at).total_seconds(), 0) / 3600, 2))),
                strategy_id=self.strategy_id, strategy_version=self.version,
            )))
        candidates.sort(key=lambda item: item[0], reverse=True)
        out.proposals = [prop for _, prop in candidates[: int(p["max_proposals_per_cycle"])]]
        return out


STRATEGY_CLASSES: dict[str, Any] = {NaiveFavorite.strategy_id: NaiveFavorite}


def load_strategies(path: Path) -> list[NaiveFavorite]:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise StrategyConfigError(f"impossible de lire {path}") from exc
    strategies = []
    for strategy_id, spec in raw.items():
        if not isinstance(spec, dict) or not spec.get("enabled"):
            continue
        cls = STRATEGY_CLASSES.get(strategy_id)
        if cls is None:
            raise StrategyConfigError(f"stratégie inconnue : {strategy_id}")
        strategies.append(cls(str(spec["version"]), str(spec["created_at"]),
                              load_params(spec.get("params"))))
    return strategies
