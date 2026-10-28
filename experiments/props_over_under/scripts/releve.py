"""Relevé des marchés « Over/Under » de sport réglés (props de joueurs, totaux, totaux d'équipe, mi-temps, quarts) et de leurs vrais échanges.

Gamma /events/keyset (jamais offset) par série, événements dont le coup d'envoi est depuis DEPUIS ; marchés dont les issues sont Over/Under.
Écrit donnees/ou_marches.jsonl : un marché par ligne (type, ligne, jetons, issue gagnante, volume, coup d'envoi, échanges des preneurs).
Usage : python releve.py [fils]   (depuis la racine du dépôt)
"""
import json, os, sys, time, datetime as dt, threading
from concurrent.futures import ThreadPoolExecutor
import requests

SERIES = {"nba": 10345, "nhl": 10346, "nfl": 12185, "cfb": 12756, "ncaab": 39, "wnba": 10105, "euroleague": 10371, "cbb": 10470, "khl": 10700, "ahl": 10699}
DEPUIS = dt.datetime(2026, 9, 1, tzinfo=dt.timezone.utc)
OUT = "experiments/props_over_under/donnees"
S = threading.local()
def sess():
    if not hasattr(S, "s"):
        S.s = requests.Session(); S.s.headers["User-Agent"] = "curl/8"
    return S.s
def get(url, params, essais=6):
    for i in range(essais):
        try:
            r = sess().get(url, params=params, timeout=60)
            if r.status_code == 200: return r.json()
        except requests.RequestException: pass
        time.sleep(1 + i)
def debut(e):
    for m in e.get("markets") or []:
        if m.get("gameStartTime"):
            return dt.datetime.fromisoformat(m["gameStartTime"].replace("+00", "+00:00").replace("Z", "+00:00"))
def liste(item):
    nom, sid = item; out = []; cur = None; vieux = 0
    while True:
        p = {"series_id": sid, "closed": "true", "limit": 100, "order": "endDate", "ascending": "false"}
        if cur: p["after_cursor"] = cur
        d = get("https://gamma-api.polymarket.com/events/keyset", p)
        if not d or not d.get("events"): break
        for e in d["events"]:
            st = debut(e)
            if st is None: continue
            vieux = vieux + 1 if st < DEPUIS else 0
            if st < DEPUIS: continue
            for m in e.get("markets") or []:
                try: outs = json.loads(m["outcomes"]); pr = [float(x) for x in json.loads(m["outcomePrices"])]
                except Exception: continue
                if outs != ["Over", "Under"] or sorted(pr) != [0.0, 1.0]: continue
                out.append(dict(sport=nom, ev=e["id"], titre=e.get("title"), type=m.get("sportsMarketType"), ligne=m.get("line"), question=m.get("question"),
                                cid=m["conditionId"], over=json.loads(m["clobTokenIds"])[0], under=json.loads(m["clobTokenIds"])[1],
                                gagnant=outs[pr.index(1.0)], vol=m.get("volumeNum"), debut=st.timestamp(), fee=m.get("feeSchedule")))
        cur = d.get("next_cursor")
        if not cur or vieux > 300: break
    print(nom, len(out), "marchés Over/Under", flush=True)
    return out
def echanges(m):
    tr = []
    for off in range(0, 10000, 1000):
        j = get("https://data-api.polymarket.com/trades", {"market": m["cid"], "limit": 1000, "offset": off, "takerOnly": "true"})
        if not j: break
        tr += [(x["timestamp"], x["asset"], x["side"], x["price"], x["size"]) for x in j]
        if len(j) < 1000: break
    m["trades"] = tr
    return m
if __name__ == "__main__":
    fils = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    with ThreadPoolExecutor(6) as ex: tous = [m for r in ex.map(liste, SERIES.items()) for m in r]
    print(len(tous), "marchés au total", flush=True)
    t = time.time()
    with ThreadPoolExecutor(fils) as ex, open(f"{OUT}/ou_marches.jsonl", "w") as f:
        for k, m in enumerate(ex.map(echanges, tous), 1):
            f.write(json.dumps(m) + "\n")
            if k % 1000 == 0: print(k, round(time.time() - t), "s", flush=True)
