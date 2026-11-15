"""Piste n° 65 : relève les événements Polymarket réglés sur l'indice PredictionMarketOdds.com (« ... odds on <date> ? »,
« ... odds leader on <date> ? »). Sortie : experiments/indice_cotes/donnees/evenements.json (ignoré par Git)."""
import json, os, requests
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
OUT = os.path.join(os.path.dirname(__file__), '..', 'donnees'); os.makedirs(OUT, exist_ok=True)
evs = {}
for q in ('odds on', 'odds leader on', 'presidential odds', 'nomination odds', 'control odds'):
    for st in ('closed', 'active'):
        for page in range(1, 12):
            r = s.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'events_status': st, 'limit_per_type': 50,
                                                                                  'page': page}, timeout=30).json()
            got = r.get('events') or []
            for e in got:
                evs[e['id']] = e
            if not r.get('pagination', {}).get('hasMore'):
                break
full = []
for eid, e in evs.items():
    e = s.get(f'https://gamma-api.polymarket.com/events/{eid}', timeout=30).json()
    if 'predictionmarketodds' in (e.get('description') or '').lower():
        full.append(e)
json.dump(full, open(os.path.join(OUT, 'evenements.json'), 'w'))
print(len(evs), 'trouvés,', len(full), 'réglés sur PredictionMarketOdds')
for e in sorted(full, key=lambda e: e.get('endDate', '')):
    print(e['id'], e.get('endDate', '')[:10], e.get('closed'), round(float(e.get('volume') or 0)), e['title'][:80])
