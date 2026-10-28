"""Historique du classement de l'arène (lot C, 15/10/2026) : qui mène, depuis quand, qui remonte.

Une photo du classement par heure (table `arena_history`), prise quand le tableau de bord est
régénéré. Elle sert au graphique « classement dans le temps » et au résumé « aujourd'hui ».
Libre : le chercheur peut changer la fréquence ou ce qui est gardé.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

SCHEMA = """
CREATE TABLE IF NOT EXISTS arena_history (
    taken_at TEXT NOT NULL,
    name TEXT NOT NULL,
    rank INTEGER NOT NULL,
    capital REAL NOT NULL,
    operations INTEGER NOT NULL,
    eliminated INTEGER NOT NULL,
    PRIMARY KEY (taken_at, name)
);
"""


def _iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat(timespec="seconds")


def record(db, rows: list[dict], now: datetime, every_minutes: float = 60) -> bool:
    """Ajoute une photo du classement (`rows` = arène du tableau de bord, déjà triée) si la
    précédente date de plus de `every_minutes`. Retourne True si une photo a été prise."""
    db.conn.executescript(SCHEMA)
    last = db.conn.execute("SELECT MAX(taken_at) FROM arena_history").fetchone()[0]
    if last and datetime.fromisoformat(last) > now - timedelta(minutes=every_minutes) + timedelta(seconds=30):
        return False
    stamp = _iso(now)
    db.conn.executemany("INSERT OR REPLACE INTO arena_history VALUES (?,?,?,?,?,?)",
                        [(stamp, r["nom"], i + 1, float(r["capital"]), int(r["operations"]), int(bool(r["eliminee"])))
                         for i, r in enumerate(rows)])
    db.conn.commit()
    return True


def series(db, now: datetime, days: float = 7) -> dict:
    """{"dates": [...], "strategies": {nom: [rang ou None, ...]}, "capital": {nom: [...]}}."""
    db.conn.executescript(SCHEMA)
    rows = db.conn.execute("SELECT taken_at, name, rank, capital FROM arena_history WHERE taken_at >= ? "
                           "ORDER BY taken_at", (_iso(now - timedelta(days=days)),)).fetchall()
    dates = sorted({r[0] for r in rows})
    index = {d: i for i, d in enumerate(dates)}
    ranks: dict[str, list] = {}
    capital: dict[str, list] = {}
    for taken, name, rank, cap in rows:
        ranks.setdefault(name, [None] * len(dates))[index[taken]] = rank
        capital.setdefault(name, [None] * len(dates))[index[taken]] = round(cap, 2)
    return {"dates": [d[:16] for d in dates], "strategies": ranks, "capital": capital}


def rank_at(db, when: datetime) -> dict[str, int]:
    """Classement de la dernière photo prise avant `when` (vide si aucune)."""
    db.conn.executescript(SCHEMA)
    row = db.conn.execute("SELECT MAX(taken_at) FROM arena_history WHERE taken_at <= ?", (_iso(when),)).fetchone()
    if not row or not row[0]:
        return {}
    return dict(db.conn.execute("SELECT name, rank FROM arena_history WHERE taken_at=?", (row[0],)).fetchall())
