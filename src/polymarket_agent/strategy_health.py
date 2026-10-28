"""Santé des stratégies : juger plus vite, miser prudemment tant que rien n'est prouvé.

Trois outils (décision d'Etienne du 15/10/2026), tous réglables dans config/settings.yaml
(section `sante_strategies`, libre) :

1. Score de prévision PROVISOIRE. Chaque achat d'un fantôme porte une probabilité estimée.
   - Dérive : sur les positions pas encore résolues, le prix du marché a-t-il bougé dans le sens
     du pari depuis l'achat ? (disponible en quelques heures, indicatif seulement) ;
   - Brier : quand le marché est réglé, écart quadratique entre la probabilité annoncée et le
     résultat (0 = parfait), comparé à celui du prix payé (ce que « pensait » le marché).
     « Avance » = Brier du marché − Brier de la stratégie : positive, la stratégie prévoit mieux
     que le marché. Ce score sert au chercheur et à la mise prudente, jamais à l'attribution du
     capital principal (qui reste fondée sur le capital réalisé, cf. arena.py).
2. Mise prudente : tant qu'une stratégie n'a pas assez de prévisions jugées, ses achats sont
   réduits (½ Kelly par défaut) ; prouvée meilleure que le marché → mise entière ; prouvée moins
   bonne → ¼.
3. Suspension : une stratégie gagnante avant frais mais perdante après (les frais mangent tout
   son avantage), après assez d'opérations clôturées, n'ouvre plus de positions (ses sorties
   continuent), tant que la condition tient.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from polymarket_agent.http_client import SourceUnavailable
from polymarket_agent.settlement import resolution_payout

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS forecast_outcomes (
    token_id TEXT PRIMARY KEY,
    market_id TEXT NOT NULL,
    payout REAL,
    checked_at TEXT NOT NULL
);
"""
DEFAULTS = {"min_resolved": 20, "base": 0.5, "proven": 1.0, "disproven": 0.25,
            "suspension_min_closed": 20, "outcomes_per_hour": 15}


def config(settings: dict) -> dict:
    return dict(DEFAULTS, **(settings.get("sante_strategies") or {}))


def forecasts(entries: list[dict]) -> list[dict]:
    """Achats d'un journal : {token_id, market_id, p, price, ts}. Le premier achat d'un jeton
    compte (un renforcement n'est pas une nouvelle prévision)."""
    out, seen = [], set()
    for e in entries:
        if e.get("type") != "BUY":
            continue
        d = e["data"]
        token = d.get("token_id")
        p = (d.get("extra") or {}).get("est_probability")
        if token in seen or p is None:
            continue
        try:
            out.append({"token_id": token, "market_id": d["market_id"], "p": float(p),
                        "price": float(d["price"]), "ts": e["ts"]})
        except (KeyError, TypeError, ValueError):
            continue
        seen.add(token)
    return out


def settled_outcomes(entries: list[dict]) -> dict[str, float]:
    """Résultat connu par le journal lui-même (21/10/2026) : un jeton réglé (SETTLE) dit déjà ce qu'il a
    payé. Avant, seules 15 prévisions par heure étaient vérifiées auprès de Gamma pour toute l'arène :
    la championne avait 15 prévisions jugées pour 97 paris réglés, aucune stratégie n'atteignait les
    20 qui débloquent la mise entière (experiments/grossir_gagnantes.md)."""
    out: dict[str, float] = {}
    for e in entries:
        if e.get("type") == "RESET":
            out.clear()
        elif e.get("type") == "SETTLE":
            d = e.get("data") or {}
            try:
                out[str(d["token_id"])] = float(d["payout_per_share"])
            except (KeyError, TypeError, ValueError):
                continue
    return out


def update_outcomes(db, get_market, items: list[dict], now: datetime, budget: int = 15,
                    recheck_hours: float = 6) -> int:
    """Résultat des marchés prévus (au plus `budget` interrogations). Retourne les nouveaux réglés."""
    db.conn.executescript(SCHEMA)
    known = {r[0]: (r[1], r[2]) for r in db.conn.execute("SELECT token_id, payout, checked_at FROM forecast_outcomes")}
    since = (now - timedelta(hours=recheck_hours)).astimezone(timezone.utc).isoformat()
    todo, seen = [], set()
    for f in items:
        k = known.get(f["token_id"])
        if f["token_id"] in seen or (k and (k[0] is not None or k[1] >= since)):
            continue
        seen.add(f["token_id"])
        todo.append(f)
    resolved = 0
    for f in todo[: max(0, int(budget))]:
        try:
            raw = get_market(f["market_id"])
        except (SourceUnavailable, ValueError) as exc:
            log.info("prévisions : marché %s illisible (%s)", f["market_id"], exc)
            continue
        result = resolution_payout(raw, f["token_id"]) if isinstance(raw, dict) else None
        payout = float(result[0]) if result else None
        db.conn.execute("INSERT OR REPLACE INTO forecast_outcomes VALUES (?, ?, ?, ?)",
                        (f["token_id"], f["market_id"], payout, now.astimezone(timezone.utc).isoformat()))
        resolved += payout is not None
    db.conn.commit()
    return resolved


