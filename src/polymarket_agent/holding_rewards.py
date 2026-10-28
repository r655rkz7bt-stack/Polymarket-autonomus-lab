"""Récompense de DÉTENTION de Polymarket : estimation pour nos positions (AMELIORATION du 19/10/2026).

Programme public (docs.polymarket.com/polymarket-learn/trading/holding-rewards, résumé lu le
19/10/2026 ; la page elle-même n'est pas joignable depuis le labo) : sur les marchés éligibles,
Polymarket verse un taux annuel (4,00 % le 19/10/2026, variable, plafonnable à sa discrétion) sur la
VALEUR des positions détenues, mesurée toutes les heures et payée chaque jour. Éligibilité marché par
marché : champ Gamma `holdingRewardsEnabled` (vérifié en direct le 19/10/2026 : 11 des 100 marchés
les plus échangés, surtout la politique à long terme).

Estimation (prudente) : à chaque cycle, valeur de chaque position éligible au MEILLEUR ACHETEUR
(prix auquel on pourrait la revendre) × taux × durée du cycle. Comme les récompenses de liquidité
(option A d'Etienne, 17/10/2026) : comptée pour le CLASSEMENT de l'arène (× prudence), jamais
dans le capital d'un fantôme ; le versement au capital public attend le noyau
(proposals/2026-10-19_detention_et_remises.md). C'est une ESTIMATION : seul le journal signé fait foi.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

SCHEMA = """
CREATE TABLE IF NOT EXISTS recompenses_detention (
    cycle_id TEXT, estime_at TEXT, portefeuille TEXT, market_id TEXT,
    valeur REAL, montant REAL,
    PRIMARY KEY (cycle_id, portefeuille, market_id)
);
"""
MINUTES_PER_YEAR = 365 * 24 * 60


def accrue(positions: dict, marks: dict[str, Decimal], by_market: dict, rate: float,
           minutes: float) -> dict[str, tuple[float, float]]:
    """{market_id: (valeur au meilleur acheteur, récompense estimée pour `minutes`)} des positions
    détenues sur des marchés éligibles. Sans prix de revente connu : rien (prudence)."""
    out: dict[str, tuple[float, float]] = {}
    for token, pos in positions.items():
        market = by_market.get(pos.market_id)
        bid = marks.get(token)
        if market is None or not getattr(market, "holding_rewards", False) or bid is None or bid <= 0:
            continue
        value = float(pos.shares * bid)
        before = out.get(pos.market_id, (0.0, 0.0))
        out[pos.market_id] = (before[0] + value, before[1] + value * rate * minutes / MINUTES_PER_YEAR)
    return out


def record(db, cycle_id: str, now: datetime, portfolio: str, amounts: dict[str, tuple[float, float]]) -> float:
    db.conn.executescript(SCHEMA)
    for market_id, (value, amount) in amounts.items():
        db.conn.execute("INSERT OR REPLACE INTO recompenses_detention VALUES (?,?,?,?,?,?)",
                        (cycle_id, now.isoformat(timespec="seconds"), portfolio, market_id, value, amount))
    db.conn.commit()
    return sum(a for _, a in amounts.values())


def totals(db, since_iso: str) -> dict[str, float]:
    """{portefeuille: récompense estimée cumulée depuis `since_iso`}."""
    db.conn.executescript(SCHEMA)
    return {p: round(t or 0.0, 6) for p, t in db.conn.execute(
        "SELECT portefeuille, SUM(montant) FROM recompenses_detention WHERE estime_at >= ? GROUP BY 1",
        (since_iso,))}


def ranking_bonus(db, starts: dict[str, datetime | None], prudence: float) -> dict[str, float]:
    """{nom de l'arène: récompense de détention estimée × prudence}, depuis le début de l'époque de
    chaque fantôme (base : « fantome:<nom> »). Jamais ajoutée à un capital."""
    if prudence <= 0:
        return {}
    out = {}
    for name, start in starts.items():
        since = start.isoformat(timespec="seconds") if start else ""
        total = totals(db, since).get("fantome:" + name, 0.0)
        if total > 0:
            out[name] = round(total * prudence, 4)
    return out
