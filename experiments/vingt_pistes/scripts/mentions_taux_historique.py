import json, math, sys, statistics as st, collections
from datetime import datetime
D = "donnees/mn"
d = json.load(open(f"{D}/data.json"))
MARGIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
K = float(sys.argv[2]) if len(sys.argv) > 2 else 2
MINN = int(sys.argv[3]) if len(sys.argv) > 3 else 3
DELAY = float(sys.argv[4]) if len(sys.argv) > 4 else 2
MINP = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
NOQUOTE = len(sys.argv) > 6 and sys.argv[6] == "1"
def ts(x): return datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None
rows = [r for r in d["rows"] if ts(r["closed"] or r["end"])]
for r in rows: r["c"] = ts(r["closed"] or r["end"])
rows.sort(key=lambda r: r["c"])
cl = [r["c"] for r in rows]
import bisect
ll_m = ll_q = 0; n = 0; trades = []
for r in d["todo"]:
    h = r.get("hist") or []
    if len(h) < 3: continue
    t_ref = h[0]["t"] + DELAY * 3600
    if t_ref > ts(r["closed"] or r["end"]) - 3600: continue
    pts = [x for x in h if x["t"] <= t_ref]
    p = pts[-1]["p"]
    if not 0.03 < p < 0.97: continue
    j = bisect.bisect_left(cl, t_ref)
    prior = [x for x in rows[:j] if x["sp"] == r["sp"]]
    same = [x for x in prior if x["w"] == r["w"]]
    if len(same) < MINN or (NOQUOTE and r["sp"].startswith('"')): continue
    g = (sum(x["yes"] for x in prior) + 1) / (len(prior) + 2)
    q = (sum(x["yes"] for x in same) + K * g) / (len(same) + K)
    y = r["yes"]
    ll_m += math.log(p if y else 1 - p); ll_q += math.log(q if y else 1 - q); n += 1
    for side, qq, cost in ((0, q, p + 0.02), (1, 1 - q, 1 - p + 0.02)):
        if qq - MARGIN > cost and MINP <= cost < 0.98:
            won = y if side == 0 else not y
            fee = 0.04 * cost * (1 - cost)
            trades.append((r["sp"], r["w"], side, cost, qq, ((1 if won else 0) - cost - fee) / cost, r["ev"]))
print(f"log-score : marché {ll_m / n:.4f}  taux historique {ll_q / n:.4f}  n {n}")
def summ(t, label):
    if len(t) < 2: print(label, len(t)); return
    g = [x[5] for x in t]; m = st.mean(g)
    print(f"{label}: {len(g)} achats, rendement {m:+.3f}, t {m / st.stdev(g) * math.sqrt(len(g)):+.2f}, gagnés {sum(x > 0 for x in g)}")
summ(trades, "tous")
summ([x for x in trades if x[2] == 0], "  OUI")
summ([x for x in trades if x[2] == 1], "  NON")
summ([x for x in trades if x[3] < 0.3], "  prix < 0,30")
summ([x for x in trades if x[3] >= 0.3], "  prix >= 0,30")
c = collections.Counter(x[0] for x in trades)
for sp, k in c.most_common(6): summ([x for x in trades if x[0] == sp], f"  {sp}")
# par événement (corrélation) : moyenne par événement
ev = collections.defaultdict(list)
for x in trades: ev[x[6]].append(x[5])
summ([(0, 0, 0, 0, 0, st.mean(v)) for v in ev.values()], "moyenne par événement")
