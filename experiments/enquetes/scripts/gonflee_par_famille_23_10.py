"""Où l'écart « gagnés − annoncés » de l'arène se loge-t-il ? (23/10/2026, contrôle estimation_gonflee, z = -10,9)
Un jeton = un pari (le plus ancien). Par famille de stratégie, par tranche de prix, par semaine d'ouverture."""
import math, sys
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, "scripts"); sys.path.insert(0, "src")
from enquete import load_published
from polymarket_agent.reporting import closed_trades

entries = load_published(Path("published_data"))
seen = {}
for name, rows in entries.items():
    if name == "principal": continue
    for t in closed_trades(rows):
        if t.get("payout") is None or t.get("est_probability") is None or float(t["shares_bought"]) <= 0: continue
        r = dict(op=t["opened_at"], strat=t["strategy"], p=float(t["cost"])/float(t["shares_bought"]),
                 e=float(t["est_probability"]), w=float(t["payout"]) > 0.5, cost=float(t["cost"]), pnl=float(t["pnl"]))
        if t["token_id"] not in seen or r["op"] < seen[t["token_id"]]["op"]: seen[t["token_id"]] = r
rows = [r for r in seen.values() if 0 < r["e"] < 1]
def fam(s):
    for k in ("nf_tennis","nf_sport","nf_court","nf_","naive_favorite","nm_","news_momentum","contrer_crypto","market_maker","market_structure","calibration","mots","compteur","loterie","crypto_threshold","outsider","apres_echeance","marche_neuf"):
        if s.startswith(k): return k
    return s
def rep(title, groups):
    print(f"\n== {title}")
    print(f"{'groupe':28} {'n':>5} {'gagn':>5} {'annonc':>7} {'prix':>7} {'z_est':>6} {'z_prix':>6} {'pnl':>8} {'mis':>8}")
    for k, g in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(g) < 15: continue
        w = sum(r["w"] for r in g); e = sum(r["e"] for r in g); p = sum(r["p"] for r in g)
        ve = sum(r["e"]*(1-r["e"]) for r in g) or 1; vp = sum(r["p"]*(1-r["p"]) for r in g) or 1
        print(f"{str(k):28} {len(g):5} {w:5} {e:7.1f} {p:7.1f} {(w-e)/math.sqrt(ve):+6.1f} {(w-p)/math.sqrt(vp):+6.1f} {sum(r['pnl'] for r in g):+8.0f} {sum(r['cost'] for r in g):8.0f}")
g = defaultdict(list)
for r in rows: g[fam(r["strat"])].append(r)
rep("famille", g)
g = defaultdict(list)
for r in rows: g[round(math.floor(r["p"]*20)/20, 2)].append(r)
rep("tranche de prix payé", g)
g = defaultdict(list)
for r in rows: g[r["op"][:10]].append(r)
rep("jour d'ouverture", dict(sorted(g.items())))
g = defaultdict(list)
for r in rows: g[round(r["e"]-r["p"], 2) // 0.02 * 0.02].append(r)
rep("écart annoncé (est - prix)", dict(sorted(g.items())))
rep("tout", {"tout": rows})

# Décomposition du rendement de l'arène : frais payés, aléa attendu à ±1 écart-type, reste.
import random
fees = {}
for name, rows_ in entries.items():
    if name == "principal": continue
    for t in closed_trades(rows_):
        if t.get("payout") is None or float(t["shares_bought"]) <= 0: continue
        if t["token_id"] not in fees or t["opened_at"] < fees[t["token_id"]][0]:
            fees[t["token_id"]] = (t["opened_at"], float(t["fees"]))
tot_fees = sum(v[1] for v in fees.values())
stake = sum(r["cost"] for r in seen.values())
pnl = sum(r["pnl"] for r in seen.values())
# gain attendu hors frais si les prix payés étaient justes = 0 ; écart-type du gain = sqrt(sum (cost/p)^2 p (1-p))
sd = math.sqrt(sum((r["cost"] / r["p"]) ** 2 * r["p"] * (1 - r["p"]) for r in seen.values()))
print(f"\nmisé {stake:.0f} €, gain {pnl:+.0f} € ({pnl/stake:+.1%}), frais payés {tot_fees:.0f} € ({tot_fees/stake:.1%} de la mise), "
      f"gain hors frais {pnl+tot_fees:+.0f} € ({(pnl+tot_fees)/stake:+.1%}), écart-type du hasard ±{sd:.0f} €")
