"""Rapports : capital, positions, opérations clôturées, performances par stratégie.

Tout est recalculé depuis le journal signé (vérifié par Ledger.open avant lecture) et,
pour le contexte (questions, décisions, état des cycles), depuis la base SQLite.
Aucun chiffre du rapport ne sert à décider : c'est un outil de lecture.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from polymarket_agent.backtest import cluster_mean_ci
from polymarket_agent.ledger import Ledger

ZERO = Decimal("0")


def read_entries(ledger: Ledger) -> list[dict]:
    """Lignes du journal. À n'appeler qu'après Ledger.open (journal vérifié)."""
    return [json.loads(line) for line in ledger.path.read_text(encoding="utf-8").splitlines() if line]


def closed_trades(entries: list[dict]) -> list[dict]:
    """Reconstitue les opérations clôturées (règlement ou vente totale), gagnantes ET perdantes."""
    open_: dict[str, dict] = {}
    trades: list[dict] = []
    for entry in entries:
        etype, data = entry["type"], entry["data"]
        if etype == "RESET":
            open_.clear()
        elif etype == "BUY":
            extra = data.get("extra") or {}
            cost = Decimal(data["shares"]) * Decimal(data["price"]) + Decimal(data["fee"])
            pos = open_.setdefault(data["token_id"], {
                "token_id": data["token_id"], "market_id": data["market_id"],
                "event_id": data["event_id"], "outcome": data["outcome"],
                "strategy": f"{data['strategy_id']} v{data['strategy_version']}",
                "opened_at": entry["ts"], "shares": ZERO, "shares_bought": ZERO, "cost": ZERO, "proceeds": ZERO,
                "fees": ZERO, "est_probability": extra.get("est_probability")})
            pos["shares"] += Decimal(data["shares"])
            pos["shares_bought"] += Decimal(data["shares"])
            pos["cost"] += cost
            pos["fees"] += Decimal(data["fee"])
        elif etype in ("SELL", "SETTLE") and data.get("token_id") in open_:
            pos = open_[data["token_id"]]
            if etype == "SELL":
                shares = Decimal(data["shares"])
                pos["proceeds"] += shares * Decimal(data["price"]) - Decimal(data["fee"])
                pos["fees"] += Decimal(data["fee"])
                pos["shares"] -= shares
                pos["resolution"] = "vendu"
                pos["payout"] = None
            else:
                payout = Decimal(data["payout_per_share"])
                pos["proceeds"] += pos["shares"] * payout
                pos["shares"] = ZERO
                pos["resolution"] = data.get("resolution", "")
                pos["payout"] = payout
            if pos["shares"] == 0:
                pos["closed_at"] = entry["ts"]
                pos["pnl"] = pos["proceeds"] - pos["cost"]
                trades.append(open_.pop(data["token_id"]))
    return trades


def equity_curve(entries: list[dict]) -> list[tuple[str, Decimal]]:
    curve = []
    for entry in entries:
        if entry["type"] == "HEARTBEAT":
            # Le solde seul n'est pas le capital (il exclut les positions) : sans total
            # estimé, le battement est ignoré pour la courbe.
            if "total_estimated" in entry["data"]:
                curve.append((entry["ts"], Decimal(entry["data"]["total_estimated"])))
        elif entry["type"] in ("GENESIS", "RESET"):
            curve.append((entry["ts"], Decimal(entry["data"]["initial_capital"])))
    return curve


def max_drawdown(curve: list[tuple[str, Decimal]]) -> float:
    peak, worst = None, 0.0
    for _, value in curve:
        peak = value if peak is None or value > peak else peak
        if peak and peak > 0:
            worst = max(worst, float((peak - value) / peak))
    return worst


def strategy_metrics(trades: list[dict]) -> dict[str, dict]:
    """Mesures par stratégie. Jamais le seul taux de réussite : profit, rendement, Brier, IC."""
    by_strategy: dict[str, list[dict]] = {}
    for trade in trades:
        by_strategy.setdefault(trade["strategy"], []).append(trade)
    out = {}
    for name, rows in sorted(by_strategy.items()):
        n = len(rows)
        settled = [t for t in rows if t.get("payout") is not None and t.get("est_probability")]
        brier = log_loss = None
        if settled:
            pairs = [(float(t["est_probability"]), float(t["payout"])) for t in settled]
            brier = sum((p - y) ** 2 for p, y in pairs) / len(pairs)
            eps = 1e-6
            log_loss = -sum(y * math.log(max(p, eps)) + (1 - y) * math.log(max(1 - p, eps))
                            for p, y in pairs) / len(pairs)
        clusters: dict[str, list[float]] = {}
        for t in rows:
            clusters.setdefault(t["event_id"], []).append(float(t["pnl"] / t["cost"]) if t["cost"] else 0.0)
        mean, lo, hi, n_events = cluster_mean_ci(clusters)
        pnl = sum((t["pnl"] for t in rows), ZERO)
        cost = sum((t["cost"] for t in rows), ZERO)
        out[name] = {
            "operations": n, "evenements": n_events,
            "gagnantes": sum(1 for t in rows if t["pnl"] > 0),
            "taux_reussite": round(sum(1 for t in rows if t["pnl"] > 0) / n, 3),
            "profit_net": str(pnl.quantize(Decimal("0.01"))),
            "frais": str(sum((t["fees"] for t in rows), ZERO).quantize(Decimal("0.01"))),
            "rendement_sur_mises": round(float(pnl / cost), 4) if cost else None,
            "esperance_par_operation": str((pnl / n).quantize(Decimal("0.01"))),
            "ic90_rendement_par_euro": [round(lo, 4), round(hi, 4)] if n >= 2 else None,
            "brier": round(brier, 4) if brier is not None else None,
            "log_loss": round(log_loss, 4) if log_loss is not None else None,
            "assez_de_donnees": n_events >= 30,
        }
    return out


def build_report(ledger: Ledger, db, marks: dict[str, Decimal] | None = None,
                 now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    entries = read_entries(ledger)
    trades = closed_trades(entries)
    curve = equity_curve(entries)
    state = ledger.state
    questions = {r[0]: r[1] for r in db.conn.execute(
        "SELECT market_id, question FROM market_snapshots GROUP BY market_id")}
    since = (now - timedelta(hours=24)).isoformat()
    cycles = dict(db.conn.execute(
        "SELECT status, COUNT(*) FROM cycles WHERE started_at >= ? GROUP BY status", (since,)).fetchall())
    reasons: dict[str, int] = {}
    accepted = rejected = 0
    for acc, raw in db.conn.execute("SELECT accepted, reasons FROM decisions WHERE decided_at >= ?", (since,)):
        if acc:
            accepted += 1
        else:
            rejected += 1
            for reason in json.loads(raw or "[]"):
                key = reason.split(" (")[0].split(" :")[0]
                reasons[key] = reasons.get(key, 0) + 1
    errors = [r[0] for r in db.conn.execute(
        "SELECT error FROM cycles WHERE error IS NOT NULL AND started_at >= ? ORDER BY started_at DESC LIMIT 5",
        (since,))]
    marks = marks or {}
    positions = []
    for token_id, pos in state.positions.items():
        mark = marks.get(token_id)
        positions.append({
            "marche": questions.get(pos.market_id, pos.market_id), "issue": pos.outcome,
            "parts": str(pos.shares), "cout": str(pos.cost_basis.quantize(Decimal("0.01"))),
            "prix_moyen": str(pos.avg_cost.quantize(Decimal("0.0001"))),
            "prix_de_marque": str(mark) if mark is not None else "inconnu",
            "latent": str((pos.shares * mark - pos.cost_basis).quantize(Decimal("0.01"))) if mark is not None else "?",
            "strategie": f"{pos.strategy_id} v{pos.strategy_version}", "groupe": pos.group,
            "ouverte_le": pos.opened_at[:16]})
    return {
        "genere_le": now.isoformat(timespec="seconds"),
        "capital": state.summary(marks),
        "faillite": {"etat": state.bankrupt, "raison": state.bankrupt_reason},
        "drawdown_max": round(max_drawdown(curve), 4),
        "dernier_battement": state.last_heartbeat_at.isoformat(timespec="seconds") if state.last_heartbeat_at else None,
        "positions_ouvertes": positions,
        "operations_cloturees": len(trades),
        "dernieres_operations": [{
            "marche": questions.get(t["market_id"], t["market_id"]), "issue": t["outcome"],
            "strategie": t["strategy"], "resultat": str(t["pnl"].quantize(Decimal("0.01"))),
            "resolution": t.get("resolution", ""), "cloturee_le": t["closed_at"][:16]}
            for t in trades[-15:]],
        "performances": strategy_metrics(trades),
        "cycles_24h": cycles,
        "decisions_24h": {"acceptees": accepted, "rejetees": rejected,
                          "raisons_de_rejet": dict(sorted(reasons.items(), key=lambda kv: -kv[1])[:8])},
        "erreurs_recentes": errors,
    }


def render_markdown(report: dict) -> str:
    cap = report["capital"]
    lines = [f"# Rapport — {report['genere_le']}", "",
             "Unités virtuelles de simulation, jamais de l'argent réel.", ""]
    if report["faillite"]["etat"]:
        lines += [f"**FAILLITE : {report['faillite']['raison']}** — aucun trading.", ""]
    lines += ["## Capital", "", "| poste | valeur |", "|---|---|"]
    labels = {"solde_disponible": "Solde disponible", "capital_immobilise": "Capital immobilisé",
              "gains_realises_nets": "Gains et pertes réalisés (nets)", "gains_latents": "Gains et pertes latents",
              "frais_payes": "Frais payés", "capital_total_estime": "Capital total estimé",
              "positions_ouvertes": "Positions ouvertes"}
    lines += [f"| {labels[k]} | {cap[k]} |" for k in labels]
    lines += [f"| Perte maximale depuis un sommet | {report['drawdown_max']:.2%} |",
              f"| Dernier battement de cœur | {report['dernier_battement']} |", ""]
    lines += ["## Positions ouvertes", ""]
    if report["positions_ouvertes"]:
        lines += ["| marché | issue | parts | coût | prix moyen | marque | latent | stratégie | groupe |",
                  "|---|---|---|---|---|---|---|---|---|"]
        lines += [f"| {p['marche'][:60]} | {p['issue']} | {p['parts']} | {p['cout']} | {p['prix_moyen']} | "
                  f"{p['prix_de_marque']} | {p['latent']} | {p['strategie']} | {p['groupe']} |"
                  for p in report["positions_ouvertes"]]
    else:
        lines.append("Aucune.")
    lines += ["", f"## Performances par stratégie ({report['operations_cloturees']} opérations clôturées)", ""]
    if report["performances"]:
        lines += ["| stratégie | opérations | réussite | profit net | rendement / mises | espérance / op. | IC 90 % | Brier | assez de données ? |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for name, m in report["performances"].items():
            lines.append(f"| {name} | {m['operations']} | {m['taux_reussite']:.1%} | {m['profit_net']} | "
                         f"{m['rendement_sur_mises']} | {m['esperance_par_operation']} | {m['ic90_rendement_par_euro']} | "
                         f"{m['brier']} | {'oui' if m['assez_de_donnees'] else 'non (< 30 événements)'} |")
    else:
        lines.append("Aucune opération clôturée pour l'instant.")
    if report["dernieres_operations"]:
        lines += ["", "### Dernières opérations clôturées", "", "| marché | issue | stratégie | résultat | résolution | date |",
                  "|---|---|---|---|---|---|"]
        lines += [f"| {t['marche'][:60]} | {t['issue']} | {t['strategie']} | {t['resultat']} | {t['resolution']} | {t['cloturee_le']} |"
                  for t in report["dernieres_operations"]]
    d = report["decisions_24h"]
    lines += ["", "## Dernières 24 h", "", f"- Cycles : {report['cycles_24h'] or 'aucun'}",
              f"- Propositions acceptées : {d['acceptees']}, rejetées : {d['rejetees']}"]
    if d["raisons_de_rejet"]:
        lines.append("- Principales raisons de rejet : " + ", ".join(f"{k} ({v})" for k, v in d["raisons_de_rejet"].items()))
    if report["erreurs_recentes"]:
        lines += ["- Erreurs récentes :"] + [f"  - {e}" for e in report["erreurs_recentes"]]
    return "\n".join(lines) + "\n"


def write_report(report: dict, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "latest.md"
    path.write_text(render_markdown(report), encoding="utf-8")
    (directory / "latest.json").write_text(json.dumps(report, ensure_ascii=False, indent=1, default=str),
                                           encoding="utf-8")
    return path
