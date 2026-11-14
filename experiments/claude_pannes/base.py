"""Fréquence de base : jours non verts du 15 à la fin du mois, selon le compte des 14 premiers jours.
Question du 14/11/2026 : novembre a 1 jour non vert au 14 ; « 5 ou plus » demande ≥ 4 jours de plus du 15 au 30."""
import csv, collections, os, math
r = list(csv.DictReader(open(os.path.join(os.path.dirname(__file__), 'releves', 'jours.csv'))))
G = '#76ad2a'
mois = collections.OrderedDict()
for x in r:
    if x['couleur'] == '#EAEAEA': continue
    k = x['date'][:7]; j = int(x['date'][8:10]); bad = x['couleur'].lower() != G
    mois.setdefault(k, [0, 0])
    mois[k][0 if j <= 14 else 1] += bad
ms = [(k, v) for k, v in mois.items() if k not in ('2023-12', '2026-11')]
def resume(sel, nom):
    n = len(sel); ge4 = sum(v[1] >= 4 for k, v in sel); moy = sum(v[1] for k, v in sel) / n
    print(f"{nom:32s} {n:2d} mois : fin de mois moyenne {moy:4.1f}, P(≥4) {ge4}/{n} = {ge4/n:.2f}")
resume(ms, 'tous (2024-01 → 2026-10)')
resume(ms[-12:], '12 derniers mois')
resume(ms[-6:], '6 derniers mois')
resume([m for m in ms if m[1][0] <= 2], 'début de mois calme (≤ 2 au 14)')
resume([m for m in ms[-18:] if m[1][0] <= 3], '18 derniers, ≤ 3 au 14')
print('corrélation début / fin :')
for k, v in ms: print(' ', k, v)
# Poisson à taux récent
for lam in (0.12, 0.15, 0.2, 0.25):
    mu = lam * 16; p = 1 - sum(math.exp(-mu) * mu**i / math.factorial(i) for i in range(4))
    print(f"Poisson {lam}/jour sur 16 jours : P(≥4) = {p:.3f}")
