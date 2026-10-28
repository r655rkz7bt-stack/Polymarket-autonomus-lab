"""moins_de_cartes : gagnés contre attendus (paiement par part) par blocs chronologiques et par jeu."""
import sys, math
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger
ps = sorted(charger('published_data/ledger/fantome/moins_de_cartes_v1.0.0.jsonl'), key=lambda p: p['ts'])
def stats(l, nom):
    if not l: return
    pay = sum(float(p['pay']) for p in l); att = sum(float(p['prix']) for p in l)
    var = sum(float(p['prix'])*(1-float(p['prix'])) for p in l)
    mise = sum(float(p['mise']) for p in l); gain = sum(float(p['gain']) for p in l)
    z = (pay-att)/math.sqrt(var) if var else 0
    print(f"{nom:28s} n={len(l):3d} payé {pay:6.1f} attendu {att:6.1f} z {z:+.2f} gain {gain:+7.1f} € / mise {mise:7.1f} = {100*gain/mise:+5.1f} %")
stats(ps, 'tout')
n = len(ps)
for i in range(0, n, 15): stats(ps[i:i+15], f'paris {i+1}-{min(i+15,n)} ({ps[i]["ts"][5:10]})')
stats([p for p in ps if p['ts'] < '2026-10-25T20'], "avant 25/10 20 h (découverte)")
stats([p for p in ps if p['ts'] >= '2026-10-25T20'], "depuis 25/10 20 h")
