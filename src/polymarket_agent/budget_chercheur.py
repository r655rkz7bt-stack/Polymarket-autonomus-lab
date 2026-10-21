"""Budget de temps du chercheur (config/chercheur.yaml, décisions d'Etienne du 21/10/2026).

Le chercheur doit utiliser environ 70 % du quota d'Etienne, sans jamais épuiser la limite de la
semaine. Il ne voit pas la jauge de cette limite : on le pilote en minutes de travail. Durée visée
d'un passage = (budget de la semaine − minutes déjà faites depuis la remise à zéro) / passages qui
restent avant la prochaine remise à zéro, bornée entre `duree_min_minutes` et `duree_max_minutes`.
Un passage trop court laisse du temps aux suivants ; un passage trop long en retire.
"""

from __future__ import annotations

import csv
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

PARIS = ZoneInfo("Europe/Paris")
DAYS = {"lundi": 0, "mardi": 1, "mercredi": 2, "jeudi": 3, "vendredi": 4, "samedi": 5, "dimanche": 6}
COLUMNS = ["debut_utc", "fin_utc", "minutes"]
LATE_START = timedelta(minutes=15)  # le passage en cours a démarré au plus 15 min avant le calcul


def week_start(now: datetime, cfg: dict) -> datetime:
    """Dernière remise à zéro de la limite de la semaine (≤ now)."""
    rule = cfg.get("remise_a_zero") or {}
    day, hour = DAYS[str(rule.get("jour", "vendredi"))], int(rule.get("heure_utc", 0))
    base = now.astimezone(timezone.utc).replace(hour=hour, minute=0, second=0, microsecond=0)
    start = base - timedelta(days=(base.weekday() - day) % 7)
    return start - timedelta(days=7) if start > now else start


def remaining_passes(now: datetime, cfg: dict) -> int:
    """Passages programmés d'ici la prochaine remise à zéro, celui qui commence compris."""
    start = week_start(now, cfg)
    end, since = start + timedelta(days=7), max(start, now - LATE_START)  # un passage d'avant la remise à zéro : semaine d'avant
    times = [tuple(int(x) for x in str(t).split(":")) for t in cfg.get("passages_paris") or []]
    first = since.astimezone(PARIS).date()
    n = 0
    for k in range(9):
        d = first + timedelta(days=k)
        for h, m in times:
            t = datetime(d.year, d.month, d.day, h, m, tzinfo=PARIS).astimezone(timezone.utc)
            if since <= t < end:
                n += 1
    return max(1, n)


def read_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        return [r for r in csv.DictReader(handle) if r.get("debut_utc")]


def used_minutes(rows: list[dict], since: datetime) -> float:
    total = 0.0
    for r in rows:
        try:
            if datetime.fromisoformat(r["debut_utc"]) >= since:
                total += float(r["minutes"])
        except (ValueError, TypeError, KeyError):
            continue
    return total


def target(now: datetime, cfg: dict, rows: list[dict]) -> dict:
    """Durée visée du passage qui commence, et l'état de la semaine (pour l'affichage)."""
    start = datetime.fromisoformat(str(cfg["demarrage"]))
    if now < start:
        lo, hi = (int(x) for x in cfg.get("avant_demarrage_minutes") or (45, 90))
        return {"minutes": hi, "min": lo, "avant_demarrage": True,
                "texte": f"Avant le {start:%d/%m %H:%M} UTC : passage de {lo} à {hi} minutes, comme avant."}
    ws = week_start(now, cfg)
    budget = float(cfg["budget_semaine_minutes"])
    if start > ws:  # première semaine entamée : budget au prorata de ce qu'il en reste
        budget *= (ws + timedelta(days=7) - start) / timedelta(days=7)
    used = used_minutes(rows, max(ws, start))
    left, n = budget - used, remaining_passes(now, cfg)
    lo, hi = int(cfg.get("duree_min_minutes", 30)), int(cfg.get("duree_max_minutes", 135))
    minutes = int(round(min(hi, max(lo, left / n))))
    spent = left <= 0
    texte = (f"Semaine depuis le {ws:%d/%m %H:%M} UTC : {used:.0f} min faites sur {budget:.0f} ; "
             f"{n} passage(s) restant(s) avant la remise à zéro. Durée visée de ce passage : {minutes} min "
             f"(fin vers {now + timedelta(minutes=minutes):%H:%M} UTC).")
    if spent:
        texte += " Budget de la semaine ÉPUISÉ : passage court, enquêtes obligatoires seulement."
    return {"minutes": minutes, "min": lo, "avant_demarrage": False, "utilise": round(used, 1),
            "budget": round(budget, 1), "restants": n, "epuise": spent, "texte": texte}


def append_row(path: Path, start: datetime, end: datetime) -> float:
    minutes = round(max(0.0, (end - start).total_seconds() / 60), 1)
    new = not path.exists()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        if new:
            writer.writerow(COLUMNS)
        writer.writerow([start.isoformat(timespec="seconds"), end.isoformat(timespec="seconds"), minutes])
    return minutes
