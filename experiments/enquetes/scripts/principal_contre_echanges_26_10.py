"""Famille 3/4 : chaque achat du principal est-il exécutable aux vrais échanges ?
Pour chaque BUY du principal (journal signé), cherche dans data-api /trades?market=<conditionId> les échanges
du même jeton dans [-90 s, +90 s] et compare le prix simulé aux vrais prix payés par des preneurs.
Usage : .venv/bin/python experiments/enquetes/scripts/principal_contre_echanges_26_10.py"""
import json, sys, datetime as dt, requests, collections
H = {"User-Agent": "curl/8"}
rows = [json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
buys = [r for r in rows if r['type'] == 'BUY']
def ts(s): return dt.datetime.fromisoformat(s).timestamp()
cond = {}
def condition(mid):
    if mid not in cond:
        r = requests.get(f"https://gamma-api.polymarket.com/markets/{mid}", headers=H, timeout=30)
        cond[mid] = r.json().get('conditionId') if r.ok else None
    return cond[mid]
res = []
for b in buys:
    d = b['data']; t = ts(b['ts']); c = condition(d['market_id'])
    if not c: res.append((b['ts'], d['strategy_id'], d['outcome'], None, None, 'no-cond')); continue
    r = requests.get("https://data-api.polymarket.com/trades", params={"market": c, "limit": 500, "takerOnly": "true"}, headers=H, timeout=30)
    tr = [x for x in (r.json() if r.ok else []) if x.get('asset') == d['token_id']]
    near = [x for x in tr if abs(x['timestamp'] - t) <= 90]
    buysnear = [x for x in near if x.get('side') == 'BUY']
    p = float(d['price'])
    low = min((x['price'] for x in buysnear), default=None)
    res.append((b['ts'], d['strategy_id'], d['outcome'], p, [float(x['price']) for x in near][:6], len(tr)))
for x in res: print(x)
