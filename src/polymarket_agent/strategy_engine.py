"""Strategy Engine : les stratégies PROPOSENT, le contrôleur de sécurité décide.

Chaque stratégie a un identifiant, une version, une date de création, des
paramètres bornés (config/strategies.yaml) et un historique (base SQLite).
Étape 4 : la référence naïve « naive_favorite » (v1) et la stratégie « calibration ».
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
        min_edge = p["min_net_edge"]  # liberté totale : plus de plancher imposé
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
            shares = size_buy(state, prob_low=low, cost_per_share=cost_ps,
                              kelly_fraction=p.get("kelly_fraction", Decimal("1")), marks=marks)
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


def market_category(market: MarketInfo) -> str:
    """Même règle que l'historique : la catégorie vient du barème de frais du marché."""
    if market.fees.enabled and market.fees.fee_type:
        return market.fees.fee_type.split("_")[0]
    return "other"


def best_limit_price(book: OrderBook, market: MarketInfo, prob_low: Decimal, min_edge: Decimal,
                     max_extra_ticks: int) -> tuple[Decimal, Decimal] | None:
    """Prix limite le plus haut (en ticks au-dessus du meilleur ask) qui garde l'avantage
    net >= min_edge. Retourne (prix limite, coût par part frais compris) ou None."""
    if book.best_ask is None:
        return None
    best = None
    for k in range(max_extra_ticks + 1):
        price = book.best_ask + book.tick_size * k
        if price >= ONE:
            break
        cost_ps = price + taker_fee(ONE, price, market.fees)
        if prob_low - cost_ps >= min_edge:
            best = (price, cost_ps)
    return best


