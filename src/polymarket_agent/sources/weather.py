"""Source : observations météo officielles des stations d'aéroport (NOAA, METAR), sans clé.

Pourquoi (inventaire du 15/10/2026) : ~200 marchés « température maximale à <ville> le <jour> »
sont tranchés par NOAA d'après la station d'aéroport citée dans `resolutionSource`
(https://www.weather.gov/wrh/timeseries?site=nzwn → station NZWN, colonne « Temp »). Cette page
n'a pas d'API publique documentée ; les mêmes relevés officiels (METAR) sont publiés par le
service météo aéronautique de NOAA, qui a une API publique :
  GET https://aviationweather.gov/api/data/metar?ids=NZWN,KDAL&format=json&hours=30
  → [{"icaoId", "obsTime" (secondes Unix), "temp" (°C), "name", "lat", "lon", ...}, ...]
Vérifié par un appel réel le 15/10/2026 (une erreur 502 passagère vue une fois : la source est
alors « indisponible » pour ce cycle, sans rien bloquer).

LIMITES (à garder en tête dans une stratégie) :
- la page de résolution peut contenir des relevés intermédiaires (toutes les 5 min aux
  États-Unis) absents des METAR horaires : le maximum METAR est un MINIMUM du maximum officiel ;
- le « jour » du marché est le jour LOCAL de la station. Le fuseau est estimé par la longitude
  (15° par heure), ce qui peut se tromper de 1 à 3 h : `day_max` ne compte que les relevés
  situés entre 03 h et 21 h « longitude » (sûrement dans le bon jour), d'où un maximum prudent ;
- les marchés s'expriment en °C ou en °F, arrondis : prévoir une marge d'au moins 1 degré.
Chaque observation est rattachée DIRECTEMENT aux marchés qui citent la station.
"""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from polymarket_agent.http_client import HttpClient
from polymarket_agent.observations import Observation

STATION = re.compile(r"weather\.gov/wrh/timeseries\?site=([a-z0-9]{3,5})", re.I)
URL = "https://aviationweather.gov/api/data/metar"


def station_of(resolution_source: str, description: str = "") -> str | None:
    found = STATION.search(resolution_source or "") or STATION.search(description or "")
    return found.group(1).upper() if found else None


def stations_for(markets) -> dict[str, list[str]]:
    """Station → identifiants des marchés qu'elle tranche."""
    out: dict[str, list[str]] = {}
    for m in markets:
        code = station_of(getattr(m, "resolution_source", ""), getattr(m, "description", ""))
        if code:
            out.setdefault(code, []).append(m.market_id)
    return out


def day_max(readings: list[tuple[int, float]], lon: float, now: datetime) -> tuple[str, float | None, int]:
    """(jour local estimé, maximum prudent du jour en °C, nombre de relevés retenus)."""
    offset = timedelta(hours=round(lon / 15))
    local_now = now + offset
    midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    lo, hi = midnight + timedelta(hours=3) - offset, midnight + timedelta(hours=21) - offset
    kept = [t for ts, t in readings
            if lo <= datetime.fromtimestamp(ts, tz=timezone.utc) <= hi]
    return midnight.strftime("%Y-%m-%d"), (max(kept) if kept else None), len(kept)


class MetarSource:
    name = "meteo_metar"

    def __init__(self, http: HttpClient, max_stations: int = 40):
        self.http, self.max_stations = http, max_stations

    def fetch(self, markets, now: datetime) -> list[Observation]:
        wanted = stations_for(markets)
        if not wanted:
            return []
        codes = sorted(wanted)[: self.max_stations]
        raw = self.http.get_json(URL, params={"ids": ",".join(codes), "format": "json", "hours": 30})
        by_station: dict[str, list[dict]] = {}
        for r in raw or []:
            if isinstance(r, dict) and r.get("temp") is not None and r.get("obsTime"):
                by_station.setdefault(str(r.get("icaoId", "")).upper(), []).append(r)
        out = []
        for code in codes:
            rows = sorted(by_station.get(code, []), key=lambda r: r["obsTime"])
            if not rows:
                continue
            readings = [(int(r["obsTime"]), float(r["temp"])) for r in rows]
            last = rows[-1]
            day, mx, n = day_max(readings, float(last.get("lon") or 0), now)
            last_t = datetime.fromtimestamp(int(last["obsTime"]), tz=timezone.utc)
            name = str(last.get("name") or code)
            summary = (f"max prudent du {day} : {mx:.1f} °C ({mx * 9 / 5 + 32:.0f} °F) sur {n} relevés"
                       if mx is not None else f"aucun relevé encore retenu pour le {day}")
            out.append(Observation(
                source=self.name, external_id=f"metar-{code}-{int(last['obsTime'])}", published_at=last_t,
                collected_at=now, url=f"https://www.weather.gov/wrh/timeseries?site={code.lower()}",
                title=f"Météo {name} ({code}) : {float(last['temp']):.1f} °C à {last_t:%H:%M} UTC",
                text=summary, domain="aviationweather.gov", market_ids=list(wanted[code]),
                data={"station": code, "jour_local": day, "max_jour_c": mx, "releves_jour": n,
                      "dernier_c": float(last["temp"]), "lon": last.get("lon"),
                      "releves": readings[-40:]}).finalize())
        return out
