"""Contrôleur de sécurité — FICHIER PROTÉGÉ.

Séparation cerveau / garde-fous : les stratégies PROPOSENT, ce module DÉCIDE.
Code déterministe, sans IA, sans réseau. Il ne fait confiance à aucun chiffre
fourni par la stratégie qu'il peut recalculer lui-même (avantage net, frais, coût).

Il applique config/risk_limits.yaml, borné par des limites dures codées ici :
même un fichier de configuration modifié ne peut pas les dépasser.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, ROUND_UP
from pathlib import Path
from typing import Any

import yaml

from polymarket_agent.ledger import LedgerState, to_decimal

ZERO = Decimal("0")
ONE = Decimal("1")
SIMULATION_ONLY_MODE = "simulation"


class SafetyConfigError(Exception):
    """Configuration de risque absente, inconnue ou hors des bornes dures."""


class RealModeForbidden(Exception):
    """Toute tentative de mode autre que la simulation."""


def assert_simulation_mode(mode: Any) -> None:
    """Le mode réel n'existe pas dans ce projet."""
    if mode != SIMULATION_ONLY_MODE:
        raise RealModeForbidden(
            f"mode {mode!r} refusé : seul le mode 'simulation' existe dans ce projet"
        )


# --------------------------------------------------------------------------- limites

# (minimum autorisé, maximum autorisé) pour chaque paramètre de risk_limits.yaml.
HARD_BOUNDS: dict[str, tuple[Decimal, Decimal]] = {
    "initial_capital": (Decimal("1"), Decimal("1000000")),
    "kelly_fraction": (Decimal("0"), Decimal("0.5")),
    "max_position_pct": (Decimal("0"), Decimal("0.10")),
    "max_event_pct": (Decimal("0"), Decimal("0.25")),
    "min_cash_pct": (Decimal("0.20"), Decimal("1")),
    "max_open_positions": (Decimal("0"), Decimal("100")),
    "daily_loss_pause_pct": (Decimal("0.01"), Decimal("0.20")),
    "min_net_edge_floor": (Decimal("0.01"), Decimal("1")),
    "max_book_age_seconds": (Decimal("1"), Decimal("600")),
}


@dataclass(frozen=True)
class RiskLimits:
    initial_capital: Decimal
    kelly_fraction: Decimal
    max_position_pct: Decimal
    max_event_pct: Decimal
    min_cash_pct: Decimal
    max_open_positions: int
    daily_loss_pause_pct: Decimal
    min_net_edge_floor: Decimal
    no_averaging_down: bool
    max_book_age_seconds: int

    @classmethod
    def from_dict(cls, raw: Any) -> "RiskLimits":
        if not isinstance(raw, dict):
            raise SafetyConfigError("risk_limits : un dictionnaire est attendu")
        expected = {f.name for f in dataclasses.fields(cls)}
        unknown, missing = set(raw) - expected, expected - set(raw)
        if unknown:
            raise SafetyConfigError(f"risk_limits : clés inconnues {sorted(unknown)}")
        if missing:
            raise SafetyConfigError(f"risk_limits : clés manquantes {sorted(missing)}")
        if raw["no_averaging_down"] is not True:
            raise SafetyConfigError("risk_limits : no_averaging_down doit valoir true")
        values: dict[str, Any] = {"no_averaging_down": True}
        for name, (low, high) in HARD_BOUNDS.items():
            try:
                value = to_decimal(raw[name], name)
            except Exception as exc:
                raise SafetyConfigError(f"risk_limits : {name} invalide") from exc
            if not (low <= value <= high):
                raise SafetyConfigError(f"risk_limits : {name}={value} hors des bornes dures [{low}, {high}]")
            values[name] = value
        if values["max_event_pct"] < values["max_position_pct"]:
            raise SafetyConfigError("risk_limits : max_event_pct < max_position_pct")
        for name in ("max_open_positions", "max_book_age_seconds"):
            if values[name] != int(values[name]):
                raise SafetyConfigError(f"risk_limits : {name} doit être un entier")
            values[name] = int(values[name])
        return cls(**values)

    @classmethod
    def from_file(cls, path: Path) -> "RiskLimits":
        try:
            raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise SafetyConfigError(f"impossible de lire {path}") from exc
        return cls.from_dict(raw)


# --------------------------------------------------------------------------- entrées


PROPOSAL_FIELDS = (
    "op_id", "side", "market_id", "event_id", "token_id", "outcome", "est_probability",
    "prob_low", "prob_high", "max_price", "shares", "net_edge", "sources", "uncertainty",
    "invalidation", "horizon_hours", "strategy_id", "strategy_version",
)