class CalibratedStrategy:
    """Probability mispricing par calibration historique (cahier des charges, stratégie 4).

    Probabilité estimée = prix du marché + écart δ mesuré sur l'historique pour la même
    case (catégorie × horizon × prix du favori), avec son intervalle de confiance. On
    n'achète que si la BORNE BASSE dépasse le prix exécutable + frais + marge. Une case
    sans assez d'événements → abstention (pas de probabilité inventée).
    """

    strategy_id = "calibration"
    required = ("min_events", "min_net_edge", "max_extra_ticks", "max_proposals_per_cycle")

    def __init__(self, version: str, created_at: str, params: dict[str, Decimal], table_path: Path):
        from polymarket_agent import calibration

        missing = [p for p in self.required if p not in params]
        if missing:
            raise StrategyConfigError(f"{self.strategy_id} : paramètres manquants {missing}")
        self.version, self.created_at, self.params = version, created_at, params
        self.table, self.table_meta = calibration.load(table_path)
        self._cell_key = calibration.cell_key

    def propose(self, watchlist: list[MarketInfo], books: dict[str, OrderBook],
                state: LedgerState, limits: RiskLimits, bucket: str,
                marks: dict[str, Decimal] | None = None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        min_edge = p["min_net_edge"]  # liberté totale : plus de plancher imposé
        candidates: list[tuple[Decimal, Proposal]] = []
        for market in watchlist:
            if len(market.token_ids) != 2 or market.end_date is None:
                out.abstain("marché non binaire")
                continue
            yes_book, no_book = books.get(market.token_ids[0]), books.get(market.token_ids[1])
            if yes_book is None or no_book is None or yes_book.mid is None:
                out.abstain("carnet indisponible")
                continue
            if any(t in state.positions for t in market.token_ids):
                out.abstain("position déjà ouverte")
                continue
            # Même univers que l'historique (volume final >= seuil) : ici le volume déjà
            # échangé, plus restrictif car il ne peut que grandir.
            if market.volume_total < p.get("min_volume", Decimal("0")):
                out.abstain("volume cumulé sous le seuil de l'historique")
                continue
            p_yes = float(yes_book.mid)
            fav = 0 if p_yes >= 0.5 else 1
            f = p_yes if fav == 0 else 1 - p_yes
            hours = (market.end_date - yes_book.fetched_at).total_seconds() / 3600
            key = self._cell_key(market_category(market), hours, f)
            cell = self.table.get(key) if key else None
            if cell is None or cell.n_events < int(p["min_events"]):
                out.abstain("case de calibration absente ou trop petite")
                continue
            proposal = self._proposal(market, books, state, limits, bucket, marks, out, f, fav,
                                      cell, min_edge, f"calibration:{key}")
            if proposal is not None:
                candidates.append((proposal.net_edge, proposal))
        candidates.sort(key=lambda item: item[0], reverse=True)
        out.proposals = [prop for _, prop in candidates[: int(p["max_proposals_per_cycle"])]]
        return out

    def _proposal(self, market, books, state, limits, bucket, marks, out, f, fav, cell,
                  min_edge, source) -> Proposal | None:
        """Favori d'abord, puis outsider : borne basse contre le prix exécutable réel."""
        q_fav = (f + cell.delta_low, f + cell.delta_shrunk, f + cell.delta_high)
        options = [(fav, q_fav), (1 - fav, (1 - q_fav[2], 1 - q_fav[1], 1 - q_fav[0]))]
        chosen = None
        try:
            for side, (low, est, high) in options:
                book = books[market.token_ids[side]]
                limit = best_limit_price(book, market, Decimal(str(round(low, 6))), min_edge,
                                         int(self.params["max_extra_ticks"]))
                if limit is not None:
                    chosen = (side, low, est, high, book, limit)
                    break
        except UnknownFees:
            out.abstain("frais inconnus")
            return None
        if chosen is None:
            out.abstain("avantage net insuffisant")
            return None
        side, low, est, high, book, (max_price, cost_ps) = chosen
        token_id = market.token_ids[side]
        low_d = Decimal(str(round(low, 6)))
        shares = size_buy(state, prob_low=low_d, cost_per_share=cost_ps,
                          kelly_fraction=self.params.get("kelly_fraction", Decimal("1")), marks=marks)
        if shares < max(market.min_order_size, book.min_order_size):
            out.abstain("taille autorisée trop faible")
            return None
        hours = (market.end_date - book.fetched_at).total_seconds() / 3600
        return Proposal(
            op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "BUY"),
            side="BUY", market_id=market.market_id, event_id=market.event_id,
            token_id=token_id, outcome=market.outcomes[side],
            est_probability=Decimal(str(round(est, 6))), prob_low=low_d,
            prob_high=Decimal(str(round(min(high, 0.995), 6))), max_price=max_price,
            shares=shares, net_edge=low_d - cost_ps, sources=("polymarket_clob", source),
            uncertainty=f"IC 90 % de δ, {cell.n_events} événements d'entraînement",
            invalidation="règles de résolution ambiguës ; table de calibration révisée",
            horizon_hours=Decimal(str(round(hours, 2))),
            strategy_id=self.strategy_id, strategy_version=self.version)


