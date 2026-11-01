"""01/11 : cohérence Sénat. Somme des courses d'État (supposées indépendantes) contre l'échelle « Republican Senate seats after the midterms »."""
import requests, json, re, itertools
H = {'User-Agent': 'curl/8'}
G = 'https://gamma-api.polymarket.com'
e = requests.get(f'{G}/events/106193', headers=H).json()
print(e['title'])
for m in e['markets']:
    print(m['id'], m.get('groupItemTitle'), m.get('outcomePrices'), m.get('liquidity'), m.get('volume24hr'))

# --- courses d'État
ids = list(range(57637, 57690)) + [59203, 59204, 59233]
courses = {}
for i in ids:
    r = requests.get(f'{G}/events/{i}', headers=H)
    if r.status_code != 200: continue
    ev = r.json()
    if 'Senate Election Winner' not in (ev.get('title') or ''): continue
    pr = {}
    for m in ev['markets']:
        if not m.get('outcomePrices'): continue
        q = m['question']; p = float(json.loads(m['outcomePrices'])[0])
        mm = re.match(r'Will (the )?(.+?) win the', q)
        pr[(m.get('groupItemTitle') or mm.group(2))] = (p, float(m.get('liquidity') or 0))
    courses[ev['title']] = pr
json.dump(courses, open('experiments/familles_nouvelles/senat_courses_01_11.json', 'w'), indent=1)
for t, pr in courses.items():
    print(t, {k: v[0] for k, v in pr.items() if v[0] > 0.005})
