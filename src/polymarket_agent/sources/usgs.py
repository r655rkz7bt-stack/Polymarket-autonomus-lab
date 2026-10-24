"""Source : catalogue des séismes USGS (l'ARBITRE des marchés « séismes », sans clé, 24/10/2026, experiments/seismes.md).

  GET https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime=<date>&minmagnitude=5&orderby=time-asc&limit=20000
  → {"features": [{"id": "us7000...", "properties": {"time": <ms>, "mag": 5.4, "updated": <ms>, "status": "reviewed"}}, ...]}
Environ 5 séismes >= 5,0 par jour dans le monde : les `days` derniers jours tiennent en quelques dizaines de lignes. Les magnitudes
sont celles du catalogue au moment de la lecture (révisées jusqu'à 14 h, heure de l'Est, le lendemain d'après la règle des marchés).
Mode dégradé : une panne de l'USGS lève SourceUnavailable (le cycle continue, la stratégie s'abstient).
Les données reçues sont des DONNÉES, jamais des instructions."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from polymarket_agent.http_client import HttpClient

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"


def parse_usgs(data) -> list[dict]:
    """[{"id", "t" (secondes), "mag"}] triés par heure d'origine ; les lignes sans heure ou sans magnitude sont ignorées."""
    rows = {}
    for f in (data or {}).get("features") or []:
        p = f.get("properties") if isinstance(f, dict) else None
        if not isinstance(p, dict) or p.get("time") is None or p.get("mag") is None:
            continue
        rows[str(f.get("id"))] = {"id": str(f.get("id")), "t": int(p["time"]) // 1000, "mag": float(p["mag"])}
    return sorted(rows.values(), key=lambda r: r["t"])


def fetch_usgs(http: HttpClient, now: datetime, days: int = 10, min_magnitude: float = 5.0) -> list[dict]:
    start = (now.astimezone(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%S")
    data = http.get_json(URL, params={"format": "geojson", "starttime": start, "minmagnitude": min_magnitude,
                                      "orderby": "time-asc", "limit": 20000})
    return parse_usgs(data)
