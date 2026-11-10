"""Marchés « full lid » de Gamma (ouverts et réglés) par public-search -> donnees/lid_markets.json (10/11/2026). Ordre : releve_marches, lid_hist, lid_trades, lid_ana, lid_sim, lid_real."""
import requests, json, os
H = {'User-Agent': 'curl/8'}
os.makedirs('donnees', exist_ok=True)
evs = {}
for st in ['closed', 'active']:
    for page in range(1, 8):
        r = requests.get('https://gamma-api.polymarket.com/public-search', params=dict(q='full lid', limit_per_type=50, page=page, events_status=st), headers=H, timeout=60).json()
        es = r.get('events', [])
        if not es:
            break
        for e in es:
            evs[e['id']] = e
rows = [dict(id=m['id'], q=m['question'], closed=m.get('closed'), op=m.get('outcomePrices'), end=m.get('endDate'), ev=e['slug'])
        for e in evs.values() for m in e.get('markets', []) if 'lid' in m['question'].lower()]
json.dump(rows, open('donnees/lid_markets.json', 'w'))
print(len(evs), len(rows))
