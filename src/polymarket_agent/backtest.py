"""Backtest sur l'historique des marchés résolus.

Principes anti-fuite temporelle :
  - une décision à l'instant T ne lit que le dernier prix d'horodatage <= T ;
  - l'issue (gagnant) n'est lue qu'au moment du règlement ;
  - les périodes entraînement / validation / test sont découpées par ÉVÉNEMENT,
    dans l'ordre chronologique : un même événement n'est jamais dans deux périodes ;
  - la période de test ne sert qu'une fois, pour la décision finale.

La simulation de portefeuille passe par le VRAI journal (ledger.py) et le VRAI
contrôleur (safety_controller.py) : mêmes limites, même comptabilité.

Hypothèse d'exécution : achat au prix de référence + demi-écart (0,01 par défaut,
mesuré sur les carnets réels le 14/10/2026), plus les frais ; profondeur suffisante
pour les petites tailles en jeu (marchés >= 50 000 de volume). Sensibilité : ×1,5 et ×2.
"""

from __future__ import annotations

import math
import random
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Callable

from polymarket_agent.history import HistoricalMarket
from polymarket_agent.ledger import Ledger, LedgerError
from polymarket_agent.safety_controller import MarketContext, Proposal, RiskLimits, evaluate

HORIZONS_H = (72, 48, 36, 24, 18, 12, 8, 6, 4, 3, 2, 1)  # décroissant : première entrée possible
BACKTEST_KEY = b"backtest-key-not-a-secret-000000000000"


@dataclass(frozen=True)
class Sample:
    """Ce qu'une stratégie sait à l'instant `ts` (et rien de plus)."""

    market_id: str
    event_id: str
    category: str
    ts: int
    horizon_h: int
    price_yes: float
    price_yes_6h_ago: float | None
    fee_rate: float
    volume: float  # volume FINAL, connu après l'issue : interdit comme filtre (biais de sélection)
    changes_24h: int = 0  # changements de prix sur les 24 h précédentes (connu à ts)


@dataclass(frozen=True)
class Outcome:
    winner: int  # 0 = Yes, 1 = No
    settled_at: int


def build_samples(markets: list[HistoricalMarket], horizons=HORIZONS_H,
                  max_age_s: int = 2 * 3600) -> tuple[dict[str, list[Sample]], dict[str, Outcome]]:
    samples: dict[str, list[Sample]] = {}
    outcomes: dict[str, Outcome] = {}
    for market in markets:
        meta = market.meta
        rows = []
        for h in horizons:
            # Horizon mesuré par rapport à l'échéance PRÉVUE (connue à l'avance), jamais
            # par rapport à la clôture réelle (connue seulement après coup : fuite).
            ts = meta["end"] - h * 3600
            if ts >= meta["closed"] or (meta.get("start") and ts < meta["start"] + 3600):
                continue  # marché déjà clos ou pas encore ouvert à cet instant
            price = market.yes_price_at(ts, max_age_s)
            if price is None or not (0.0 < price < 1.0):
                continue
            rows.append(Sample(meta["id"], meta["event_id"], meta["category"], ts, h, price,
                               market.yes_price_at(ts - 6 * 3600, max_age_s),
                               float(meta["fee_rate"]), float(meta["volume"]),
                               market.price_changes(ts)))
        if rows:
            samples[meta["id"]] = rows
            outcomes[meta["id"]] = Outcome(int(meta["winner"]), max(meta["closed"], market.limit))
    return samples, outcomes


def split_by_event(samples: dict[str, list[Sample]], fractions=(0.6, 0.2, 0.2)):
    """Découpage chronologique par événement (un événement entier dans une seule période)."""
    event_time: dict[str, int] = {}
    for rows in samples.values():
        for s in rows:
            event_time[s.event_id] = max(event_time.get(s.event_id, 0), s.ts)
    ordered = sorted(event_time, key=lambda e: event_time[e])
    n = len(ordered)
    cut1, cut2 = int(n * fractions[0]), int(n * (fractions[0] + fractions[1]))
    group = {e: (0 if i < cut1 else 1 if i < cut2 else 2) for i, e in enumerate(ordered)}
    parts: list[dict[str, list[Sample]]] = [{}, {}, {}]
    for market_id, rows in samples.items():
        parts[group[rows[0].event_id]][market_id] = rows
    bounds = [event_time[ordered[0]], event_time[ordered[cut1 - 1]] if cut1 else None,
              event_time[ordered[cut2 - 1]] if cut2 else None, event_time[ordered[-1]]]
    return parts, bounds


