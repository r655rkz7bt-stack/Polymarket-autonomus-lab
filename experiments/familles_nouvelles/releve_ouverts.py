"""01/11 : relevé des événements ouverts les plus échangés (volume 24 h) pour repérer des familles répétitives non jouées."""
import requests, json, re, collections, sys
H = {'User-Agent': 'curl/8'}
evs, cursor = [], None
while len(evs) < 2000:
    params = dict(closed='false', order='volume24hr', ascending='false', limit=100)
    if cursor: params['after_cursor'] = cursor
    r = requests.get('https://gamma-api.polymarket.com/events/keyset', params=params, headers=H, timeout=60)
    if r.status_code != 200: break
    b = r.json(); evs += b.get('events', [])
    cursor = b.get('next_cursor')
    if not cursor or not b.get('events'): break
print(len(evs), file=sys.stderr)
out = [dict(id=e['id'], slug=e.get('slug'), title=e.get('title'), v24=e.get('volume24hr'), liq=e.get('liquidity'), n=len(e.get('markets') or []), tags=[t.get('slug') for t in e.get('tags') or []], end=e.get('endDate')) for e in evs]
json.dump(out, open('experiments/familles_nouvelles/ouverts_01_11.json', 'w'))
