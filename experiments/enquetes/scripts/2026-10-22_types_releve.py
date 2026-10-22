import json,glob,re,requests,os,collections,pickle
H={'User-Agent':'curl/8'}
cache_f='/tmp/mk.pkl'
cache=pickle.load(open(cache_f,'rb')) if os.path.exists(cache_f) else {}
bets={}  # (strat,token)-> dict
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    sid=os.path.basename(f)[:-6]
    rows=[json.loads(l) for l in open(f)]
    sett={r['data']['token_id']:float(r['data']['payout_per_share']) for r in rows if r['type']=='SETTLE'}
    for r in rows:
        if r['type']!='BUY': continue
        d=r['data'];k=(sid,d['token_id'])
        b=bets.setdefault(k,dict(cost=0,sh=0,fee=0,est=None,mid=d['market_id'],out=d['outcome'],ts=r['ts']))
        sh=float(d['shares']);p=float(d['price'])
        b['cost']+=sh*p;b['sh']+=sh;b['fee']+=float(d.get('fee',0))
        e=d['extra'].get('est_probability')
        if e: b['est']=float(e)
    for k,b in bets.items():
        if k[0]==sid: b['pay']=sett.get(k[1])
mids={b['mid'] for b in bets.values()}-set(cache)
print(len(bets),len(mids))
from concurrent.futures import ThreadPoolExecutor
def get(m):
    try:
        j=requests.get('https://gamma-api.polymarket.com/markets/'+m,headers=H,timeout=20).json()
        return m,{'q':j.get('question'),'type':j.get('sportsMarketType'),'ev':(j.get('events') or [{}])[0].get('title')}
    except Exception as e: return m,None
with ThreadPoolExecutor(8) as ex:
    for m,v in ex.map(get,mids): 
        if v: cache[m]=v
pickle.dump(cache,open(cache_f,'wb'))
pickle.dump(bets,open('/tmp/bets.pkl','wb'))
