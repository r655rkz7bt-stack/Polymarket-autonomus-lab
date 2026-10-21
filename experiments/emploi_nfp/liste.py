"""Liste les événements américains « How many jobs added in <mois> ? » et « <mois> Unemployment Rate » (Gamma), réglés ou non.
Données -> experiments/emploi_nfp/donnees/events.json (ignoré par Git)."""
import re, json, requests
H = {'User-Agent': 'curl/8'}
out = {}
for q in ['how many jobs added', 'jobs added in', 'unemployment rate', 'U-3 unemployment', 'Jobs added', 'Unemployment Rate']:
    for pg in range(1, 6):
        for st in ('closed', 'open'):
            r = requests.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'limit_per_type': 50, 'page': pg, 'events_status': st}, headers=H, timeout=30)
            if r.status_code != 200: continue
            for e in r.json().get('events', []): out[e['id']] = e
PAT = re.compile(r'^(How many [Jj]obs added in [A-Z][a-z]+\?|(?:What will be the U-3 u|[A-Z][a-z]+ U)nemployment [Rr]ate(?: in [A-Z][a-z]+\?)?|Unemployment rate over [0-9.]+% in [A-Z][a-z]+\?)$')
sel = {}
for k, e in out.items():
    if PAT.match(e['title']):
        full = requests.get(f'https://gamma-api.polymarket.com/events/{k}', headers=H, timeout=30).json()
        sel[k] = full
for e in sorted(sel.values(), key=lambda e: e.get('endDate') or ''):
    print(e['id'], (e.get('endDate') or '')[:19], e['closed'], len(e['markets']), e['title'])
json.dump(sel, open('experiments/emploi_nfp/donnees/events.json', 'w'))
