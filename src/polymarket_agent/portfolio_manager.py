"""Portfolio Manager : taille prudente des positions (Kelly fractionné + limites de risque).

Le contrôleur de sécurité revérifie tout ; ce module sert seulement à proposer
une taille qui a des chances d'être acceptée.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_DOWN

from polymarket_agent.ledger import LedgerState
from polymarket_agent.safety_controller import RiskLimits, kelly_fraction_binary

ZERO = Decimal("0")
SAFETY_MARGIN = Decimal("0.98")  # marge contre les effets d'arrondi


def size_buy(state: LedgerState, limits: RiskLimits, *, token_id: str, event_id: str,
             prob_low: Decimal, cost_per_share: Decimal,
             marks: dict[str, Decimal] | None = None) -> Decimal:
    """Nombre de parts à proposer (0 si rien de raisonnable)."""
    if state.bankrupt or state.cash <= 0 or cost_per_share <= 0:
        return ZERO
    total = state.total_estimated(marks)
    if total <= 0:
        return ZERO
    existing = state.positions.get(token_id)
    existing_cost = existing.cost_basis if existing else ZERO
    event_cost = sum((p.cost_basis for p in state.positions.values() if p.event_id == event_id), ZERO)
    budget = min(
        limits.kelly_fraction * kelly_fraction_binary(prob_low, cost_per_share) * total,
        limits.max_position_pct * total - existing_cost,
        limits.max_event_pct * total - event_cost,
        state.cash - limits.min_cash_pct * total,
    ) * SAFETY_MARGIN
    if budget <= 0:
        return ZERO
    return (budget / cost_per_share).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
