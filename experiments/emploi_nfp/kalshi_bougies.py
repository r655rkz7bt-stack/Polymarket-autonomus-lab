"""Bougies horaires (meilleur acheteur / vendeur à la clôture) de chaque marché Kalshi KXPAYROLLS, 8 jours avant la publication.
Données -> experiments/emploi_nfp/donnees/kalshi_bougies.json (ignoré par Git). Reprend là où il s'est arrêté."""
import json, time, requests, os, datetime as dt
B = 'https://api.elections.kalshi.com/trade-api/v2'; H = {'User-Agent': 'curl/8'}
ms = json.load(open('experiments/emploi_nfp/donnees/kalshi_hist.json'))
live = json.load(open('experiments/emploi_nfp/donnees/kalshi.json'))
seen = {m['ticker'] for m in ms}
ms += [dict(m, live=True) for m in live if m['ticker'] not in seen]
# seuls les seuils Kalshi qui sont une borne d'une tranche Polymarket servent (limite de débit de l'API : ~3 s par appel)
import re
MON = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])}
edges = set()
for r in json.load(open('experiments/emploi_nfp/donnees/marches.json')):
    if r['kind'] != 'jobs': continue
    t = r['bucket'].replace(',', '').replace('–', '-').lower().replace(' ', '').replace('to', '-')
    for x in re.findall(r'\d+(?:\.\d+)?', t): edges.add((tuple(r['ref']), float(x) * 1000))
def utile(m):
    mm = re.search(r'(\d\d)([A-Z]{3})B?$', m['event_ticker'])
    return bool(mm) and m.get('floor_strike') is not None and ((2000 + int(mm.group(1)), MON[mm.group(2)]), float(m['floor_strike'])) in edges
ms = [m for m in ms if utile(m)]
print(len(ms), 'marchés utiles', flush=True)
P = 'experiments/emploi_nfp/donnees/kalshi_bougies.json'
out = json.load(open(P)) if os.path.exists(P) else {}
for i, m in enumerate(ms):
    if m['ticker'] in out or not m.get('close_time'): continue
    t1 = int(dt.datetime.fromisoformat(m['close_time'].replace('Z', '+00:00')).timestamp())
    path = (f"/series/KXPAYROLLS/markets/{m['ticker']}/candlesticks" if m.get('live') else f"/historical/markets/{m['ticker']}/candlesticks")
    for k in range(30):
        r = requests.get(B + path, params={'start_ts': t1 - 8 * 86400, 'end_ts': t1, 'period_interval': 60}, headers=H, timeout=30)
        if r.status_code == 429: time.sleep(min(30, 3 + 2 * k)); continue
        break
    if r.status_code != 200: print(m['ticker'], r.status_code, r.text[:80]); continue
    out[m['ticker']] = {'close': t1, 'floor': m.get('floor_strike'), 'result': m.get('result'), 'value': m.get('expiration_value'),
                        'c': [(c['end_period_ts'], c['yes_bid']['close'], c['yes_ask']['close']) for c in r.json().get('candlesticks', [])]}
    print(i, len(ms), len(out), flush=True); json.dump(out, open(P, 'w'))
    time.sleep(1.2)
json.dump(out, open(P, 'w')); print('fini', len(out))