def fee_per_share(price: float, rate: float) -> float:
    return rate * price * (1 - price)


def cluster_mean_ci(values_by_cluster: dict[str, list[float]], n_boot: int = 1000,
                    seed: int = 7, alpha: float = 0.10) -> tuple[float, float, float, int]:
    """Moyenne et intervalle (1-alpha) par bootstrap sur les grappes (événements)."""
    clusters = [v for v in values_by_cluster.values() if v]
    total = sum(len(v) for v in clusters)
    if not clusters:
        return float("nan"), float("nan"), float("nan"), 0
    mean = sum(sum(v) for v in clusters) / total
    rng = random.Random(seed)
    means = []
    sums = [(sum(v), len(v)) for v in clusters]
    for _ in range(n_boot):
        s = c = 0.0
        for _ in range(len(sums)):
            a, b = sums[rng.randrange(len(sums))]
            s += a
            c += b
        means.append(s / c)
    means.sort()
    lo = means[int(n_boot * alpha / 2)]
    hi = means[int(n_boot * (1 - alpha / 2)) - 1]
    return mean, lo, hi, len(clusters)


# --------------------------------------------------------------------------- simulation


@dataclass
class Decision:
    side: int  # 0 = acheter Yes, 1 = acheter No
    prob_low: float
    est: float
    prob_high: float


Rule = Callable[[Sample], Decision | None]


@dataclass
class BacktestResult:
    name: str
    trades: list[dict] = field(default_factory=list)
    rejected: int = 0
    equity: list[tuple[int, float]] = field(default_factory=list)
    final_cash: float = 0.0
    initial: float = 0.0
    bankrupt: bool = False

    def metrics(self) -> dict:
        n = len(self.trades)
        pnl = [t["pnl"] for t in self.trades]
        wins = sum(1 for t in self.trades if t["won"])
        peak, mdd = self.initial, 0.0
        for _, eq in self.equity:
            peak = max(peak, eq)
            mdd = max(mdd, (peak - eq) / peak if peak > 0 else 0)
        brier = (sum((t["est"] - t["won"]) ** 2 for t in self.trades) / n) if n else float("nan")
        brier_mkt = (sum((t["price"] - t["won"]) ** 2 for t in self.trades) / n) if n else float("nan")
        by_event: dict[str, list[float]] = {}
        for t in self.trades:
            by_event.setdefault(t["event_id"], []).append(t["pnl_per_cost"])
        mean_r, lo_r, hi_r, n_ev = cluster_mean_ci(by_event)
        return {
            "strategie": self.name, "operations": n, "evenements": n_ev, "rejets_controleur": self.rejected,
            "taux_reussite": round(wins / n, 4) if n else None,
            "profit_net": round(sum(pnl), 2),
            "rendement": round(self.final_cash / self.initial - 1, 4) if self.initial else None,
            "croissance_log": round(math.log(self.final_cash / self.initial), 4) if self.final_cash > 0 else None,
            "drawdown_max": round(mdd, 4),
            "rendement_moyen_par_euro_mise": round(mean_r, 4) if n else None,
            "ic90_rendement_par_euro": [round(lo_r, 4), round(hi_r, 4)] if n else None,
            "brier_strategie": round(brier, 4) if n else None,
            "brier_marche": round(brier_mkt, 4) if n else None,
            "faillite": self.bankrupt,
        }


