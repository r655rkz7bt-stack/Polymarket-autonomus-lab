"""Météo : biais et flou PAR STATION, appris sur les jours précédents (16/10/2026).

Chaque station d'aéroport a son propre écart avec les modèles (relief, mer, capteur). On le
mesure sans source supplémentaire : la tranche gagnante d'un marché résolu donne la vraie
température du jour à un degré près. Pour chaque station et chaque type (maximum, minimum) :
  erreur du jour = valeur réelle − moyenne des prévisions faites AVANT ce jour ;
  biais = moyenne des erreurs des 7 derniers jours, tirée vers le biais global (`shrink` jours
  fictifs au biais global) ; flou = leur écart-type, tiré vers le flou global, jamais < plancher.
Test sur le passé (experiments/meteo_backtest.md, 8-15/10) : Brier 0,092 au lieu de 0,097 (réglage
global), marché 0,113 ; NON sur la tranche favorite : +26 à +29 % des mises au lieu de +24 %.
"""

from __future__ import annotations

import json
import re
import statistics
from datetime import datetime, timedelta, timezone

from polymarket_agent import weather_model as wm

SCHEMA = """
CREATE TABLE IF NOT EXISTS meteo_previsions (
    station TEXT, jour TEXT, type TEXT, moyenne REAL, collecte TEXT,
    PRIMARY KEY (station, jour, type)
);
CREATE TABLE IF NOT EXISTS meteo_reel (
    station TEXT, jour TEXT, type TEXT, valeur REAL, marche TEXT,
    PRIMARY KEY (station, jour, type)
);
"""
GAMMA_EVENTS = "https://gamma-api.polymarket.com/events"
PREVIOUS_RUNS = "https://previous-runs-api.open-meteo.com/v1/forecast"
WEATHER_TAG = 84
_SITE = re.compile(r"site=([a-z0-9]{3,5})", re.I)


def record_forecasts(db, observations, now: datetime) -> int:
    """Garde, par station / jour / type, la DERNIÈRE prévision faite avant le début du jour local."""
    db.conn.executescript(SCHEMA)
    n = 0
    for o in observations:
        if o.source != "meteo_prevision":
            continue
        offset = timedelta(seconds=int(o.data.get("utc_offset") or 0))
        for day, values in (o.data.get("jours") or {}).items():
            start = datetime.fromisoformat(day).replace(tzinfo=timezone.utc) - offset
            if now >= start:
                continue  # le jour a commencé : ce n'est plus une prévision « de la veille »
            for kind in ("max", "min"):
                members = values.get(kind) or []
                if members:
                    db.conn.execute("INSERT OR REPLACE INTO meteo_previsions VALUES (?,?,?,?,?)",
                                    (o.data["station"], day, kind, sum(members) / len(members),
                                     now.astimezone(timezone.utc).isoformat(timespec="seconds")))
                    n += 1
    db.conn.commit()
    return n


def backfill_forecasts(db, http, coords: dict[str, tuple[float, float]], now: datetime, days: int = 10,
                       per_request: int = 10) -> int:
    """Une seule fois par station : prévisions « de la veille » des `days` derniers jours, d'après
    l'archive des prévisions d'Open-Meteo (mêmes données que le test sur le passé), pour que
    l'étalonnage serve tout de suite au lieu d'attendre plusieurs jours de collecte.
      GET https://previous-runs-api.open-meteo.com/v1/forecast?latitude=..&longitude=..
          &hourly=temperature_2m_previous_day1&models=gfs_seamless,ecmwf_ifs025&timezone=auto
          &start_date=AAAA-MM-JJ&end_date=AAAA-MM-JJ
    Les prévisions collectées en direct ne sont jamais remplacées."""
    from polymarket_agent.sources.weather import MODELS, ForecastSource
    db.conn.executescript(SCHEMA)
    todo = sorted(c for c in coords if not db.get_value(f"meteo_rattrapage:{c}"))
    today = now.astimezone(timezone.utc).date()
    n = 0
    for i in range(0, len(todo), per_request):
        chunk = todo[i:i + per_request]
        raw = http.get_json(PREVIOUS_RUNS, params={
            "latitude": ",".join(str(coords[c][0]) for c in chunk),
            "longitude": ",".join(str(coords[c][1]) for c in chunk),
            "hourly": "temperature_2m_previous_day1", "models": ",".join(MODELS), "timezone": "auto",
            "start_date": (today - timedelta(days=days)).isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat()})
        raw = raw if isinstance(raw, list) else [raw]
        for code, item in zip(chunk, raw):
            h = item.get("hourly") or {} if isinstance(item, dict) else {}
            hourly = {"time": h.get("time") or []}
            hourly.update({f"temperature_2m_{m}": h.get(f"temperature_2m_previous_day1_{m}") or [] for m in MODELS})
            for day, values in ForecastSource.daily(hourly).items():
                if day >= today.isoformat():
                    continue
                for kind in ("max", "min"):
                    cur = db.conn.execute("INSERT OR IGNORE INTO meteo_previsions VALUES (?,?,?,?,?)",
                                          (code, day, kind, sum(values[kind]) / len(values[kind]), "archive"))
                    n += cur.rowcount
            db.set_value(f"meteo_rattrapage:{code}", today.isoformat())
    db.conn.commit()
    return n


