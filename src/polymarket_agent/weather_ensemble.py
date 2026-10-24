"""Météo : probabilité de chaque tranche d'après les prévisions d'ENSEMBLE, relevée en base à côté des prix (23/10/2026).

Probabilité d'une tranche = part des membres (31 GEFS + 51 ECMWF, Open-Meteo) dont le maximum (ou minimum) du jour
LOCAL tombe dans la tranche, dans l'unité du marché (°C ou °F), avec la règle de règlement du marché : arrondi
(« 16°C » = [15,5 ; 16,5[, stations METAR) ou troncature (Hong Kong : « 27°C » = [27,0 ; 28,0[).

Pourquoi un relevé : il n'existe pas d'historique gratuit des membres d'ensemble chez Open-Meteo (3 jours passés
seulement, recollés à partir des derniers passages : experiments/meteo_ensemble.md). Pour juger l'idée sur des
marchés réglés, il faut donc garder NOUS-MÊMES, à chaque passage de la source, la probabilité de chaque tranche ET
le prix du marché au même instant (tables `meteo_ensemble_releves` et `meteo_ensemble_membres`, gardées par la
sauvegarde quotidienne de la base). Évaluation : experiments/meteo_ensemble/evaluer_releve.py (log-score contre le
prix, puis achats aux prix réellement payés). Aucune stratégie ne s'en sert tant que ce test n'est pas fait.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from polymarket_agent import weather_model as wm

SCHEMA = """
CREATE TABLE IF NOT EXISTS meteo_ensemble_releves (
    pris_le TEXT, marche TEXT, evenement TEXT, question TEXT, station TEXT, jour TEXT, type TEXT, regle TEXT,
    avance_h REAL, p_gefs REAL, p_ecmwf REAL, p_ensemble REAL, membres INTEGER,
    meilleur_acheteur REAL, meilleur_vendeur REAL, dernier_prix REAL, jeton_oui TEXT, fin TEXT,
    PRIMARY KEY (pris_le, marche)
);
CREATE TABLE IF NOT EXISTS meteo_ensemble_membres (
    pris_le TEXT, station TEXT, jour TEXT, type TEXT, utc_offset INTEGER, gefs TEXT, ecmwf TEXT,
    PRIMARY KEY (pris_le, station, jour, type)
);
"""


def share(q: wm.TempQuestion, members_c: list[float], truncation: bool = False, shift_c: float = 0.0) -> float | None:
    """Part des membres (°C, décalés de `shift_c`) dans la tranche [bas ; haut[ du marché, dans son unité."""
    if not members_c:
        return None
    b = wm.truncated(q) if truncation else q
    inside = sum(1 for m in members_c if b.low <= wm.to_unit(m + shift_c, q.unit) < b.high)
    return inside / len(members_c)


def market_day(q: wm.TempQuestion, now: datetime) -> str:
    """Date AAAA-MM-JJ du marché (la question ne donne ni l'année ni le fuseau)."""
    year = now.year + (1 if q.month == 1 and now.month == 12 else -1 if q.month == 12 and now.month == 1 else 0)
    return f"{year}-{q.month:02d}-{q.day:02d}"


def probabilities(q: wm.TempQuestion, day: dict, truncation: bool) -> dict | None:
    """{"p_gefs", "p_ecmwf", "p_ensemble", "membres"} pour une tranche, d'après les membres du jour (EnsembleSource.daily)."""
    groups = (day or {}).get(q.kind) or {}
    pool = [x for v in groups.values() for x in v]
    if not pool:
        return None
    return {"p_gefs": share(q, groups.get("gefs") or [], truncation), "p_ecmwf": share(q, groups.get("ecmwf") or [], truncation),
            "p_ensemble": share(q, pool, truncation), "membres": len(pool)}


def _f(x) -> float | None:
    return None if x is None else float(x)


GAMMA_EVENTS = "https://gamma-api.polymarket.com/events"
METAR_URL = "https://aviationweather.gov/api/data/metar"


def open_temperature_markets(http, now: datetime, hours: float = 48, max_pages: int = 6) -> list:
    """TOUS les marchés de température ouverts qui finissent dans `hours` heures (Gamma, étiquette météo 84) : la liste
    surveillée du cycle n'en garde que les plus échangés (150 marchés toutes familles confondues), trop peu pour un test."""
    from polymarket_agent.sources.polymarket_gamma import parse_market
    out = []
    for page in range(max_pages):
        batch = http.get_json(GAMMA_EVENTS, params={
            "tag_id": 84, "closed": "false", "limit": 100, "offset": 100 * page,
            "end_date_min": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date_max": (now + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")})
        if not isinstance(batch, list):
            break
        for ev in batch:
            if "temperature" not in str(ev.get("slug", "")):
                continue
            for raw in ev.get("markets") or []:
                if raw.get("closed"):
                    continue
                raw = dict(raw, events=[{"id": ev.get("id"), "title": ev.get("title", "")}])
                try:
                    out.append(parse_market(raw))
                except (KeyError, ValueError, TypeError):
                    continue
        if len(batch) < 100:
            break
    return out


def locate_stations(http, db, codes: list[str]) -> int:
    """Coordonnées des stations METAR encore inconnues (un appel aviationweather.gov), gardées comme `meteo_metar`."""
    todo = sorted(c for c in codes if not db.get_value(f"station:{c}"))
    found: set[str] = set()
    for i in range(0, len(todo), 40):
        for r in http.get_json(METAR_URL, params={"ids": ",".join(todo[i:i + 40]), "format": "json", "hours": 3}) or []:
            if isinstance(r, dict) and r.get("icaoId") and r.get("lat") is not None and r.get("lon") is not None:
                code = str(r["icaoId"]).upper()
                if code in todo and code not in found:
                    db.set_value(f"station:{code}", json.dumps([r["lat"], r["lon"]]))
                    found.add(code)
    return len(found)


def record(db, markets, observations, now: datetime) -> int:
    """Garde, pour chaque marché de température qui a un ensemble à sa station, la probabilité de la tranche et
    les prix du même instant ; et une fois par station / jour / type, les membres eux-mêmes. Retourne le nombre de
    marchés relevés."""
    from polymarket_agent.sources import hko
    from polymarket_agent.sources.weather import station_for_market
    ens = {o.data["station"]: o.data for o in observations if o.source == "meteo_ensemble" and "station" in o.data}
    if not ens:
        return 0
    db.conn.executescript(SCHEMA)
    stamp = now.astimezone(timezone.utc).isoformat(timespec="seconds")
    n = 0
    stored: set[tuple[str, str, str]] = set()
    for m in markets:
        station = station_for_market(m)
        q = wm.parse_question(getattr(m, "question", ""))
        data = ens.get(station) if station else None
        if q is None or data is None:
            continue
        day_key = market_day(q, now)
        day = (data.get("jours") or {}).get(day_key)
        truncation = station == hko.STATION
        probs = probabilities(q, day, truncation)
        if probs is None:
            continue
        offset = timedelta(seconds=int(data.get("utc_offset") or 0))
        start = datetime.fromisoformat(day_key).replace(tzinfo=timezone.utc) - offset  # minuit local
        tokens = list(getattr(m, "token_ids", []) or [])
        db.conn.execute("INSERT OR REPLACE INTO meteo_ensemble_releves VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
            stamp, m.market_id, m.event_id, m.question, station, day_key, q.kind, "troncature" if truncation else "arrondi",
            round((start - now).total_seconds() / 3600, 2), probs["p_gefs"], probs["p_ecmwf"], probs["p_ensemble"],
            probs["membres"], _f(m.best_bid), _f(m.best_ask), _f(getattr(m, "last_trade_price", None)),
            tokens[0] if tokens else None, m.end_date.isoformat() if getattr(m, "end_date", None) else None))
        n += 1
        if (station, day_key, q.kind) not in stored:
            stored.add((station, day_key, q.kind))
            groups = day[q.kind]
            db.conn.execute("INSERT OR REPLACE INTO meteo_ensemble_membres VALUES (?,?,?,?,?,?,?)", (
                stamp, station, day_key, q.kind, int(data.get("utc_offset") or 0),
                json.dumps(groups.get("gefs") or []), json.dumps(groups.get("ecmwf") or [])))
    db.conn.commit()
    return n
