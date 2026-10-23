"""Source : Observatoire de Hong Kong (HKO), l'arbitre des marchés de température de Hong Kong, sans clé.

Pourquoi (veille du 23/10/2026, experiments/veille_api_publiques.md) : les marchés « highest / lowest
temperature in Hong Kong on <jour> » (8 ouverts le 23/10) se règlent sur « Absolute Daily Max / Min
(deg. C) » de l'Observatoire (Daily Extract, https://www.weather.gov.hk/en/cis/climat.htm), au DIXIÈME de
degré. Ils ne citent aucune station METAR : `meteo_metar` ne les voyait pas.

Règlement : la tranche « 27°C » contient [27,0 ; 28,0[ (TRONCATURE, pas arrondi). Vérifié le 23/10/2026
sur 122 marchés réglés d'août-septembre (relevés officiels CLMMAXT / CLMMINT : troncature 122/122,
arrondi 61/122) et 44 marchés d'octobre (bulletin du lendemain RYES : 44/44) :
experiments/meteo_ensemble/hk_reglement.py. `weather_model.parse_question` suppose l'arrondi
([26,5 ; 27,5[) : utiliser `weather_model.truncated(q)` pour ces marchés.

API publiques (open data HKO, vérifiées par un appel réel le 23/10/2026) :
  GET https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_since_midnight_maxmin.csv
      → « Date time,Automatic Weather Station,Maximum Air Temperature Since Midnight(degree Celsius),
         Minimum ... » ; ligne « 202610240210,HK Observatory,28.3,27.1 » (heure de Hong Kong, UTC+8)
  GET https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=RYES&date=AAAAMMJJ&lang=en
      → bulletin de la veille (≈ 00 h 15 heure de Hong Kong, « provisoire ») : HKOReadingsMaxTemp, ...MinTemp

LIMITES : le maximum « depuis minuit » est celui de la station automatique de l'Observatoire, publié toutes
les 10 minutes ; le chiffre qui tranche est celui du Daily Extract (même station, validé). Non comparés
jour par jour à ce jour (les relevés gardés en base le permettront : `max_jour_c` du soir contre `veille`).
Le maximum relevé ne peut que monter, le minimum que descendre : ce sont des bornes, pas la valeur finale.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timedelta, timezone

from polymarket_agent.http_client import HttpClient
from polymarket_agent.observations import Observation

STATION = "HKO"
LAT, LON = 22.302, 114.174  # Observatoire, Tsim Sha Tsui
HKT = timezone(timedelta(hours=8))  # pas d'heure d'été à Hong Kong
MAXMIN_URL = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_since_midnight_maxmin.csv"
OPENDATA_URL = "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php"
ROW_NAME = "HK Observatory"


def is_hko_market(m) -> bool:
    """Marché tranché par l'Observatoire de Hong Kong (règles de Gamma)."""
    text = f"{getattr(m, 'resolution_source', '') or ''} {getattr(m, 'description', '') or ''}"
    return "Hong Kong Observatory" in text or "weather.gov.hk" in text


def parse_maxmin(text: str) -> tuple[datetime, float, float] | None:
    """(heure du relevé en UTC, maximum depuis minuit, minimum depuis minuit) de l'Observatoire, ou None."""
    for row in csv.reader(io.StringIO(text or "")):
        if len(row) >= 4 and row[1].strip() == ROW_NAME:
            try:
                stamp = datetime.strptime(row[0].strip(), "%Y%m%d%H%M").replace(tzinfo=HKT)
                return stamp.astimezone(timezone.utc), float(row[2]), float(row[3])
            except ValueError:
                return None
    return None


class HkoSource:
    name = "meteo_hko"

    def __init__(self, http: HttpClient, yesterday: bool = True):
        self.http, self.yesterday = http, yesterday

    def fetch(self, markets, now: datetime) -> list[Observation]:
        ids = [m.market_id for m in markets if is_hko_market(m)]
        if not ids:
            return []  # aucun marché de Hong Kong : aucun appel
        parsed = parse_maxmin(self.http.get_text(MAXMIN_URL))
        if parsed is None:
            raise ValueError("relevé de l'Observatoire illisible (ligne « HK Observatory » absente)")
        when, mx, mn = parsed
        local = when.astimezone(HKT)
        day = local.strftime("%Y-%m-%d")
        data = {"station": STATION, "jour_local": day, "max_jour_c": mx, "min_jour_c": mn,
                "heure_locale": local.strftime("%H:%M"), "lat": LAT, "lon": LON, "regle": "troncature"}
        if self.yesterday:  # bulletin de la veille : la valeur (provisoire) qui tranchera le marché d'hier
            before = (local - timedelta(days=1)).strftime("%Y%m%d")
            try:
                ryes = self.http.get_json(OPENDATA_URL, params={"dataType": "RYES", "date": before, "lang": "en"})
            except Exception:  # noqa: BLE001 - complément : le relevé du jour suffit
                ryes = None
            if isinstance(ryes, dict) and ryes.get("HKOReadingsMaxTemp") and ryes.get("HKOReadingsMinTemp"):
                try:
                    data["veille"] = {"jour": f"{before[:4]}-{before[4:6]}-{before[6:]}",
                                      "max_c": float(ryes["HKOReadingsMaxTemp"]), "min_c": float(ryes["HKOReadingsMinTemp"])}
                except ValueError:
                    pass
        return [Observation(
            source=self.name, external_id=f"hko-{local:%Y%m%d%H%M}", published_at=when, collected_at=now,
            url="https://www.weather.gov.hk/en/cis/climat.htm", domain="weather.gov.hk",
            title=f"Observatoire de Hong Kong : max {mx:.1f} °C, min {mn:.1f} °C depuis minuit ({local:%H:%M} heure locale)",
            text=f"max depuis minuit du {day} : {mx:.1f} °C ; min : {mn:.1f} °C (tranches par troncature)",
            market_ids=ids, data=data).finalize()]