@dataclass(frozen=True)
class Proposal:
    """Proposition d'une stratégie. Elle n'a AUCUN pouvoir sur les règles."""

    op_id: str
    side: str  # "BUY" (ouvrir/renforcer) ou "SELL" (réduire/fermer)
    market_id: str
    event_id: str
    token_id: str
    outcome: str
    est_probability: Decimal
    prob_low: Decimal
    prob_high: Decimal
    max_price: Decimal  # BUY : prix maximal ; SELL : prix minimal accepté
    shares: Decimal
    net_edge: Decimal  # déclaré par la stratégie, recalculé par le contrôleur
    sources: tuple[str, ...]
    uncertainty: str
    invalidation: str
    horizon_hours: Decimal
    strategy_id: str
    strategy_version: str

    @classmethod
    def from_dict(cls, raw: dict) -> "Proposal":
        """Construit depuis un dictionnaire (ex. sortie d'un modèle). Toute clé inconnue est refusée."""
        if not isinstance(raw, dict):
            raise ValueError("proposition : dictionnaire attendu")
        unknown = set(raw) - set(PROPOSAL_FIELDS)
        if unknown:
            raise ValueError(f"proposition : champs non autorisés {sorted(unknown)}")
        missing = set(PROPOSAL_FIELDS) - set(raw)
        if missing:
            raise ValueError(f"proposition : champs manquants {sorted(missing)}")
        values = dict(raw)
        for name in ("est_probability", "prob_low", "prob_high", "max_price", "shares",
                     "net_edge", "horizon_hours"):
            values[name] = to_decimal(raw[name], name)
        values["sources"] = tuple(str(s) for s in raw["sources"])
        for name in ("op_id", "side", "market_id", "event_id", "token_id", "outcome",
                     "uncertainty", "invalidation", "strategy_id", "strategy_version"):
            values[name] = str(raw[name])
        return cls(**values)


@dataclass(frozen=True)
class MarketContext:
    """Ce que le contrôleur sait du marché au moment de décider."""

    token_id: str
    active: bool
    closed: bool
    accepting_orders: bool
    data_ok: bool  # aucune incohérence détectée par le scanner
    best_bid: Decimal | None
    best_ask: Decimal | None
    book_time: datetime | None  # horodatage du carnet
    fees_enabled: bool | None  # None = inconnu
    fee_rate: Decimal | None
    fee_exponent: Decimal | None
    min_order_size: Decimal
    issues: tuple[str, ...] = ()


@dataclass
class Verdict:
    accepted: bool
    reasons: list[str] = field(default_factory=list)  # raisons de rejet
    checks: dict[str, str] = field(default_factory=dict)  # valeurs recalculées


# --------------------------------------------------------------------------- calculs


def fee_per_share(price: Decimal, rate: Decimal, exponent: Decimal) -> Decimal:
    """Frais « taker » par part, recalculés ici indépendamment de fees.py.

    Formule retenue (la plus prudente des deux lectures publiées) :
    frais = parts × taux × (p × (1 − p)) ^ exposant.
    """
    base = price * (ONE - price)
    if base <= 0:
        return ZERO
    if exponent == exponent.to_integral_value():
        value = rate * base ** int(exponent)
    else:
        value = rate * Decimal(str(float(base) ** float(exponent)))
    return value.quantize(Decimal("0.000001"), rounding=ROUND_UP)


def kelly_fraction_binary(prob: Decimal, cost_per_share: Decimal) -> Decimal:
    """Fraction de Kelly pour une part qui paie 1 si l'événement se produit."""
    if cost_per_share <= 0 or cost_per_share >= ONE:
        return ZERO
    return max(ZERO, (prob - cost_per_share) / (ONE - cost_per_share))


# --------------------------------------------------------------------------- décision


