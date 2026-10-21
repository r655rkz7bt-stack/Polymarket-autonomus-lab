"""Bougies horaires (meilleur acheteur / vendeur à la clôture) de chaque marché Kalshi KXPAYROLLS, 8 jours avant la publication.
Données -> experiments/emploi_nfp/donnees/kalshi_bougies.json (ignoré par Git). Reprend là où il s'est arrêté."""
import json, time, requests, os, datetime as dt
B = 'https://api.elections.kalshi.com/trade-api/v2'; H = {'User-Agent': 'curl/8'}
ms = json.load(open('experiments/emploi_nfp/donnees/kalshi_hist.json'))
live = json.load(open('experiments/emploi_nfp/donnees/kalshi.json'))
seen = {m['ticker'] for m in ms}
ms += [dict(m, live=True) for m in live if m['ticker'] not in seen]
P = 'experiments/emploi_nfp/donnees/kalshi_bougies.json'
out = json.load(open(P)) if os.path.exists(P) else {}
for i, m in enumerate(ms):
    if m['ticker'] in out or not m.get('close_time'): continue
    t1 = int(dt.datetime.fromisoformat(m['close_time'].replace('Z', '+00:00')).timestamp())
    path = (f"/series/KXPAYROLLS/markets/{m['ticker']}/candlesticks" if m.get('live') else f"/historical/markets/{m['ticker']}/candlesticks")
    for k in range(10):
        r = requests.get(B + path, params={'start_ts': t1 - 8 * 86400, 'end_ts': t1, 'period_interval': 60}, headers=H, timeout=30)
        if r.status_code == 429: time.sleep(2 + 2 * k); continue
        break
    if r.status_code != 200: print(m['ticker'], r.status_code, r.text[:80]); continue
    out[m['ticker']] = {'close': t1, 'floor': m.get('floor_strike'), 'result': m.get('result'), 'value': m.get('expiration_value'),
                        'c': [(c['end_period_ts'], c['yes_bid']['close'], c['yes_ask']['close']) for c in r.json().get('candlesticks', [])]}
    if i % 25 == 0: print(i, len(ms), flush=True); json.dump(out, open(P, 'w'))
    time.sleep(0.3)
json.dump(out, open(P, 'w')); print('fini', len(out))
