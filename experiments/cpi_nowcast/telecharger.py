"""Télécharge, pour chaque événement CPI américain réglé (mensuel, annuel, core), les marchés par tranche, leur règlement
et le prix OUI heure par heure (CLOB prices-history) avant la publication. Données -> experiments/cpi_nowcast/donnees/ (ignoré par Git)."""
import json, re, requests, concurrent.futures as cf, datetime as dt
H = {'User-Agent': 'curl/8'}
ev = json.load(open('experiments/cpi_nowcast/donnees/events.json'))
PAT = re.compile(r'^(?:[A-Z][a-z]+ Inflation(?: US)? - (Annual|Monthly)|Core CPI (YoY|MoM) - .*)$')
sel = [e for e in ev.values() if e['closed'] and PAT.match(e['title'])]
print(len(sel), 'événements')
def one(e):
    rows = []
    for m in e['markets']:
        try:
            toks = json.loads(m['clobTokenIds']); op = json.loads(m['outcomePrices'])
        except Exception:
            continue
        end = dt.datetime.fromisoformat(e['endDate'].replace('Z', '+00:00'))
        t1 = int(end.timestamp()); t0 = t1 - 15 * 86400
        r = requests.get('https://clob.polymarket.com/prices-history', params={'market': toks[0], 'startTs': t0, 'endTs': t1, 'fidelity': 60}, headers=H, timeout=30)
        h = r.json().get('history', []) if r.status_code == 200 else []
        rows.append({'event': e['id'], 'title': e['title'], 'release': e['endDate'], 'market': m['id'], 'bucket': m.get('groupItemTitle') or m['question'],
                     'question': m['question'], 'yes_final': float(op[0]), 'closed': m.get('closed'), 'uma': m.get('umaResolutionStatus'),
                     'volume': float(m.get('volume') or 0), 'feeSchedule': m.get('feeSchedule'), 'hist': [(x['t'], x['p']) for x in h]})
    return rows
out = []
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, sel): out += r
json.dump(out, open('experiments/cpi_nowcast/donnees/marches.json', 'w'))
print(len(out), 'marchés', sum(1 for r in out if r['hist']), 'avec historique')
