"""Étalonnage historique du module en production (16/11/2026, passage de 21 h) : la marche aléatoire × K (σ = écart-type des 60
dernières variations quotidiennes) redonne-t-elle la VRAIE fréquence des barrières touchées sur 1990-2026 ?

Chaque 5e jour ouvré (moins de dépendance entre observations), chaque durée (2, 5, 10, 30 ans), horizons n = 5, 10, 20, 30 jours
ouvrés, barrières à z × σ60 × √n au-dessus et au-dessous de la dernière clôture (z = 0,5 à 2,5) ; « touchée » = une clôture des n
jours suivants ≥ (ou ≤) la barrière. Chance du modèle : formule fermée de la barrière discrète (correction de Broadie-Glasserman,
comme trajectoires.py) avec σ = K × σ60. Sortie : fréquence observée contre chance prévue par z, log-score par K et par période.
Données : experiments/taux_tresor/donnees/par_<année>.csv (CSV du Trésor, robots.txt : tout permis)."""
import csv, glob, math, os
from datetime import datetime

D = os.path.join(os.path.dirname(__file__), "..", "donnees")
COL = {2: "2 Yr", 5: "5 Yr", 10: "10 Yr", 30: "30 Yr"}
par = {}
for f in glob.glob(os.path.join(D, "par_*.csv")):
    for r in csv.DictReader(open(f)):
        try:
            d = datetime.strptime(r["Date"], "%m/%d/%Y").date()
        except (KeyError, ValueError):
            continue
        par[d] = {k: float(r[v]) for k, v in COL.items() if r.get(v) not in (None, "", "N/A")}
days = sorted(par)
PHI = lambda x: 0.5 * (1 + math.erf(x / math.sqrt(2)))
BETA = 0.5826


def p_hit(b, s, n):
    """Chance qu'une marche gaussienne d'écart-type s par pas touche b > 0 en n pas (barrière discrète)."""
    if s <= 0:
        return 0.0
    return min(1.0, 2 * (1 - PHI((b + BETA * s) / (s * math.sqrt(n)))))


KS = (0.8, 1.0, 1.15, 1.3, 1.5)
ZS = (0.5, 1.0, 1.5, 2.0, 2.5)
NS = (5, 10, 20, 30)
obs = []   # (année, durée, n, z, sens, touchée, sd60)
for ten in COL:
    s = [(d, par[d][ten]) for d in days if ten in par[d]]
    v = [x for _, x in s]
    for i in range(61, len(v) - max(NS), 5):
        ch = [v[j] - v[j - 1] for j in range(i - 59, i + 1)]
        sd = math.sqrt(sum(c * c for c in ch) / 60)
        if sd <= 0:
            continue
        for n in NS:
            fut = v[i + 1:i + 1 + n]
            hi, lo = max(fut) - v[i], v[i] - min(fut)
            for z in ZS:
                b = round(z * sd * math.sqrt(n), 2)
                if b < 0.01:
                    continue
                obs.append((s[i][0].year, ten, n, z, "haut", hi >= b - 1e-9, sd, b))
                obs.append((s[i][0].year, ten, n, z, "bas", lo >= b - 1e-9, sd, b))
print(len(obs), "observations")


def ls(rows, k):
    t = 0.0
    for r in rows:
        p = min(max(p_hit(r[7], k * r[6], r[2]), 0.005), 0.995)
        t += math.log(p if r[5] else 1 - p)
    return t / len(rows)


periodes = {"1990-2007": lambda y: y <= 2007, "2008-2019": lambda y: 2008 <= y <= 2019, "2020-2026": lambda y: y >= 2020,
            "2024-2026": lambda y: y >= 2024, "tout": lambda y: True}
print("\nlog-score par K (plus haut = mieux)")
print("période".ljust(12), " ".join(f"K={k:<5}" for k in KS), " n")
for nom, f in periodes.items():
    rows = [r for r in obs if f(r[0])]
    print(nom.ljust(12), " ".join(f"{ls(rows, k):+.4f}" for k in KS), len(rows))
print("\nfréquence observée contre chance prévue (K = 1,0 et 1,3), 2020-2026 et tout")
for nom in ("2020-2026", "tout"):
    f = periodes[nom]
    for n in NS:
        line = []
        for z in ZS:
            rows = [r for r in obs if f(r[0]) and r[2] == n and r[3] == z]
            fr = sum(r[5] for r in rows) / len(rows)
            p1 = sum(p_hit(r[7], r[6], n) for r in rows) / len(rows)
            p13 = sum(p_hit(r[7], 1.3 * r[6], n) for r in rows) / len(rows)
            line.append(f"z{z}: {fr:.3f} / {p1:.3f} / {p13:.3f}")
        print(nom, f"n={n:2}", " | ".join(line))
print("\npar durée (tout), log-score K=1,0 / 1,3")
for ten in COL:
    rows = [r for r in obs if r[1] == ten]
    print(ten, f"{ls(rows, 1.0):+.4f} {ls(rows, 1.3):+.4f}")
