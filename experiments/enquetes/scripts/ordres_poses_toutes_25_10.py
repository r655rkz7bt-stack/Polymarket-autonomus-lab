"""Ordres posés contre achats immédiats sur TOUTES les stratégies (un compte par jeton), hors favoris de sport déjà vus
(ordres_poses_en_jeu_25_10.py). Découpage par stratégie mère approximative (préfixe du nom)."""
import sys, glob, os, math, collections
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
tok = {}
for f in sorted(glob.glob('published_data/ledger/fantome/*.jsonl')) + ['published_data/ledger/ledger.jsonl']:
    nom = os.path.basename(f)[:-6]
    for p in charger(f):
        if p['token'] not in tok:
            p['strat'] = nom; tok[p['token']] = p
def mode(p): return p['achats'][0][3].get('order_type') or 'marche'
def st(L):
    n = len(L)
    if n < 2: return f"n={n}"
    r = [float(p['pay']) / float(p['prix']) - 1 for p in L]
    m = sum(r) / n; sd = (sum((x - m) ** 2 for x in r) / (n - 1)) ** .5
    gag = sum(float(p['pay']) for p in L); att = sum(float(p['prix']) for p in L)
    var = sum(float(p['prix']) * (1 - float(p['prix'])) for p in L)
    g = sum(float(p['gain']) for p in L); mi = sum(float(p['mise']) for p in L)
    return f"n={n:4d} gain={g:7.0f} rend={100*g/mi:6.1f}% unit={100*m:6.1f}% t={m/(sd/math.sqrt(n)+1e-9):5.2f} gag/att={gag:6.1f}/{att:6.1f} z={(gag-att)/math.sqrt(var+1e-9):5.2f}"
def famille(nom):
    for k in ('contrer_crypto', 'crypto_threshold', 'meteo_prevision', 'news_momentum', 'market_structure', 'market_maker', 'naive_favorite', 'nf_', 'nm_'):
        if nom.startswith(k): return k
    return 'autres'
fam = collections.defaultdict(list)
for p in tok.values(): fam[famille(p['strat'])].append(p)
for k, L in sorted(fam.items()):
    print(k)
    for m in ('limite', 'marche'):
        print('   ', m, st([p for p in L if mode(p) == m]))
tous = list(tok.values())
hors = [p for p in tous if famille(p['strat']) not in ('nf_', 'naive_favorite', 'nm_')]
print('HORS favoris/nouvelles:'); [print('   ', m, st([p for p in hors if mode(p) == m])) for m in ('limite', 'marche')]