class ReversionStrategy(CalibratedStrategy):
    """Mean reversion conditionnelle (cahier des charges, stratégie 1).

    Si le prix du favori a bougé d'au moins `min_move` en 6 h, sa probabilité est estimée
    par prix + δ mesuré sur l'historique après un mouvement de même sens (table
    `reversion_v1.json`). Mêmes règles d'achat que « calibration » : borne basse contre
    le prix exécutable réel + frais + marge. Caractéristiques de prix calculées comme dans
    le backtest (price_features.py). Prix 6 h avant inconnu → abstention.
    """

    strategy_id = "reversion"
    needs_price_history = True
    required = ("min_move", "min_changes_24h", "min_events", "min_net_edge", "max_extra_ticks",
                "max_proposals_per_cycle")

    def propose(self, watchlist: list[MarketInfo], books: dict[str, OrderBook],
                state: LedgerState, limits: RiskLimits, bucket: str,
                marks: dict[str, Decimal] | None = None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        min_edge = p["min_net_edge"]  # liberté totale : plus de plancher imposé
        candidates: list[tuple[Decimal, Proposal]] = []
        for market in watchlist:
            if len(market.token_ids) != 2 or market.end_date is None:
                out.abstain("marché non binaire")
                continue
            if market.yes_price_6h_ago is None or market.changes_24h is None:
                out.abstain("historique de prix indisponible")
                continue
            if market.changes_24h < int(p["min_changes_24h"]):
                out.abstain("marché trop peu actif sur 24 h")
                continue
            yes_book, no_book = books.get(market.token_ids[0]), books.get(market.token_ids[1])
            if yes_book is None or no_book is None or yes_book.mid is None:
                out.abstain("carnet indisponible")
                continue
            if any(t in state.positions for t in market.token_ids):
                out.abstain("position déjà ouverte")
                continue
            p_yes = float(yes_book.mid)
            fav = 0 if p_yes >= 0.5 else 1
            f = p_yes if fav == 0 else 1 - p_yes
            before = market.yes_price_6h_ago if fav == 0 else 1 - market.yes_price_6h_ago
            if abs(f - before) < float(p["min_move"]):
                out.abstain("pas de mouvement brusque")
                continue
            direction = "hausse" if f > before else "baisse"
            cell = self.table.get(direction)
            if cell is None or cell.n_events < int(p["min_events"]):
                out.abstain("case de calibration absente ou trop petite")
                continue
            proposal = self._proposal(market, books, state, limits, bucket, marks, out, f, fav,
                                      cell, min_edge, f"reversion:{direction}")
            if proposal is not None:
                candidates.append((proposal.net_edge, proposal))
        candidates.sort(key=lambda item: item[0], reverse=True)
        out.proposals = [prop for _, prop in candidates[: int(p["max_proposals_per_cycle"])]]
        return out


class CryptoThresholdStrategy:
    """Marchés crypto à seuil : probabilité INDÉPENDANTE tirée du prix au comptant et de la
    volatilité réalisée (crypto_model.py), comparée au prix exécutable réel.

    Achète « Oui » si la borne basse de P(Oui) dépasse ask + frais + min_net_edge, ou « Non »
    si la borne basse de P(Non) le fait. Données de prix de plus de `max_quote_age_minutes`
    → abstention.
    """

    strategy_id = "crypto_threshold"
    required = ("min_net_edge", "max_extra_ticks", "max_proposals_per_cycle", "max_quote_age_minutes",
                "min_hours")

    def __init__(self, version: str, created_at: str, params: dict[str, Decimal]):
        missing = [p for p in self.required if p not in params]
        if missing:
            raise StrategyConfigError(f"{self.strategy_id} : paramètres manquants {missing}")
        self.version, self.created_at, self.params = version, created_at, params

    def propose(self, watchlist: list[MarketInfo], books: dict[str, OrderBook],
                state: LedgerState, limits: RiskLimits, bucket: str,
                marks: dict[str, Decimal] | None = None) -> StrategyOutput:
        from polymarket_agent.crypto_model import parse_question, probability_band

        out = StrategyOutput()
        p = self.params
        candidates: list[tuple[Decimal, Proposal]] = []
        for market in watchlist:
            question = parse_question(market.question)
            if question is None or len(market.token_ids) != 2 or market.end_date is None:
                out.abstain("pas un marché crypto à seuil")
                continue
            quote = market.crypto_quote
            if quote is None:
                out.abstain("prix crypto indisponible")
                continue
            yes_book, no_book = books.get(market.token_ids[0]), books.get(market.token_ids[1])
            if yes_book is None or no_book is None:
                out.abstain("carnet indisponible")
                continue
            if (yes_book.fetched_at - quote.as_of).total_seconds() > float(p["max_quote_age_minutes"]) * 60:
                out.abstain("prix crypto périmé")
                continue
            if any(t in state.positions for t in market.token_ids):
                out.abstain("position déjà ouverte")
                continue
            hours = (market.end_date - yes_book.fetched_at).total_seconds() / 3600
            if hours < float(p["min_hours"]):
                out.abstain("échéance trop proche")
                continue
            band = probability_band(question, quote.price, quote.hourly_vol, hours)
            if band is None:
                out.abstain("issue déjà connue ou données absurdes")
                continue
            low, est, high = band
            chosen = None
            try:
                for side, (s_low, s_est, s_high) in ((0, (low, est, high)), (1, (1 - high, 1 - est, 1 - low))):
                    book = books[market.token_ids[side]]
                    limit = best_limit_price(book, market, Decimal(str(round(s_low, 6))), p["min_net_edge"],
                                             int(p["max_extra_ticks"]))
                    if limit is not None:
                        chosen = (side, s_low, s_est, s_high, book, limit)
                        break
            except UnknownFees:
                out.abstain("frais inconnus")
                continue
            if chosen is None:
                out.abstain("avantage net insuffisant")
                continue
            side, s_low, s_est, s_high, book, (max_price, cost_ps) = chosen
            low_d = Decimal(str(round(s_low, 6)))
            shares = size_buy(state, prob_low=low_d, cost_per_share=cost_ps,
                              kelly_fraction=p.get("kelly_fraction", Decimal("1")), marks=marks)
            if shares < max(market.min_order_size, book.min_order_size):
                out.abstain("taille autorisée trop faible")
                continue
            token_id = market.token_ids[side]
            candidates.append((low_d - cost_ps, Proposal(
                op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "BUY"),
                side="BUY", market_id=market.market_id, event_id=market.event_id, token_id=token_id,
                outcome=market.outcomes[side], est_probability=Decimal(str(round(s_est, 6))),
                prob_low=low_d, prob_high=Decimal(str(round(min(s_high, 0.999), 6))),
                max_price=max_price, shares=shares, net_edge=low_d - cost_ps,
                sources=("polymarket_clob", f"crypto_prices:{quote.source}"),
                uncertainty=f"volatilité ×0,75 à ×1,5 ; prix {quote.price:.2f}, σ horaire {quote.hourly_vol:.4%}",
                invalidation="saut de prix, source de résolution différente, question mal comprise",
                horizon_hours=Decimal(str(round(hours, 2))),
                strategy_id=self.strategy_id, strategy_version=self.version)))
        candidates.sort(key=lambda item: item[0], reverse=True)
        out.proposals = [prop for _, prop in candidates[: int(p["max_proposals_per_cycle"])]]
        return out


