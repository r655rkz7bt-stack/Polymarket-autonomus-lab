"""Famille 5 : le classement « capital réalisé » ignore les positions ouvertes. Mise en jeu et ancienneté par fantôme."""
import json, glob, os, sys, collections
from decimal import Decimal as D
from datetime import datetime, timezone
now = datetime.now(timezone.utc)
rows = []
for f in sorted(glob.glob('published_data/ledger/fantome/*/ledger.jsonl') + glob.glob('published_data/ledger/fantome/*.jsonl')):
    name = os.path.basename(os.path.dirname(f)) if f.endswith('/ledger.jsonl') else os.path.basename(f)[:-6]
    buys = collections.OrderedDict(); settled = set(); realised = D(0); cash0 = None
    for l in open(f):
        x = json.loads(l); d = x['data']
        if x['type'] == 'BUY':
            b = buys.setdefault(d['token_id'], dict(cout=D(0), ts=x['ts'], m=d.get('market_id')))
            b['cout'] += D(d['price']) * D(d['shares']) + D(d['fee'])
        elif x['type'] == 'SETTLE':
            settled.add(d['token_id'])
        elif x['type'] == 'SELL':
            settled.add(d['token_id']) if False else None
    op = [(t, b) for t, b in buys.items() if t not in settled]
    cout = sum(b['cout'] for t, b in op)
    ages = [(now - datetime.fromisoformat(b['ts'])).total_seconds() / 86400 for t, b in op]
    rows.append((name, len(buys), len(op), float(cout), max(ages) if ages else 0))
rows.sort(key=lambda r: -r[3])
print('fantôme | jetons | ouverts | mise en jeu € | plus vieux (j)')
for r in rows[:25]:
    print('%-55s %5d %5d %9.1f %6.1f' % r)
print('total mise en jeu', sum(r[3] for r in rows))
