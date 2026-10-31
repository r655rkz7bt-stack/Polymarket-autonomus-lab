"""31/10/2026 : échelles « How many House seats will the Democrats win in <État> ? » contre les marchés « XX-NN House Election Winner » des mêmes districts.
Relève les prix actuels (aucun historique) et écrit releve.json. Lancer avec .venv/bin/python."""
import json, re, sys, time, requests
H = {'User-Agent': 'curl/8'}
G = 'https://gamma-api.polymarket.com'

def get(path, **params):
    for _ in range(4):
        r = requests.get(G + path, params=params, headers=H, timeout=40)
        if r.status_code == 200:
            return r.json()
        time.sleep(2)
    return None

ladders = {}
for pg in range(1, 8):
    r = get('/public-search', q='How many House seats will the Democrats win in', events_status='active', limit_per_type=50, page=pg)
    if not r or not r.get('events'):
        break
    for e in r['events']:
        m = re.match(r'How many House seats will the Democrats win in (.+)\?', e['title'])
        if m:
            ladders[m.group(1)] = e['id']
print(len(ladders), 'échelles', sorted(ladders))
out = {}
for state, eid in ladders.items():
    e = get(f'/events/{eid}')
    rows = []
    for mk in e['markets']:
        p = json.loads(mk['outcomePrices'])[0]
        rows.append((mk['question'], float(p), float(mk.get('volumeNum') or 0), float(mk.get('liquidityNum') or 0)))
    out[state] = {'ladder_event': eid, 'ladder': rows, 'districts': {}}
json.dump(out, open('experiments/coherence_sieges/releve_echelles.json', 'w'), ensure_ascii=False, indent=1)

# --- districts : « XX-NN House Election Winner » (slug xx-nn-house-election-winner), prix du OUI du parti démocrate
from concurrent.futures import ThreadPoolExecutor
ABBR = {'Alabama': 'AL', 'Arizona': 'AZ', 'California': 'CA', 'Colorado': 'CO', 'Florida': 'FL', 'Iowa': 'IA', 'Michigan': 'MI', 'Minnesota': 'MN',
        'Nevada': 'NV', 'New Jersey': 'NJ', 'New York': 'NY', 'North Carolina': 'NC', 'Ohio': 'OH', 'Pennsylvania': 'PA', 'South Carolina': 'SC',
        'Tennessee': 'TN', 'Texas': 'TX', 'Virginia': 'VA', 'Wisconsin': 'WI'}
N = {'AL': 7, 'AZ': 9, 'CA': 52, 'CO': 8, 'FL': 28, 'IA': 4, 'MI': 13, 'MN': 8, 'NV': 4, 'NJ': 12, 'NY': 26, 'NC': 14, 'OH': 15, 'PA': 17, 'SC': 7, 'TN': 9, 'TX': 38, 'VA': 11, 'WI': 8}

def district(args):
    ab, n = args
    d = f'{ab}-{n:02d}'
    r = get('/events', slug=f'{d.lower()}-house-election-winner')
    if not r:
        return ab, d, None
    dem = None
    for mk in r[0]['markets']:
        if re.search(r'Democrat', mk['question']) and 'outcomePrices' in mk:
            dem = (float(json.loads(mk['outcomePrices'])[0]), float(mk.get('volumeNum') or 0), float(mk.get('liquidityNum') or 0), mk['question'])
    return ab, d, dem

jobs = [(ab, n) for ab in ABBR.values() for n in range(1, N[ab] + 1)]
with ThreadPoolExecutor(6) as ex:
    res = list(ex.map(district, jobs))
inv = {v: k for k, v in ABBR.items()}
for ab, d, dem in res:
    out[inv[ab]]['districts'][d] = dem
json.dump(out, open('experiments/coherence_sieges/releve_echelles.json', 'w'), ensure_ascii=False, indent=1)
print({k: sum(1 for v in o['districts'].values() if v) for k, o in out.items()})
