"""Le principal obtient-il un prix meilleur que tout échange réel autour de lui ? (±120 s, tous échanges du jeton)
Un prix payé inférieur au plus bas prix réellement échangé (achats ET ventes) dans la fenêtre = irréaliste."""
import json, requests, datetime as dt
H = {"User-Agent": "curl/8"}
rows = [json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
n = vide = pire = 0; bad = []
cache = {}
for r in rows:
    if r['type'] != 'BUY': continue
    d = r['data']; t = dt.datetime.fromisoformat(r['ts']).timestamp()
    mid = d['market_id']
    if mid not in cache:
        m = requests.get(f"https://gamma-api.polymarket.com/markets/{mid}", headers=H, timeout=30).json()
        tr = requests.get("https://data-api.polymarket.com/trades", params={"market": m['conditionId'], "limit": 500}, headers=H, timeout=30).json()
        cache[mid] = tr if isinstance(tr, list) else []
    tr = [x for x in cache[mid] if x['asset'] == d['token_id'] and abs(x['timestamp'] - t) <= 120]
    n += 1
    if not tr: vide += 1; continue
    lo = min(x['price'] for x in tr); p = float(d['price'])
    if p < lo - 0.005:
        bad.append((r['ts'][:19], d['strategy_id'], d['outcome'], p, round(lo, 3), len(tr), d['extra'].get('fill_status')))
print(n, 'achats;', vide, 'sans échange à ±120 s;', len(bad), 'à un prix sous le plus bas échange réel')
for b in bad: print(b)
