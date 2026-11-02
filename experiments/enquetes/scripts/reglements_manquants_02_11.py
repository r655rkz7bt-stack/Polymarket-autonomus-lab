import json,glob,collections,requests
from decimal import Decimal as D
from concurrent.futures import ThreadPoolExecutor
pos=collections.defaultdict(list)
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    rows=[json.loads(l) for l in open(f)]
    if rows[-1]['ts'][:10]!='2026-11-02': continue
    b={};s=set()
    for x in rows:
        d=x['data']
        if x['type']=='BUY': b.setdefault(d['token_id'],[x['ts'],d['market_id'],D(0)])[2]+=D(d['price'])*D(d['shares'])
        if x['type']=='SETTLE': s.add(d['token_id'])
    for t,(ts,m,c) in b.items():
        if t not in s and ts<'2026-10-30': pos[m].append((f.split('/')[-1][:-6],t,c,ts))
print(len(pos),'marchés')
S=requests.Session();S.headers['User-Agent']='curl/8'
def g(m):
    try: return m,S.get(f'https://gamma-api.polymarket.com/markets/{m}',timeout=20).json()
    except Exception as e: return m,None
with ThreadPoolExecutor(8) as ex: R=dict(ex.map(g,pos))
tot=D(0);byS=collections.Counter();n=0
for m,j in R.items():
    if j and j.get('closed'):
        for s,t,c,ts in pos[m]: tot+=c;byS[s]+=1;n+=1
        print(m,j.get('closedTime'),j.get('umaResolutionStatus'),j.get('outcomePrices'),j['question'][:50],len(pos[m]))
print(n,'positions',tot)
print(byS.most_common(10))
