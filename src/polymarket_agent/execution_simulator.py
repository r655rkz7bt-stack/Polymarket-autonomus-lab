"""Simulateur d'exécution « taker ».

Hypothèses (documentées, testées) :
- l'ordre parcourt le carnet RELU juste avant l'exécution, niveau par niveau ;
- il ne dépasse jamais le prix limite ; s'il manque de profondeur, exécution partielle ;
- s'il ne trouve rien, l'ordre n'est PAS exécuté et rien n'est comptabilisé ;
- les parts sont arrondies vers le bas au centième ;
- frais calculés niveau par niveau (fees.py), arrondis vers le haut ;
- on suppose qu'on est le seul à consommer la liquidité affichée (optimiste :
  sera testé avec slippage ×1,5 et ×2 à l'étape 4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_DOWN

from polymarket_agent.fees import taker_fee
from polymarket_agent.models import FeeSchedule, OrderBook

ZERO = Decimal("0")
SHARE_QUANTUM = Decimal("0.01")


@dataclass
class Fill:
    status: str  # FILLED, PARTIAL, UNFILLED
    side: str
    requested_shares: Decimal
    filled_shares: Decimal = ZERO
    notional: Decimal = ZERO  # parts × prix, hors frais
    fee: Decimal = ZERO
    levels: list[tuple[str, str]] = field(default_factory=list)
    reason: str = ""

    @property
    def avg_price(self) -> Decimal:
        return self.notional / self.filled_shares if self.filled_shares > 0 else ZERO

    @property
    def executed(self) -> bool:
        return self.filled_shares > 0


def _walk(levels, shares: Decimal, accept) -> tuple[Decimal, Decimal, list[tuple[Decimal, Decimal]]]:
    remaining = shares
    notional = ZERO
    used: list[tuple[Decimal, Decimal]] = []
    for level in levels:
        if remaining <= 0 or not accept(level.price):
            break
        take = min(remaining, level.size).quantize(SHARE_QUANTUM, rounding=ROUND_DOWN)
        if take <= 0:
            continue
        used.append((level.price, take))
        notional += take * level.price
        remaining -= take
    return shares - remaining, notional, used


def _finish(side, shares, filled, notional, used, fees: FeeSchedule) -> Fill:
    if filled <= 0:
        return Fill("UNFILLED", side, shares, reason="aucune liquidité au prix limite")
    fee = sum((taker_fee(qty, price, fees) for price, qty in used), ZERO)
    status = "FILLED" if filled == shares else "PARTIAL"
    return Fill(status, side, shares, filled, notional, fee,
                [(str(p), str(q)) for p, q in used])


def simulate_buy(book: OrderBook, shares: Decimal, max_price: Decimal, fees: FeeSchedule) -> Fill:
    shares = shares.quantize(SHARE_QUANTUM, rounding=ROUND_DOWN)
    if shares <= 0:
        return Fill("UNFILLED", "BUY", shares, reason="taille nulle")
    filled, notional, used = _walk(book.asks, shares, lambda p: p <= max_price)
    return _finish("BUY", shares, filled, notional, used, fees)


def simulate_sell(book: OrderBook, shares: Decimal, min_price: Decimal, fees: FeeSchedule) -> Fill:
    shares = shares.quantize(SHARE_QUANTUM, rounding=ROUND_DOWN)
    if shares <= 0:
        return Fill("UNFILLED", "SELL", shares, reason="taille nulle")
    filled, notional, used = _walk(book.bids, shares, lambda p: p >= min_price)
    return _finish("SELL", shares, filled, notional, used, fees)
