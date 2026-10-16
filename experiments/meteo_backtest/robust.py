import json, sys, re
from collections import defaultdict
SP = sys.argv[1]; sys.path.insert(0, sys.argv[2])
from polymarket_agent import weather_model as wm
exec(open(f"{SP}/btcode/evaluate.py").read().split("best = None")[0].replace("print(", "(lambda *a, **k: None)("))
best = {"max": (1.5, 0.5), "min": (1.8, 0.0)}
f_model = lambda r: P(r, *best[r["q"].kind])
def fee(p): return 0.05 * p * (1 - p)
for spread in (0.01, 0.02, 0.04):
    agg = defaultdict(lambda: [0, 0.0, 0.0]); city = defaultdict(float)
    for r in test:
        pm = f_model(r); y = r["p"] + spread; no = 1 - r["p"] + spread
        if pm - y - fee(y) > 0.05: side, cost, g = "OUI", y, r["won"] - y - fee(y)
        elif (1 - pm) - no - fee(no) > 0.05: side, cost, g = "NON", no, (1 - r["won"]) - no - fee(no)
        else: continue
        b = f"{side} {'<0,2' if cost < 0.2 else '0,2-0,8' if cost < 0.8 else '>0,8'}"
        agg[b][0] += 1; agg[b][1] += g; agg[b][2] += cost
        city[re.sub(r"-on-.*", "", r["event"])] += g
    tot = sum(v[1] for v in agg.values()); st = sum(v[2] for v in agg.values())
    print(f"écart {spread:.2f} : total {tot:+.1f} pour {st:.1f} misés ({tot/st*100:+.1f} %)")
    for k, v in sorted(agg.items()): print(f"   {k:12} {v[0]:5} paris  {v[1]:+8.1f}  ({v[1]/v[2]*100:+.1f} %)")
    if spread == 0.02:
        neg = sorted(city.items(), key=lambda x: x[1])
        print("   villes : positives", sum(1 for _, v in neg if v > 0), "/", len(neg), "; pires", [(k, round(v, 1)) for k, v in neg[:4]])
