"""Après une tendance de 60 jours, les clôtures du Trésor continuent-elles (élan) ou reviennent-elles (retour) ? (16/11/2026, 21 h)
Tendance = (clôture − clôture d'il y a 60 jours ouvrés) / (σ60 × √60). Pour chaque tranche de tendance, fréquence des barrières touchées
DANS le sens de la tendance et CONTRE elle, rapportée à la loi empirique sans condition (même n, même z). 1990-2026, chaque 3e jour."""
import math, os, sys
from bisect import bisect_left
sys.path.insert(0, os.path.dirname(__file__))
import etalonnage_historique as eh

NS, ZS = (10, 20, 30), (1.0, 1.5, 2.0, 3.0)   # z = écart / σ60 (pas × √n : barrières des marchés, en σ60)
rows = []
for ten in eh.COL:
    v = [eh.par[d][ten] for d in eh.days if ten in eh.par[d]]
    yrs = [d.year for d in eh.days if ten in eh.par[d]]
    for i in range(121, len(v) - max(NS), 3):
        ch = [v[j] - v[j - 1] for j in range(i - 59, i + 1)]
        sd = math.sqrt(sum(c * c for c in ch) / 60)
        if sd <= 0:
            continue
        tr = (v[i] - v[i - 60]) / (sd * math.sqrt(60))
        for n in NS:
            fut = v[i + 1:i + 1 + n]
            up, dn = (max(fut) - v[i]) / sd, (v[i] - min(fut)) / sd
            sens, contre = (up, dn) if tr >= 0 else (dn, up)
            rows.append((abs(tr), n, sens, contre, yrs[i]))
print(len(rows), "observations")
TR = [(0, 0.5), (0.5, 1.0), (1.0, 1.5), (1.5, 9)]
for n in NS:
    base = [r for r in rows if r[1] == n]
    for z in ZS:
        p0 = sum((r[2] >= z) + (r[3] >= z) for r in base) / (2 * len(base))
        out = []
        for a, b in TR:
            g = [r for r in base if a <= r[0] < b]
            out.append(f"|tend| {a}-{b}: sens {sum(r[2] >= z for r in g)/len(g):.3f} contre {sum(r[3] >= z for r in g)/len(g):.3f} (n {len(g)})")
        print(f"n={n} z={z} sans condition {p0:.3f} :: " + " ; ".join(out))
print("\n2010-2026 seulement, n=20")
base = [r for r in rows if r[1] == 20 and r[4] >= 2010]
for z in ZS:
    out = []
    for a, b in TR:
        g = [r for r in base if a <= r[0] < b]
        out.append(f"{a}-{b}: sens {sum(r[2] >= z for r in g)/len(g):.3f} contre {sum(r[3] >= z for r in g)/len(g):.3f}")
    print(f"z={z} :: " + " ; ".join(out))
