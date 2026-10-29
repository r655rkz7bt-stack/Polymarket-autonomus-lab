"""Cours de 5 minutes sur 60 jours (Yahoo, recherche seulement, jamais en production)."""
import requests, json, sys, time
H = {'User-Agent': 'Mozilla/5.0'}
syms = sys.argv[1:] or ['^GSPC', 'SPY', 'QQQ', '^NDX', '^DJI', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NFLX', 'PLTR', 'COIN', 'MSTR', 'HOOD', 'ORCL', 'AMD', 'GC=F', 'SI=F', 'CL=F']
out = {}
for s in syms:
    for k in range(3):
        r = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/' + requests.utils.quote(s), params={'range': '60d', 'interval': '5m'}, headers=H, timeout=40)
        if r.status_code == 200: break
        time.sleep(3)
    if r.status_code != 200:
        print(s, r.status_code); continue
    j = r.json()['chart']['result'][0]; q = j['indicators']['quote'][0]
    out[s] = dict(t=j['timestamp'], o=q['open'], h=q['high'], l=q['low'], c=q['close'], prev=j['meta'].get('chartPreviousClose'))
    print(s, len(j['timestamp']), flush=True)
json.dump(out, open('experiments/actions_jour/donnees/yahoo_5m.json', 'w'))
