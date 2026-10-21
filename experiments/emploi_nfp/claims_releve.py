"""Premier relevé de la piste n° 7 : « Will weekly jobless claims exceed #K for the week ending on … » (échelles de seuils).
Liste, règlement, prix OUI (CLOB, max) et échanges. Données -> donnees/claims/ (ignoré par Git)."""
import re, json, sys, requests, concurrent.futures as cf, datetime as dt
from pathlib import Path
sys.path.insert(0, 'src')
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {'User-Agent': 'curl/8'}
out = {}
for q in ['weekly jobless claims', 'jobless initial claims', 'How many jobless claims', 'jobless claims exceed']:
    for pg in range(1, 5):
        for st in ('closed', 'open'):
            r = requests.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'limit_per_type': 50, 'page': pg, 'events_status': st}, headers=H, timeout=30)
            if r.status_code == 200:
                for e in r.json().get('events', []):
                    if 'jobless' in e['title'].lower(): out[e['id']] = e
print(len(out), 'événements', sorted({e['title'][:40] for e in out.values()})[:6])
def full(eid): return requests.get(f'https://gamma-api.polymarket.com/events/{eid}', headers=H, timeout=30).json()
with cf.ThreadPoolExecutor(6) as ex: evs = list(ex.map(full, out))
def hist(tok):
    for fid in (60, 240, 720):
        h = requests.get('https://clob.polymarket.com/prices-history', params={'market': tok, 'interval': 'max', 'fidelity': fid}, headers=H, timeout=30).json().get('history', [])
        if h: return [(x['t'], x['p']) for x in h]
    return []
rows = []
for e in evs:
    if not e['closed']: continue
    for m in e['markets']:
        try: toks = json.loads(m['clobTokenIds']); yes = float(json.loads(m['outcomePrices'])[0])
        except Exception: continue
        rows.append({'event': e['id'], 'title': e['title'], 'end': e.get('endDate'), 'market': m['id'], 'bucket': m.get('groupItemTitle') or m['question'], 'question': m['question'],
                     'yes_final': yes, 'tokens': toks, 'feesEnabled': m.get('feesEnabled'), 'hist': hist(toks[0])})
json.dump(rows, open('experiments/emploi_nfp/donnees/claims/marches.json', 'w'))
http = HttpClient(timeout=40, min_interval=0.15); cache = Path('experiments/emploi_nfp/donnees/claims/echanges'); cache.mkdir(exist_ok=True)
tot = sum(len(fetch_event_trades(http, cache, e['id'])) for e in evs if e['closed'])
print(len(rows), 'marchés réglés', sum(1 for r in rows if r['hist']), 'avec historique ;', tot, 'échanges ;', len({r['event'] for r in rows}), 'événements réglés')
for r in rows[:6]: print(r['title'][:70], r['end'], r['bucket'], r['yes_final'])
