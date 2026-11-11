"""11/11/2026 : table des fréquences de base pour `seismes_pays` (src/polymarket_agent/seismes_pays.json) : par pays, nombre de JOURS
par an avec au moins un séisme >= 6,0 (USGS, 2000-2025) dont la description de lieu se termine par ce pays (règle des marchés « Where
will a 6.0+ magnitude earthquake occur … » : pays nommé dans la description ; un séisme d'Alaska compte pour les États-Unis, marché
de septembre 2026). Compter les jours et non les séismes : les répliques du même jour ne font qu'un. Usage :
.venv/bin/python experiments/seismes_pays/table.py"""
import json, datetime as dt, collections, requests
from pathlib import Path
import sys
sys.path.insert(0, "src")
from polymarket_agent.seismes import country_of
cat = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", params={"format": "geojson", "minmagnitude": 5.95,
                   "starttime": "2000-01-01", "endtime": "2026-01-01", "limit": 20000}, timeout=120).json()
days = collections.defaultdict(set)
for f in cat["features"]:
    p = f["properties"]
    if p["mag"] is None or round(p["mag"] + 1e-9, 1) < 6.0:
        continue
    c = country_of(p["place"] or "")
    if c:
        days[c].add(dt.datetime.utcfromtimestamp(p["time"] / 1000).date())
table = {c: round(len(d) / 26, 3) for c, d in sorted(days.items(), key=lambda x: -len(x[1])) if len(d) >= 5}
out = {"source": "USGS M>=6.0 2000-2025, jours par an avec au moins un séisme attribué au pays", "jours_par_an": table}
Path("src/polymarket_agent/seismes_pays.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(len(table), list(table.items())[:25])
