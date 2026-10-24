"""Relevé du 24/10/2026 : (1) lancements SpaceX de Launch Library 2 (sans clé), (2) événements Polymarket « How many SpaceX launches in … ».
Sortie : donnees/lancements.json (liste de [net, statut, nom]), donnees/evenements.json. Usage : .venv/bin/python releve.py"""
import json, time, requests
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "donnees"; OUT.mkdir(exist_ok=True)
H = {"User-Agent": "curl/8"}
rows, url = [], "https://ll.thespacedevs.com/2.2.0/launch/previous/?lsp__name=SpaceX&limit=100&ordering=-net&format=json&mode=list"
while url:
    r = requests.get(url, headers=H, timeout=60)
    if r.status_code != 200:
        print("LL2", r.status_code, r.text[:200]); break
    d = r.json()
    rows += [[x["net"], x["status"]["abbrev"], x["name"], x.get("window_start"), x.get("last_updated")] for x in d["results"]]
    url = d.get("next"); time.sleep(1)
print(len(rows), "lancements", rows[-1][:3] if rows else None)
json.dump(rows, open(OUT / "lancements.json", "w"))
ev = {}
for st in ("active", "closed"):
    for q in ("How many SpaceX launches", "SpaceX launches"):
        for p in range(1, 6):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params={"q": q, "events_status": st, "page": p, "limit_per_type": 50}, headers=H, timeout=40).json()
            for e in r.get("events", []):
                if "spacex launches" in e["title"].lower() and "starship" not in e["title"].lower():
                    ev[e["id"]] = e
            if len(r.get("events", [])) < 50: break
json.dump(list(ev.values()), open(OUT / "evenements.json", "w"))
for e in sorted(ev.values(), key=lambda e: e["endDate"]):
    print(e["id"], e["title"], e["endDate"][:10], e["closed"], round(float(e["volume"] or 0)), len(e["markets"]))
