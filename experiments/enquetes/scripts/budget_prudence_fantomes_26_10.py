"""Fantômes dont le budget `prudence × capital − investi` est ≤ 0 : `Weighted._scale` écarte alors TOUS leurs achats, sans raison notée.
Usage : .venv/bin/python experiments/enquetes/scripts/budget_prudence_fantomes_26_10.py   (après fetch_published.sh et fetch_data.sh)"""
import json, glob, os
from decimal import Decimal as D
data = json.load(open('published/data.json'))
sante = {r['nom']: r.get('sante') or {} for r in data['arene']}
ops = {r['nom']: r['operations'] for r in data['arene']}
res = []
for path in sorted(glob.glob('published_data/ledger/fantome/*.jsonl')):
    name = os.path.basename(path)[:-6]
    rows = [json.loads(l) for l in open(path)]
    cash = D(0); pos = {}; last = None; lastbuy = None
    for r in rows:
        d = r['data']
        if r['type'] == 'GENESIS': cash = D(d['initial_capital'])
        elif r['type'] == 'BUY':
            c = D(d['price']) * D(d['shares']) + D(d['fee']); cash -= c
            q = pos.setdefault(d['token_id'], [D(0), D(0)]); q[0] += D(d['shares']); q[1] += c; lastbuy = r['ts']
        elif r['type'] == 'SELL':
            q = pos.get(d['token_id'])
            if q and q[0] > 0:
                part = D(d['shares']) / q[0]; q[1] -= q[1] * part; q[0] -= D(d['shares'])
            cash += D(d['price']) * D(d['shares']) - D(d['fee'])
        elif r['type'] == 'SETTLE':
            q = pos.pop(d['token_id'], None)
            if q: cash += q[0] * D(d['payout_per_share'])
        elif r['type'] == 'HEARTBEAT' and 'total_estimated' in d: last = D(d['total_estimated'])
    if last is None: continue
    invested = sum(q[1] for q in pos.values() if q[0] > 0)
    p = D(str((sante.get(name) or {}).get('prudence', 1)))
    budget = p * last - invested
    res.append((name, p, last, invested, budget, lastbuy))
bloques = [r for r in res if r[1] > 0 and r[4] <= 0]
print(len(res), 'fantômes ;', len([r for r in res if r[1] < 1]), 'avec prudence < 1 ;', len(bloques), 'au budget épuisé (aucun achat possible)')
for n, p, last, inv, b, lb in sorted(bloques, key=lambda r: r[4]):
    print(f"{n:55s} prudence {p} capital {last:8.1f} investi {inv:7.1f} budget {b:8.1f} dernier achat {lb[:16] if lb else '-'}")
