"""Caractéristiques de prix passées, calculées EXACTEMENT comme dans le backtest.

- prix il y a 6 h : dernier point d'horodatage <= now − 6 h, s'il a moins de 2 h ;
- changements sur 24 h : nombre de variations entre points consécutifs sur ]now − 24 h, now].
"""

from __future__ import annotations

MAX_AGE_S = 2 * 3600


def price_at(points: list[tuple[int, float]], ts: int, max_age: int = MAX_AGE_S) -> float | None:
    best = None
    for t, p in points:
        if t > ts:
            break
        best = (t, p)
    if best is None or ts - best[0] > max_age:
        return None
    return best[1]


def changes_in_window(points: list[tuple[int, float]], ts: int, window: int = 24 * 3600) -> int:
    changes, previous = 0, None
    for t, p in points:
        if t > ts:
            break
        if t > ts - window and previous is not None and p != previous:
            changes += 1
        previous = p
    return changes
