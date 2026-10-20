import json, math, statistics as st, sys
from collections import defaultdict
sys.argv = ["x", "0.01"]
exec(open("experiments/achat_echelonne/univers_moment_et_baisse.py").read().split("# 1. Moment")[0])
FAM = {"itf": "tennis", "atp": "tennis", "wta": "tennis", "cs2": "esport", "lol": "esport", "dota2": "esport", "val": "esport", "r6siege": "esport"}
for spread_label, sp in (("preneur (+1 ct)", 0.01), ("ordre posé (−1 ct, sans frais)", -0.01)):
    fam = defaultdict(lambda: defaultdict(list))
    for x in games:
        q = at(x["path"], x["start"] - 3600)
        if q is None or not 0.70 <= q <= 0.95: continue
        c = q + sp
        if sp > 0: c += x["rate"] * c * (1 - c)
        g = ((1 if x["won"] else 0) - c) / c
        f = FAM.get(x["sport"], "autres")
        fam[f]["all"].append((g, q, x["won"])); fam[f][x["week"]].append(g)
    for f, v in sorted(fam.items()):
        a = v.pop("all"); g = [y[0] for y in a]
        print(f"{spread_label:30} {f:7} {len(a):4} favoris 1 h avant : prix {st.mean(y[1] for y in a):.3f} gagnés {st.mean(y[2] for y in a):.3f} "
              f"rendement {st.mean(g):+.3f} t {t_of(g):+.2f} | " + " ".join(f"{w[-3:]}:{st.mean(x):+.2f}" for w, x in sorted(v.items())))
