"""Écrit src/polymarket_agent/taux_tresor_excursions.json (16/11/2026, passage de 21 h) : loi EMPIRIQUE de l'excursion maximale des
clôtures du Trésor en n jours ouvrés (n = 1 à 90), divisée par l'écart-type des 60 variations d'avant (σ60), haut et bas mélangés,
2, 5, 10 et 30 ans, clôtures du 02/01/1990 au 31/07/2026 (aucune fenêtre d'après la coupure du test de septembre-octobre).
Table : survie S_n(z) = part des excursions ≥ z, z = 0 à 8 par pas de 0,05. Jugée hors échantillon par etalonnage_hors_echantillon.py
(apprise sur 1990-2015, jugée sur 2016-2026 : log-score −0,3761 contre −0,3788 pour la gaussienne K 1,0 et −0,3918 pour K 1,3)."""
import csv, glob, json, math, os
from bisect import bisect_left
from datetime import date, datetime

D = os.path.join(os.path.dirname(__file__), "..", "donnees")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "..", "src", "polymarket_agent", "taux_tresor_excursions.json")
COL = {2: "2 Yr", 5: "5 Yr", 10: "10 Yr", 30: "30 Yr"}
COUPURE = date(2026, 8, 1)
NMAX, PAS, ZMAX = 90, 0.05, 8.0
par = {}
for f in glob.glob(os.path.join(D, "par_*.csv")):
    for r in csv.DictReader(open(f)):
        try:
            d = datetime.strptime(r["Date"], "%m/%d/%Y").date()
        except (KeyError, ValueError):
            continue
        par[d] = {k: float(r[v]) for k, v in COL.items() if r.get(v) not in (None, "", "N/A")}
days = sorted(d for d in par if d < COUPURE)
ex = {n: [] for n in range(1, NMAX + 1)}
for ten in COL:
    v = [par[d][ten] for d in days if ten in par[d]]
    for i in range(61, len(v) - NMAX):
        ch = [v[j] - v[j - 1] for j in range(i - 59, i + 1)]
        sd = math.sqrt(sum(c * c for c in ch) / 60)
        if sd <= 0:
            continue
        hi = lo = 0.0
        for n in range(1, NMAX + 1):
            mv = v[i + n] - v[i]
            hi, lo = max(hi, mv), min(lo, mv)
            ex[n].append(hi / sd); ex[n].append(-lo / sd)
zs = [round(i * PAS, 2) for i in range(int(ZMAX / PAS) + 1)]
table = {}
for n, xs in ex.items():
    xs.sort()
    m = len(xs)
    table[str(n)] = [round((m - bisect_left(xs, z - 1e-12) + 0.5) / (m + 1), 6) for z in zs]
json.dump({"source": "home.treasury.gov Daily Treasury Par Yield Curve Rates, 1990-01-02 → 2026-07-31, 2/5/10/30 ans",
           "pas_z": PAS, "n_max": NMAX, "observations_par_n": len(ex[1]), "survie": table}, open(OUT, "w"), separators=(",", ":"))
print(OUT, len(ex[1]), "excursions par n ;", "S_10(1,0) =", table["10"][20], "S_30(2,0) =", table["30"][40])
