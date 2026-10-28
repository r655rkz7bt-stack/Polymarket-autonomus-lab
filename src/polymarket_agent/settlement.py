"""Règlement des positions dont le marché est résolu (docs.polymarket.com/concepts/resolution).

Un marché est considéré comme réglé seulement si :
  - Gamma indique `closed = true` ;
  - le statut UMA est « resolved » (ou absent, pour les marchés Chainlink « up/down ») ;
  - les prix finaux sont nets : 1/0, ou 0,5/0,5 (résolution « 50-50 », chaque part vaut 0,50).
Sinon (proposition en cours, litige, prix intermédiaires), on attend le cycle suivant.
"""

from __future__ import annotations

import json
import logging
from decimal import Decimal, InvalidOperation

log = logging.getLogger(__name__)
FINAL_PAYOUTS = {Decimal("0"), Decimal("1"), Decimal("0.5")}


def _list(value) -> list:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value) if isinstance(value, str) else []
    except ValueError:
        return []
    return parsed if isinstance(parsed, list) else []


def resolution_payout(raw: dict, token_id: str) -> tuple[Decimal, str] | None:
    """Paiement par part pour ce jeton, ou None si le marché n'est pas encore réglé."""
    if raw.get("closed") is not True:
        return None
    if raw.get("umaResolutionStatus") not in (None, "", "resolved"):
        return None
    tokens = [str(t) for t in _list(raw.get("clobTokenIds"))]
    if token_id not in tokens:
        return None
    try:
        prices = [Decimal(str(p)) for p in _list(raw.get("outcomePrices"))]
    except (InvalidOperation, ValueError):
        return None
    if len(prices) != len(tokens) or any(p not in FINAL_PAYOUTS for p in prices):
        return None
    if sum(prices) != 1:
        return None
    payout = prices[tokens.index(token_id)]
    outcomes = [str(o) for o in _list(raw.get("outcomes"))]
    winner = outcomes[prices.index(max(prices))] if outcomes and max(prices) == 1 else "50-50"
    return payout, f"résolu : {winner}"


def settle_positions(ledger, gamma, now) -> list[dict]:
    """Règle toutes les positions résolues. Une erreur réseau n'empêche pas les autres."""
    from polymarket_agent.http_client import SourceUnavailable

    settled = []
    for token_id, pos in list(ledger.state.positions.items()):
        try:
            raw = gamma.get_market(pos.market_id)
        except (SourceUnavailable, ValueError) as exc:
            log.warning("règlement %s : marché illisible (%s), nouvel essai au prochain cycle",
                        pos.market_id, exc)
            continue
        result = resolution_payout(raw, token_id) if isinstance(raw, dict) else None
        if result is None:
            continue
        payout, label = result
        ledger.record_settlement(op_id=f"settle-{token_id}", token_id=token_id,
                                 payout_per_share=payout, resolution=label, now=now)
        pnl = pos.shares * payout - pos.cost_basis
        settled.append({"token_id": token_id, "market_id": pos.market_id, "payout": str(payout),
                        "pnl": str(pnl.quantize(Decimal("0.0001"))), "resolution": label})
        log.info("règlement %s : %s, %s parts × %s, résultat %s", pos.market_id, label,
                 pos.shares, payout, pnl.quantize(Decimal("0.01")))
        if ledger.state.bankrupt:
            break
    return settled
