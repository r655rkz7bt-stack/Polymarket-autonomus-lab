"""Mentions « the announcers » / « anyone » aux prix des VRAIS échanges (data-api).
Usage : analyse_echanges.py <delai_h> <marge> <K> <min_precedents> <fenetre_h> [--serie=...] [--det]
Décision : à partir de `delai_h` heures après l'ouverture, au premier échange réel de preneur sur le jeton
(prix payé par quelqu'un d'autre, +0,01 d'écart) dans la fenêtre. Taux historique = marchés de la même série
réglés AVANT cet échange. Aucun échange dans la fenêtre = pas de pari (pas de liquidité)."""
import bisect
import collections
import gzip
import json
import math
import re
import statistics as st
import sys
from datetime import datetime

sys.path.insert(0, "src")
from polymarket_agent import idea_test  # noqa: E402

A = [a for a in sys.argv[1:] if not a.startswith("--")]
DELAY, MARGIN, K, MINN, WIN = float(A[0]), float(A[1]), float(A[2]), int(A[3]), float(A[4])
ONLY = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--serie=")), None)
TITRE = next((a.split("=", 1)[1].lower() for a in sys.argv if a.startswith("--titre=")), None)  # sous-chaîne du titre
SANS = next((a.split("=", 1)[1].lower() for a in sys.argv if a.startswith("--sans=")), None)
DEPUIS = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--depuis=")), "")  # AAAA-MM-JJ : moitiés dans le temps
AVANT = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--avant=")), "9")
FEE, SPREAD = 0.04, 0.01
D = "donnees/mn"


def ts(x):
    return datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None


def series(r):
    t = r["title"].lower()
    if r["sp"] == "the announcers":
        if "world cup" in t:
            return "announcers:worldcup"
        return "announcers:match" if " game" in t else "announcers:autre"  # match = NFL / football américain (titre « … game »)
    for k in ("big brother", "love island", "rick and morty", "house of the dragon", "president curtis", "south park",
              "earnings call", "debate"):
        if k in t:
            return "anyone:" + k
    return "anyone:autre"


rows = json.load(open(f"{D}/annonceurs.json"))
ids = json.load(open(f"{D}/ids.json"))
other = {}
for e in json.load(open(f"{D}/events.json")):
    for m in e["markets"]:
        try:
            tk = json.loads(m["tok"] or "[]")
        except Exception:
            continue
        if len(tk) == 2:
            other[tk[0]] = tk[1]
cache = {}
for r in rows:
    r["c"], r["s"], r["k"] = ts(r["closed"] or r["end"]), series(r), re.sub(r"\s*/\s*", "/", r["w"].lower().strip())
    r["no"] = other.get(r["tok"])
    eid = ids.get(r["ev"])
    if eid not in cache:
        cache[eid] = json.load(gzip.open(f"{D}/echanges/echanges_{eid}.json.gz")) if eid else []
    r["tr"] = cache[eid]
byc = sorted(rows, key=lambda r: r["c"])
cl = [r["c"] for r in byc]
bets, ll_m, ll_q, nn = [], 0.0, 0.0, 0
for r in rows:
    if ONLY and r["s"] != ONLY or len(r["hist"]) < 3 or r["no"] is None:
        continue
    if TITRE and TITRE not in r["title"].lower() or SANS and SANS in r["title"].lower():
        continue
    if not DEPUIS <= r["end"][:10] < AVANT:
        continue
    t0 = r["hist"][0]["t"] + DELAY * 3600
    if t0 > r["c"] - 3600:
        continue
    mine = [t for t in r["tr"] if t[1] in (r["tok"], r["no"]) and t0 <= t[0] <= t0 + WIN * 3600]
    if not mine:
        continue
    t_dec = min(t[0] for t in mine)
    y_cost = idea_test.taker_cost(r["tr"], r["tok"], r["no"], t_dec - 1, window=WIN * 3600, after=True)
    n_cost = idea_test.taker_cost(r["tr"], r["no"], r["tok"], t_dec - 1, window=WIN * 3600, after=True)
    if y_cost is None or n_cost is None:
        continue
    j = bisect.bisect_left(cl, t_dec)
    prior = [x for x in byc[:j] if x["s"] == r["s"]]
    same = [x for x in prior if x["k"] == r["k"]]
    if len(same) < MINN:
        continue
    g = (sum(x["yes"] for x in prior) + 1) / (len(prior) + 2)
    q = (sum(x["yes"] for x in same) + K * g) / (len(same) + K)
    y = r["yes"]
    p = y_cost
    if 0.03 < p < 0.97:
        ll_m += math.log(p if y else 1 - p); ll_q += math.log(q if y else 1 - q); nn += 1
    for side, qq, cost0 in ((0, q, y_cost), (1, 1 - q, n_cost)):
        cost = cost0 + SPREAD
        if qq - MARGIN > cost and cost < 0.98:
            won = y if side == 0 else not y
            gain = ((1 if won else 0) - cost - FEE * cost * (1 - cost)) / cost
            bets.append({"gain": gain, "evenement": r["ev"], "mois": datetime.fromtimestamp(r["c"]).strftime("%Y-%m"),
                         "cout": cost, "s": r["s"], "side": side, "w": r["w"], "q": qq})


def summ(t, label):
    if len(t) < 3:
        print(f"{label}: {len(t)}"); return
    g = [x["gain"] for x in t]; m = st.mean(g)
    ev = collections.defaultdict(list)
    for x in t:
        ev[x["evenement"]].append(x["gain"])
    em = [st.mean(v) for v in ev.values()]
    te = st.mean(em) / st.stdev(em) * math.sqrt(len(em)) if len(em) > 2 and st.stdev(em) > 0 else 0
    print(f"{label}: {len(g)} achats / {len(em)} événements, rendement {m:+.3f}, t {m / st.stdev(g) * math.sqrt(len(g)):+.2f}, "
          f"par événement {st.mean(em):+.3f} t {te:+.2f}, gagnés {sum(x > 0 for x in g)}")


print(f"réglage délai {DELAY} h, marge {MARGIN}, K {K}, précédents >= {MINN}, fenêtre {WIN} h")
if nn:
    print(f"log-score aux prix payés : marché {ll_m / nn:.4f}  taux historique {ll_q / nn:.4f}  n {nn}")
summ(bets, "tous")
for s in sorted({x["s"] for x in bets}):
    summ([x for x in bets if x["s"] == s], f"  {s}")
summ([x for x in bets if x["side"] == 0], "  OUI"); summ([x for x in bets if x["side"] == 1], "  NON")
for lo, hi in ((0, .3), (.3, .7), (.7, 1)):
    summ([x for x in bets if lo <= x["cout"] < hi], f"  coût {lo}-{hi}")
if "--det" in sys.argv:
    print(json.dumps(idea_test.verdict(bets), ensure_ascii=False))
if "--mots" in sys.argv:
    byw = collections.defaultdict(list)
    for x in bets:
        byw[(x["w"], x["side"])].append(x["gain"])
    for (w, side), v in sorted(byw.items(), key=lambda kv: -len(kv[1]))[:25]:
        print(f"  {w:28s} {'OUI' if side == 0 else 'NON'} {len(v):3d} achats {st.mean(v):+.2f}")
