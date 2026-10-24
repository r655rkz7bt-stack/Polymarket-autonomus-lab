"""Découpages des paris du test (donnees/paris.json de backtest.py, ou deux fichiers passés en arguments) : par matière, côté, prix, mois ; sans les 3 meilleurs paris."""
import collections, json, math, sys
b = []
for f in sys.argv[1:]:
    b += json.load(open(f))
def stat(bs, label):
    if len(bs) < 3:
        print(f"{label:30s} vide({len(bs)})"); return
    ev = collections.defaultdict(list)
    for x in bs: ev[x["evenement"]].append(x["gain"])
    em = [sum(v) / len(v) for v in ev.values()]
    m = sum(em) / len(em); sd = (sum((x - m) ** 2 for x in em) / max(1, len(em) - 1)) ** .5
    t = m / (sd / math.sqrt(len(em))) if sd > 0 else 0
    costs = [x["cout"] for x in bs]; wins = sum(1 for x in bs if x["gain"] > 0)
    z = (wins - sum(costs)) / math.sqrt(sum(c * (1 - c) for c in costs))
    g = sorted((x["gain"] for x in bs), reverse=True)
    print(f"{label:30s} paris {len(bs):3d} évén. {len(ev):2d} rend {sum(g)/len(g):+.3f} sans3meilleurs {sum(g[3:])/max(1,len(g)-3):+.3f} par-évén {m:+.3f} t {t:+.2f} gagnés {wins}/{sum(costs):.1f} z {z:+.2f}")
for seuil in (0.05, 0.10, 0.20):
    s = [x for x in b if x["seuil"] == seuil]; print("--- seuil", seuil); stat(s, "tous")
    for tk in sorted({x["tk"] for x in b}): stat([x for x in s if x["tk"] == tk], "  " + tk)
    for c in ("OUI", "NON"): stat([x for x in s if x["cote"] == c], "  " + c)
    for lo, hi in ((0, .15), (.15, .4), (.4, .7), (.7, 1)): stat([x for x in s if lo <= x["cout"] < hi], f"  prix {lo}-{hi}")
    ms = collections.defaultdict(list)
    for x in s: ms[x["mois"]].append(x)
    for k in sorted(ms): stat(ms[k], "  mois " + k)
