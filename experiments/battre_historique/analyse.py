"""Piste n° 61 : historique de « beat » par société (marchés Polymarket réglés AVANT la décision) contre le prix à T-d jours."""
import json, math, sys
from collections import defaultdict
from datetime import datetime
rows = json.load(open("experiments/battre_historique/donnees/marches.json"))
def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
for r in rows: r["tc"] = ts(r["closed"]) if r.get("closed") else ts(r["end"])
by = defaultdict(list)
for r in rows: by[r["ticker"]].append(r)
D = int(sys.argv[1]) if len(sys.argv) > 1 else 1
BASE = 0.744
def ll(p, y): p = min(max(p, 1e-3), 1 - 1e-3); return math.log(p if y else 1 - p)
cas = []
for r in rows:
    p = r.get(f"p{D}")
    if p is None or not 0.02 <= p <= 0.98: continue
    t0 = r["tc"] - D * 86400
    prev = [x for x in by[r["ticker"]] if x["tc"] < t0 - 86400 and x["eid"] != r["eid"]]   # réglés au moins 1 j avant la décision
    n, b = len(prev), sum(x["won"] for x in prev)
    cas.append(dict(r=r, p=p, n=n, b=b, y=r["won"], mois=datetime.utcfromtimestamp(r["tc"]).strftime("%Y-%m")))
print(f"T-{D} j : {len(cas)} marchés ; avec ≥ 1 trimestre passé : {sum(c['n'] >= 1 for c in cas)}, ≥ 2 : {sum(c['n'] >= 2 for c in cas)}, ≥ 3 : {sum(c['n'] >= 3 for c in cas)}")
# 1) gagnés contre attendus par historique
print("\nhistorique                     marchés  OUI réalisés  prix moyen  écart")
groupes = {"aucun passé": lambda c: c["n"] == 0, "toujours battu (n≥2)": lambda c: c["n"] >= 2 and c["b"] == c["n"],
           "toujours battu (n≥3)": lambda c: c["n"] >= 3 and c["b"] == c["n"], "1 raté (n≥2)": lambda c: c["n"] >= 2 and c["n"] - c["b"] == 1,
           "≥ 2 ratés": lambda c: c["n"] - c["b"] >= 2, "raté le dernier": None, "battu le dernier": None}
for k, f in groupes.items():
    if f is None: continue
    g = [c for c in cas if f(c)]
    if g:
        y = sum(c["y"] for c in g); e = sum(c["p"] for c in g); v = sum(c["p"] * (1 - c["p"]) for c in g)
        print(f"{k:28s} {len(g):7d} {y:13d} {e/len(g):11.3f} {(y-e)/len(g):+.3f}  z {(y-e)/math.sqrt(v):+.2f}")
def dernier(c):
    prev = sorted((x for x in by[c["r"]["ticker"]] if x["tc"] < c["r"]["tc"] - D * 86400 - 86400), key=lambda x: x["tc"])
    return prev[-1]["won"] if prev else None
for lab, val in (("raté le dernier", 0), ("battu le dernier", 1)):
    g = [c for c in cas if dernier(c) == val]
    y = sum(c["y"] for c in g); e = sum(c["p"] for c in g); v = sum(c["p"] * (1 - c["p"]) for c in g)
    print(f"{lab:28s} {len(g):7d} {y:13d} {e/len(g):11.3f} {(y-e)/len(g):+.3f}  z {(y-e)/math.sqrt(v):+.2f}")
# 2) par tranche de prix et historique (n≥2)
print("\npar tranche de prix (n ≥ 2) : toujours battu / au moins un raté")
for lo, hi in ((0.02, 0.5), (0.5, 0.7), (0.7, 0.85), (0.85, 0.93), (0.93, 0.98)):
    out = []
    for f in (lambda c: c["b"] == c["n"], lambda c: c["b"] < c["n"]):
        g = [c for c in cas if c["n"] >= 2 and lo <= c["p"] < hi and f(c)]
        y = sum(c["y"] for c in g); e = sum(c["p"] for c in g)
        out.append(f"{len(g):4d} : {y:4d} pour {e:6.1f}")
    print(f"  {lo:.2f}-{hi:.2f}  " + "   |   ".join(out))
# 3) log-score : prix contre prix + correction par l'historique (coefficient ajusté sur la 1re moitié du temps, jugé sur la 2e)
cas.sort(key=lambda c: c["r"]["tc"])
h = len(cas) // 2
def lg(p): p = min(max(p, 1e-3), 1 - 1e-3); return math.log(p / (1 - p))
def sg(x): return 1 / (1 + math.exp(-x))
def feat(c, a=3): return lg((c["b"] + a * BASE) / (c["n"] + a)) - lg(BASE)
best = None
for k in [i / 10 for i in range(-10, 21)]:
    s = sum(ll(sg(lg(c["p"]) + k * feat(c)), c["y"]) for c in cas[:h])
    if best is None or s > best[1]: best = (k, s)
k = best[0]
lp = sum(ll(c["p"], c["y"]) for c in cas[h:]) / (len(cas) - h)
lm = sum(ll(sg(lg(c["p"]) + k * feat(c)), c["y"]) for c in cas[h:]) / (len(cas) - h)
print(f"\nlog-score, 2e moitié ({len(cas)-h} marchés, coefficient {k} appris sur la 1re) : prix {lp:.4f}, prix + historique {lm:.4f}")
json.dump([dict(eid=c["r"]["eid"], ticker=c["r"]["ticker"], p=c["p"], n=c["n"], b=c["b"], y=c["y"], mois=c["mois"], fee=c["r"].get("fee"), cond=c["r"]["cond"], yes=c["r"]["yes"], tc=c["r"]["tc"]) for c in cas],
          open(f"experiments/battre_historique/donnees/cas_T{D}.json", "w"))
