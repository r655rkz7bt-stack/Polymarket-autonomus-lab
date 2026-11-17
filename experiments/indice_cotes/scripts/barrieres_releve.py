"""Piste n° 65, barrières (17/11/2026) : relevé des événements « odds hit / dip » réglés sur PredictionMarketOdds -> barr.json."""
import json, requests
s = requests.Session(); s.headers['User-Agent'] = 'polymarket-autonomous-lab'
evs = {}
for q in ('odds hit', 'odds dip', 'odds reach', 'odds hit by'):
    for st in ('closed', 'active'):
        for page in range(1, 12):
            r = s.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'events_status': st, 'limit_per_type': 50, 'page': page}, timeout=30).json()
            for e in r.get('events') or []: evs[e['id']] = e
            if not r.get('pagination', {}).get('hasMore'): break
full=[]
for eid in evs:
    e = s.get(f'https://gamma-api.polymarket.com/events/{eid}', timeout=30).json()
    if 'predictionmarketodds' in (e.get('description') or '').lower() or any('predictionmarketodds' in (m.get('description') or '').lower() for m in e.get('markets') or []):
        full.append(e)
json.dump(full, open('barr.json','w'))
for e in sorted(full, key=lambda e: e.get('endDate', '')):
    print(e['id'], e.get('createdAt','')[:10], e.get('endDate', '')[:10], e.get('closed'), round(float(e.get('volume') or 0)), e['title'][:80])
