"""Strategy Engine : les stratégies PROPOSENT, le contrôleur de sécurité décide.

Chaque stratégie a un identifiant, une version, une date de création, des
paramètres bornés (config/strategies.yaml) et un historique (base SQLite).
Étape 4 : la référence naïve « naive_favorite » (v1) et la stratégie « calibration ».
"""

from __future__ import annotations

import dataclasses
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    # Ordres à cours limité à POSER dans le carnet (max_price = prix limite). Exécutés plus tard,
    # seulement si le marché passe au travers du prix (execution_simulator.simulate_resting_*).
    limit_orders: list[Proposal] = field(default_factory=list)
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

    # Options (16/10/2026, experiments/favori.md) — sans elles, comportement d'origine :
    #   familles (YAML, liste) : familles de marchés acceptées (market_family) ;
    #   min_hours / max_hours : fenêtre de temps avant l'échéance (avant le coup d'envoi en sport) ;
    #   underdog = 1 : acheter l'OUTSIDER (l'issue la moins chère) au lieu du favori ;
    #   shrink : estimation = milieu + shrink × (1 − milieu) au lieu de milieu + bias (le favori
    #   perd « shrink » fois moins souvent que son prix ne l'annonce) ;
    #   q_max (22/10/2026) : plafond de l'estimation (0,99 par défaut). Avec 0,99, un favori vendu 0,985 ou plus
    #   ne peut jamais montrer d'avantage (borne basse 0,987) : `favori_politique_quasi_certain` restait muette ;
    #   holding_only = 1 (19/10/2026) : seulement les marchés à récompense de détention (Gamma
    #   holdingRewardsEnabled) ; leur avantage compte alors `holding_rate` × années jusqu'à la fin
    #   (au plus `holding_years_max`), puisque Polymarket verse ce taux sur la valeur détenue.
    families: tuple[str, ...] = ()
    exclude_words: tuple[str, ...] = ()

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        """Variante ciblée (familles + `max_candidates`) : demande ses propres marchés au scanner,
        ceux dont l'issue visée (favori ou outsider) est dans la plage de prix."""
        p = self.params
        if not self.families or p.get("max_candidates", Decimal("0")) <= 0:
            return []
        out = []
        for m in markets:
            if len(m.outcome_prices) != 2 or market_family(m) not in self.families or excluded(m, self.exclude_words):
                continue
            if p.get("holding_only", Decimal("0")) > 0 and not m.holding_rewards:
                continue
            price = min(m.outcome_prices) if p.get("underdog", Decimal("0")) > 0 else max(m.outcome_prices)
            if p["min_ask"] - Decimal("0.02") <= price <= p["max_ask"]:
                out.append(m)
        out.sort(key=lambda m: -m.volume_24h)
        return out[: int(p["max_candidates"])]

    def _window_ok(self, market: MarketInfo, now) -> bool:
        p = self.params
        ref = market.game_start or market.end_date
        if ref is None or ("min_hours" not in p and "max_hours" not in p):
            return "min_hours" not in p and "max_hours" not in p
        hours = (ref - now).total_seconds() / 3600
        return p.get("min_hours", Decimal("-1e9")) <= Decimal(str(hours)) <= p.get("max_hours", Decimal("1e9"))

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
            if (self.families and market_family(market) not in self.families) or excluded(market, self.exclude_words):
                out.abstain("famille de marchés exclue")
                continue
            if p.get("holding_only", Decimal("0")) > 0 and not market.holding_rewards:
                out.abstain("pas de récompense de détention")
                continue
            idx = 0 if market.outcome_prices[0] >= market.outcome_prices[1] else 1
            if p.get("underdog", Decimal("0")) > 0:
                idx = 1 - idx
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
            if not self._window_ok(market, book.fetched_at):
                out.abstain("hors de la fenêtre de temps")
                continue
            q_cap = p.get("q_max", Decimal("0.99"))  # 22/10/2026 : plafond de l'estimation, 0,99 par défaut
            if "shrink" in p:
                q = min(book.mid + p["shrink"] * (ONE - book.mid), q_cap)
            else:
                q = min(book.mid + p["bias"], q_cap)
            low = q - p["uncertainty"]
            high = min(q + p["uncertainty"], max(Decimal("0.995"), q_cap))
            # Récompense de détention attendue (par part, en fraction du prix) : elle s'ajoute à
            # l'avantage et à la mise, pas aux probabilités déclarées (le contrôleur les vérifie).
            bonus = Decimal("0")
            if p.get("holding_only", Decimal("0")) > 0 and market.end_date is not None:
                years = Decimal(str(max((market.end_date - book.fetched_at).total_seconds(), 0) / (365 * 86400)))
                bonus = p.get("holding_rate", Decimal("0")) * min(years, p.get("holding_years_max", Decimal("1")))
            best: tuple[Decimal, Decimal] | None = None  # (prix limite, coût par part)
            tick = book.tick_size
            try:
                for k in range(int(p["max_extra_ticks"]) + 1):
                    price = ask + tick * k
                    if price >= ONE:
                        break
                    cost_ps = price + taker_fee(ONE, price, market.fees)
                    if low + bonus - cost_ps >= min_edge:
                        best = (price, cost_ps)
            except UnknownFees:
                out.abstain("frais inconnus")
                continue
            if best is None:
                out.abstain("avantage net insuffisant")
                continue
            max_price, cost_ps = best
            shares = size_buy(state, prob_low=min(low + bonus, Decimal("0.995")), cost_per_share=cost_ps,
                              kelly_fraction=p.get("kelly_fraction", Decimal("1")), marks=marks)
            if shares < max(market.min_order_size, book.min_order_size):
                out.abstain("taille autorisée trop faible")
                continue
            edge = low + bonus - cost_ps
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


