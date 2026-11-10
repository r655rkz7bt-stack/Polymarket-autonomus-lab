"""Marchés « Will the White House call a full lid by 6:30 PM on <date>? » (10/11/2026, experiments/lid_agenda.md).

Le marché se règle sur l'heure du premier « lid » de fin de journée notée par Roll Call Factbase (rollcall.com/factbase/trump/calendar/,
où il s'écrit « White House Press Office: Travel/Photo lid called » : jamais « full lid » ; 199 règlements sur 210 suivent cette lecture, les
11 autres sont des lids d'après minuit rangés sous la date suivante). Factbase publie tout son calendrier en JSON
(`media-cdn.factba.se/rss/json/trump/calendar-full.json`, lien donné par la page elle-même, sans clé) : l'agenda public du Président
(« President Schedule », publié la veille au soir) et les annonces du service de presse (« Pool Report Schedule »).

Sur 607 jours (mars 2025 - novembre 2026), deux cases de l'agenda tranchent nettement et tiennent sur les deux moitiés de la période :
  - aucun voyage (ni « departs » ni « arrives ») et dernier rendez-vous avant 17 h : lid avant 18 h 30 dans 86 % des jours (204/238 ; 84 % puis 89 %) ;
  - voyage et dernier rendez-vous à 17 h ou plus tard : 14 % (21/149 ; 14 % puis 14 %).
Les deux autres cases changent d'une moitié à l'autre (31 % puis 58 %, 64 % puis 42 %) : on ne dit rien.
Le marché cotait ces deux cases 0,73 et 0,22 douze heures avant l'échéance (prix horaires du CLOB, 56 et 46 jours).
RISQUE de regard vers le futur : le calendrier archivé est l'agenda FINAL ; des rendez-vous ajoutés dans la journée peuvent faire paraître la
case plus nette qu'elle ne l'était la veille. Seule l'arène le dira : la stratégie ne lit que ce que Factbase montre au moment du cycle.
`attach_lid` pose `market.references["lid"] = {"p", "cas", "h", "vu_le"}`. Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")
URL = "https://media-cdn.factba.se/rss/json/trump/calendar-full.json"
MONTHS = {m: i + 1 for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August",
                                           "September", "October", "November", "December"))}
QUESTION = re.compile(r"^Will the White House call a full lid by (?P<h>\d{1,2}):(?P<mn>\d{2}) ?(?P<ampm>AM|PM) on (?P<mois>[A-Za-z]+) (?P<jour>\d{1,2})\??$",
                      re.IGNORECASE)
LID = re.compile(r"travel/photo lid called", re.IGNORECASE)
# Chances mesurées (experiments/lid_agenda.md) ; None = case instable, pas d'avis.
P_CALME = 0.86      # pas de voyage, dernier rendez-vous avant 17 h
P_CHARGE = 0.14     # voyage, dernier rendez-vous à 17 h ou après
P_DEJA_APPELE = 0.97  # lid déjà noté avant l'heure limite (reste : erreur de saisie, règlement par une autre source)


def parse_question(question: str) -> dict | None:
    """{"heure": "HH:MM:00" (24 h), "mois", "jour"} d'une question de lid, ou None."""
    m = QUESTION.match((question or "").strip())
    if not m or m.group("mois").capitalize() not in MONTHS:
        return None
    h = int(m.group("h")) % 12 + (12 if m.group("ampm").upper() == "PM" else 0)
    return {"heure": f"{h:02d}:{int(m.group('mn')):02d}:00", "mois": MONTHS[m.group("mois").capitalize()], "jour": int(m.group("jour"))}


def target_day(parsed: dict, now: datetime) -> date | None:
    for year in (now.year, now.year + 1, now.year - 1):
        try:
            d = date(year, parsed["mois"], parsed["jour"])
        except ValueError:
            return None
        if abs((d - now.date()).days) < 183:
            return d
    return None


def deadline(parsed: dict, day: date) -> datetime:
    hh, mm, _ = (int(x) for x in parsed["heure"].split(":"))
    return datetime(day.year, day.month, day.day, hh, mm, tzinfo=NEW_YORK).astimezone(timezone.utc)


