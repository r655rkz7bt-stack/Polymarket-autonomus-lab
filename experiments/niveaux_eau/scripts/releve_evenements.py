"""Relevé des événements Polymarket de niveaux d'eau (fleuves, lacs) : public-search, ouverts et clos."""
import json, sys, time, requests
H = {"User-Agent": "curl/8"}
REQ = ["Mississippi", "Lake Mead", "Lake Powell", "Great Salt Lake", "Rhine", "Danube", "river level", "lake level", "water level", "Kaub"]
out = {}
for q in REQ:
    for status in ("closed", "active"):
        for page in range(1, 8):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params=dict(q=q, events_status=status, limit_per_type=50, page=page), headers=H, timeout=30)
            if r.status_code != 200:
                print(q, status, page, r.status_code, file=sys.stderr); break
            evs = r.json().get("events") or []
            for e in evs:
                out[e["id"]] = dict(id=e["id"], slug=e.get("slug"), title=e.get("title"), closed=e.get("closed"), end=e.get("endDate"),
                                    n=len(e.get("markets") or []), vol=e.get("volume"))
            if len(evs) < 50: break
            time.sleep(0.2)
json.dump(out, open(sys.argv[1], "w"), indent=0)
for e in sorted(out.values(), key=lambda e: e["end"] or ""):
    print(e["id"], e["closed"], (e["end"] or "")[:10], e["n"], round(float(e["vol"] or 0)), e["title"][:90])