def truth_from_event(event: dict) -> tuple[str, str, str, float] | None:
    """(station, jour, type, valeur réelle en °C) d'après la tranche gagnante d'un événement clos."""
    for m in event.get("markets") or []:
        try:
            prices = json.loads(m.get("outcomePrices") or "[]")
        except ValueError:
            continue
        if not prices or str(prices[0]) != "1":
            continue
        q = wm.parse_question(m.get("question", ""))
        site = _SITE.search(m.get("resolutionSource") or "") or _SITE.search(m.get("description") or "")
        end = m.get("endDate") or event.get("endDate") or ""
        if q is None or site is None or len(end) < 4:
            return None
        lo, hi = q.low, q.high
        v = (lo + hi) / 2 if lo != -wm.INF and hi != wm.INF else (lo + 0.5 if hi == wm.INF else hi - 0.5)
        v = (v - 32) / 1.8 if q.unit == "F" else v
        return site.group(1).upper(), f"{end[:4]}-{q.month:02d}-{q.day:02d}", q.kind, v
    return None


def update_truth(db, http, now: datetime, days: int = 10, max_pages: int = 15) -> int:
    """Valeurs réelles des derniers jours (événements météo clos de Gamma)."""
    db.conn.executescript(SCHEMA)
    start = (now - timedelta(days=days)).strftime("%Y-%m-%dT00:00:00Z")
    n = 0
    for page in range(max_pages):
        batch = http.get_json(GAMMA_EVENTS, params={"tag_id": WEATHER_TAG, "closed": "true", "limit": 100,
                                                    "offset": page * 100, "end_date_min": start,
                                                    "end_date_max": now.strftime("%Y-%m-%dT%H:%M:%SZ")})
        if not isinstance(batch, list):
            break
        for ev in batch:
            if "temperature" not in str(ev.get("slug", "")):
                continue
            t = truth_from_event(ev)
            if t:
                db.conn.execute("INSERT OR REPLACE INTO meteo_reel VALUES (?,?,?,?,?)", (*t, str(ev.get("id"))))
                n += 1
        if len(batch) < 100:
            break
    db.conn.commit()
    return n


def errors(db, station: str, kind: str, before: str, window: int = 7) -> list[float]:
    db.conn.executescript(SCHEMA)
    rows = db.conn.execute(
        "SELECT r.valeur - p.moyenne FROM meteo_reel r JOIN meteo_previsions p "
        "ON p.station=r.station AND p.jour=r.jour AND p.type=r.type "
        "WHERE r.station=? AND r.type=? AND r.jour < ? ORDER BY r.jour DESC LIMIT ?",
        (station, kind, before, window)).fetchall()
    return [r[0] for r in rows]


def station_params(errs: list[float], sigma0: float, bias0: float, min_days: int = 3, shrink: float = 3.0,
                   sigma_floor: float = 0.8) -> tuple[float, float, int]:
    """(flou, biais, jours utilisés) : sans assez d'historique, le réglage global."""
    n = len(errs)
    if n < min_days:
        return sigma0, bias0, n
    bias = (sum(errs) + shrink * bias0) / (n + shrink)
    sd = statistics.pstdev(errs) if n > 1 else sigma0
    sigma = max(sigma_floor, ((n * sd * sd + shrink * sigma0 * sigma0) / (n + shrink)) ** 0.5)
    return round(sigma, 3), round(bias, 3), n


def calibration(db, station: str, today: str, globals_: dict[str, tuple[float, float]], **kw) -> dict:
    """{"max": [flou, biais, jours], "min": [...]} pour une station (jours < aujourd'hui)."""
    return {kind: list(station_params(errors(db, station, kind, today), *globals_[kind], **kw))
            for kind in ("max", "min")}