def evaluate(
    proposal: Proposal,
    state: LedgerState,
    market: MarketContext,
    limits: RiskLimits,
    now: datetime,
    marks: dict[str, Decimal] | None = None,
) -> Verdict:
    """Accepte ou rejette une proposition. Toutes les raisons de rejet sont listées."""
    reasons: list[str] = []
    checks: dict[str, str] = {}
    marks = marks or {}
    now = now.astimezone(timezone.utc)

    # 1. Survie : à 0 € tu meurs.
    if state.bankrupt:
        return Verdict(False, [f"FAILLITE : {state.bankrupt_reason}"], checks)
    if state.cash <= 0:
        return Verdict(False, [f"FAILLITE : solde disponible {state.cash} <= 0"], checks)
    if not state.initialized:
        return Verdict(False, ["journal non initialisé"], checks)

    # 2. Forme de la proposition.
    if proposal.side not in ("BUY", "SELL"):
        return Verdict(False, [f"sens inconnu : {proposal.side!r}"], checks)
    if not proposal.op_id or not proposal.strategy_id or not proposal.strategy_version:
        reasons.append("identifiant d'opération, stratégie ou version manquant")
    if proposal.op_id in state.op_ids:
        reasons.append("opération déjà comptabilisée (doublon)")
    if proposal.token_id != market.token_id:
        reasons.append("le contexte de marché ne correspond pas au jeton proposé")
    if proposal.shares <= 0:
        reasons.append("nombre de parts <= 0")
    if not (ZERO < proposal.max_price < ONE):
        reasons.append("prix limite hors de ]0, 1[")

    # 3. Qualité des données de marché.
    if not market.active or market.closed or not market.accepting_orders:
        reasons.append("marché inactif, fermé ou n'acceptant pas d'ordres")
    if not market.data_ok:
        reasons.append(f"données de marché non fiables : {list(market.issues)}")
    if market.book_time is None:
        reasons.append("carnet d'ordres absent")
    else:
        age = (now - market.book_time.astimezone(timezone.utc)).total_seconds()
        checks["book_age_seconds"] = f"{age:.1f}"
        if age > limits.max_book_age_seconds:
            reasons.append(f"carnet périmé ({age:.0f} s > {limits.max_book_age_seconds} s)")
        if age < -60:
            reasons.append("horodatage du carnet dans le futur")

    if proposal.side == "SELL":
        pos = state.positions.get(proposal.token_id)
        if pos is None or proposal.shares > pos.shares:
            reasons.append("vente supérieure aux parts détenues")
        if market.best_bid is None:
            reasons.append("aucun acheteur dans le carnet")
        return Verdict(not reasons, reasons, checks)

    # ----- BUY : ouverture ou renforcement de position
    if not (ZERO < proposal.prob_low <= proposal.est_probability <= proposal.prob_high < ONE):
        reasons.append("probabilités incohérentes (attendu 0 < bas <= estimée <= haut < 1)")
    if market.best_ask is None:
        reasons.append("aucun vendeur dans le carnet")
    if proposal.shares < market.min_order_size:
        reasons.append(f"taille inférieure au minimum du marché ({market.min_order_size})")
    if market.fees_enabled is None:
        reasons.append("frais du marché inconnus")
    elif market.fees_enabled and (market.fee_rate is None or market.fee_exponent is None
                                  or market.fee_rate < 0 or market.fee_exponent <= 0):
        reasons.append("barème de frais du marché inconnu ou invalide")
    if reasons:
        return Verdict(False, reasons, checks)

    price = proposal.max_price
    fee_ps = fee_per_share(price, market.fee_rate, market.fee_exponent) if market.fees_enabled else ZERO
    cost_ps = price + fee_ps
    cost_bound = proposal.shares * cost_ps  # coût maximal possible de l'ordre
    edge = proposal.prob_low - cost_ps  # avantage net dans le pire cas de l'intervalle
    total = state.total_estimated(marks)
    checks.update({"fee_per_share": str(fee_ps), "cost_bound": str(cost_bound),
                   "recomputed_net_edge": str(edge), "total_estimated": str(total)})

    if edge < limits.min_net_edge_floor:
        reasons.append(f"avantage net {edge:.4f} < plancher {limits.min_net_edge_floor}")
    if proposal.net_edge < limits.min_net_edge_floor:
        reasons.append("avantage net déclaré par la stratégie sous le plancher")
    if cost_bound > state.cash:
        reasons.append("coût supérieur au solde disponible")
    if total <= 0:
        reasons.append("capital total estimé <= 0")
        return Verdict(False, reasons, checks)

    existing = state.positions.get(proposal.token_id)
    existing_cost = existing.cost_basis if existing else ZERO
    if existing_cost + cost_bound > limits.max_position_pct * total:
        reasons.append(f"position > {limits.max_position_pct:.0%} du capital total")
    event_cost = sum((p.cost_basis for p in state.positions.values()
                      if p.event_id == proposal.event_id), ZERO)
    if event_cost + cost_bound > limits.max_event_pct * total:
        reasons.append(f"exposition à l'événement > {limits.max_event_pct:.0%} du capital total")
    if state.cash - cost_bound < limits.min_cash_pct * total:
        reasons.append(f"liquidités restantes < {limits.min_cash_pct:.0%} du capital total")
    if existing is None and len(state.positions) >= limits.max_open_positions:
        reasons.append(f"nombre maximal de positions ouvertes atteint ({limits.max_open_positions})")

    kelly = kelly_fraction_binary(proposal.prob_low, cost_ps)
    kelly_cap = limits.kelly_fraction * kelly * total
    checks["kelly_cap"] = str(kelly_cap)
    if cost_bound > kelly_cap:
        reasons.append("taille supérieure à la fraction de Kelly autorisée")

    if limits.no_averaging_down and existing is not None:
        mark = marks.get(proposal.token_id, market.best_bid)
        if mark is None or mark < existing.avg_cost:
            reasons.append("renforcement d'une position perdante interdit")

    loss_today = -state.realized_today(now)
    if loss_today > 0 and loss_today >= limits.daily_loss_pause_pct * (total + loss_today):
        reasons.append("pause : perte réalisée du jour >= limite quotidienne")

    return Verdict(not reasons, reasons, checks)