def _mid(db, token: str) -> float | None:
    row = db.conn.execute("SELECT best_bid, best_ask FROM book_snapshots WHERE token_id=? "
                          "ORDER BY collected_at DESC LIMIT 1", (token,)).fetchone()
    if not row or row[0] is None or row[1] is None:
        return None
    return (float(row[0]) + float(row[1])) / 2


def score(db, items: list[dict], settled: dict[str, float] | None = None) -> dict:
    """{"jugees", "brier", "brier_marche", "avance", "derive", "positions_derive"}. `settled` : résultats
    lus dans le journal (settled_outcomes), prioritaires sur ceux vérifiés auprès de Gamma."""
    db.conn.executescript(SCHEMA)
    outcomes = {r[0]: r[1] for r in db.conn.execute("SELECT token_id, payout FROM forecast_outcomes")}
    outcomes.update(settled or {})
    b_s = b_m = 0.0
    n = 0
    drift, nd = 0.0, 0
    for f in items:
        payout = outcomes.get(f["token_id"])
        if payout is not None:
            n += 1
            b_s += (f["p"] - payout) ** 2
            b_m += (f["price"] - payout) ** 2
        else:
            mid = _mid(db, f["token_id"])
            if mid is not None:
                drift += mid - f["price"]
                nd += 1
    return {"jugees": n, "brier": round(b_s / n, 4) if n else None,
            "brier_marche": round(b_m / n, 4) if n else None,
            "avance": round((b_m - b_s) / n, 4) if n else None,
            "derive": round(drift / nd, 4) if nd else None, "positions_derive": nd}


def prudence(s: dict, cfg: dict) -> float:
    """Fraction de la mise habituelle (Kelly de la stratégie) autorisée."""
    if s["jugees"] < int(cfg["min_resolved"]) or s["avance"] is None:
        return float(cfg["base"])
    return float(cfg["proven"]) if s["avance"] > 0 else float(cfg["disproven"])


def boost(row: dict | None, cfg: dict) -> float:
    """Renfort (« grossir les gagnantes », décision d'Etienne du 21/10/2026) : une stratégie qui prouve
    PLUS d'avantage qu'elle n'en suppose mise davantage, avec un plafond. Avantage mesuré = Σ(gagné −
    prix payé) / (opérations + `paris_fictifs`), comparé à l'avantage supposé à l'achat (estimation −
    prix payé). Seulement après `min_operations` opérations et avec une confiance par jour d'au moins
    `confiance_jour_min` ; renfort = mesuré / supposé, entre 1 et `max`. `row` : une ligne du
    classement de l'arène (Standing.report). Sans réglage `renfort` : 1 (aucun renfort)."""
    rule = cfg.get("renfort") or {}
    if not rule or not row:
        return 1.0
    n = int(row.get("closed_trades") or 0)
    excess, assumed, conf = row.get("excess_wins"), row.get("assumed_edge"), row.get("day_confidence")
    if n < int(rule.get("min_operations", 30)) or excess is None or not assumed or float(assumed) <= 0:
        return 1.0
    if conf is None or float(conf) < float(rule.get("confiance_jour_min", 0.8)):
        return 1.0
    measured = float(excess) / (n + float(rule.get("paris_fictifs", 30)))
    return round(min(float(rule.get("max", 2.0)), max(1.0, measured / float(assumed))), 4)


def suspension(state, closed: int, cfg: dict) -> str | None:
    """Raison de suspendre (ou None) : ne gagne même pas ses frais après assez d'opérations."""
    if closed < int(cfg["suspension_min_closed"]):
        return None
    net, fees = state.realized_pnl, state.fees_paid
    gross = net + fees
    # Gagnante avant frais, perdante après : les frais mangent tout l'avantage. (Une stratégie
    # qui perd déjà avant frais n'est pas suspendue : l'élimination hebdomadaire s'en charge.)
    if net < 0 and gross >= Decimal("0"):
        return (f"ne gagne pas ses frais : gains bruts {gross:.2f}, frais {fees:.2f} "
                f"sur {closed} opérations clôturées")
    return None


def save(db, name: str, data: dict) -> None:
    db.set_value(f"sante:{name}", json.dumps(data, ensure_ascii=False))


def load(db, name: str) -> dict | None:
    raw = db.get_value(f"sante:{name}")
    try:
        return json.loads(raw) if raw else None
    except ValueError:
        return None
