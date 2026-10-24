"""compteur_tweets : l'estimation s'écarte-t-elle du prix quand il reste peu de temps ? (23/10/2026)
Un jeton = un achat (le plus ancien des fantômes `compteur_tweets*`), avec l'horizon (heures avant la fin) et le résultat."""
import json, math, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
from enquete import load_published
from polymarket_agent.reporting import closed_trades
E = load_published(Path("published_data"))
first = {}
for name, rows in E.items():
    if not name.startswith("compteur_tweets"): continue
    hor = {}
    for e in rows:
        if e["type"] == "BUY":
            hor.setdefault(e["data"]["token_id"], (e["data"].get("extra") or {}).get("horizon_hours"))
    for t in closed_trades(rows):
        if t.get("payout") is None: continue
        r = dict(op=t["opened_at"], name=name, p=float(t["cost"]) / float(t["shares_bought"]), e=float(t["est_probability"]),
                 w=float(t["payout"]) > 0.5, cost=float(t["cost"]), pnl=float(t["pnl"]), h=float(hor[t["token_id"]] or -1),
                 out=t["outcome"], mk=t["market_id"])
        if t["token_id"] not in first or r["op"] < first[t["token_id"]]["op"]: first[t["token_id"]] = r
rows = list(first.values())
print(len(rows), "achats distincts")
def rep(title, key):
    g = defaultdict(list)
    for r in rows: g[key(r)].append(r)
    print("\n==", title)
    for k, v in sorted(g.items()):
        w = sum(r["w"] for r in v); e = sum(r["e"] for r in v); p = sum(r["p"] for r in v)
        print(f"{str(k):16} n={len(v):3} gagnés {w:3} annoncés {e:6.1f} prix {p:6.1f}  gain {sum(r['pnl'] for r in v):+7.1f} € / {sum(r['cost'] for r in v):7.1f} €")
rep("horizon (h avant la fin)", lambda r: "<1" if r["h"] < 1 else "1-6" if r["h"] < 6 else "6-24" if r["h"] < 24 else "24-72" if r["h"] < 72 else ">72")
rep("écart estimation - prix", lambda r: "<0.1" if r["e"] - r["p"] < .1 else "0.1-0.2" if r["e"] - r["p"] < .2 else "0.2-0.4" if r["e"] - r["p"] < .4 else ">0.4")
print("\nles plus gros écarts :")
for r in sorted(rows, key=lambda r: -(r["e"] - r["p"]))[:12]:
    print(r["op"][:16], r["name"][:34], r["out"], f"est {r['e']:.2f} prix {r['p']:.2f} h {r['h']:.1f}", "GAGNÉ" if r["w"] else "perdu", f"{r['pnl']:+.1f}", r["mk"])
