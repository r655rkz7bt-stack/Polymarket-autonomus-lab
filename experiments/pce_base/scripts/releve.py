"""Relevé des événements « Core PCE / PCE » de Gamma (public-search, ouverts et clos) -> donnees/evenements.json."""
import json, sys, pathlib, requests
H = {"User-Agent": "curl/8"}
out, seen = [], set()
for q in ("Core PCE", "PCE MoM", "PCE YoY", "PCE inflation"):
    for status in ("closed", "active"):
        for page in range(1, 8):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=30,
                             params={"q": q, "events_status": status, "limit_per_type": 50, "page": page})
            evs = (r.json() or {}).get("events") or []
            for e in evs:
                if e["id"] not in seen and "pce" in e.get("title", "").lower():
                    seen.add(e["id"]); out.append(e)
            if len(evs) < 50:
                break
d = pathlib.Path(__file__).resolve().parent.parent / "donnees"; d.mkdir(exist_ok=True)
full = []
for e in out:
    full.append(requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=30).json())
(d / "evenements.json").write_text(json.dumps(full))
for e in sorted(full, key=lambda e: e.get("endDate") or ""):
    print(e["id"], (e.get("endDate") or "")[:10], e.get("closed"), len(e.get("markets") or []), round(float(e.get("volume") or 0)), e["title"])
