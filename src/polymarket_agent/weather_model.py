"""Marchés « température maximale » : lecture de la question et issue déjà certaine (chantier n°0).

Le maximum du jour ne peut que monter. Si le maximum prudent déjà relevé (`sources/weather.py`,
`data.max_jour_c`) dépasse nettement le haut d'une tranche, cette tranche est perdue d'avance ;
s'il atteint le bas d'une tranche « X ou plus », elle est gagnée d'avance.
Formes de questions vérifiées le 16/10/2026 sur Gamma :
  « Will the highest temperature in Paris be 18°C on October 15? »
  « … be 17°C or below on …», « … 27°C or higher on …», « … between 76-77°F on … »
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MONTHS = {m: i for i, m in enumerate(
    ("january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"), 1)}
PATTERN = re.compile(
    r"highest temperature in .+? be (?:between )?(-?\d+)(?:\s*-\s*(-?\d+))?\s*°\s*([CF])( or below| or higher)?"
    r" on ([A-Za-z]+) (\d{1,2})", re.I)


@dataclass(frozen=True)
class Bucket:
    low: float | None   # None : « X ou moins »
    high: float | None  # None : « X ou plus »
    unit: str           # "C" ou "F"
    month: int
    day: int


def parse_bucket(question: str) -> Bucket | None:
    m = PATTERN.search(question or "")
    if not m:
        return None
    a, b, unit, tail, month, day = m.groups()
    month_n = MONTHS.get(month.lower())
    if month_n is None:
        return None
    lo, hi = float(a), float(b if b is not None else a)
    tail = (tail or "").strip().lower()
    if tail == "or below":
        return Bucket(None, hi, unit.upper(), month_n, int(day))
    if tail == "or higher":
        return Bucket(lo, None, unit.upper(), month_n, int(day))
    return Bucket(lo, hi, unit.upper(), month_n, int(day))


def certain_side(bucket: Bucket, max_c: float, margin_c: float = 1.0, margin_f: float = 2.0) -> int | None:
    """0 = « Oui » certain, 1 = « Non » certain, None = rien de sûr.

    Marge : METAR en °C entiers, conversion °F arrondie, relevés intermédiaires absents : on exige
    `margin` degrés d'avance (le maximum METAR est un minimum du maximum officiel : jamais trop haut)."""
    if bucket.unit == "F":
        value, margin = max_c * 9 / 5 + 32, margin_f
    else:
        value, margin = max_c, margin_c
    if bucket.high is not None and value >= bucket.high + margin:
        return 1  # le maximum a déjà dépassé le haut de la tranche
    if bucket.high is None and bucket.low is not None and value >= bucket.low + margin:
        return 0  # « X ou plus » déjà atteint
    return None
