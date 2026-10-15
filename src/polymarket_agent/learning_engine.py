"""Learning Engine (cahier des charges §4.I) : tirer les leçons des opérations clôturées.

Pour chaque opération clôturée (gagnante ou perdante, toutes conservées) :
  prévision initiale vs issue (erreur de Brier), avantage estimé vs résultat réel, prix
  d'entrée, frais, durée de détention, catégorie, stratégie.
Pour chaque stratégie : profit net, rendement sur mises, espérance par opération, taux de
réussite, Sharpe par opération, Brier, log loss, calibration par tranche, résultats par
catégorie et par durée, intervalle de confiance par événement, probabilité que le résultat
soit dû au hasard, et un VERDICT honnête :
  - « données insuffisantes » (< 20 opérations) ;
  - « ne fonctionne pas » (borne haute de l'IC 90 % < 0) ;
  - « prometteuse » (borne basse > 0) ;
  - « indéterminée » (le résultat peut être dû au hasard).
Ne juge jamais sur le seul taux de réussite ni sur le profit brut.
"""

from __future__ import annotations

import math
import random
from datetime import datetime

from polymarket_agent.backtest import cluster_mean_ci
from polymarket_agent.ledger import Ledger
from polymarket_agent.reporting import closed_trades, read_entries

MIN_TRADES = 20
HOLD_BUCKETS = ((0, 1, "< 1 h"), (1, 6, "1–6 h"), (6, 24, "6–24 h"), (24, 1e9, "> 24 h"))
CAL_EDGES = (0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 1.0001)


def post_mortem(trade: dict, categories: dict[str, str]) -> dict:
    """Analyse d'une opération clôturée."""
    est = float(trade["est_probability"]) if trade.get("est_probability") else None
    payout = float(trade["payout"]) if trade.get("payout") is not None else None
    cost, pnl = float(trade["cost"]), float(trade["pnl"])
    opened = datetime.fromisoformat(trade["opened_at"])
    closed = datetime.fromisoformat(trade["closed_at"])
    hours = (closed - opened).total_seconds() / 3600
    shares = float(trade["shares_bought"]) if trade.get("shares_bought") else None
    entry = (cost - float(trade["fees"])) / shares if shares else None
    lessons = []
    if est is not None and payout is not None:
        if payout == 0 and est >= 0.8:
            lessons.append("surconfiance : probabilité >= 0,8 et perte")
        if payout == 1 and est <= 0.3:
            lessons.append("sous-estimation : probabilité <= 0,3 et gain")
    if float(trade["fees"]) > 0.5 * abs(pnl) and pnl != 0:
        lessons.append("frais supérieurs à la moitié du résultat")
    return {
        "strategie": trade["strategy"], "marche": trade["market_id"], "evenement": trade["event_id"],
        "categorie": categories.get(trade["market_id"], "inconnue"), "issue": trade["outcome"],
        "probabilite_estimee": est, "paiement": payout,
        "brier": (est - payout) ** 2 if est is not None and payout is not None else None,
        "prix_entree_moyen": round(entry, 4) if entry else None, "frais": float(trade["fees"]),
        "cout": cost, "resultat": pnl, "rendement": pnl / cost if cost else 0.0,
        "duree_h": round(hours, 2), "resolution": trade.get("resolution", ""), "lecons": lessons,
    }


def _prob_luck(values_by_event: dict[str, list[float]], n_boot: int = 2000, seed: int = 3) -> float | None:
    """Probabilité (bootstrap par événement) que le vrai rendement moyen soit <= 0."""
    clusters = [v for v in values_by_event.values() if v]
    if len(clusters) < 2:
        return None
    rng = random.Random(seed)
    sums = [(sum(v), len(v)) for v in clusters]
    below = 0
    for _ in range(n_boot):
        s = c = 0.0
        for _ in range(len(sums)):
            a, b = sums[rng.randrange(len(sums))]
            s, c = s + a, c + b
        below += s / c <= 0
    return below / n_boot