STRATEGY_CLASSES: dict[str, Any] = {NaiveFavorite.strategy_id: NaiveFavorite,
                                    CryptoThresholdStrategy.strategy_id: CryptoThresholdStrategy,
                                    CalibratedStrategy.strategy_id: CalibratedStrategy,
                                    ReversionStrategy.strategy_id: ReversionStrategy}


def load_strategies(path: Path) -> list:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise StrategyConfigError(f"impossible de lire {path}") from exc
    from polymarket_agent.strategies_v2 import CLASSES as V2  # import tardif : évite une boucle

    classes = dict(STRATEGY_CLASSES, **V2)
    strategies = []
    for strategy_id, spec in raw.items():
        if not isinstance(spec, dict) or not spec.get("enabled"):
            continue
        cls = classes.get(strategy_id)
        if cls is None:
            raise StrategyConfigError(f"stratégie inconnue : {strategy_id}")
        args = [str(spec["version"]), str(spec["created_at"]), load_params(spec.get("params"))]
        if "table" in spec:
            args.append(Path(path).parent / str(spec["table"]))
        strategy = cls(*args)
        mode = str(spec.get("mode", "principal"))
        if mode not in ("principal", "fantome"):
            raise StrategyConfigError(f"{strategy_id} : mode inconnu {mode!r}")
        strategy.mode = mode  # « fantome » : journal séparé, ne touche jamais le capital principal
        strategies.append(strategy)
    return strategies
