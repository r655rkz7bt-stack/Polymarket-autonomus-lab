"""Enquête du 22/10 : nf_sport_patiente (championne) sans ses plus gros paris, par jour, prix, sport, mode d'achat."""
import json, sys, math
from collections import defaultdict
from decimal import Decimal
sys.path.insert(0, "src")
from polymarket_agent.reporting import closed_trades

def load(p):
    return [json.loads(l) for l in open(p)]

name = sys.argv[1] if len(sys.argv) > 1 else "nf_sport_patiente_v1.0.0"
ents = load(f"published_data/ledger/fantome/{name}.jsonl")
# index BUY info per token
buys = defaultdict(list)
for e in ents:
    if e["type"] == "BUY":
        buys[e["data"]["token_id"]].append(e)
tr = closed_trades(ents)
rows = []
for t in tr:
    b = buys[t["token_id"]]
    cost = float(t["cost"]); pnl = float(t["pnl"])
    px = float(sum(Decimal(x["data"]["price"]) * Decimal(x["data"]["shares"]) for x in b) / sum(Decimal(x["data"]["shares"]) for x in b))
    ex = b[0]["data"].get("extra") or {}
    rows.append(dict(ts=t["closed_at"], opened=t["opened_at"], pnl=pnl, cost=cost, px=px, out=t["outcome"],
                     won=float(t["payout"] or 0) > 0.5, posted=bool(ex.get("resting_order") or ex.get("order_type")),
                     market=t["market_id"], ev=t["event_id"], nbuy=len(b), ex=ex))
n = len(rows)
tot = sum(r["pnl"] for r in rows); stake = sum(r["cost"] for r in rows)
print(f"{n} paris, pnl {tot:.1f}, mise {stake:.0f}, rendement {tot/stake*100:.2f}%")
print("gagnés", sum(r["won"] for r in rows), "attendus (prix)", round(sum(r["px"] for r in rows), 1))
rs = sorted(rows, key=lambda r: -r["pnl"])
for k in (3, 5, 10):
    rest = rs[k:]
    print(f"sans top{k}: pnl {sum(r['pnl'] for r in rest):.1f} rend {sum(r['pnl'] for r in rest)/sum(r['cost'] for r in rest)*100:.2f}%")
print("top3", [(r['out'], round(r['pnl']), round(r['px'],3), round(r['cost'])) for r in rs[:3]])
print("pires", [(r['out'], round(r['pnl']), round(r['px'],3), round(r['cost'])) for r in rs[-5:]])
def grp(key, label):
    g = defaultdict(list)
    for r in rows: g[key(r)].append(r)
    print("--", label)
    for k in sorted(g, key=str):
        v = g[k]; c = sum(r["cost"] for r in v); p = sum(r["pnl"] for r in v)
        w = sum(r["won"] for r in v); e = sum(r["px"] for r in v)
        print(f"  {k}: n={len(v)} pnl={p:.0f} rend={p/c*100:.1f}% gagnés {w} / attendus {e:.1f}")
grp(lambda r: r["opened"][:10], "jour d'ouverture")
grp(lambda r: "posé" if r["posted"] else "comptant", "mode")
grp(lambda r: round(r["px"]*40)/40, "prix (tranches 0,025)")
grp(lambda r: r["nbuy"], "nb d'achats")
# taille de mise relative au capital?
print("mise médiane", sorted(r["cost"] for r in rows)[n//2], "max", max(r["cost"] for r in rows))
# bootstrap par événement
import random
byev = defaultdict(lambda: [0,0])
for r in rows: byev[r["ev"]][0]+=r["pnl"]; byev[r["ev"]][1]+=r["cost"]
ev_ret = [v[0]/v[1] for v in byev.values()]
m = sum(ev_ret)/len(ev_ret); sd = (sum((x-m)**2 for x in ev_ret)/(len(ev_ret)-1))**.5
print(f"événements {len(ev_ret)} rendement moyen {m*100:.2f}% t={m/(sd/len(ev_ret)**.5):.2f}")
# z des prix
var = sum(r["px"]*(1-r["px"]) for r in rows)
z = (sum(r["won"] for r in rows) - sum(r["px"] for r in rows))/math.sqrt(var)
print("z_prix", round(z,2))
print("clés extra:", list(rows[0]["ex"].keys()))