def strategy_report(rows: list[dict]) -> dict:
    n = len(rows)
    pnl = sum(r["resultat"] for r in rows)
    cost = sum(r["cout"] for r in rows)
    rets = [r["rendement"] for r in rows]
    mean_r = sum(rets) / n
    sd = math.sqrt(sum((x - mean_r) ** 2 for x in rets) / (n - 1)) if n > 1 else 0.0
    by_event: dict[str, list[float]] = {}
    for r in rows:
        by_event.setdefault(r["evenement"], []).append(r["rendement"])
    _, lo, hi, n_events = cluster_mean_ci(by_event)
    scored = [r for r in rows if r["brier"] is not None]
    brier = sum(r["brier"] for r in scored) / len(scored) if scored else None
    log_loss = (-sum(math.log(max(r["probabilite_estimee"], 1e-6)) if r["paiement"] >= 0.5
                     else math.log(max(1 - r["probabilite_estimee"], 1e-6)) for r in scored) / len(scored)
                if scored else None)
    calibration = []
    for a, b in zip(CAL_EDGES, CAL_EDGES[1:]):
        bucket = [r for r in scored if a <= r["probabilite_estimee"] < b]
        if bucket:
            calibration.append({"tranche": f"{a:.2f}–{min(b, 1):.2f}", "n": len(bucket),
                                "prevu": round(sum(r["probabilite_estimee"] for r in bucket) / len(bucket), 3),
                                "observe": round(sum(r["paiement"] for r in bucket) / len(bucket), 3)})

    def group(key):
        out = {}
        for r in rows:
            g = out.setdefault(key(r), {"n": 0, "resultat": 0.0})
            g["n"] += 1
            g["resultat"] = round(g["resultat"] + r["resultat"], 2)
        return out

    luck = _prob_luck(by_event)
    if n < MIN_TRADES:
        verdict = "données insuffisantes"
    elif hi < 0:
        verdict = "ne fonctionne pas"
    elif lo > 0:
        verdict = "prometteuse"
    else:
        verdict = "indéterminée (le résultat peut être dû au hasard)"
    return {
        "operations": n, "evenements": n_events, "profit_net": round(pnl, 2),
        "rendement_sur_mises": round(pnl / cost, 4) if cost else None,
        "esperance_par_operation": round(pnl / n, 2),
        "taux_reussite": round(sum(1 for r in rows if r["resultat"] > 0) / n, 3),
        "sharpe_par_operation": round(mean_r / sd, 3) if sd > 0 else None,
        "ic90_rendement": [round(lo, 4), round(hi, 4)] if n > 1 else None,
        "probabilite_hasard": round(luck, 3) if luck is not None else None,
        "brier": round(brier, 4) if brier is not None else None,
        "log_loss": round(log_loss, 4) if log_loss is not None else None,
        "frais": round(sum(r["frais"] for r in rows), 2),
        "calibration": calibration,
        "par_categorie": group(lambda r: r["categorie"]),
        "par_duree": group(lambda r: next(lbl for a, b, lbl in HOLD_BUCKETS if a <= r["duree_h"] < b)),
        "lecons_frequentes": _top_lessons(rows),
        "verdict": verdict,
    }


def _top_lessons(rows: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in rows:
        for lesson in r["lecons"]:
            counts[lesson] = counts.get(lesson, 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1])[:5])


def analyze(ledgers: dict[str, Ledger], categories: dict[str, str] | None = None) -> dict:
    """{nom du portefeuille: {stratégie: rapport}} + toutes les analyses par opération."""
    categories = categories or {}
    out = {}
    for name, ledger in ledgers.items():
        trades = closed_trades(read_entries(ledger))
        rows = [post_mortem(t, categories) for t in trades]
        per_strategy: dict[str, list[dict]] = {}
        for r in rows:
            per_strategy.setdefault(r["strategie"], []).append(r)
        out[name] = {"strategies": {s: strategy_report(rs) for s, rs in per_strategy.items()},
                     "operations": rows}
    return out


def categories_from_db(db) -> dict[str, str]:
    """Catégorie de chaque marché d'après son barème de frais (même règle que l'historique)."""
    rows = db.conn.execute("SELECT market_id, fee_type FROM market_snapshots GROUP BY market_id").fetchall()
    return {r[0]: (r[1].split("_")[0] if r[1] else "other") for r in rows}
