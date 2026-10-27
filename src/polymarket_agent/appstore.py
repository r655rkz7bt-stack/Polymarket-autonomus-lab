"""App Store (27/10/2026, experiments/appstore_direct.md) : marchés « #1 Free App » et « #1 Paid App in the US Apple App Store on <date> ».

Le marché se règle sur le classement « Top Charts » de l'App Store américain à 12 h (heure de l'Est) du jour visé ; Apple publie ce classement (sources/appstore.py,
relevé toutes les 10 minutes). Entre la veille et midi du jour visé, l'application qui est n°1 AU MOMENT DE LA LECTURE a de bonnes chances de l'être encore à midi :
`rester_n1(h)` donne cette chance selon les heures restantes. Aucune mesure sur le passé (Apple n'archive pas le classement) : les valeurs sont des hypothèses
prudentes, à étalonner sur le journal du classement (`appstore:histo`, un relevé toutes les 30 minutes, gardé 21 jours et sauvegardé avec la base).
`attach_appstore` pose `market.references["appstore"] = {"rang", "n1", "h", "p", "vu_le"}` pour chaque marché dont l'application est dans le top 10 relevé.
Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

NEW_YORK = ZoneInfo("America/New_York")
MONTHS = {m: i + 1 for i, m in enumerate(("January", "February", "March", "April", "May", "June", "July", "August",
                                           "September", "October", "November", "December"))}
QUESTION = re.compile(r"^Will (?P<app>.+?) be #1 (?P<kind>Free|Paid) App in the US Apple App Store on (?P<mois>[A-Za-z]+) (?P<jour>\d{1,2})\?$", re.IGNORECASE)
HISTORY_KEY = "appstore:histo"
HISTORY_DAYS = 21
HISTORY_EVERY_MINUTES = 30


def parse_question(question: str) -> dict | None:
    """{"app", "kind" ('free'|'paid'), "mois", "jour"} d'une question de n°1 du jour, ou None."""
    m = QUESTION.match((question or "").strip())
    if not m or m.group("mois").capitalize() not in MONTHS:
        return None
    return {"app": m.group("app").strip(), "kind": m.group("kind").lower(), "mois": MONTHS[m.group("mois").capitalize()], "jour": int(m.group("jour"))}


def noon_eastern(parsed: dict, now: datetime) -> datetime | None:
    """12 h heure de l'Est du jour visé (l'année est celle de `now`, ou la suivante si la date est passée depuis plus de 6 mois), en UTC."""
    for year in (now.year, now.year + 1, now.year - 1):
        try:
            target = datetime(year, parsed["mois"], parsed["jour"], 12, 0, tzinfo=NEW_YORK).astimezone(timezone.utc)
        except ValueError:
            return None
        if abs((target - now).days) < 183:
            return target
    return None


def rester_n1(hours: float) -> float:
    """Chance que le n°1 du moment le soit encore à midi (heure de l'Est), `hours` heures plus tard. Hypothèses prudentes (aucune mesure) : 0,95 dans l'heure,
    0,90 à 3 h, 0,85 à 6 h ; au-delà de 6 h, on ne dit rien (None) tant que le journal du classement n'a pas servi à l'étalonner."""
    if hours < 0:
        return 0.0
    if hours <= 1:
        return 0.95
    if hours <= 3:
        return 0.90
    if hours <= 6:
        return 0.85
    return 0.0


def record_history(db, rows: list[dict], now: datetime) -> bool:
    """Ajoute le haut du classement (5 premiers, gratuit et payant) au journal `appstore:histo`, au plus toutes les 30 minutes, gardé 21 jours."""
    if db is None or not rows:
        return False
    try:
        histo = json.loads(db.get_value(HISTORY_KEY) or "[]")
    except (ValueError, TypeError):
        histo = []
    t = int(now.timestamp())
    if histo and t - int(histo[-1]["t"]) < HISTORY_EVERY_MINUTES * 60:
        return False
    top = {kind: [r["nom"] for r in rows if r["kind"] == kind and r["rang"] <= 5] for kind in ("free", "paid")}
    histo.append({"t": t, **top})
    horizon = t - HISTORY_DAYS * 86400
    db.set_value(HISTORY_KEY, json.dumps([h for h in histo if int(h["t"]) >= horizon], ensure_ascii=False))
    return True


def attach_appstore(markets, db, now: datetime) -> int:
    """Rattache le rang actuel de l'application aux marchés « #1 Free / Paid App … on <date> » (références `ref:appstore`)."""
    if db is None:
        return 0
    from polymarket_agent.references import _load
    seen, rows = _load(db, "ref:appstore")
    if seen is None or not rows:
        return 0
    record_history(db, rows, now)
    n = 0
    for m in markets:
        parsed = parse_question(m.question)
        if parsed is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        noon = noon_eastern(parsed, now)
        if noon is None:
            continue
        chart = {r["nom"].lower(): r for r in rows if r["kind"] == parsed["kind"]}
        top = next((r for r in rows if r["kind"] == parsed["kind"] and r["rang"] == 1), None)
        mine = chart.get(parsed["app"].lower())
        hours = (noon - now).total_seconds() / 3600
        m.references = dict(m.references or {}, appstore={
            "rang": mine["rang"] if mine else None, "n1": top["nom"] if top else None, "h": round(hours, 2),
            "p": rester_n1(hours) if mine and mine["rang"] == 1 else None, "vu_le": seen.isoformat()})
        n += 1
    return n