def simulate(name: str, rule: Rule, samples: dict[str, list[Sample]], outcomes: dict[str, Outcome],
             limits: RiskLimits, half_spread: float = 0.01, initial: float | None = None) -> BacktestResult:
    """Simulation de portefeuille via le vrai journal et le vrai contrôleur.

    Au plus une entrée par marché : le premier horizon (le plus lointain) où la règle se déclenche.
    """
    from datetime import datetime, timezone

    from polymarket_agent.portfolio_manager import size_buy

    def dt(ts: int) -> datetime:
        return datetime.fromtimestamp(ts, tz=timezone.utc)

    entries = []
    for market_id, rows in samples.items():
        for sample in sorted(rows, key=lambda s: s.ts):
            decision = rule(sample)
            if decision is not None:
                entries.append((sample.ts, 0, market_id, sample, decision))
                break
    events_sorted = sorted(entries, key=lambda e: (e[0], e[2]))
    result = BacktestResult(name)
    with tempfile.TemporaryDirectory() as tmp:
        ledger = Ledger.create(Path(tmp) / "l.jsonl", BACKTEST_KEY, Path(tmp) / "lock",
                               initial if initial is not None else limits.initial_capital,
                               now=dt(events_sorted[0][0] - 1) if events_sorted else None)
        result.initial = float(ledger.state.cash)
        pending: list[tuple[int, str, dict]] = []  # (instant de règlement, jeton, opération)

        def settle_until(ts: int) -> None:
            pending.sort(key=lambda p: p[0])
            while pending and pending[0][0] <= ts:
                when, token, trade = pending.pop(0)
                payout = 1 if trade["won"] else 0
                try:
                    ledger.record_settlement(op_id=f"s-{token}", token_id=token,
                                             payout_per_share=payout, resolution="backtest",
                                             now=dt(when))
                except LedgerError:
                    pass
                result.equity.append((when, float(ledger.state.total_estimated())))

        for ts, _, market_id, sample, decision in events_sorted:
            settle_until(ts)
            if ledger.state.bankrupt:
                result.bankrupt = True
                break
            side_price = sample.price_yes if decision.side == 0 else 1 - sample.price_yes
            ask = min(round(side_price + half_spread, 4), 0.999)
            fee_ps = fee_per_share(ask, sample.fee_rate)
            token = f"{market_id}:{decision.side}"
            shares = size_buy(ledger.state, limits, token_id=token, event_id=sample.event_id,
                              prob_low=Decimal(str(decision.prob_low)),
                              cost_per_share=Decimal(str(ask + fee_ps)))
            if shares < 5:
                continue
            proposal = Proposal(
                op_id=f"b-{token}", side="BUY", market_id=market_id, event_id=sample.event_id,
                token_id=token, outcome=str(decision.side),
                est_probability=Decimal(str(round(decision.est, 6))),
                prob_low=Decimal(str(round(decision.prob_low, 6))),
                prob_high=Decimal(str(round(decision.prob_high, 6))),
                max_price=Decimal(str(ask)), shares=shares,
                net_edge=Decimal(str(round(decision.prob_low - ask - fee_ps, 6))),
                sources=("history",), uncertainty="backtest", invalidation="-",
                horizon_hours=Decimal(sample.horizon_h), strategy_id=name, strategy_version="bt")
            context = MarketContext(
                token_id=token, active=True, closed=False, accepting_orders=True, data_ok=True,
                best_bid=Decimal(str(max(round(side_price - half_spread, 4), 0.001))),
                best_ask=Decimal(str(ask)), book_time=dt(ts), fees_enabled=sample.fee_rate > 0,
                fee_rate=Decimal(str(sample.fee_rate)), fee_exponent=Decimal("1"),
                min_order_size=Decimal("5"))
            verdict = evaluate(proposal, ledger.state, context, limits, dt(ts))
            if not verdict.accepted:
                result.rejected += 1
                continue
            fee = Decimal(str(round(float(shares) * fee_ps, 5)))
            try:
                ledger.record_buy(op_id=proposal.op_id, token_id=token, market_id=market_id,
                                  event_id=sample.event_id, outcome=str(decision.side),
                                  shares=shares, price=Decimal(str(ask)), fee=fee,
                                  strategy_id=name, strategy_version="bt", now=dt(ts))
            except LedgerError:
                result.rejected += 1
                continue
            outcome = outcomes[market_id]
            won = outcome.winner == decision.side
            cost = float(shares) * ask + float(fee)
            trade = {"market_id": market_id, "event_id": sample.event_id, "category": sample.category,
                     "ts": ts, "horizon_h": sample.horizon_h, "side": decision.side,
                     "price": side_price, "ask": ask, "est": decision.est, "won": won,
                     "shares": float(shares), "cost": cost,
                     "pnl": (float(shares) if won else 0.0) - cost}
            trade["pnl_per_cost"] = trade["pnl"] / cost
            result.trades.append(trade)
            pending.append((outcome.settled_at, token, trade))
        settle_until(2 ** 62)
        result.final_cash = float(ledger.state.cash)
        result.bankrupt = result.bankrupt or ledger.state.bankrupt
    return result
