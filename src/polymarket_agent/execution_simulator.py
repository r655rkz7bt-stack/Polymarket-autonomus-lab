"""Simulateur d'exécution : ordres « taker » et ordres à cours limité posés dans le carnet.

Hypothèses (documentées, testées) :
- l'ordre parcourt le carnet RELU juste avant l'exécution, niveau par niveau ;
- il ne dépasse jamais le prix limite ; s'il manque de profondeur, exécution partielle ;
- s'il ne trouve rien, l'ordre n'est PAS exécuté et rien n'est comptabilisé ;
- les parts sont arrondies vers le bas au centième ;
- frais calculés niveau par niveau (fees.py), arrondis vers le haut ;
- on suppose qu'on est le seul à consommer la liquidité affichée (optimiste :
  sera testé avec slippage ×1,5 et ×2 à l'étape 4).

Ordres à cours limité posés dans le carnet (« maker », décision d'Etienne du 15/10/2026),
règle prudente du « passage au travers » :
- un ordre posé au cycle t n'est jamais exécuté avec le carnet du cycle t (pas de regard en
  arrière) : seulement avec un carnet relu APRÈS sa pose ;
- un achat posé à L n'est exécuté que si le carnet affiche des vendeurs à L − 1 tick ou moins
  (le marché est passé au travers de notre prix : nous aurions été servis, même derniers de la
  file d'attente), pour la quantité qu'ils affichent, au prix L, jamais mieux ;
- symétrique pour une vente : acheteurs à L + 1 tick ou plus ;
- un toucher exact (meilleur prix = L) ne suffit pas : on ne connaît pas notre place dans la file ;
- tout ce qui s'est échangé entre deux relectures est ignoré (on rate des exécutions : prudent) ;
- frais : nuls seulement si le barème dit explicitement « taker seulement » (ou frais
  désactivés) ; sinon les frais taker sont comptés. Aucune remise n'est jamais comptée.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_DOWN

from polymarket_agent.fees import UnknownFees, taker_fee
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


# --------------------------------------------------------------------------- ordres posés

def maker_fee(shares: Decimal, price: Decimal, fees: FeeSchedule) -> Decimal:
    """Frais d'un ordre posé exécuté : 0 seulement si le barème est explicitement « taker
    seulement » ; frais inconnus = refus (comme pour un ordre taker)."""
    if fees.enabled is None:
        raise UnknownFees("frais inconnus pour ce marché")
    if fees.enabled and fees.taker_only is True:
        return ZERO
    return taker_fee(shares, price, fees)


def _resting(side: str, levels, shares: Decimal, limit: Decimal, tick: Decimal, through,
             fees: FeeSchedule, consumed: Decimal) -> Fill:
    shares = shares.quantize(SHARE_QUANTUM, rounding=ROUND_DOWN)
    if shares <= 0:
        return Fill("UNFILLED", side, shares, reason="taille nulle")
    if tick is None or tick <= 0:
        return Fill("UNFILLED", side, shares, reason="pas de cotation (tick) inconnu")
    depth = sum((level.size for level in levels if through(level.price, limit, tick)), ZERO)
    available = max(depth - max(consumed, ZERO), ZERO)
    filled = min(shares, available).quantize(SHARE_QUANTUM, rounding=ROUND_DOWN)
    if filled <= 0:
        return Fill("UNFILLED", side, shares, reason="le marché n'est pas passé au travers du prix limite")
    fee = maker_fee(filled, limit, fees)
    status = "FILLED" if filled == shares else "PARTIAL"
    return Fill(status, side, shares, filled, filled * limit, fee, [(str(limit), str(filled))])


def simulate_resting_buy(book: OrderBook, shares: Decimal, limit: Decimal, fees: FeeSchedule,
                         consumed: Decimal = ZERO) -> Fill:
    """Achat posé à `limit` AVANT la relecture de `book`. `consumed` : parts de cette même
    contrepartie déjà attribuées à d'autres ordres du même portefeuille pendant ce cycle."""
    return _resting("BUY", book.asks, shares, limit, book.tick_size,
                    lambda price, lim, tick: price <= lim - tick, fees, consumed)


def simulate_resting_sell(book: OrderBook, shares: Decimal, limit: Decimal, fees: FeeSchedule,
                          consumed: Decimal = ZERO) -> Fill:
    """Vente posée à `limit` AVANT la relecture de `book` (voir simulate_resting_buy)."""
    return _resting("SELL", book.bids, shares, limit, book.tick_size,
                    lambda price, lim, tick: price >= lim + tick, fees, consumed)
