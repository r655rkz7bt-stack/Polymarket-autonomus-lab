"""Famille 3 (25/10 soir) : tirage de paris réglés, relecture Gamma (marché, résultat, question)."""
import glob, os, random, sys, json, collections
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
import requests
H = {'User-Agent': 'curl/8'}
tout = []
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    s = os.path.basename(f).replace('.jsonl', '')
    for p in charger(f):
        p['strat'] = s; tout.append(p)
print(len(tout), 'paris réglés')
cles = collections.Counter()
for p in tout:
    for k in p['achats'][0][3]:
        cles[k] += 1
print([k for k, v in cles.most_common(40) if k.startswith(('ref', 'kal', 'pred', 'odds', 'src'))])
random.seed(25)
ext = [p for p in tout if p['reglé_ts'] >= '2026-10-20']
print(len(ext), 'réglés depuis le 20/10')
par = collections.Counter(p['strat'] for p in ext); print(par.most_common(12))
ech = random.sample(ext, min(30, len(ext)))
bad = 0
for p in ech:
    r = requests.get(f"https://gamma-api.polymarket.com/markets/{p['market']}", headers=H, timeout=30).json()
    prices = json.loads(r['outcomePrices']) if isinstance(r.get('outcomePrices'), str) else r.get('outcomePrices')
    outs = json.loads(r['outcomes']) if isinstance(r.get('outcomes'), str) else r.get('outcomes')
    off = float(prices[outs.index(p['outcome'])]) if p['outcome'] in outs else None
    ok = off is not None and abs(off - float(p['pay'])) < 1e-6
    bad += not ok
    ex = {k: v for k, v in p['achats'][0][3].items() if k not in ('cycle_id', 'levels', 'portfolio')}
    print('OK ' if ok else 'XX ', p['strat'], p['outcome'], 'journal', p['pay'], 'gamma', off, '|', r['question'][:70], '|', str(ex)[:200])
print('écarts', bad)
