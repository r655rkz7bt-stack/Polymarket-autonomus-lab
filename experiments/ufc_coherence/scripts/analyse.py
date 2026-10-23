"""Piste n° 6 : KO/TKO + soumission + décision = 1 (UFC). Paniers de 3 jetons achetés aux prix des vrais échanges.
Panier OUI (KO, soumission, 'fight to go the distance') : paie 1 si le combat se termine par l'une des trois issues.
Panier NON : paie 2 (sauf issue 'autre' : 3). Prix = 1er échange preneur dans les 30 min APRÈS l'instant de décision (prix qu'on aurait payé)."""
import json, collections, sys, math
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import taker_cost, fee, verdict
ev = {e["id"]: e for e in json.load(open("donnees/events.json"))}
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["event"]] = o["trades"]
def jl(x): return json.loads(x) if isinstance(x, str) else x
import datetime
def ts(s): return int(datetime.datetime.fromisoformat(s.replace("+00", "+00:00").replace("Z", "+00:00")).timestamp())
import os
WIN = int(os.environ.get("WIN", 1800))
LAGS = [-21600, -10800, -3600, -1800]
out = []
for eid, e in ev.items():
    ms = e["markets"]
    ko = [m for m in ms if m["question"] == "Will the fight be won by KO or TKO?"]
    sub = [m for m in ms if m["question"] == "Will the fight be won by submission?"]
    dist = [m for m in ms if m.get("sportsMarketType") == "ufc_go_the_distance"]
    if not (ko and sub and dist) or eid not in tr: continue
    legs = [ko[0], sub[0], dist[0]]
    start = ts(legs[0].get("gameStartTime") or e["startTime"])
    res = []
    ok = True
    for m in legs:
        pr = [str(p) for p in jl(m["outcomePrices"])]
        if sorted(pr) != ["0", "1"]: ok = False
        res.append(1 if pr[0] == "1" else 0)
    if not ok: continue
    toks = [jl(m["clobTokenIds"]) for m in legs]
    rate = 0.05
    for lag in LAGS:
        t0 = start + lag
        for side in ("yes", "no"):
            cost = []; fees = 0
            for (y, n), r in zip(toks, res):
                tok, oth = (y, n) if side == "yes" else (n, y)
                p = taker_cost(tr[eid], tok, oth, t0, window=WIN, after=True)
                if p is None: break
                cost.append(p); fees += fee(p, rate)
            if len(cost) < 3: continue
            pay = sum(res) if side == "yes" else sum(1 - r for r in res)
            out.append({"event": eid, "titre": e["title"], "lag": lag, "side": side, "cost": sum(cost), "fees": fees, "pay": pay, "S": sum(cost), "res": res})
json.dump(out, open("donnees/paniers.json", "w"))
print("paniers", len(out), "événements", len({o['event'] for o in out}))
for lag in LAGS:
    for side in ("yes", "no"):
        sel = [o for o in out if o["lag"] == lag and o["side"] == side]
        if not sel: continue
        thr = (lambda o: o["cost"] < 1 - o["fees"]) if side == "yes" else (lambda o: o["cost"] < 2 - o["fees"])
        arb = [o for o in sel if thr(o)]
        print(f"lag {lag/3600:+.1f} h {side}: {len(sel)} paniers, coût moyen {sum(o['cost'] for o in sel)/len(sel):.3f}, "
              f"{len(arb)} sous le seuil; gain moyen sous seuil {sum(o['pay']-o['cost']-o['fees'] for o in arb)/max(1,len(arb)):+.4f}")
