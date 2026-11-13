"""Événements « OpenRouter token usage week of <lundi>? » réglés : tranches, résultat, prix horaires du CLOB (piste n° 50)."""
import json, sys, time
from datetime import datetime
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).parent / "donnees"
OUT.mkdir(exist_ok=True)
evs = {}
for page in range(1, 6):
    r = requests.get("https://gamma-api.polymarket.com/public-search",
                     params={"q": "OpenRouter token usage", "limit_per_type": 50, "page": page, "events_status": "closed"},
                     headers=H, timeout=30).json()
    for e in r.get("events") or []:
        evs[e["id"]] = e
    if len(r.get("events") or []) < 50:
        break
res = []
for eid in sorted(evs):
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    if "week" not in e["title"].lower():
        continue
    for m in e["markets"]:
        if not m.get("closed") or not m.get("clobTokenIds"):
            continue
        tok = json.loads(m["clobTokenIds"])[0]
        end = int(datetime.fromisoformat(m["endDate"].replace("Z", "+00:00")).timestamp())
        h = requests.get("https://clob.polymarket.com/prices-history",
                         params={"market": tok, "startTs": end - 12 * 86400, "endTs": end + 86400, "fidelity": 60}, timeout=30).json()
        res.append({"event": eid, "title": e["title"], "end": m["endDate"], "tranche": m.get("groupItemTitle"),
                    "won": json.loads(m["outcomePrices"])[0], "hist": [(x["t"], x["p"]) for x in h.get("history", [])]})
    print(eid, e["title"], file=sys.stderr)
(OUT / "marches.json").write_text(json.dumps(res))
