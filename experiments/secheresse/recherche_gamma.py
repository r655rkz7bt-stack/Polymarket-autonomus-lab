"""Piste n° 23 : relevé des événements « niveau d'eau » de Gamma (public-search, ouverts et clos)."""
import json, sys
import requests
H = {"User-Agent": "curl/8"}
out = {}
for q in sys.argv[1:]:
    for status in ("closed", "active"):
        for page in range(1, 6):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=30,
                             params={"q": q, "events_status": status, "limit_per_type": 50, "page": page})
            evs = (r.json() or {}).get("events") or []
            for e in evs:
                out[e["id"]] = {"id": e["id"], "title": e.get("title"), "slug": e.get("slug"), "end": e.get("endDate"),
                                "closed": e.get("closed"), "vol": e.get("volume"), "n": len(e.get("markets") or [])}
            if len(evs) < 50:
                break
json.dump(out, open("evenements.json", "w"), indent=1)
for e in sorted(out.values(), key=lambda e: str(e["end"])):
    print(e["id"], str(e["end"])[:10], e["closed"], e["n"], round(float(e["vol"] or 0)), e["title"])
