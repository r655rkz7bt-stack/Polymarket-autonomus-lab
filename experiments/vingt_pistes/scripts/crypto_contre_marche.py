import bisect, json, math, sys, statistics as st
from datetime import datetime, timedelta
D = "donnees/cr"
data = json.load(open(f"{D}/data.json"))
MARGIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.03
VOLH = int(sys.argv[2]) if len(sys.argv) > 2 else 168
TAIL = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0  # multiplie la vol (queues épaisses)
Phi = lambda z: 0.5 * (1 + math.erf(z / math.sqrt(2)))
K = {a: (([r[0] for r in rows]), rows) for a, rows in data["klines"].items()}
ll_m = ll_q = 0.0; n = 0; trades = []
for e in data["events"]:
    if e["s0"] is None or e["s1"] is None or not e["hist"]: continue
    res = json.loads(e["prix_final"] or "[]")
    if res not in (["1", "0"], ["0", "1"]): continue
    up = res == ["1", "0"]
    if up != (e["s1"] > e["s0"]):  # contrôle : notre lecture de Binance donne le même règlement
        print("  écart", e["slug"], e["s0"], e["s1"], res); continue
    ts_k, rows = K[e["actif"]]
    start = datetime.fromisoformat(e["debut"]); end = datetime.fromisoformat(e["fin"])
    ht = [x["t"] for x in e["hist"]]; hp = [x["p"] for x in e["hist"]]
    for h in range(1, 24):
        t = start + timedelta(hours=h)
        ms = int(t.timestamp() * 1000)
        i = bisect.bisect_left(ts_k, ms)
        if i >= len(rows) or rows[i][0] != ms or i < VOLH + 1: continue
        S = rows[i][1]
        closes = [r[2] for r in rows[i - VOLH - 1:i]]
        rets = [math.log(closes[k + 1] / closes[k]) for k in range(len(closes) - 1)]
        sig = st.pstdev(rets) * TAIL
        tau = 24 - h
        q = Phi(math.log(S / e["s0"]) / (sig * math.sqrt(tau)))
        j = bisect.bisect_right(ht, t.timestamp()) - 1
        if j < 0 or t.timestamp() - ht[j] > 1800: continue
        p = hp[j]
        if not 0.02 < p < 0.98: continue
        ll_m += math.log(p if up else 1 - p); ll_q += math.log(max(min(q if up else 1 - q, 1 - 1e-4), 1e-4)); n += 1
        for side, qq, cost in ((0, q, p + 0.01), (1, 1 - q, 1 - p + 0.01)):
            if qq - MARGIN > cost and cost < 0.99:
                fee = 0.07 * cost * (1 - cost)
                won = up if side == 0 else not up
                trades.append((e["actif"], e["slug"], h, side, cost, qq, ((1 if won else 0) - cost - fee) / cost))
print(f"log-score : marché {ll_m / n:.4f}  modèle {ll_q / n:.4f}  n {n}")
def summ(rows, label):
    if len(rows) < 2: print(label, len(rows)); return
    g = [r[-1] for r in rows]; m, s = st.mean(g), st.stdev(g)
    print(f"{label}: {len(g)} achats, rendement {m:+.3f}, t {m / s * math.sqrt(len(g)):+.2f}")
summ(trades, "tous")
for a in K: summ([r for r in trades if r[0] == a], "  " + a)
for lo, hi in ((1, 8), (8, 16), (16, 24)): summ([r for r in trades if lo <= r[2] < hi], f"  heures {lo}-{hi}")
seen, first = set(), []
for r in trades:
    if r[1] not in seen: seen.add(r[1]); first.append(r)
summ(first, "un achat par jour et actif")
