"""28/10/2026 : pour chaque achat du principal depuis le 21/10, même jeton, même côté et même prix (±) que le jumeau du fantôme copié ? Lancer depuis la racine."""
import json, glob, os, statistics as st
from decimal import Decimal as D
rows = [json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
n = opp = 0; dpx = []; hors = []
for r in rows:
    if r['type'] != 'BUY' or r['ts'] < '2026-10-21': continue
    d = r['data']; f = f"published_data/ledger/fantome/{d['strategy_id']}_v{d['strategy_version']}.jsonl"
    if not os.path.exists(f): continue
    g = [json.loads(l)['data'] for l in open(f) if '"BUY"' in l]
    g = [x for x in g if x['token_id'] == d['token_id']]
    if not g: continue
    n += 1
    if any(x['outcome'] != d['outcome'] for x in g): opp += 1
    dpx.append(float(D(d['price']) - D(g[0]['price'])))
print(n, 'achats du principal avec jumeau ;', opp, 'de côté opposé ; écart de prix : médiane %.4f, min %.4f, max %.4f' % (st.median(dpx), min(dpx), max(dpx)))
print('achats du principal à plus de 2 centimes du jumeau :', sum(abs(x) > 0.02 for x in dpx))
