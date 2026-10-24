"""Relevé du catalogue USGS (M >= 5,0, 2014 -> aujourd'hui) : heure d'origine, magnitude, heure de mise à jour."""
import gzip, json, sys, requests
from datetime import date
H = {"User-Agent": "curl/8"}
out = []
for year in range(2014, 2027):
    for a, b in ((f"{year}-01-01", f"{year}-07-01"), (f"{year}-07-01", f"{year+1}-01-01")):
        if year == 2026 and a.endswith("07-01"): b = "2026-10-25"
        r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query", headers=H, timeout=120,
                         params=dict(format="geojson", starttime=a, endtime=b, minmagnitude=5.0, orderby="time-asc", limit=20000))
        r.raise_for_status()
        for f in r.json()["features"]:
            p = f["properties"]
            out.append([f["id"], p["time"] // 1000, p["mag"], (p.get("updated") or 0) // 1000, p.get("magType"), p.get("status")])
        print(a, b, len(out), file=sys.stderr)
seen = {}
for o in out: seen[o[0]] = o
rows = sorted(seen.values(), key=lambda o: o[1])
with gzip.open("experiments/seismes/releves/usgs_m5.json.gz", "wt") as f: json.dump(rows, f)
print(len(rows))
