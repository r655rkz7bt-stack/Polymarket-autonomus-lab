"""Relit sur Gamma le règlement de chaque pari de moins_de_cartes (le fantôme a-t-il bien été payé comme le marché ?)."""
import sys, os, json, requests
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
ps = charger('published_data/ledger/fantome/moins_de_cartes_v1.0.0.jsonl')
bad = 0; vus = 0
for p in ps:
    r = requests.get(f"https://gamma-api.polymarket.com/markets/{p['market']}", headers={'User-Agent': 'curl/8'}, timeout=30)
    if r.status_code != 200:
        print('HTTP', r.status_code, p['market']); continue
    m = r.json()
    outs = json.loads(m['outcomes']); prix = [float(x) for x in json.loads(m['outcomePrices'])]
    officiel = prix[outs.index(p['outcome'])] if p['outcome'] in outs else None
    vus += 1
    ok = officiel is not None and (officiel >= 0.99) == p['gagne'] and m.get('closed')
    if not ok:
        bad += 1; print('ÉCART', p['market'], m['question'][:70], p['outcome'], officiel, 'journal gagné=', p['gagne'], 'closed=', m.get('closed'))
print(vus, 'relus,', bad, 'écarts')
