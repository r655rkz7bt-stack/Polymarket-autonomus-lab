"""Suite d'etalonnage_historique.py : modèle EMPIRIQUE (part des trajectoires passées, divisées par leur σ60, dont l'excursion maximale
dépasse z = b / σ60 en n jours ouvrés) appris sur 1990-2015, jugé sur 2016-2026 contre la marche gaussienne K = 1,0 / 1,15 / 1,3."""
import math, os, sys
from bisect import bisect_left
sys.path.insert(0, os.path.dirname(__file__))
import etalonnage_historique as eh   # recharge les données et les observations (chaque 5e jour)

NMAX = 30
norm = {n: [] for n in range(1, NMAX + 1)}   # excursions max normalisées, haut et bas mélangés, apprises avant 2016
for ten in eh.COL:
    s = [(d, eh.par[d][ten]) for d in eh.days if ten in eh.par[d]]
    v = [x for _, x in s]
    for i in range(61, len(v) - NMAX):
        if s[i + NMAX][0].year > 2015:
            break
        ch = [v[j] - v[j - 1] for j in range(i - 59, i + 1)]
        sd = math.sqrt(sum(c * c for c in ch) / 60)
        if sd <= 0:
            continue
        hi = lo = 0.0
        for n in range(1, NMAX + 1):
            mv = v[i + n] - v[i]
            hi, lo = max(hi, mv), min(lo, mv)
            norm[n].append(hi / sd); norm[n].append(-lo / sd)
for n in norm:
    norm[n].sort()


def p_emp(b, sd, n):
    xs = norm[n]
    return (len(xs) - bisect_left(xs, b / sd - 1e-9) + 0.5) / (len(xs) + 1)


test = [r for r in eh.obs if r[0] >= 2016]
def score(f):
    t = 0.0
    for r in test:
        p = min(max(f(r), 0.005), 0.995)
        t += math.log(p if r[5] else 1 - p)
    return t / len(test)
print("2016-2026 :", len(test), "observations")
print("empirique (appris 1990-2015)", f"{score(lambda r: p_emp(r[7], r[6], r[2])):+.4f}")
for k in (1.0, 1.15, 1.3):
    print(f"gauss K={k}", f"{score(lambda r: eh.p_hit(r[7], k * r[6], r[2])):+.4f}")
for n in eh.NS:
    print(f"n={n}", " | ".join(
        f"z{z}: obs {sum(r[5] for r in test if r[2]==n and r[3]==z)/max(1,sum(1 for r in test if r[2]==n and r[3]==z)):.3f}"
        f" emp {sum(p_emp(r[7], r[6], n) for r in test if r[2]==n and r[3]==z)/max(1,sum(1 for r in test if r[2]==n and r[3]==z)):.3f}"
        for z in eh.ZS))
