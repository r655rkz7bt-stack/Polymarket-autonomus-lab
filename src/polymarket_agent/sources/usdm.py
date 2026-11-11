"""Source : US Drought Monitor, part de chaque État en D0..D4 (université du Nebraska, sans clé, 11/11/2026).

  GET https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent
      ?aoi=01,04,…&startdate=M/J/AAAA&enddate=M/J/AAAA&statisticsType=2     (en-tête Accept: application/json)
  → [{"mapDate": "2026-11-03T00:00:00", "stateAbbreviation": "AL", "none": 27.98, "d0": …, "d4": 0.00, …}, …]
C'est l'ARBITRE des marchés « Exceptional drought (D4) by state — week of <mardi> » (D4 >= 0,05 % de la surface de l'État dans
la carte du mardi, publiée le jeudi à 8 h 30, heure de l'Est). Une carte n'apparaît dans l'API qu'une fois publiée : la dernière
carte du relevé est celle que tout le monde peut lire (experiments/secheresse.md).
Mode dégradé : une panne lève SourceUnavailable (le cycle continue, la stratégie garde le relevé précédent puis s'abstient).
Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from polymarket_agent.http_client import HttpClient

URL = "https://usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent"
FIPS = {"AL": "01", "AZ": "04", "AR": "05", "CA": "06", "CO": "08", "CT": "09", "DE": "10", "FL": "12", "GA": "13", "ID": "16",
        "IL": "17", "IN": "18", "IA": "19", "KS": "20", "KY": "21", "LA": "22", "ME": "23", "MD": "24", "MA": "25", "MI": "26",
        "MN": "27", "MS": "28", "MO": "29", "MT": "30", "NE": "31", "NV": "32", "NH": "33", "NJ": "34", "NM": "35", "NY": "36",
        "NC": "37", "ND": "38", "OH": "39", "OK": "40", "OR": "41", "PA": "42", "RI": "44", "SC": "45", "SD": "46", "TN": "47",
        "TX": "48", "UT": "49", "VT": "50", "VA": "51", "WA": "53", "WV": "54", "WI": "55", "WY": "56"}


def parse_usdm(data) -> list[dict]:
    """[{"id": "AL:2026-11-03", "etat": "AL", "date": "2026-11-03", "d2", "d3", "d4"}] (parts en %, catégories exclusives)."""
    rows = {}
    for r in data or []:
        if not isinstance(r, dict):
            continue
        try:
            st, day = str(r["stateAbbreviation"]), str(r["mapDate"])[:10]
            rows[f"{st}:{day}"] = {"id": f"{st}:{day}", "etat": st, "date": day,
                                   "d2": float(r["d2"]), "d3": float(r["d3"]), "d4": float(r["d4"])}
        except (KeyError, TypeError, ValueError):
            continue
    return sorted(rows.values(), key=lambda r: (r["etat"], r["date"]))


def fetch_usdm(http: HttpClient, now: datetime, days: int = 21) -> list[dict]:
    start = (now.astimezone(timezone.utc) - timedelta(days=days)).date()
    end = now.astimezone(timezone.utc).date() + timedelta(days=1)
    data = http.get_json(URL, params={"aoi": ",".join(FIPS.values()), "startdate": f"{start.month}/{start.day}/{start.year}",
                                      "enddate": f"{end.month}/{end.day}/{end.year}", "statisticsType": 2},
                         headers={"Accept": "application/json"})
    return parse_usdm(data)
