"""Échanges réels (data-api) des marchés « <action> Up or Down on <date> ? » réglés depuis août 2026."""
import requests, json, re, sys, concurrent.futures as cf, os
H = {'User-Agent': 'curl/8'}
OK = {'SPX', 'SPY', 'RUT', 'DJIA', 'META', 'NVDA', 'GOOGL', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'PLTR', 'NFLX', 'HOOD', 'COIN', 'RKLB', 'OPEN', 'MU', 'ABNB', 'WTI', 'XAUUSD', 'XAGUSD', 'NG'}
ev = json.load(open('experiments/actions_jour/donnees/evenements.json'))
cas = []
for e in ev:
    m = re.match(r'^(.*)\((.+)\) Up or Down on (.+)\?$', e['title'])
    if not m or m.group(2) not in OK or 'Opens' in e['title']: continue
    mk = e['markets'][0]
    cas.append(dict(event=e['id'], ticker=m.group(2), date=m.group(3), cid=mk['conditionId'], tokens=json.loads(mk['clobTokenIds']), outcomes=json.loads(mk['outcomes']),
                    prices=json.loads(mk['outcomePrices']), end=e['endDate'], closed=e['closedTime'], vol=mk.get('volume'), start=e['startDate']))
print(len(cas), flush=True)
def trades(c):
    out = []; off = 0
    while off <= 10000:
        for k in range(4):
            try:
                r = requests.get('https://data-api.polymarket.com/trades', params={'market': c['cid'], 'limit': 1000, 'offset': off, 'takerOnly': 'false'}, headers=H, timeout=40)
                if r.status_code == 200: break
            except Exception: pass
        else: break
        j = r.json()
        out += [dict(ts=t['timestamp'], p=t['price'], s=t['size'], side=t['side'], o=t['outcome'], w=t.get('proxyWallet')) for t in j]
        if len(j) < 1000: break
        off += 1000
    return out
res = []
with cf.ThreadPoolExecutor(6) as ex:
    for c, t in zip(cas, ex.map(trades, cas)):
        c['trades'] = t; res.append(c)
        if len(res) % 100 == 0: print(len(res), flush=True)
json.dump(res, open('experiments/actions_jour/donnees/echanges.json', 'w'))
print('fini', sum(len(c['trades']) for c in res))
