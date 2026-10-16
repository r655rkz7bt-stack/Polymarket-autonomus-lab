"""Modèle météo pour les marchés « température maximale / minimale à <ville> le <jour> ».

Probabilité INDÉPENDANTE qu'une tranche soit la bonne, tirée des prévisions d'ensemble (31
scénarios du modèle américain GFS, Open-Meteo, gratuit) pour les coordonnées de la station qui
tranche le marché, corrigée par ce que la station a déjà relevé ce jour-là (le maximum ne peut
que monter, le minimum que descendre).

Chaque scénario est « flouté » par une erreur normale d'écart-type `sigma` (écart entre la grille
du modèle et la station, arrondis de l'affichage), puis la fourchette prudente est le minimum et
le maximum de la probabilité quand on décale tous les scénarios de ±`bias` et qu'on élargit le
flou. Paramètres bornés dans config/strategies.yaml ; rien n'est supposé calibré : l'arène juge.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass

MONTHS = {m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august", "september",
     "october", "november", "december"], start=1)}
INF = float("inf")


@dataclass(frozen=True)
class TempQuestion:
    kind: str        # "max" ou "min"
    low: float       # borne basse de la tranche, dans l'unité du marché (incluse)
    high: float      # borne haute (exclue)
    unit: str        # "C" ou "F"
    month: int
    day: int


def parse_question(question: str) -> TempQuestion | None:
    """« Will the highest temperature in Paris be 16°C on October 17? » → tranche [15,5 ; 16,5[."""
    q = (question or "").replace("º", "°")
    kind = "max" if "highest temperature" in q else "min" if "lowest temperature" in q else None
    date = re.search(r" on ([A-Z][a-z]+) (\d{1,2})\b", q)
    if kind is None or not date or date.group(1).lower() not in MONTHS:
        return None
    month, day = MONTHS[date.group(1).lower()], int(date.group(2))
    m = re.search(r"between (-?\d+)-(-?\d+)°([CF])", q)
    if m:
        return TempQuestion(kind, float(m.group(1)) - 0.5, float(m.group(2)) + 0.5, m.group(3), month, day)
    m = re.search(r"(-?\d+)°([CF]) or (?:higher|above)", q)
    if m:
        return TempQuestion(kind, float(m.group(1)) - 0.5, INF, m.group(2), month, day)
    m = re.search(r"(-?\d+)°([CF]) or (?:below|lower)", q)
    if m:
        return TempQuestion(kind, -INF, float(m.group(1)) + 0.5, m.group(2), month, day)
    m = re.search(r"be (-?\d+)°([CF]) on", q)
    if m:
        return TempQuestion(kind, float(m.group(1)) - 0.5, float(m.group(1)) + 0.5, m.group(2), month, day)
    return None


def to_unit(celsius: float, unit: str) -> float:
    return celsius if unit == "C" else celsius * 9 / 5 + 32


def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def probability(q: TempQuestion, members_c: list[float], sigma_c: float, shift_c: float = 0.0,
                observed_c: float | None = None) -> float | None:
    """P(valeur du jour dans la tranche) : moyenne des scénarios floutés (unité du marché)."""
    if not members_c or sigma_c <= 0:
        return None
    scale = 1.0 if q.unit == "C" else 1.8
    sigma = sigma_c * scale
    total = 0.0
    floor = to_unit(observed_c, q.unit) if observed_c is not None else None
    for m in members_c:
        v = to_unit(m + shift_c, q.unit)
        if floor is not None:  # un scénario ne peut pas contredire ce qui a déjà été relevé
            v = max(v, floor) if q.kind == "max" else min(v, floor)
        hi = 1.0 if q.high == INF else _phi((q.high - v) / sigma)
        lo = 0.0 if q.low == -INF else _phi((q.low - v) / sigma)
        p = max(0.0, hi - lo)
        if floor is not None:
            # Déjà relevé : un maximum ne descendra plus sous `floor`, un minimum ne remontera plus.
            if q.kind == "max" and q.high != INF and q.high <= floor:
                p = 0.0
            elif q.kind == "min" and q.low != -INF and q.low > floor:
                p = 0.0
        total += p
    return total / len(members_c)


def band(q: TempQuestion, members_c: list[float], sigma_c: float, bias_c: float, widen: float,
         observed_c: float | None = None) -> tuple[float, float, float] | None:
    """(bas, estimation, haut) : décalage ±bias et flou ×widen, le pire et le meilleur cas."""
    est = probability(q, members_c, sigma_c, 0.0, observed_c)
    if est is None:
        return None
    variants = [probability(q, members_c, s, b, observed_c)
                for s in (sigma_c, sigma_c * widen) for b in (-bias_c, 0.0, bias_c)]
    return min(variants), est, max(variants)


# --------------------------------------------------------------------------- stratégie temperature_floor
# (ajouté par le chercheur le 16/10/2026) : issue déjà certaine d'après le relevé du jour.
# Mesuré le même jour : le marché cote déjà ces tranches 0,001 (33 cas sur 33), voir
# experiments/meteo_backtest.md ; gardé, l'arène le confirmera.

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