def excluded(market: MarketInfo, words: tuple[str, ...]) -> bool:
    q = (market.question or "").lower()
    return any(w in q for w in words)


def market_family(market: MarketInfo) -> str:
    """Famille d'un marché d'après son barème de frais (Gamma `feeType`, vérifié le 16/10/2026) :
    « politics_fees » → politics, « sports_fees_v3 » → sports, « weather_fees » → weather… ;
    marché SANS frais → sans_frais (surtout la géopolitique, mais aussi santé, séismes…) ;
    barème inconnu → other."""
    if market.fees.enabled is False:
        return "sans_frais"
    if market.fees.enabled and market.fees.fee_type:
        return market.fees.fee_type.split("_")[0]
    return "other"


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


class PatientOrders:
    """Mode « patient » d'une stratégie : au lieu d'acheter tout de suite au vendeur (ask), elle
    pose un ordre d'achat à cours limité `ticks` crans au-dessus du meilleur acheteur, sans
    jamais toucher le vendeur. Elle paie moins cher (et souvent sans frais), mais n'est servie
    que si le marché redescend au travers de son prix — souvent jamais. Ventes inchangées."""

    def __init__(self, strategy, ticks: int):
        if ticks < 0:
            raise StrategyConfigError("limit_ticks doit être >= 0")
        self.inner, self.ticks = strategy, ticks
        self.strategy_id, self.version = strategy.strategy_id, strategy.version
        self.needs_price_history = getattr(strategy, "needs_price_history", False)
        if hasattr(strategy, "exits"):
            self.exits = strategy.exits

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.execution_simulator import maker_fee  # import tardif

        out = self.inner.propose(watchlist, books, state, limits, bucket, marks)
        markets = {m.market_id: m for m in watchlist}
        kept = []
        for p in out.proposals:
            book, market = books.get(p.token_id), markets.get(p.market_id)
            if p.side != "BUY" or book is None or market is None or book.best_bid is None \
                    or book.best_ask is None:
                kept.append(p)
                continue
            limit = min(book.best_bid + book.tick_size * self.ticks, book.best_ask - book.tick_size)
            if limit <= 0 or limit <= book.best_bid - book.tick_size:
                out.abstain("écart trop serré pour poser un ordre")
                continue
            try:
                edge = p.prob_low - limit - maker_fee(ONE, limit, market.fees)
            except UnknownFees:
                out.abstain("frais inconnus")
                continue
            out.limit_orders.append(dataclasses.replace(p, max_price=limit, net_edge=edge))
        out.proposals = kept
        return out

    def __getattr__(self, name):
        return getattr(self.inner, name)


FILTER_KEYS = ("familles", "prix_min", "prix_max", "heures_min", "heures_max", "issue", "heure_utc",
               "disciplines", "types_pari", "echeance_min", "echeance_max", "ecart_max", "sources",
               "sources_exclues", "question_contient", "question_exclut", "prix_final", "un_match")