def keep_rows(data, now: datetime, before_days: int = 1, after_days: int = 4) -> list[dict]:
    """Lignes du calendrier des jours proches (heure de l'Est), réduites aux champs utiles."""
    today = now.astimezone(NEW_YORK).date()
    lo, hi = (today - timedelta(days=before_days)).isoformat(), (today + timedelta(days=after_days)).isoformat()
    rows = []
    for r in data if isinstance(data, list) else []:
        if not isinstance(r, dict) or not lo <= str(r.get("date") or "") <= hi:
            continue
        rows.append({"date": str(r["date"]), "time": str(r.get("time") or ""), "type": str(r.get("type") or ""),
                     "details": str(r.get("details") or "")[:300], "location": str(r.get("location") or "")})
    return rows


def fetch_lid(http, now: datetime) -> list[dict]:
    rows = keep_rows(http.get_json(URL), now)
    if not rows:
        raise ValueError("calendrier Factbase vide autour d'aujourd'hui")
    return rows


def first_lid(rows: list[dict], day: str) -> str | None:
    """Heure (HH:MM:SS, Est) du premier lid de fin de journée du jour ; les lids d'avant 6 h appartiennent à la veille, les heures « Local » sont à l'étranger."""
    times = sorted(r["time"] for r in rows if r["date"] == day and LID.search(r["details"]) and r["time"] >= "06:00:00"
                   and "local" not in r["details"].lower() and " for " not in r["details"].lower())
    return times[0] if times else None


def assess(rows: list[dict], day: str, cutoff: str) -> tuple[float | None, str]:
    """(chance d'un lid avant `cutoff`, case) d'après ce que montre le calendrier MAINTENANT."""
    lid = first_lid(rows, day)
    if lid is not None and lid <= cutoff:
        return P_DEJA_APPELE, f"lid déjà noté à {lid[:5]}"
    if lid is not None:
        return 1 - P_DEJA_APPELE, f"premier lid noté à {lid[:5]}, après l'heure limite"
    schedule = [r for r in rows if r["date"] == day and r["type"] == "President Schedule"]
    if not schedule:
        return None, "agenda du jour pas encore publié"
    text = " ".join(r["details"].lower() for r in schedule)
    travel = "departs" in text or "arrives" in text
    last = max((r["time"] for r in schedule if r["time"]), default="00:00:00")
    if not travel and last < "17:00:00":
        return P_CALME, f"sans voyage, dernier rendez-vous {last[:5]}"
    if travel and last >= "17:00:00":
        return P_CHARGE, f"voyage, dernier rendez-vous {last[:5]}"
    return None, f"case instable ({'voyage' if travel else 'sans voyage'}, dernier rendez-vous {last[:5]})"


HISTORY_KEY = "lid:histo"
HISTORY_DAYS = 60


def record_history(db, rows: list[dict], now: datetime) -> None:
    """Journal `lid:histo` : pour chaque jour, la PREMIÈRE case d'agenda vue (et quand) et la dernière, gardé 60 jours (sauvegardé avec la base).
    Sert à mesurer le regard vers le futur du test (experiments/lid_agenda.md) : la case vue la veille au soir est-elle celle de l'agenda final ?"""
    import json
    try:
        histo = json.loads(db.get_value(HISTORY_KEY) or "{}")
    except (ValueError, TypeError):
        histo = {}
    t = now.isoformat(timespec="minutes")
    for day in sorted({r["date"] for r in rows}):
        p, case = assess(rows, day, "18:30:00")
        if case == "agenda du jour pas encore publié":
            continue
        entry = histo.setdefault(day, {"premiere": case, "p_premiere": p, "vu_le": t})
        entry.update({"derniere": case, "p_derniere": p, "maj": t})
    horizon = (now.date() - timedelta(days=HISTORY_DAYS)).isoformat()
    db.set_value(HISTORY_KEY, json.dumps({d: v for d, v in histo.items() if d >= horizon}, ensure_ascii=False))


def attach_lid(markets, db, now: datetime) -> int:
    """Rattache la chance d'un lid avant l'heure limite aux marchés de lid (références `ref:lid`)."""
    if db is None:
        return 0
    from polymarket_agent.references import _load
    seen, rows = _load(db, "ref:lid")
    if seen is None or not rows:
        return 0
    record_history(db, rows, now)
    n = 0
    for m in markets:
        parsed = parse_question(m.question)
        if parsed is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        day = target_day(parsed, now)
        if day is None:
            continue
        end = deadline(parsed, day)
        p, case = assess(rows, day.isoformat(), parsed["heure"])
        m.references = dict(m.references or {}, lid={"p": p, "cas": case, "h": round((end - now).total_seconds() / 3600, 2),
                                                     "vu_le": seen.isoformat()})
        n += 1
    return n
