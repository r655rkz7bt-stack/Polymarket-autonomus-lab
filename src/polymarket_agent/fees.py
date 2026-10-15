"""Frais simulés des ordres « taker ».

Source : le barème de chaque marché est fourni par Gamma (champs `feesEnabled` et
`feeSchedule = {rate, exponent, takerOnly, rebateRate}`), observé le 14/10/2026.
Formule officielle (docs.polymarket.com/trading/fees, vérifiée le 14/10/2026) :
frais (USDC) = parts × taux × p × (1 − p), arrondis à 5 décimales, minimum 0,00001.
L'exposant du barème vaut 1 sur tous les marchés observés ; il reste pris en compte.
Les remises « maker » et « taker » ne sont jamais comptées (prudence).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_UP

from polymarket_agent.models import FeeSchedule

ZERO = Decimal("0")
ONE = Decimal("1")
FEE_QUANTUM = Decimal("0.00001")  # doc : frais arrondis à 5 décimales (ici vers le haut)


class UnknownFees(Exception):
    """Barème absent : on préfère ne pas trader plutôt que d'inventer des frais."""


def taker_fee(shares: Decimal, price: Decimal, schedule: FeeSchedule) -> Decimal:
    if schedule.enabled is None:
        raise UnknownFees("frais inconnus pour ce marché")
    if not schedule.enabled:
        return ZERO
    if schedule.rate is None or schedule.exponent is None:
        raise UnknownFees("barème de frais incomplet")
    base = price * (ONE - price)
    if base <= 0 or shares <= 0:
        return ZERO
    if schedule.exponent == schedule.exponent.to_integral_value():
        factor = base ** int(schedule.exponent)
    else:
        factor = Decimal(str(float(base) ** float(schedule.exponent)))
    return (shares * schedule.rate * factor).quantize(FEE_QUANTUM, rounding=ROUND_UP)