class Filtered:
    """« Fille » d'une stratégie (entonnoir, 17/10/2026) : la stratégie mère ne joue qu'UN MORCEAU
    des marchés, défini par `filtres` (YAML). Comparer chaque fille à sa mère dans l'arène montre
    quel morceau fait vraiment gagner (ou perdre). Filtres possibles :
      familles : [sports, politics, …] (market_family) ; heures_min / heures_max : délai jusqu'à
      l'échéance (au coup d'envoi en sport) ; prix_min / prix_max : prix payé ;
      issue : [oui, non, autre] (autre = équipe, joueur…) ; heure_utc : [début, fin[ (heure de la
      journée en temps universel, ex. [4, 12] ; [20, 4] passe minuit) ;
      disciplines : [tennis, counter-strike, nfl, …] et types_pari : [vainqueur, handicap, total, …]
      (20/10/2026, entonnoir 80/20 : même classement que pareto.discipline / pareto.bet_type) ;
      echeance_min / echeance_max : heures jusqu'à l'ÉCHÉANCE du marché (pas le coup d'envoi),
      comme le délai noté à l'achat ; ecart_max : écart achat-vente maximal (marchés liquides) ;
      sources : domaines de la source de résolution acceptés, ex. [itftennis.com] pour le seul
      circuit ITF (20/10/2026 : outsiders ITF sous-cotés, ATP et WTA non) ; sources_exclues :
      domaines refusés (favoris ITF : −13,9 % aux vrais prix, experiments/achat_echelonne.md) ;
      question_contient : le marché est gardé si sa question contient un de ces mots (sans tenir
      compte des majuscules) ; question_exclut : refusé s'il en contient un (21/10/2026 : annonceurs
      NFL gagnants, Coupe du monde perdante, experiments/mentions_annonceurs.md) ;
      un_match : true → seulement les paris sur UN match (Gamma donne un `sportsMarketType`) ; false → seulement les
      marchés de saison (gagnant du championnat…). Refuse, si true, les
      marchés de saison ou de prix (Ballon d'Or, Coupe, Série mondiale), que la famille « sports »
      laisse passer (23/10/2026 : 359 € = 30 % du capital sur « Mbappé gagne le Ballon d'Or, NON » à 0,94,
      experiments/enquetes/2026-10-23_marches_de_saison_dans_le_sport.md) ;
      prix_final : true (avec `limit_ticks`) → prix_min / prix_max portent sur le prix de l'ORDRE POSÉ
      et non sur le prix du vendeur (21/10/2026 : sinon une fille « prix payé 0,875-0,90 » achète à 0,84,
      experiments/enquetes/2026-10-21_filtres_et_prix_executable.md).
    Les filtres de marché s'appliquent AVANT la stratégie (elle choisit ses meilleurs paris dans le
    morceau) ; ceux qui dépendent de l'issue choisie (prix, issue) APRÈS. Ventes jamais filtrées."""

    def __init__(self, strategy, filters: dict):
        unknown = set(filters) - set(FILTER_KEYS)
        if unknown:
            raise StrategyConfigError(f"filtres inconnus : {sorted(unknown)}")
        self.inner, self.filters = strategy, dict(filters)
        self.strategy_id, self.version = strategy.strategy_id, strategy.version
        self.needs_price_history = getattr(strategy, "needs_price_history", False)
        if hasattr(strategy, "exits"):
            self.exits = strategy.exits

    def _market_ok(self, m: MarketInfo, now) -> bool:
        f = self.filters
        if "familles" in f and market_family(m) not in f["familles"]:
            return False
        if ("echeance_min" in f or "echeance_max" in f) and now is not None:
            if m.end_date is None:
                return False
            hours = (m.end_date - now).total_seconds() / 3600
            if not float(f.get("echeance_min", -1e9)) <= hours <= float(f.get("echeance_max", 1e9)):
                return False
        if "un_match" in f and bool(f["un_match"]) != bool(getattr(m, "sports_market_type", None)):
            return False
        question = (m.question or "").lower()
        if "question_contient" in f and not any(str(w).lower() in question for w in f["question_contient"]):
            return False
        if any(str(w).lower() in question for w in f.get("question_exclut", ())):
            return False
        if "ecart_max" in f and (m.spread is None or float(m.spread) > float(f["ecart_max"])):
            return False
        if "sources" in f or "sources_exclues" in f:
            from polymarket_agent.resolution_sources import domain_of
            domain = domain_of(m.resolution_source) if m.resolution_source else ""
            if "sources" in f and domain not in f["sources"]:
                return False
            if domain and domain in f.get("sources_exclues", ()):
                return False
        if "disciplines" in f or "types_pari" in f:
            from polymarket_agent.pareto import bet_type, discipline  # import tardif : évite une boucle
            if "disciplines" in f and discipline(m.question, m.resolution_source) not in f["disciplines"]:
                return False
            if "types_pari" in f and bet_type(m.question, getattr(m, "sports_market_type", None)) not in f["types_pari"]:
                return False
        if ("heures_min" in f or "heures_max" in f) and now is not None:
            ref = m.game_start or m.end_date
            if ref is None:
                return False
            hours = (ref - now).total_seconds() / 3600
            if not float(f.get("heures_min", -1e9)) <= hours <= float(f.get("heures_max", 1e9)):
                return False
        return True

    def _order_ok(self, p) -> bool:
        if p.side != "BUY":
            return True
        f = self.filters
        if not float(f.get("prix_min", 0)) <= float(p.max_price) <= float(f.get("prix_max", 1)):
            return False
        if "issue" in f:
            o = (p.outcome or "").lower()
            kind = "oui" if o == "yes" else "non" if o == "no" else "autre"
            return kind in f["issue"]
        return True

    # Filtres assez étroits pour qu'une fille demande ELLE-MÊME ses marchés au scanner (21/10/2026) :
    # sans cela, statu_quo_ia (« best ai model ») et outsider_itf (source itftennis.com) ne voyaient
    # que les 150 marchés les plus échangés, où leurs marchés n'entrent presque jamais.
    OWN_MARKETS = ("question_contient", "sources")
    OWN_MARKETS_MAX = 25

    def candidates(self, markets):
        inner = getattr(self.inner, "candidates", None)
        out = [m for m in inner(markets) if self._market_ok(m, None)] if inner else []
        if not out and any(k in self.filters for k in self.OWN_MARKETS):
            out = sorted((m for m in markets if self._market_ok(m, None)), key=lambda m: -float(m.volume_24h or 0))
            out = out[: self.OWN_MARKETS_MAX]
        return out

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        now = max((b.fetched_at for b in books.values()), default=None)
        if "heure_utc" in self.filters and now is not None:
            start, end = (int(h) for h in self.filters["heure_utc"])
            hour = now.astimezone(timezone.utc).hour
            if not (start <= hour < end if start <= end else hour >= start or hour < end):
                return StrategyOutput()  # hors de la plage horaire : aucune nouvelle position
        kept = [m for m in watchlist if self._market_ok(m, now)]
        out = self.inner.propose(kept, books, state, limits, bucket, marks)
        out.proposals = [p for p in out.proposals if self._order_ok(p)]
        if getattr(out, "limit_orders", None):
            out.limit_orders = [p for p in out.limit_orders if self._order_ok(p)]
        return out

    def __getattr__(self, name):
        return getattr(self.inner, name)


