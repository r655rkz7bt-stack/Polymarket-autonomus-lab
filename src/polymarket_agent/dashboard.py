"""Tableau de bord (cahier des charges §4.K) : une page HTML statique, autonome, sans dépendance.

Publié sur GitHub Pages par le cycle (étape 9) et régénéré toutes les 30 minutes.
Toutes les données viennent des journaux vérifiés et de la base SQLite.

Sécurité : les textes venus de l'extérieur (questions de marchés, raisons, noms de sources)
sont insérés dans la page avec `textContent`, jamais comme du HTML. Le JSON embarqué
échappe `</` pour qu'aucun texte ne puisse fermer la balise <script>.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

from polymarket_agent.arena import days_since_record, ranking, standing
from polymarket_agent.config import resolve
from polymarket_agent.learning_engine import analyze, categories_from_db
from polymarket_agent.ledger import Ledger
from polymarket_agent.reporting import closed_trades, equity_curve, max_drawdown, read_entries

MAX_POINTS = 300


def _downsample(curve: list[tuple[str, Decimal]], n: int = MAX_POINTS) -> list[list]:
    if len(curve) > n:
        step = len(curve) / n
        curve = [curve[int(i * step)] for i in range(n - 1)] + [curve[-1]]
    return [[ts, float(v)] for ts, v in curve]


def _marks(db, tokens) -> dict[str, Decimal]:
    marks = {}
    for token in tokens:
        row = db.conn.execute("SELECT best_bid FROM book_snapshots WHERE token_id=? "
                              "ORDER BY collected_at DESC LIMIT 1", (token,)).fetchone()
        if row and row[0] is not None:
            marks[token] = Decimal(row[0])
    return marks


def collect(main: Ledger, shadows: dict[str, Ledger], db, settings: dict, root: Path,
            now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    state = main.state
    questions = {r[0]: r[1] for r in db.conn.execute(
        "SELECT market_id, question FROM market_snapshots GROUP BY market_id")}
    learning = analyze(dict(shadows, principal=main), categories_from_db(db))
    marks = _marks(db, state.positions)

    # --- capital principal et cliquet
    curve = equity_curve(read_entries(main))
    capital = {k: str(v) for k, v in state.summary(marks).items()}
    capital.update({"capital_realise": str(state.realized_capital().quantize(Decimal("0.01"))),
                    "palier_suivant": str(state.next_target), "champion": state.champion or "",
                    "drawdown_max": round(max_drawdown(curve), 4),
                    "jours_depuis_palier": round(days_since_record(main, now), 2),
                    "faillite": state.bankrupt, "raison_faillite": state.bankrupt_reason})

    # --- arène
    arena = []
    for s in ranking([standing(n, l, state.eliminated) for n, l in shadows.items()]):
        verdicts = learning.get(s.name, {}).get("strategies", {})
        verdict = next(iter(verdicts.values()), {}).get("verdict", "aucune opération clôturée")
        arena.append({"nom": s.name, "operations": s.closed_trades, "capital": round(s.realized_capital, 2),
                      "croissance": round(s.log_growth, 4) if s.log_growth != float("-inf") else None,
                      "jours": round(s.days(now), 1), "eliminee": s.eliminated,
                      "champion": s.name == state.champion, "verdict": verdict,
                      "courbe": _downsample(equity_curve(read_entries(shadows[s.name])), 60),
                      "positions": len(shadows[s.name].state.positions)})

    # --- positions ouvertes (tous portefeuilles), avec prévision et incertitude
    buys = {}
    for name, ledger in dict(shadows, principal=main).items():
        for e in read_entries(ledger):
            if e["type"] == "BUY":
                buys[(name, e["data"]["token_id"])] = e["data"].get("extra") or {}
    positions = []
    for name, ledger in dict(shadows, principal=main).items():
        pm = _marks(db, ledger.state.positions)
        for token, pos in ledger.state.positions.items():
            extra = buys.get((name, token), {})
            mark = pm.get(token)
            positions.append({
                "portefeuille": name, "marche": questions.get(pos.market_id, pos.market_id),
                "issue": pos.outcome, "parts": float(pos.shares), "cout": round(float(pos.cost_basis), 2),
                "prix_moyen": round(float(pos.avg_cost), 4), "marque": float(mark) if mark is not None else None,
                "latent": round(float(pos.shares * mark - pos.cost_basis), 2) if mark is not None else None,
                "proba": extra.get("est_probability"), "proba_bas": extra.get("prob_low"),
                "proba_haut": extra.get("prob_high"), "strategie": pos.strategy_id,
                "ouverte": pos.opened_at[:16]})

    # --- opérations clôturées récentes
    closed = []
    for name, ledger in dict(shadows, principal=main).items():
        for t in closed_trades(read_entries(ledger)):
            closed.append({"portefeuille": name, "marche": questions.get(t["market_id"], t["market_id"]),
                           "issue": t["outcome"], "strategie": t["strategy"],
                           "resultat": round(float(t["pnl"]), 2), "resolution": t.get("resolution", ""),
                           "date": t["closed_at"][:16]})
    closed.sort(key=lambda t: t["date"], reverse=True)

    # --- décisions récentes, marchés surveillés, cycles, sources
    decisions = [{"date": r[0][:16], "strategie": r[1], "marche": questions.get(r[2], r[2]), "sens": r[3],
                  "acceptee": bool(r[4]), "raisons": json.loads(r[5] or "[]"), "execution": r[6] or ""}
                 for r in db.conn.execute("SELECT decided_at, strategy_id, market_id, side, accepted, reasons, "
                                          "fill_status FROM decisions ORDER BY decided_at DESC LIMIT 25")]
    last_cycle = db.conn.execute("SELECT cycle_id FROM market_snapshots ORDER BY collected_at DESC LIMIT 1").fetchone()
    watched = []
    if last_cycle:
        for r in db.conn.execute("SELECT question, best_bid, best_ask, end_date, fee_type FROM market_snapshots "
                                 "WHERE cycle_id=? AND eligible=1 ORDER BY CAST(volume_24h AS REAL) DESC LIMIT 15",
                                 (last_cycle[0],)):
            watched.append({"marche": r[0], "bid": r[1], "ask": r[2], "echeance": (r[3] or "")[:16],
                            "categorie": (r[4] or "other").split("_")[0]})
    since = (now - timedelta(hours=24)).isoformat()
    cycles = dict(db.conn.execute("SELECT status, COUNT(*) FROM cycles WHERE started_at >= ? GROUP BY status",
                                  (since,)).fetchall())
    last = db.conn.execute("SELECT started_at, status FROM cycles WHERE finished_at IS NOT NULL "
                           "ORDER BY started_at DESC LIMIT 1").fetchone()
    # État de chaque source : le plus récent résultat réel (« pas encore (fréquence) » ne dit rien).
    source_state: dict[str, str] = {}
    for (summary,) in db.conn.execute("SELECT summary FROM cycles WHERE finished_at IS NOT NULL "
                                      "ORDER BY started_at DESC LIMIT 24"):
        for name, status in (json.loads(summary or "{}").get("sources") or {}).items():
            if name not in source_state or source_state[name].startswith("pas encore"):
                source_state[name] = status
    source_runs = dict(db.conn.execute("SELECT source, last_run FROM source_runs").fetchall())
    errors = [{"date": r[0][:16], "erreur": r[1]} for r in db.conn.execute(
        "SELECT started_at, error FROM cycles WHERE error IS NOT NULL AND started_at >= ? "
        "ORDER BY started_at DESC LIMIT 8", (since,))]
    obs_by_source = dict(db.conn.execute("SELECT source, COUNT(*) FROM observations WHERE collected_at >= ? "
                                         "GROUP BY source", (since,)).fetchall())
    # Pouls : les derniers cycles, du plus ancien au plus récent (durée en secondes, exécutions).
    pulse = []
    for started, finished, status, fills, error in reversed(db.conn.execute(
            "SELECT started_at, finished_at, status, fills, error FROM cycles WHERE finished_at IS NOT NULL "
            "ORDER BY started_at DESC LIMIT 96").fetchall()):
        try:
            seconds = round((datetime.fromisoformat(finished) - datetime.fromisoformat(started)).total_seconds(), 1)
        except (TypeError, ValueError):
            seconds = None
        pulse.append({"date": started[:16], "statut": status, "duree": seconds, "executions": fills or 0,
                      "erreur": bool(error)})
    counts = db.conn.execute("SELECT markets_scanned, watchlist_size, proposals, accepted, fills FROM cycles "
                             "WHERE finished_at IS NOT NULL ORDER BY started_at DESC LIMIT 1").fetchone()
    try:
        open_orders = db.conn.execute("SELECT COUNT(*) FROM pending_orders WHERE status='OUVERT'").fetchone()[0]
    except Exception:  # noqa: BLE001 - base d'avant les ordres posés
        open_orders = 0
    system = {"marches_scannes": counts[0] if counts else 0, "surveilles": counts[1] if counts else 0,
              "propositions": counts[2] if counts else 0, "acceptees": counts[3] if counts else 0,
              "executions": counts[4] if counts else 0, "ordres_poses": open_orders,
              "strategies_actives": sum(1 for s in arena if not s["eliminee"]),
              "positions_tous_portefeuilles": len(positions)}

    def listing(folder: str) -> list[dict]:
        path = root / folder
        files = sorted((p for p in path.glob("*.md") if p.name != "README.md"), key=lambda p: p.name, reverse=True)
        return [{"nom": p.name, "date": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")}
                for p in files[:12]] if path.exists() else []

    tests = None
    tests_file = root / "state" / "tests_status.json"
    if tests_file.exists():
        try:
            tests = json.loads(tests_file.read_text(encoding="utf-8"))
        except ValueError:
            tests = None
    # Audit indépendant des exécutions (écrit par le job protégé « audit » dans la branche data).
    audit = None
    audit_file = root / "_data" / "audit" / "etat.json"
    if audit_file.exists():
        try:
            raw_audit = json.loads(audit_file.read_text(encoding="utf-8"))
            audit = {"verifiees": raw_audit.get("verifiees", 0), "non_verifiables": raw_audit.get("non_verifiables", 0),
                     "anomalies": len(raw_audit.get("anomalies", [])), "derniere": raw_audit.get("derniere_execution"),
                     "dernieres_anomalies": raw_audit.get("anomalies", [])[-5:]}
        except ValueError:
            audit = None
    llm = settings.get("llm", {})
    return {
        "audit": audit,
        "genere_le": now.isoformat(timespec="seconds"),
        "capital": capital,
        "courbe": _downsample(curve),
        "paliers": state.milestones,
        "capital_initial": float(state.initial_capital),
        "arene": arena,
        "positions": positions,
        "cloturees": closed[:20],
        "decisions": decisions,
        "surveilles": watched,
        "sante": {"dernier_battement": state.last_heartbeat_at.isoformat(timespec="seconds")
                  if state.last_heartbeat_at else None,
                  "dernier_cycle": {"date": last[0][:16], "statut": last[1]} if last else None,
                  "cycles_24h": cycles, "erreurs": errors, "pouls": pulse},
        "systeme": system,
        "sources": {"etat": source_state, "dernier_passage": {k: v[:16] for k, v in source_runs.items()},
                    "observations_24h": obs_by_source},
        "experiences": listing("experiments"),
        "propositions": listing("proposals"),
        "tests": tests,
        "couts": {"services_payants_eur": 0, "appels_ia_aujourdhui": db.llm_calls(now.date().isoformat()),
                  "plafond_ia": llm.get("max_calls_per_day", 0)},
    }


def to_json(data: dict) -> str:
    """JSON sûr à embarquer dans <script> : aucune séquence « </ » ne peut fermer la balise."""
    return json.dumps(data, ensure_ascii=False, default=str).replace("</", "<\\/")


def render(data: dict, full_document: bool = True) -> str:
    """Page complète (GitHub Pages) ou contenu seul (aperçu Artifact, enveloppé à la publication)."""
    template = (Path(__file__).parent / "dashboard_template.html").read_text(encoding="utf-8")
    body = template.replace("__DATA__", to_json(data))
    if not full_document:
        return body
    return ("<!doctype html>\n<html lang=\"fr\">\n<head>\n<meta charset=\"utf-8\">\n"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
            "</head>\n<body>\n" + body + "\n</body>\n</html>\n")


def write_site(data: dict, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "index.html").write_text(render(data, full_document=True), encoding="utf-8")
    (out_dir / "data.json").write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return out_dir / "index.html"


def open_ledgers(settings: dict, root: Path, key: bytes) -> tuple[Ledger, dict[str, Ledger]]:
    """Journal principal + journaux fantômes, tous vérifiés (signatures et chaîne)."""
    paths = settings["paths"]
    main = Ledger.open(resolve(root, paths["ledger"]), key, resolve(root, paths["bankruptcy_lock"]))
    shadow_dir = resolve(root, paths["shadow_dir"])
    shadows = {p.stem: Ledger.open(p, key, p.with_suffix(".BANKRUPT.lock"))
               for p in sorted(shadow_dir.glob("*.jsonl"))} if shadow_dir.exists() else {}
    return main, shadows


def is_due(out_dir: Path, now: datetime, every_minutes: float) -> bool:
    """Vrai si la page n'existe pas encore ou date de plus de `every_minutes`."""
    data_file = out_dir / "data.json"
    if not data_file.exists():
        return True
    try:
        generated = datetime.fromisoformat(json.loads(data_file.read_text(encoding="utf-8"))["genere_le"])
    except (ValueError, KeyError, TypeError):
        return True
    return (now - generated).total_seconds() >= every_minutes * 60 - 30  # marge : cycles toutes les 5 min


def build(settings: dict, root: Path, key: bytes, db, now: datetime | None = None) -> Path:
    main, shadows = open_ledgers(settings, root, key)
    data = collect(main, shadows, db, settings, root, now)
    return write_site(data, resolve(root, settings["dashboard"]["output_dir"]))
