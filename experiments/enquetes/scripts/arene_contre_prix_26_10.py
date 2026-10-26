"""Famille 2/5 (26/10) : l'arène entière gagne-t-elle autant que les prix qu'elle paie ?
UN pari par jeton (le plus ancien de tous les fantômes), paiement réel `pay` (0 / 0,5 / 1), prix moyen payé.
Découpes : famille de stratégie, bande de prix, période (avant/après le 22/10), 50-50 compris."""
import glob, math, os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger

seen = {}
for f in sorted(glob.glob('published_data/ledger/fantome/*.jsonl')):
    nom = os.path.basename(f)[:-6].rsplit('_v', 1)[0]
    for p in charger(f):
        t = p['token']
        if t not in seen or p['ts'] < seen[t]['ts']:
            seen[t] = dict(ts=p['ts'], prix=float(p['prix']), pay=float(p['pay']), nom=nom, ev=p['event'])
rows = list(seen.values())

def ligne(nom, v):
    if not v: return
    n = len(v); w = sum(r['pay'] for r in v); e = sum(r['prix'] for r in v)
    var = sum(r['prix'] * (1 - r['prix']) for r in v)
    evs = collections.defaultdict(float)
    for r in v: evs[r['ev']] += r['pay'] - r['prix']
    m = sum(evs.values()) / len(evs); sd = (sum((x - m) ** 2 for x in evs.values()) / max(1, len(evs) - 1)) ** .5
    t = m / (sd / math.sqrt(len(evs))) if sd else 0
    print(f'{nom:34s} n={n:5d} payé {w:7.1f} / prix {e:7.1f}  écart {(w-e)/n*100:+5.1f} pts  z {(w-e)/math.sqrt(var):+5.2f}  t/événement {t:+5.2f} ({len(evs)} ev)')

def famille(nom):
    for pre, fam in (('nf_tennis', 'nf_tennis'), ('nf_sport', 'nf_sport'), ('nf_court', 'nf_court'), ('nf_', 'nf_autres'), ('naive_favorite', 'naive'),
                     ('nm_', 'news_momentum'), ('compteur', 'tweets'), ('crypto', 'crypto'), ('contrer', 'contrer_crypto'), ('market_maker', 'market_maker')):
        if nom.startswith(pre): return fam
    return 'autres'

print('TOUTE L\'ARÈNE'); ligne('tous', rows)
print('\nPAR FAMILLE')
fam = collections.defaultdict(list)
for r in rows: fam[famille(r['nom'])].append(r)
for k, v in sorted(fam.items(), key=lambda kv: -len(kv[1])): ligne(k, v)
print('\nPAR BANDE DE PRIX (tous)')
for lo, hi in [(0, .3), (.3, .6), (.6, .8), (.8, .85), (.85, .9), (.9, .95), (.95, .99), (.99, 1.01)]:
    ligne(f'{lo:.2f}-{hi:.2f}', [r for r in rows if lo <= r['prix'] < hi])
print('\nPAR BANDE, famille nf_* seulement')
nf = [r for r in rows if r['nom'].startswith(('nf_', 'naive'))]
for lo, hi in [(.6, .8), (.8, .85), (.85, .9), (.9, .95), (.95, .99), (.99, 1.01)]:
    ligne(f'{lo:.2f}-{hi:.2f}', [r for r in nf if lo <= r['prix'] < hi])
print('\nPAR PÉRIODE (nf_*)')
for nom, a, b in [('<= 21/10', '', '2026-10-22'), ('22/10 - 24/10', '2026-10-22', '2026-10-25'), ('>= 25/10', '2026-10-25', '9')]:
    ligne(nom, [r for r in nf if a <= r['ts'][:10] < b])
print('\nDÉTAIL « autres » par stratégie (paris dont le plus ancien est cette stratégie)')
par = collections.defaultdict(list)
for r in rows:
    if famille(r['nom']) == 'autres': par[r['nom']].append(r)
for k, v in sorted(par.items(), key=lambda kv: -len(kv[1]))[:16]: ligne(k, v)