def load_strategies(path: Path) -> list:
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        raise StrategyConfigError(f"impossible de lire {path}") from exc
    from polymarket_agent.strategies_v2 import CLASSES as V2  # import tardif : évite une boucle
    from polymarket_agent.strategies_v3 import CLASSES as V3  # vingt nouvelles pistes (20/10/2026)

    classes = dict(STRATEGY_CLASSES, **V2, **V3)
    strategies = []
    for strategy_id, spec in raw.items():
        if not isinstance(spec, dict) or not spec.get("enabled"):
            continue
        # « class: » : variante d'une stratégie existante sous un autre nom (son propre fantôme).
        cls = classes.get(str(spec.get("class", strategy_id)))
        if cls is None:
            raise StrategyConfigError(f"stratégie inconnue : {spec.get('class', strategy_id)}")
        args = [str(spec["version"]), str(spec["created_at"]), load_params(spec.get("params"))]
        if "table" in spec:
            args.append(Path(path).parent / str(spec["table"]))
        strategy = cls(*args)
        if "class" in spec:
            strategy.strategy_id = strategy_id
        if "familles" in spec:  # familles de marchés acceptées (ex. [politics, sans_frais])
            strategy.families = tuple(str(f) for f in spec["familles"])
        if "exclure_mots" in spec:  # marchés exclus si la question contient un de ces mots
            strategy.exclude_words = tuple(str(w).lower() for w in spec["exclure_mots"])
        filters = dict(spec.get("filtres") or {})
        if filters.pop("prix_final", False) and "limit_ticks" in spec:
            # Le filtre de prix se lit sur l'ordre posé : le mode patient passe DANS la fille.
            strategy = Filtered(PatientOrders(strategy, int(spec["limit_ticks"])), filters)
        else:
            if "filtres" in spec:  # fille : la stratégie mère sur un morceau des marchés
                strategy = Filtered(strategy, dict(spec["filtres"]))
            if "limit_ticks" in spec:  # mode patient : ordres posés au lieu d'achats immédiats
                strategy = PatientOrders(strategy, int(spec["limit_ticks"]))
        mode = str(spec.get("mode", "principal"))
        if mode not in ("principal", "fantome"):
            raise StrategyConfigError(f"{strategy_id} : mode inconnu {mode!r}")
        strategy.mode = mode  # « fantome » : journal séparé, ne touche jamais le capital principal
        strategies.append(strategy)
    return strategies
