"""Kalshi KXPAYROLLS (emplois, seuils « plus de X ») : marchés réglés + prix de clôture par bougie horaire autour de la publication.
Données -> experiments/emploi_nfp/donnees/kalshi.json (ignoré par Git). API publique, limitée (429) : pauses."""
import json, time, requests
B = 'https://api.elections.kalshi.com/trade-api/v2'
H = {'User-Agent': 'curl/8'}
def get(path, **params):
    for k in range(8):
        r = requests.get(B + path, params=params, headers=H, timeout=30)
        if r.status_code == 429: time.sleep(2 + 2 * k); continue
        r.raise_for_status(); time.sleep(0.4); return r.json()
    raise RuntimeError(path)
evs, cur = [], None
while True:
    d = get('/events', series_ticker='KXPAYROLLS', status='settled', limit=100, **({'cursor': cur} if cur else {}))
    evs += d['events']; cur = d.get('cursor')
    if not cur or not d['events']: break
print(len(evs), 'événements réglés', [e['event_ticker'] for e in evs][:40])
out = []
for e in evs:
    d = get('/markets', event_ticker=e['event_ticker'], limit=200)
    for m in d['markets']:
        out.append({k: m.get(k) for k in ('ticker', 'event_ticker', 'title', 'subtitle', 'yes_sub_title', 'strike_type', 'floor_strike', 'cap_strike', 'result', 'close_time', 'expiration_time', 'settlement_value', 'volume', 'status')})
json.dump(out, open('experiments/emploi_nfp/donnees/kalshi.json', 'w'))
print(len(out), 'marchés', out[0])

# marchés plus anciens : API « historical » (au-delà de la date de bascule)
cur, hist = None, []
while True:
    d = get('/historical/markets', series_ticker='KXPAYROLLS', limit=1000, **({'cursor': cur} if cur else {}))
    hist += d['markets']; cur = d.get('cursor')
    if not cur or not d['markets']: break
keep = ('ticker', 'event_ticker', 'floor_strike', 'cap_strike', 'strike_type', 'result', 'close_time', 'expiration_value', 'last_price_dollars', 'volume_fp', 'open_time')
json.dump([{k: m.get(k) for k in keep} for m in hist], open('experiments/emploi_nfp/donnees/kalshi_hist.json', 'w'))
print(len(hist), 'marchés historiques', sorted({m['event_ticker'] for m in hist}))
