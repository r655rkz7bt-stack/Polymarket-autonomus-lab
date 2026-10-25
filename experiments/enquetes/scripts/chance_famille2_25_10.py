"""Famille 2 (25/10) : le gain des stratégies résiste-t-il sans ses 3 plus gros paris / son meilleur jour ?
Gagné contre attendu (prix payé), rendement par mise, z de Bernoulli sur le prix payé."""
import glob, os, sys, math, collections
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger

lignes = []
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    nom = os.path.basename(f)[:-6]
    ps = charger(f)
    if len(ps) < 25:
        continue
    gain = float(sum(p['gain'] for p in ps)); mise = float(sum(p['mise'] for p in ps))
    tri = sorted(ps, key=lambda p: -p['gain'])
    sans3 = gain - float(sum(p['gain'] for p in tri[:3]))
    jours = collections.defaultdict(float)
    for p in ps:
        jours[p['reglé_ts'][:10]] += float(p['gain'])
    meilleur = max(jours.values())
    att = sum(float(p['prix']) for p in ps); gag = sum(float(p['pay']) for p in ps)
    var = sum(float(p['prix']) * (1 - float(p['prix'])) for p in ps)
    z = (gag - att) / math.sqrt(var) if var else 0
    lignes.append((gain, nom, len(ps), mise, sans3, gain - meilleur, gag, att, z))
lignes.sort(reverse=True)
print(f"{'stratégie':48} n   gain  rend%  sans3  sansJour  gagnés/att   z")
for g, nom, n, mise, s3, sj, gag, att, z in lignes[:25]:
    print(f"{nom[:48]:48} {n:3d} {g:6.0f} {100*g/mise:6.1f} {s3:6.0f} {sj:8.0f}  {gag:5.1f}/{att:5.1f} {z:5.2f}")
pos = [l for l in lignes if l[0] > 0]
print('\npositives:', len(pos), 'dont gain>0 sans3:', sum(1 for l in pos if l[4] > 0), 'sans meilleur jour:', sum(1 for l in pos if l[5] > 0))
print('z>2:', [(l[1], round(l[8], 2)) for l in lignes if l[8] > 2])
