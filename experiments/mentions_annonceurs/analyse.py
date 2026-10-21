"""Test sur le passé des mentions « the announcers » et « anyone » (donnees/mn/annonceurs.json).
Usage : analyse.py <delai_h> <marge> <K> <min_precedents> [prix_min]
Sans regard vers le futur : prix lu `delai_h` heures après le premier point de l'historique, taux
historique calculé seulement avec les marchés de la même série réglés AVANT cet instant."""
import bisect
import collections
import json
import math
import re
import statistics as st
import sys
from datetime import datetime

DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 2
MARGIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.05
K = float(sys.argv[3]) if len(sys.argv) > 3 else 2
MINN = int(sys.argv[4]) if len(sys.argv) > 4 else 3
MINP = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
FEE, SPREAD = 0.04, 0.02  # barème utilisé le 20/10 pour les mentions (à relire sur feeSchedule)


def ts(x):
    return datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None


def series(r):
    t = r["title"].lower()
    if r["sp"] == "the announcers":
        return "announcers:worldcup" if "world cup" in t else "announcers:autre"
    for k in ("big brother", "love island", "rick and morty", "house of the dragon", "president curtis", "south park",
              "earnings call", "debate"):
        if k in t:
            return "anyone:" + k
    return "anyone:autre"


def norm(w):
    return re.sub(r"\s*/\s*", "/", w.lower().strip())


rows = json.load(open("donnees/mn/annonceurs.json"))
for r in rows:
    r["c"] = ts(r["closed"] or r["end"])
    r["s"] = series(r)
    r["k"] = norm(r["w"])
    h = r["hist"]
    r["tref"] = h[0]["t"] + DELAY * 3600 if len(h) >= 3 else None
byc = sorted(rows, key=lambda r: r["c"])
cl = [r["c"] for r in byc]
trades, ll_m, ll_q, n = [], 0.0, 0.0, 0
cal = collections.defaultdict(list)
for r in rows:
    if r["tref"] is None or r["tref"] > r["c"] - 3600:
        continue
    pts = [x for x in r["hist"] if x["t"] <= r["tref"]]
    p = pts[-1]["p"]
    if not 0.03 < p < 0.97:
        continue
    j = bisect.bisect_left(cl, r["tref"])
    prior = [x for x in byc[:j] if x["s"] == r["s"]]
    same = [x for x in prior if x["k"] == r["k"]]
    y = r["yes"]
    cal[(r["s"], min(int(p * 5), 4))].append((p, y))
    if len(same) < MINN:
        continue
    g = (sum(x["yes"] for x in prior) + 1) / (len(prior) + 2)
    q = (sum(x["yes"] for x in same) + K * g) / (len(same) + K)
    ll_m += math.log(p if y else 1 - p); ll_q += math.log(q if y else 1 - q); n += 1
    for side, qq, cost in ((0, q, p + SPREAD), (1, 1 - q, 1 - p + SPREAD)):
        if qq - MARGIN > cost and MINP <= cost < 0.98:
            won = y if side == 0 else not y
            fee = FEE * cost * (1 - cost)
            trades.append((r["s"], r["w"], side, cost, qq, ((1 if won else 0) - cost - fee) / cost, r["ev"], r["c"]))


def summ(t, label):
    if len(t) < 3:
        print(f"{label}: {len(t)}"); return
    g = [x[5] for x in t]; m = st.mean(g)
    print(f"{label}: {len(g)} achats, rendement {m:+.3f}, t {m / st.stdev(g) * math.sqrt(len(g)):+.2f}, gagnés {sum(x > 0 for x in g)}")


print(f"réglage délai {DELAY} h, marge {MARGIN}, K {K}, précédents >= {MINN}, prix >= {MINP}")
if n:
    print(f"log-score : marché {ll_m / n:.4f}  taux historique {ll_q / n:.4f}  n {n}")
summ(trades, "tous")
for s in sorted({x[0] for x in trades}):
    summ([x for x in trades if x[0] == s], f"  {s}")
summ([x for x in trades if x[2] == 0], "  OUI")
summ([x for x in trades if x[2] == 1], "  NON")
summ([x for x in trades if x[3] < 0.3], "  prix < 0,30")
summ([x for x in trades if x[3] >= 0.3], "  prix >= 0,30")
ev = collections.defaultdict(list)
for x in trades:
    ev[x[6]].append(x[5])
summ([(0, 0, 0, 0, 0, st.mean(v)) for v in ev.values()], "moyenne par événement")
if "--cal" in sys.argv:
    print("calibrage : série, tranche de prix, n, prix moyen, OUI réalisé")
    for (s, b), v in sorted(cal.items()):
        print(f"  {s:24s} {b / 5:.1f}-{(b + 1) / 5:.1f}  {len(v):4d}  {st.mean(x[0] for x in v):.3f}  {st.mean(x[1] for x in v):.3f}")
