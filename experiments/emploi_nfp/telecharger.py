"""Pour chaque événement emploi américain réglé : marchés par tranche, règlement, prix OUI heure par heure (CLOB) avant la
publication, et vrais échanges (idea_test.fetch_event_trades). Données -> experiments/emploi_nfp/donnees/ (ignoré par Git).
Heure de publication = date de l'événement « Unemployment Rate » du même mois à 12:30 UTC (13:30 l'hiver) : les dates de fin
Gamma des événements « jobs added » sont des placeholders (parfois +5 jours, parfois la veille)."""
import json, re, sys, requests, datetime as dt, concurrent.futures as cf
from pathlib import Path
sys.path.insert(0, 'src')
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades
H = {'User-Agent': 'curl/8'}
ev = json.load(open('experiments/emploi_nfp/donnees/events.json'))
MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December']
def month_of(t):
    for i, m in enumerate(MONTHS):
        if re.search(r'\b' + m + r'\b', t): return i + 1
def kind(t):
    return 'jobs' if 'jobs added' in t.lower() else 'chomage'
rows = []
for e in ev.values():
    if not e['closed'] or 'Eurozone' in e['title'] or e['id'] == '5843': continue
    rows.append({'id': e['id'], 'kind': kind(e['title']), 'month': month_of(e['title']), 'title': e['title'], 'end': e['endDate']})
# date de publication : celle de l'événement chômage du même mois de référence (+ année déduite de la date de fin)
def year_ref(r):
    d = dt.date.fromisoformat(r['end'][:10]); m = r['month']
    y = d.year if m < d.month or (m == d.month) else d.year - 1
    return y if m <= d.month else d.year - 1
for r in rows: r['ref'] = (year_ref(r), r['month'])
chom = {r['ref']: r for r in rows if r['kind'] == 'chomage'}
for r in rows:
    anchor = chom.get(r['ref']) if r['kind'] == 'jobs' else r
    d = dt.date.fromisoformat((anchor or r)['end'][:10])
    if r['kind'] == 'jobs' and r['id'] in ('563235',): d = dt.date(2026, 7, 2)
    hh = 12 if 3 <= d.month <= 10 else 13
    r['release'] = dt.datetime(d.year, d.month, d.day, hh, 30, tzinfo=dt.timezone.utc).isoformat()
    r['anchor'] = bool(anchor)
http = HttpClient(timeout=40, min_interval=0.15)
cache = Path('experiments/emploi_nfp/donnees/echanges'); cache.mkdir(exist_ok=True)
def one(r):
    e = ev[r['id']]; out = []
    t1 = int(dt.datetime.fromisoformat(r['release']).timestamp()); t0 = t1 - 15 * 86400
    for m in e['markets']:
        try: toks = json.loads(m['clobTokenIds']); op = json.loads(m['outcomePrices'])
        except Exception: continue
        h = []
        for fid in (60, 240, 720):  # les marchés clos refusent les pas fins : le plus fin qui répond
            rr = requests.get('https://clob.polymarket.com/prices-history', params={'market': toks[0], 'interval': 'max', 'fidelity': fid}, headers=H, timeout=30)
            h = rr.json().get('history', []) if rr.status_code == 200 else []
            if h: break
        out.append({'event': r['id'], 'kind': r['kind'], 'ref': r['ref'], 'title': r['title'], 'release': r['release'], 'market': m['id'],
                    'bucket': m.get('groupItemTitle') or m['question'], 'question': m['question'], 'yes_final': float(op[0]), 'uma': m.get('umaResolutionStatus'),
                    'volume': float(m.get('volume') or 0), 'tokens': toks, 'feeSchedule': m.get('feeSchedule'), 'feesEnabled': m.get('feesEnabled'),
                    'fid': fid, 'hist': [(x['t'], x['p']) for x in h]})
    return out
allr = []
with cf.ThreadPoolExecutor(6) as ex:
    for o in ex.map(one, rows): allr += o
json.dump(allr, open('experiments/emploi_nfp/donnees/marches.json', 'w'))
json.dump(rows, open('experiments/emploi_nfp/donnees/evenements.json', 'w'))
print(len(rows), 'événements', len(allr), 'marchés', sum(1 for r in allr if r['hist']), 'avec historique')
tot = 0
for r in rows:
    tr = fetch_event_trades(http, cache, r['id']); tot += len(tr)
print('échanges', tot)
