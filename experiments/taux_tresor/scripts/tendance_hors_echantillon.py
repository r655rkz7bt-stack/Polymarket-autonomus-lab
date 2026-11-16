"""Modèle conditionnel à la tendance de 60 jours, appris 1990-2015, jugé 2016-2026 (16/11/2026, 21 h). Tranches fixées AVANT le test
(|tendance| 0-0,5 / 0,5-1 / 1-1,5 / ≥ 1,5, sens et contre) ; comparé à la loi empirique sans condition apprise sur la même période.
Barrières des marchés : écart en σ60 (pas × √n), z = 0,5 à 4 par 0,5, n = 5, 10, 20, 30 ; chaque 2e jour ouvré."""
import math, os, sys
from bisect import bisect_left
sys.path.insert(0, os.path.dirname(__file__))
import etalonnage_historique as eh

NS, ZS = (5, 10, 20, 30), tuple(x / 2 for x in range(1, 9))
TR = (0.5, 1.0, 1.5)
def tranche(t): return sum(abs(t) >= x for x in TR)
learn = {}   # (n, tranche, sens?) -> sorted excursions
learn0 = {n: [] for n in NS}
obs = []
for ten in eh.COL:
    dd = [d for d in eh.days if ten in eh.par[d]]
    v = [eh.par[d][ten] for d in dd]
    for i in range(121, len(v) - max(NS), 2):
        ch = [v[j] - v[j - 1] for j in range(i - 59, i + 1)]
        sd = math.sqrt(sum(c * c for c in ch) / 60)
        if sd <= 0:
            continue
        tr = (v[i] - v[i - 60]) / (sd * math.sqrt(60))
        for n in NS:
            fut = v[i + 1:i + 1 + n]
            up, dn = (max(fut) - v[i]) / sd, (v[i] - min(fut)) / sd
            sens, contre = (up, dn) if tr >= 0 else (dn, up)
            if dd[i + n].year <= 2015:
                learn.setdefault((n, tranche(tr), True), []).append(sens)
                learn.setdefault((n, tranche(tr), False), []).append(contre)
                learn0[n] += [up, dn]
            elif dd[i].year >= 2016:
                obs.append((n, tranche(tr), sens, contre))
for k in learn: learn[k].sort()
for n in learn0: learn0[n].sort()
def S(xs, z): return (len(xs) - bisect_left(xs, z - 1e-12) + 0.5) / (len(xs) + 1)
tot = {"sans condition": 0.0, "tendance": 0.0}; m = 0
for n, t, s_, c_ in obs:
    for z in ZS:
        for val, sens in ((s_, True), (c_, False)):
            hit = val >= z
            for nom, p in (("sans condition", S(learn0[n], z)), ("tendance", S(learn[(n, t, sens)], z))):
                p = min(max(p, 0.005), 0.995)
                tot[nom] += math.log(p if hit else 1 - p)
            m += 1
print(len(obs), "points de décision 2016-2026,", m, "barrières")
for k, v in tot.items():
    print(k, f"{v / m:+.4f}")
# seulement les fortes tendances (|t| ≥ 1)
for lim in (1, 2, 3):
    tt = {"sans condition": 0.0, "tendance": 0.0}; mm = 0
    for n, t, s_, c_ in obs:
        if t < lim: continue
        for z in ZS:
            for val, sens in ((s_, True), (c_, False)):
                hit = val >= z
                for nom, p in (("sans condition", S(learn0[n], z)), ("tendance", S(learn[(n, t, sens)], z))):
                    p = min(max(p, 0.005), 0.995); tt[nom] += math.log(p if hit else 1 - p)
                mm += 1
    print(f"tranche ≥ {lim}:", {k: round(v / mm, 4) for k, v in tt.items()}, mm)
