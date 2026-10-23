"""Historique quotidien IMF PortWatch (passages par détroit) -> CSV. Usage : portwatch.py <nom du détroit> <sortie.csv>"""
import csv, sys, datetime as dt, requests
URL = "https://services9.arcgis.com/weJ1QsnbMYJlCHdG/arcgis/rest/services/Daily_Chokepoints_Data/FeatureServer/0/query"
name, out = sys.argv[1], sys.argv[2]
rows, off = [], 0
while True:
    r = requests.get(URL, params=dict(where=f"portname='{name}'", outFields="*", orderByFields="date ASC", resultOffset=off, resultRecordCount=1000, f="json"),
                     headers={"User-Agent": "curl/8"}, timeout=60).json()
    feats = r.get("features")
    if feats is None:
        print(str(r)[:300]); break
    rows += [f["attributes"] for f in feats]
    if len(feats) < 1000 and not r.get("exceededTransferLimit"):
        break
    off += len(feats)
for x in rows:
    x["jour"] = str(x["date"])[:10]
cols = ["jour", "portname", "n_total", "n_tanker", "n_container", "n_cargo", "n_dry_bulk", "n_roro", "capacity"]
with open(out, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=[c for c in cols if rows and c in rows[0]], extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
print(len(rows), rows[0]["jour"] if rows else None, rows[-1]["jour"] if rows else None, list(rows[0])[:20] if rows else "")
