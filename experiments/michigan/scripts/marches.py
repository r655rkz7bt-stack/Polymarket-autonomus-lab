"""Événements Polymarket « University of Michigan Consumer Sentiment - <mois> » (réglés et ouverts) : tranches, issue, prix
horaires du OUI de chaque tranche (CLOB). Sortie : releves/marches.json"""
import gzip, json, re, time
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1] / "releves"
H = {"User-Agent": "curl/8"}
evs = {}
for st in ("closed", "active"):
    for q in ("University of Michigan Consumer Sentiment", "Michigan Consumer Sentiment", "consumer sentiment"):
        r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=60,
                         params={"q": q, "events_status": st, "limit_per_type": 50}).json()
        for e in r.get("events") or []:
            if "sentiment" in e["title"].lower():
                evs[e["id"]] = e["title"]
out = []
for eid, title in evs.items():
    ev = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=60).json()
    for m in ev.get("markets") or []:
        tok = json.loads(m.get("clobTokenIds") or "[]")
        hist = []
        if tok:
            # `interval=max` rend [] pour un marché clos : tranches de 13 jours (astuce du 04/11)
            from datetime import datetime
            a = datetime.fromisoformat(m["createdAt"].replace("Z", "+00:00")).timestamp()
            b = time.time()
            s = a
            while s < b:
                e = min(s + 13 * 86400, b)
                h = requests.get("https://clob.polymarket.com/prices-history", timeout=60,
                                 params={"market": tok[0], "startTs": int(s), "endTs": int(e), "fidelity": 60}).json().get("history", [])
                hist += [[x["t"], x["p"]] for x in h]
                s = e
        out.append({"event": eid, "titre": title, "fin": ev.get("endDate"), "tranche": m.get("groupItemTitle"), "id": m["id"],
                    "clos": bool(m.get("closed")), "prix": m.get("outcomePrices"), "creation": m.get("createdAt"),
                    "ferme": m.get("closedTime"), "tokens": tok, "hist": hist, "volume": float(m.get("volume") or 0)})
        time.sleep(0.2)
gzip.open(R / "marches.json.gz", "wt").write(json.dumps(out))
print(len(evs), "événements", len(out), "marchés", sum(1 for x in out if x["hist"]), "avec prix")
for eid, t in evs.items():
    print(eid, t)
