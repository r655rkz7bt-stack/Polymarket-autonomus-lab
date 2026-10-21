"""Relevé des autres séries économiques à tranches : PIB américain (« US GDP growth in … »), ISM Services / Manufacturing PMI. Même format que telecharger.py.
Heure de publication = saut du prix du gagnant dans les échanges (les dates de fin Gamma sont des placeholders). Données -> donnees/macro/ (ignoré par Git)."""
import re, json, sys, gzip, requests, concurrent.futures as cf, datetime as dt
from pathlib import Path
sys.path.insert(0, 'src')
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {'User-Agent': 'curl/8'}
PAT = re.compile(r'^(US GDP growth in .*|ISM (Services|Manufacturing) PMI - .*)$')
out = {}
for q in ['US GDP growth', 'GDP growth in', 'ISM Services PMI', 'ISM Manufacturing PMI', 'ISM PMI']:
    for pg in range(1, 4):
        for st in ('closed', 'open'):
            r = requests.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'limit_per_type': 50, 'page': pg, 'events_status': st}, headers=H, timeout=30)
            if r.status_code == 200:
                for e in r.json().get('events', []):
                    if PAT.match(e['title']): out[e['id']] = e
def full(eid): return requests.get(f'https://gamma-api.polymarket.com/events/{eid}', headers=H, timeout=30).json()
with cf.ThreadPoolExecutor(6) as ex: evs = [e for e in ex.map(full, out) if e['closed']]
def hist(tok):
    for fid in (60, 240, 720):
        h = requests.get('https://clob.polymarket.com/prices-history', params={'market': tok, 'interval': 'max', 'fidelity': fid}, headers=H, timeout=30).json().get('history', [])
        if h: return [(x['t'], x['p']) for x in h]
    return []
http = HttpClient(timeout=40, min_interval=0.15); cache = Path('experiments/emploi_nfp/donnees/macro/echanges'); cache.mkdir(exist_ok=True)
rows = []
for e in evs:
    tr = fetch_event_trades(http, cache, e['id'])
    ms = [m for m in e['markets'] if m.get('clobTokenIds')]
    # publication = premier échange après lequel le jeton gagnant reste > 0,9
    jump = None
    for m in ms:
        yes = json.loads(m['clobTokenIds'])[0]
        if float(json.loads(m['outcomePrices'])[0]) < .5: continue
        pts = sorted((t[0], t[3]) for t in tr if t[1] == yes)
        low = [w for w, p in pts if p < .6]; hi = [w for w, p in pts if p > .9 and (not low or w > low[-1])]
        if low and hi: jump = hi[0]
    for m in ms:
        toks = json.loads(m['clobTokenIds'])
        rows.append({'event': e['id'], 'title': e['title'], 'end': e.get('endDate'), 'release_ts': jump, 'market': m['id'], 'bucket': m.get('groupItemTitle') or m['question'],
                     'yes_final': float(json.loads(m['outcomePrices'])[0]), 'tokens': toks, 'feesEnabled': m.get('feesEnabled'), 'hist': hist(toks[0])})
json.dump(rows, open('experiments/emploi_nfp/donnees/macro/marches.json', 'w'))
print(len(evs), 'événements réglés,', len(rows), 'marchés ;', 'avec heure de publication :', len({r['event'] for r in rows if r['release_ts']}))
for e in evs: print(e['id'], e['title'], (e.get('endDate') or '')[:10], len(e['markets']))
