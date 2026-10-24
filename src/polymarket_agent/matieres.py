"""Barres touchées par l'or et l'argent (24/10/2026, experiments/commodites_toucher.md) : marchés « What will Gold (XAUUSD) / Silver (XAGUSD) hit Week of … ».

Une barre HIGH (« hit (HIGH) $4,300 ») est gagnée si le prix monte à 4 300 $ ou plus avant la fin de la semaine ; une barre LOW si le prix descend à la barre ou
en dessous. Le règlement lit les bougies d'1 minute de Pyth ; on enregistre, à chaque cycle, le prix au comptant (sources/goldapi.py, table `prix_matieres`) et on
en tire le maximum et le minimum déjà atteints depuis la création du marché.
Chance de toucher d'ici la fin : barrière d'un mouvement brownien sans dérive, volatilité par heure fixe (`SIGMA_H`, médiane quadratique d'un an de
contrats à terme), `2 × (1 − Φ(|ln(K / S)| / (σ √τ)))` avec τ = heures restantes × 23/24. Barre déjà atteinte (ou à moins de `MARGE_BOUGIE` d'un extrême relevé :
une bougie d'1 minute a pu la toucher entre deux relevés) : pas de chance calculée. `attach_matieres` pose `market.references["matieres"] = {"p", "titre", "vu_le"}`
(p = chance du OUI), seulement si le journal des prix couvre le marché depuis sa création (premier relevé au plus `COUVERTURE_H` heures après).
Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from math import erfc, log, sqrt

SIGMA_H = {"XAUUSD": 0.0036, "XAGUSD": 0.0080}       # écart-type du rendement d'une heure
TITLE = re.compile(r"What will (?:Gold|Silver) \((XAUUSD|XAGUSD)\) hit Week of", re.IGNORECASE)
BAR = re.compile(r"hit \((HIGH|LOW)\) \$([\d,]+(?:\.\d+)?)", re.IGNORECASE)
MIN_HOURS_LEFT = 18.0     # le test sur le passé s'arrête 18 h avant la fin
COUVERTURE_H = 12.0
MAX_STALE_MINUTES = 30.0
MARGE_BOUGIE = 0.001      # 0,1 % : un extrême relevé à moins de cette distance de la barre = barre peut-être touchée


def symbol_of(event_title: str) -> str | None:
    m = TITLE.search(event_title or "")
    return m.group(1).upper() if m else None


def bar_of(question: str) -> tuple[str, float] | None:
    m = BAR.search(question or "")
    return (m.group(1).upper(), float(m.group(2).replace(",", ""))) if m else None


def record_prices(db, rows: list[dict], now: datetime, keep_days: float = 30) -> int:
    """Ajoute les prix relevés à la table `prix_matieres` (symbole, t) ; garde `keep_days` jours."""
    if db is None or not rows:
        return 0
    db.conn.executescript("CREATE TABLE IF NOT EXISTS prix_matieres (symbole TEXT, t INTEGER, prix REAL, PRIMARY KEY (symbole, t));")
    db.conn.executemany("INSERT OR REPLACE INTO prix_matieres VALUES (?,?,?)", [(r["symbole"], int(r["t"]), float(r["prix"])) for r in rows])
    db.conn.execute("DELETE FROM prix_matieres WHERE t < ?", (int((now - timedelta(days=keep_days)).timestamp()),))
    db.conn.commit()
    return len(rows)


def history(db, symbol: str, since: float) -> list[tuple[int, float]]:
    try:
        cur = db.conn.execute("SELECT t, prix FROM prix_matieres WHERE symbole = ? AND t >= ? ORDER BY t", (symbol, int(since)))
    except Exception:  # noqa: BLE001 - table absente : pas encore de relevé
        return []
    return [(int(t), float(p)) for t, p in cur.fetchall()]


def hit_probability(side: str, strike: float, spot: float, sigma: float, hours_left: float) -> float:
    """Chance de toucher `strike` d'ici la fin (mouvement brownien sans dérive, rien déjà touché)."""
    tau = max(hours_left * 23 / 24, 0.5)
    d = abs(log(strike / spot)) / (sigma * sqrt(tau))
    return min(1.0, erfc(d / sqrt(2)))          # 2 × (1 − Φ(d))


def bar_state(side: str, strike: float, extreme: float) -> str:
    """« touchee », « incertaine » (moins de MARGE_BOUGIE de la barre) ou « libre »."""
    reach = extreme >= strike if side == "HIGH" else extreme <= strike
    if reach:
        return "touchee"
    gap = abs(log(strike / extreme))
    return "incertaine" if gap <= MARGE_BOUGIE else "libre"


def attach_matieres(markets, db, now: datetime) -> int:
    """Rattache la chance du OUI aux barres de la semaine de l'or et de l'argent (journal `prix_matieres`)."""
    if db is None:
        return 0
    n, cache = 0, {}
    for m in markets:
        if [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        sym, bar = symbol_of(m.event_title or ""), bar_of(m.question)
        if sym is None or bar is None or m.end_date is None or m.created_at is None:
            continue
        start = max(m.created_at, now - timedelta(days=9)).astimezone(timezone.utc)
        end = m.end_date.astimezone(timezone.utc)
        hours_left = (end - now).total_seconds() / 3600
        if hours_left < MIN_HOURS_LEFT or now < start:
            continue
        key = (sym, int(start.timestamp()))
        if key not in cache:
            cache[key] = history(db, sym, start.timestamp())
        rows = cache[key]
        if not rows or rows[0][0] > start.timestamp() + COUVERTURE_H * 3600 or (now.timestamp() - rows[-1][0]) > MAX_STALE_MINUTES * 60:
            continue
        side, strike = bar
        extreme = max(p for _, p in rows) if side == "HIGH" else min(p for _, p in rows)
        state = bar_state(side, strike, extreme)
        spot = rows[-1][1]
        if state == "touchee":
            p, label = 0.99, f"{sym} a déjà touché {strike:g} (extrême relevé {extreme:g})"
        elif state == "incertaine":
            continue
        else:
            p = hit_probability(side, strike, spot, SIGMA_H[sym], hours_left)
            label = f"{sym} {spot:g}, barre {side} {strike:g}, {hours_left:.0f} h restantes : chance de toucher {p:.3f}"
        m.references = dict(m.references or {}, matieres={"p": round(p, 4), "titre": label, "vu_le": datetime.fromtimestamp(rows[-1][0], timezone.utc).isoformat(), "touchee": state == "touchee"})
        n += 1
    return n
