"""Modèle de probabilité pour les marchés crypto à seuil (« Bitcoin au-dessus de 80 000 $ le 15 ? »).

Estimation INDÉPENDANTE du prix Polymarket : prix au comptant (Coinbase/Kraken) et
volatilité réalisée horaire sur ~7 jours, marche aléatoire log-normale sans dérive.
  - « au-dessus / en dessous de K à l'échéance » : P = Φ(∓ ln(K/S) / (σ√τ)) ;
  - « atteindre / descendre à K avant l'échéance » (barrière) : P = 2 × P(finir au-delà),
    principe de réflexion, plafonné à 1.
Incertitude de modèle : on recalcule avec σ × 0,8 et σ × 1,25 (les queues épaisses de la
crypto) ; l'intervalle va du plus petit au plus grand des trois résultats.
LIMITES : marchés « entre X et Y » ignorés ; la source de résolution (souvent une bougie
Binance à 12 h ET) peut différer légèrement de Coinbase/Kraken ; pas de saut de prix modélisé.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

ABOVE = ("above", "over", "greater than", "higher than", "at or above", "au-dessus")
BELOW = ("below", "under", "less than", "lower than", "at or below", "en dessous", "sous")
TOUCH_DOWN = ("dip to", "fall to", "drop to", "dip below", "fall below", "drop below", "crash to")
TOUCH_UP = ("reach", "hit", "rise to", "pump to", "climb to", "surpass", "break")
_PRICE = re.compile(r"\$\s?([\d][\d,]*(?:\.\d+)?)\s?([kKmM])?\b")


@dataclass(frozen=True)
class ThresholdQuestion:
    kind: str  # "above", "below", "touch_up", "touch_down"
    threshold: float


def parse_question(question: str) -> ThresholdQuestion | None:
    q = question.lower()
    if " between " in q or " and $" in q:
        return None
    m = _PRICE.search(question)
    if not m:
        return None
    value = float(m.group(1).replace(",", ""))
    suffix = (m.group(2) or "").lower()
    value *= 1000 if suffix == "k" else 1_000_000 if suffix == "m" else 1
    if value <= 0:
        return None
    for words, kind in ((TOUCH_DOWN, "touch_down"), (TOUCH_UP, "touch_up"), (ABOVE, "above"), (BELOW, "below")):
        if any(re.search(rf"\b{re.escape(w)}\b", q) for w in words):  # mots entiers (« hit » ≠ « white »)
            return ThresholdQuestion(kind, value)
    return None


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def probability(question: ThresholdQuestion, spot: float, hourly_vol: float, hours: float) -> float | None:
    """Probabilité de « Oui ». None si l'issue est déjà connue ou les données absurdes."""
    if spot <= 0 or hourly_vol <= 0 or hours <= 0:
        return None
    s = hourly_vol * math.sqrt(hours)
    z = math.log(question.threshold / spot) / s
    if question.kind == "above":
        return 1 - _phi(z)
    if question.kind == "below":
        return _phi(z)
    if question.kind == "touch_up":
        return None if spot >= question.threshold else min(1.0, 2 * (1 - _phi(z)))
    if question.kind == "touch_down":
        return None if spot <= question.threshold else min(1.0, 2 * _phi(z))
    return None


def probability_band(question: ThresholdQuestion, spot: float, hourly_vol: float,
                     hours: float) -> tuple[float, float, float] | None:
    """(bas, estimée, haut) en faisant varier la volatilité (incertitude de modèle)."""
    values = [probability(question, spot, hourly_vol * k, hours) for k in (0.8, 1.0, 1.25)]
    if any(v is None for v in values):
        return None
    clip = lambda v: min(max(v, 0.001), 0.999)
    return clip(min(values)), clip(values[1]), clip(max(values))
