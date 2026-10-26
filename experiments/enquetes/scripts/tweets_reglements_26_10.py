import sys, json, requests
sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
ps=charger('published_data/ledger/fantome/compteur_tweets_v1.0.0.jsonl')
print(len(ps))
H={'User-Agent':'curl/8'}
bad=0
for p in ps:
    m=requests.get(f"https://gamma-api.polymarket.com/markets/{p['market']}",headers=H,timeout=30).json()
    op=json.loads(m['outcomes']); pr=json.loads(m['outcomePrices'])
    i=op.index(p['outcome']) if p['outcome'] in op else None
    ok = i is not None and abs(float(pr[i])-float(p['pay']))<1e-6
    if not ok: bad+=1
    print(p['ts'][5:16], p['outcome'], round(float(p['prix']),2), round(float(p['gain']),1), 'OK' if ok else f'MISMATCH gamma={pr} ledger={p["pay"]}', '|', m['question'][:90], '|', (m.get('endDate') or '')[:10])
print('mismatch',bad)
