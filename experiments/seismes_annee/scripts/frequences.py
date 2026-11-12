"""Fréquences de base (USGS ComCat, sans clé) pour les marchés annuels de séismes : séismes >= 7,0 par an (2000-2025), séismes
>= 8,0 / 8,2 / … / 9,0 par an (1950-2025), séismes >= 7,0 en Californie (description de lieu « CA » / « California », 1950-2025)."""
import collections, datetime, json, requests
U = "https://earthquake.usgs.gov/fdsnws/event/1/query"
r = requests.get(U, params={"format": "geojson", "starttime": "1950-01-01", "endtime": "2026-01-01", "minmagnitude": 7.0}, timeout=180).json()
rows = [(datetime.datetime.utcfromtimestamp(f["properties"]["time"] / 1000), f["properties"]["mag"], f["properties"]["place"] or "")
        for f in r["features"]]
an = collections.Counter(t.year for t, m, p in rows if t.year >= 2000)
out = {"m7_par_an_2000_2025": sum(an.values()) / 26, "m7_par_an": dict(sorted(an.items()))}
for s in (8.0, 8.2, 8.4, 8.6, 8.8, 9.0):
    out[f"m{s:.1f}_par_an_1950_2025"] = sum(1 for t, m, p in rows if round(m + 1e-9, 1) >= s) / 76
ca = [(t.isoformat()[:10], m, p) for t, m, p in rows if p.endswith(", CA") or "California" in p]
out["californie_m7"] = ca
out["californie_m7_par_an_1950_2025"] = len(ca) / 76
print(json.dumps({k: v for k, v in out.items() if k != "m7_par_an"}, indent=1, ensure_ascii=False))
json.dump(out, open("experiments/seismes_annee/frequences.json", "w"), indent=1, ensure_ascii=False)
