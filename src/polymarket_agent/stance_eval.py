"""Justesse de Gemini : ses avis comparés au résultat réel des marchés résolus.

Chaque avis (« oui » : le texte rend l'issue Oui plus probable, « non » : moins probable) est
jugé quand le marché est réglé (prix finaux 1/0, cf. settlement.py). Les marchés 50-50 et
les avis « neutre » ne comptent pas. Mesure brute ET pondérée par la confiance déclarée.
C'est un indicateur de recherche : il dit si les avis de Gemini méritent qu'on s'y fie.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.settlement import resolution_payout

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS stance_outcomes (
    market_id TEXT PRIMARY KEY,
    yes_payout REAL,
    checked_at TEXT NOT NULL
);
"""


def _iso(ts: datetime) -> str:
    return ts.astimezone(timezone.utc).isoformat()


def update_outcomes(db, get_market, now: datetime, budget: int = 10, recheck_hours: float = 6) -> int:
    """Interroge au plus `budget` marchés classés par Gemini pas encore résolus (chacun au plus
    toutes les `recheck_hours` heures). Retourne le nombre de marchés nouvellement résolus."""
    db.conn.executescript(SCHEMA)
    since = _iso(now - timedelta(hours=recheck_hours))
    rows = db.conn.execute(
        "SELECT DISTINCT s.market_id FROM stances s LEFT JOIN stance_outcomes o ON o.market_id = s.market_id "
        "WHERE o.market_id IS NULL OR (o.yes_payout IS NULL AND o.checked_at < ?) "
        "ORDER BY s.market_id LIMIT ?", (since, int(budget))).fetchall()
    resolved = 0
    for (market_id,) in rows:
        try:
            raw = get_market(market_id)
        except (SourceUnavailable, ValueError) as exc:
            log.info("justesse Gemini : marché %s illisible (%s)", market_id, exc)
            continue
        payout = None
        if isinstance(raw, dict):
            tokens = raw.get("clobTokenIds")
            tokens = json.loads(tokens) if isinstance(tokens, str) else tokens
            if isinstance(tokens, list) and tokens:
                result = resolution_payout(raw, str(tokens[0]))  # issue n°0 = « Oui »
                payout = float(result[0]) if result else None
        db.conn.execute("INSERT OR REPLACE INTO stance_outcomes VALUES (?, ?, ?)", (market_id, payout, _iso(now)))
        resolved += payout is not None
    db.conn.commit()
    return resolved


def score(db) -> dict:
    """{"avis": n, "justes": k, "justesse": k/n, "justesse_ponderee": …, "marches": m}."""
    db.conn.executescript(SCHEMA)
    rows = db.conn.execute(
        "SELECT s.market_id, s.stance, o.yes_payout FROM stances s JOIN stance_outcomes o ON o.market_id = s.market_id "
        "WHERE o.yes_payout IN (0, 1)").fetchall()
    n = right = 0
    weight = weighted_right = 0.0
    markets = set()
    for market_id, stance_json, payout in rows:
        try:
            st = json.loads(stance_json)
        except ValueError:
            continue
        if st.get("stance") not in ("oui", "non"):
            continue
        conf = max(0.0, min(1.0, float(st.get("confidence") or 0)))
        ok = (st["stance"] == "oui") == (payout == 1)
        n += 1
        right += ok
        weight += conf
        weighted_right += conf * ok
        markets.add(market_id)
    return {"avis": n, "justes": right, "marches": len(markets),
            "justesse": round(right / n, 3) if n else None,
            "justesse_ponderee": round(weighted_right / weight, 3) if weight else None}


def status_text(s: dict) -> str:
    if not s["avis"]:
        return "en attente (aucun marché classé n'est encore résolu)"
    return (f"ok ({s['avis']} avis jugés sur {s['marches']} marchés résolus : {s['justesse'] * 100:.0f} % justes, "
            f"{(s['justesse_ponderee'] or 0) * 100:.0f} % pondéré par la confiance)")
