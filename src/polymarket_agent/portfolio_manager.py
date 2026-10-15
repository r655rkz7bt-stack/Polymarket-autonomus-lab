"""Portfolio Manager : taille des positions.

Liberté totale (décision du 15/10/2026) : aucune limite de taille ou de concentration.
Par défaut, la taille suit le critère de Kelly COMPLET (fraction 1) : c'est la mise qui
maximise la croissance du capital sur la durée. Miser plus fait croître MOINS vite (et à
partir de 2× Kelly, on perd en moyenne même avec un bon pari). Chaque stratégie peut
changer sa fraction (`kelly_fraction` dans config/strategies.yaml).
Seule contrainte : on ne dépense pas plus que le solde disponible (règle du jeu).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_DOWN

from polymarket_agent.ledger import LedgerState
from polymarket_agent.safety_controller import kelly_fraction_binary

ZERO = Decimal("0")
SAFETY_MARGIN = Decimal("0.999")  # marge contre les effets d'arrondi (frais, ticks)
DEFAULT_KELLY_FRACTION = Decimal("1")


def size_buy(state: LedgerState, *, prob_low: Decimal, cost_per_share: Decimal,
             kelly_fraction: Decimal = DEFAULT_KELLY_FRACTION,
             marks: dict[str, Decimal] | None = None) -> Decimal:
    """Nombre de parts à proposer (0 si l'avantage estimé est nul ou négatif)."""
    if state.bankrupt or state.cash <= 0 or cost_per_share <= 0 or kelly_fraction <= 0:
        return ZERO
    total = state.total_estimated(marks)
    if total <= 0:
        return ZERO
    budget = min(kelly_fraction * kelly_fraction_binary(prob_low, cost_per_share) * total,
                 state.cash) * SAFETY_MARGIN
    if budget <= 0:
        return ZERO
    return (budget / cost_per_share).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
