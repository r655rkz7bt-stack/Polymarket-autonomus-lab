"""Événements « Which company has the best AI model end of <mois>? » (Text Arena overall) réglés : règle, résultat, prix horaires
du CLOB sur les 20 derniers jours (piste n° 51). Sortie : donnees/marches.json."""
import json, sys
from datetime import datetime
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).parent / "donnees"
evs = {}
for q in ["best AI model end of", "Which company has best AI model end of", "top AI model end of"]:
    for page in range(1, 6):
        r = requests.get("https://gamma-api.polymarket.com/public-search",
                         params={"q": q, "events_status": "closed", "limit_per_type": 50, "page": page}, headers=H, timeout=30).json()
        for e in r.get("events") or []:
            evs[e["id"]] = e
        if len(r.get("events") or []) < 50:
            break
res = []
for eid, e0 in sorted(evs.items(), key=lambda x: x[1].get("endDate") or ""):
    t = e0["title"].lower()
    if "best ai model" not in t or any(w in t for w in ("math", "code", "webdev", "vision", "style", "image", "video", "search", "second", "#2", "third")):
        continue
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    if not e.get("closed"):
        continue
    for m in e["markets"]:
        if not m.get("clobTokenIds") or not m.get("closed"):
            continue
        won = json.loads(m["outcomePrices"])[0]
        tok = json.loads(m["clobTokenIds"])[0]
        end = int(datetime.fromisoformat(m["endDate"].replace("Z", "+00:00")).timestamp())
        hist = []
        for s in (end - 21 * 86400, end - 10 * 86400):
            h = requests.get("https://clob.polymarket.com/prices-history",
                             params={"market": tok, "startTs": s, "endTs": min(end, s + 11 * 86400), "fidelity": 60}, timeout=30).json()
            hist += [(x["t"], x["p"]) for x in h.get("history", [])]
        if not hist:
            continue
        res.append({"event": eid, "title": e["title"], "end": m["endDate"], "company": m.get("groupItemTitle"), "won": won,
                    "description": e.get("description", "")[:700], "hist": sorted(set(hist))})
    print(eid, e["title"], file=sys.stderr)
(OUT / "marches.json").write_text(json.dumps(res))
print(len(res), file=sys.stderr)
