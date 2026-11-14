"""Relevé des événements « # of views of next MrBeast video on day 1 / week 1 » réglés (Gamma public-search).
Sortie : experiments/mrbeast_vues/donnees/evenements.json (ignoré par Git)."""
import json, os, sys, requests
H = {"User-Agent": "curl/8"}
OUT = os.path.join(os.path.dirname(__file__), "..", "donnees")
os.makedirs(OUT, exist_ok=True)
seen = {}
for q in ("MrBeast video on day 1", "MrBeast video on week 1", "views of next MrBeast video"):
    for status in ("closed", "active"):
        for page in range(1, 12):
            r = requests.get("https://gamma-api.polymarket.com/public-search",
                             params={"q": q, "events_status": status, "limit_per_type": 50, "page": page},
                             headers=H, timeout=30)
            evs = (r.json() or {}).get("events") or []
            new = 0
            for e in evs:
                if "mrbeast" in (e.get("title") or "").lower() and e["id"] not in seen:
                    seen[e["id"]] = e; new += 1
            if not evs:
                break
full = []
for eid in seen:
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    full.append(e)
json.dump(full, open(os.path.join(OUT, "evenements.json"), "w"))
print(len(full))
