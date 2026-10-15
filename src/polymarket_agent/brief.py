"""Feuille de mission du chercheur : classement, cliquet, obligations d'innovation.

Lue au début de chaque session de recherche (CLAUDE.md, « Méthode de recherche »).
Règles décidées par Etienne (15/10/2026) :
  - au moins `min_strategies_in_test` idées en test en permanence ;
  - une stratégie éliminée doit être remplacée par une NOUVELLE idée ;
  - aucun nouveau palier depuis `radical_idea_after_days_without_record` jours → la
    prochaine idée doit être radicalement différente (nouvelle source, nouveau type de
    marché, nouveau mécanisme), pas une variante.
"""

from __future__ import annotations

from datetime import datetime, timezone

from polymarket_agent.arena import days_since_record, ranking, standing
from polymarket_agent.ledger import Ledger


def build_brief(main: Ledger, competitors: dict[str, Ledger], active: list[str], cfg: dict,
                now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    state = main.state
    standings = ranking([standing(n, l, state.eliminated) for n, l in competitors.items()])
    realized = state.realized_capital()
    days = days_since_record(main, now)
    in_test = [n for n in active if n not in state.eliminated]
    obligations = []
    missing = int(cfg.get("min_strategies_in_test", 3)) - len(in_test)
    if missing > 0:
        obligations.append(f"Ajouter {missing} nouvelle(s) stratégie(s) : il faut au moins "
                           f"{cfg.get('min_strategies_in_test', 3)} idées en test.")
    replace = [n for n in state.eliminated if n in active]
    if replace:
        obligations.append(f"Remplacer les stratégies éliminées encore configurées : {', '.join(replace)}.")
    if days >= float(cfg.get("radical_idea_after_days_without_record", 7)):
        obligations.append(f"Aucun nouveau palier depuis {days:.1f} jours : la prochaine idée doit être "
                           "RADICALEMENT différente (nouvelle source, nouveau type de marché, "
                           "nouveau mécanisme), pas une variante.")
    return {
        "genere_le": now.isoformat(timespec="seconds"),
        "mission": "Battre le record : atteindre le palier suivant le plus vite possible, sans jamais atteindre 0.",
        "champion": state.champion or "aucun (ne rien faire)",
        "capital_realise": str(realized.quantize(realized.__class__("0.01"))),
        "palier_suivant": str(state.next_target),
        "distance_au_palier": str((state.next_target - realized).quantize(realized.__class__("0.01"))),
        "paliers_atteints": state.milestones,
        "jours_depuis_dernier_palier": round(days, 2),
        "classement": [{"strategie": s.name, "operations_cloturees": s.closed_trades,
                        "capital_realise": round(s.realized_capital, 2),
                        "croissance_log": round(s.log_growth, 4), "jours": round(s.days(now), 1),
                        "eliminee": s.eliminated, "champion": s.name == state.champion}
                       for s in standings],
        "obligations": obligations,
    }


def render_brief(brief: dict) -> str:
    lines = [f"# Feuille de mission — {brief['genere_le']}", "", f"**{brief['mission']}**", "",
             f"- Champion (pilote le capital principal) : **{brief['champion']}**",
             f"- Capital réalisé : {brief['capital_realise']} — palier suivant : **{brief['palier_suivant']}** "
             f"(encore {brief['distance_au_palier']})",
             f"- Jours depuis le dernier palier : {brief['jours_depuis_dernier_palier']}", ""]
    if brief["paliers_atteints"]:
        lines += ["## Paliers atteints", "", "| palier | atteint le | en |", "|---|---|---|"]
        lines += [f"| {m['target']} | {m['reached_at'][:16]} | {m['seconds'] / 3600:.1f} h |"
                  for m in brief["paliers_atteints"]]
        lines.append("")
    lines += ["## Classement de l'arène", "",
              "| # | stratégie | opérations clôturées | capital réalisé | croissance log | jours | statut |",
              "|---|---|---|---|---|---|---|"]
    for i, s in enumerate(brief["classement"], start=1):
        status = "champion" if s["champion"] else ("éliminée" if s["eliminee"] else "en test")
        lines.append(f"| {i} | {s['strategie']} | {s['operations_cloturees']} | {s['capital_realise']} | "
                     f"{s['croissance_log']:+.4f} | {s['jours']} | {status} |")
    lines += ["", "## Obligations de cette session", ""]
    lines += [f"- {o}" for o in brief["obligations"]] or ["- Aucune obligation : améliorer le champion ou tenter une idée neuve."]
    return "\n".join(lines) + "\n"
