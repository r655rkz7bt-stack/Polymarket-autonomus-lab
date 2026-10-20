"""Modèle du compteur de tweets contre le prix du marché, sur les périodes passées."""
import bisect, json, math, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "src")
from polymarket_agent import references as refs
D = "donnees/xt"
ev = json.load(open(sys.argv[1] if len(sys.argv) > 1 else f"{D}/marches.json"))
DISP, R, W = float(sys.argv[2]) if len(sys.argv) > 2 else 8, 168, 0.5
MARGIN = float(sys.argv[3]) if len(sys.argv) > 3 else 0.03
MINP = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
posts = {}
def P(h):
    if h not in posts:
        posts[h] = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")) for t in json.load(open(f"{D}/{h}.json")))
    return posts[h]
def count(h, a, b):
    ts = P(h); return bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)
def tracking(h, start, end, t):
    hour = t.replace(minute=0, second=0, microsecond=0)
    hourly = [count(h, hour - timedelta(hours=k + 1), hour - timedelta(hours=k)) for k in range(335, -1, -1)]
    return {"debut": start.isoformat(), "fin": end.isoformat(), "total": count(h, start, t), "vu_le": t.isoformat(), "heures": hourly}
res = {"mk": 0.0, "mo": 0.0, "n": 0}
trades = []
per = {}
for e in ev:
    h = e["compte"]; start = datetime.fromisoformat(e["debut"]); end = datetime.fromisoformat(e["fin"]) - timedelta(seconds=1)
    if P(h)[0] > start - timedelta(days=14):
        continue
    final = count(h, start, end + timedelta(seconds=1))
    bks = []
    for m in e["marches"]:
        b = refs.bucket_of(m["titre"] or "")
        if b and m["hist"]:
            bks.append((b, [x["t"] for x in m["hist"]], [x["p"] for x in m["hist"]], m["prix_final"]))
    if not bks: continue
    win = [b for b in bks if b[0][0] <= final <= b[0][1]]
    paid = [b for b in bks if json.loads(b[3] or "[0]")[0] in ("1", 1)]
    if len(win) != 1 or (paid and paid[0][0] != win[0][0]):
        print("  écart règlement", h, e["slug"], final, [p[0] for p in paid]); continue
    t = start + timedelta(hours=6)
    while t < end - timedelta(hours=3):
        ts = t.timestamp()
        prices = []
        for b, tt, pp, _ in bks:
            i = bisect.bisect_right(tt, ts) - 1
            prices.append(pp[i] if i >= 0 and ts - tt[i] < 6 * 3600 else None)
        if all(p is not None for p in prices) and sum(prices) > 0.5:
            tr = tracking(h, start, end, t)
            tot = sum(prices)
            for (b, *_), p in zip(bks, prices):
                q = refs.tweet_bucket_probability(tr, b, t, DISP, R, 336, W)
                won = b[0] <= final <= b[1]
                if won:
                    res["mk"] += math.log(max(p / tot, 1e-3)); res["mo"] += math.log(max(q, 1e-3)); res["n"] += 1
                    k = per.setdefault(h, [0, 0, 0]); k[0] += math.log(max(p / tot, 1e-3)); k[1] += math.log(max(q, 1e-3)); k[2] += 1
                spread = 0.01 if h == "elonmusk" else 0.02
                for side, qq, cost in ((0, q, p + spread), (1, 1 - q, 1 - p + spread)):
                    if max(0.01, MINP) <= cost < 0.99 and qq - MARGIN > cost:
                        fee = 0.05 * cost * (1 - cost)
                        gain = ((1.0 if (won if side == 0 else not won) else 0.0) - cost - fee) / cost
                        trades.append((h, e["slug"], t.isoformat()[:13], b, side, round(cost, 3), round(qq, 3), gain))
        t += timedelta(hours=6)
print(f"log-score par prévision : marché {res['mk'] / res['n']:.3f}  modèle {res['mo'] / res['n']:.3f}  (n {res['n']})")
for h, k in per.items():
    print(f"  {h:16} marché {k[0] / k[2]:.3f} modèle {k[1] / k[2]:.3f} n {k[2]}")
import statistics as st
def summ(rows, label):
    if len(rows) < 2: print(label, len(rows)); return
    g = [r[-1] for r in rows]
    m, s = st.mean(g), st.stdev(g)
    print(f"{label}: {len(g)} achats, rendement moyen {m:+.3f}, t {m / s * math.sqrt(len(g)):+.2f}, gagnés {sum(x > 0 for x in g)}")
summ(trades, "tous")
summ([r for r in trades if r[4] == 0], "  OUI (tranche)")
summ([r for r in trades if r[4] == 1], "  NON")
summ([r for r in trades if r[5] < 0.1], "  prix < 0,10")
summ([r for r in trades if r[5] >= 0.1], "  prix >= 0,10")
for h in per: summ([r for r in trades if r[0] == h], f"  {h}")
# un achat par (période, tranche, côté) : le premier signal seulement (pas de répétitions corrélées)
seen, first = set(), []
for r in trades:
    k = (r[1], r[3], r[4])
    if k not in seen: seen.add(k); first.append(r)
summ(first, "premier signal par tranche")

import collections
ev = collections.defaultdict(list)
for r in trades: ev[r[1]].append(r[-1])
g = [st.mean(v) for v in ev.values()]
print(f"moyenne par période : {len(g)} périodes, {st.mean(g):+.3f}, t {st.mean(g) / st.stdev(g) * math.sqrt(len(g)):+.2f}, périodes gagnantes {sum(x > 0 for x in g)}")
mo = collections.defaultdict(list)
for r in trades: mo[r[2][:7]].append(r[-1])
print("par mois :", {k: round(st.mean(v), 3) for k, v in sorted(mo.items())})
