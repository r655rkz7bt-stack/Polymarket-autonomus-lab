"""Séismes (24/10/2026, experiments/seismes.md) : marchés « plus gros séisme du jour » et « combien de séismes cette semaine ».

Les deux se règlent sur le catalogue USGS (l'ARBITRE), que l'on peut lire en direct (sources/usgs.py, séismes >= 5,0).
- Jour (UTC) : loi du plus gros séisme = maximum déjà observé + chance qu'aucun séisme plus fort n'arrive d'ici minuit, d'après la part
  des jours des 3 dernières années sans séisme >= x dans les mêmes heures restantes (seismes_tables.json, `jour`).
- Semaine (lundi 00 h à dimanche 24 h, heure de l'Est) : nombre déjà observé + reste ~ binomiale négative (Gamma-Poisson des 156
  dernières semaines, `semaine`) : elle prend en compte les répliques (variance 3 fois la moyenne à 5,5).
Test sur le passé : experiments/seismes.md. `attach_seismes` pose `market.references["seismes"] = {"p", "titre", "vu_le"}` (p = chance du OUI).
Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from math import exp, lgamma, log
from pathlib import Path
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")
MONTHS = {m: i + 1 for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August",
                                           "September", "October", "November", "December"))}
DAILY = re.compile(r"biggest earthquake be on (\w+) (\d+), (\d{4})", re.IGNORECASE)
WEEKLY = re.compile(r"How many ([\d.]+) or above earthquakes.*?(\w+) (\d+) - (?:(\w+) )?(\d+)\?", re.IGNORECASE)
# Seuils (arrondi au dixième : « 5,3 à 5,4 » = [5,25 ; 5,45[) des tranches du jour.
DAILY_THRESHOLDS = (5.25, 5.45, 5.65, 5.85, 6.05)
DAILY_BRACKETS = {"under 5.3": (-1.0, 5.25), "5.3 to 5.4": (5.25, 5.45), "5.5 to 5.6": (5.45, 5.65),
                  "5.7 to 5.8": (5.65, 5.85), "5.9 to 6.0": (5.85, 6.05), "6.1 or more": (6.05, 99.0)}
FIRST_HOUR, LAST_HOUR = 6.0, 23.0   # le test sur le passé couvre 6 h, 12 h et 18 h UTC ; avant 6 h : pas de test
WEEK_MIN_DAYS, WEEK_MAX_DAYS = 0.5, 6.6


@lru_cache(maxsize=1)
def tables() -> dict:
    return json.loads((Path(__file__).with_name("seismes_tables.json")).read_text())


def daily_target(event_title: str) -> datetime | None:
    """Début (UTC) du jour visé par « What will the biggest earthquake be on <date> ? »."""
    m = DAILY.search(event_title or "")
    try:
        return datetime(int(m.group(3)), MONTHS[m.group(1).capitalize()], int(m.group(2)), tzinfo=timezone.utc) if m else None
    except (KeyError, ValueError):
        return None


def daily_bracket(question: str) -> tuple[float, float] | None:
    q = (question or "").lower()
    for key, bounds in DAILY_BRACKETS.items():
        if key in q:
            return bounds
    return None


def weekly_target(event_title: str, end_date: datetime | None) -> tuple[float, datetime, datetime] | None:
    """(magnitude, début, fin) en UTC : jours entiers à l'heure de l'Est (New York), année tirée de la date de fin du marché."""
    m = WEEKLY.search(event_title or "")
    if not m or end_date is None:
        return None
    try:
        year = end_date.astimezone(timezone.utc).year
        mo1, d1 = MONTHS[m.group(2).capitalize()], int(m.group(3))
        mo2, d2 = (MONTHS[m.group(4).capitalize()] if m.group(4) else mo1), int(m.group(5))
        start = datetime(year - 1 if mo1 > mo2 else year, mo1, d1, tzinfo=NEW_YORK)
        end = datetime(year, mo2, d2, tzinfo=NEW_YORK) + timedelta(days=1)
        return float(m.group(1)), start.astimezone(timezone.utc), end.astimezone(timezone.utc)
    except (KeyError, ValueError):
        return None


def weekly_bracket(question: str) -> tuple[int, int] | None:
    """(bas, haut) du nombre de séismes de la tranche, bornes comprises ; haut très grand = « plus de N »."""
    q = question or ""
    m = re.search(r"more than (\d+)", q)
    if m:
        return int(m.group(1)) + 1, 10 ** 6
    m = re.search(r"(\d+) or fewer", q) or re.search(r"≤\s*(\d+)", q)
    if m:
        return 0, int(m.group(1))
    m = re.search(r"(?:exactly )?(\d+) earthquake", q)
    return (int(m.group(1)), int(m.group(1))) if m else None


def _interp_no_event(hour: float, x: float) -> float:
    jour = tables()["jour"]
    h0 = min(int(hour), 23)
    a, b = jour[str(h0)][str(x)], jour[str(h0 + 1)][str(x)]
    return a + (b - a) * (hour - h0)


def daily_cdf(rows: list[dict], day: datetime, now: datetime) -> dict[float, float] | None:
    """{x: chance que le plus gros séisme du jour soit < x}, ou None hors de la plage horaire testée."""
    hour = (now - day).total_seconds() / 3600
    if not FIRST_HOUR <= hour <= LAST_HOUR:
        return None
    a, b = day.timestamp(), min(now.timestamp(), day.timestamp() + 86400)
    so_far = max([float(r["mag"]) for r in rows if a <= float(r["t"]) < b and r.get("mag") is not None] or [0.0])
    return {x: (1.0 if so_far < x else 0.0) * _interp_no_event(hour, x) for x in DAILY_THRESHOLDS}


def daily_p(rows, day, now, bracket) -> float | None:
    cdf = daily_cdf(rows, day, now)
    if cdf is None:
        return None
    lo, hi = bracket
    return max(0.0, (cdf[hi] if hi in cdf else 1.0) - (cdf[lo] if lo in cdf else 0.0))


def _nb_pmf(k: int, r: float, p: float) -> float:
    return exp(lgamma(k + r) - lgamma(r) - lgamma(k + 1) + r * log(p) + k * log(1 - p))


def weekly_count(rows: list[dict], mag: float, start: datetime, now: datetime) -> int:
    a, b = start.timestamp(), now.timestamp()
    return sum(1 for r in rows if a <= float(r["t"]) < b and r.get("mag") is not None and round(float(r["mag"]) + 1e-9, 1) >= mag)


def weekly_p(rows, mag: float, start: datetime, end: datetime, now: datetime, bracket: tuple[int, int]) -> tuple[float, int] | None:
    """(chance que le compte final tombe dans la tranche, compte déjà observé) ; None hors des 6,6 jours qui précèdent la fin."""
    prm = tables()["semaine"].get(f"{mag:.1f}")
    left = (end - now).total_seconds() / 86400
    if prm is None or not WEEK_MIN_DAYS <= left <= WEEK_MAX_DAYS or (now - start).total_seconds() > 9 * 86400:
        return None
    n = weekly_count(rows, mag, start, now)
    f = (now - start).total_seconds() / (end - start).total_seconds()
    r, p = prm["alpha"] + n, (prm["beta"] + f) / (prm["beta"] + 1)
    lo, hi = bracket
    if hi < n:
        return 0.0, n
    return min(1.0, sum(_nb_pmf(k - n, r, p) for k in range(max(lo, n), min(hi, n + 80) + 1))), n


def attach_seismes(markets, db, now: datetime) -> int:
    """Rattache la chance du OUI aux marchés « plus gros séisme du jour » et « nombre de séismes de la semaine » (références `ref:usgs`)."""
    if db is None:
        return 0
    from polymarket_agent.references import _load
    seen, rows = _load(db, "ref:usgs")
    if seen is None or not rows:
        return 0
    n = 0
    for m in markets:
        title = m.event_title or ""
        if [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        label = None
        day = daily_target(title)
        if day is not None:
            br = daily_bracket(m.question)
            p = daily_p(rows, day, now, br) if br else None
            if p is not None:
                label = f"plus gros séisme du {day:%d/%m} : loi calculée {p:.3f} pour cette tranche (maximum déjà vu et heures restantes)"
        else:
            wk = weekly_target(title, m.end_date)
            br = weekly_bracket(m.question) if wk else None
            res = weekly_p(rows, wk[0], wk[1], wk[2], now, br) if wk and br else None
            if res is not None:
                p, seen_n = res
                label = f"séismes >= {wk[0]:g} du {wk[1]:%d/%m} au {wk[2] - timedelta(seconds=1):%d/%m} : {seen_n} déjà vus, loi calculée {p:.3f} pour cette tranche"
        if label is None:
            continue
        m.references = dict(m.references or {}, seismes={"p": round(p, 4), "titre": label, "vu_le": seen.isoformat()})
        n += 1
    return n
