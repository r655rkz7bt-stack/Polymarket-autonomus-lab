import json, math, statistics as st, collections, sys
D = "donnees/mn"
rows = json.load(open(f"{D}/new.json"))
DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 2
from datetime import datetime
def ts(x): return datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp()
v = []
for r in rows:
    h = r.get("hist") or []
    if len(h) < 3: continue
    t = h[0]["t"] + DELAY * 3600
    if t > ts(r["closed"] or r["end"]) - 3600: continue
    p = [x for x in h if x["t"] <= t][-1]["p"]
    if 0.03 < p < 0.97: v.append((p, r["yes"], r["sp"], r["ev"]))
print("mots nouveaux avec prix", len(v), "prix moyen", round(st.mean(x[0] for x in v), 3), "OUI", round(st.mean(x[1] for x in v), 3))
for lo, hi in ((0, .15), (.15, .3), (.3, .5), (.5, .7), (.7, .85), (.85, 1)):
    w = [x for x in v if lo <= x[0] < hi]
    if not w: continue
    def ret(side):
        g = []
        for p, y, *_ in w:
            c = (p if side == 0 else 1 - p) + 0.02; win = y if side == 0 else not y
            g.append(((1 if win else 0) - c - 0.04 * c * (1 - c)) / c)
        return st.mean(g), st.mean(g) / st.stdev(g) * math.sqrt(len(g))
    a, b = ret(0), ret(1)
    print(f"prix {lo:.2f}-{hi:.2f}: n {len(w):4} prix {st.mean(x[0] for x in w):.3f} OUI {st.mean(x[1] for x in w):.3f} | OUI {a[0]:+.3f} (t {a[1]:+.2f}) | NON {b[0]:+.3f} (t {b[1]:+.2f})")
