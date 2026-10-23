"""Piste n° 6, version stricte : les trois jambes (KO/TKO, soumission, 'fight to go the distance') doivent s'échanger dans les
WIN secondes qui suivent l'instant de décision, et tout doit finir avant le coup d'envoi. Grille : toutes les 10 minutes de -24 h à -5 min."""
import json, sys, os, datetime, collections
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import taker_cost, fee, verdict
WIN = int(os.environ.get("WIN", 300))
ev = {e["id"]: e for e in json.load(open("donnees/events.json"))}
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["event"]] = o["trades"]
jl = lambda x: json.loads(x) if isinstance(x, str) else x
def ts(s): return int(datetime.datetime.fromisoformat(s.replace("+00", "+00:00").replace("Z", "+00:00")).timestamp())
bets = {"yes": [], "no": []}; nb = collections.Counter()
for eid, e in ev.items():
    if eid not in tr: continue
    ms = e["markets"]
    legs = [[m for m in ms if m["question"] == "Will the fight be won by KO or TKO?"], [m for m in ms if m["question"] == "Will the fight be won by submission?"],
            [m for m in ms if m.get("sportsMarketType") == "ufc_go_the_distance"]]
    if not all(legs): continue
    legs = [l[0] for l in legs]
    start = ts(legs[0].get("gameStartTime") or e["startTime"])
    res = []
    for m in legs:
        pr = [str(p) for p in jl(m["outcomePrices"])]
        res.append(1 if pr == ["1", "0"] else 0 if pr == ["0", "1"] else None)
    if None in res: continue
    toks = [jl(m["clobTokenIds"]) for m in legs]
    first = True
    for t0 in range(start - 24 * 3600, start - 300 - WIN, 600):
        for side in ("yes", "no"):
            cost = []; fees = 0
            for (y, n) in toks:
                tok, oth = (y, n) if side == "yes" else (n, y)
                p = taker_cost(tr[eid], tok, oth, t0, window=WIN, after=True)
                if p is None: break
                cost.append(p); fees += fee(p, 0.05)
            if len(cost) < 3: continue
            nb[side] += 1
            pay = sum(res) if side == "yes" else sum(1 - r for r in res)
            net = pay - sum(cost) - fees
            if (side == "yes" and sum(cost) + fees < 1) or (side == "no" and sum(cost) + fees < 2):
                bets[side].append({"eid": eid, "t": t0 - start, "cost": sum(cost), "fees": fees, "pay": pay, "net": net, "titre": e["title"][:45]})
print("WIN", WIN, "paniers observables", dict(nb))
for side in bets:
    b = bets[side]
    print(side, "sous le seuil :", len(b), "événements", len({x['eid'] for x in b}), "gain moyen", round(sum(x['net'] for x in b) / max(1, len(b)), 4))
    for x in b[:12]: print("   ", x["titre"], round(x["t"] / 3600, 2), "h", round(x["cost"], 3), round(x["fees"], 3), x["pay"])
