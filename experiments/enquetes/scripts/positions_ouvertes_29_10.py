import json,glob,collections,datetime as dt,sys
from decimal import Decimal as D
now=dt.datetime.now(dt.timezone.utc)
files=glob.glob('published_data/ledger/fantome/*')+glob.glob('published_data/ledger/*.jsonl')
print(len(files),files[:2])
open_=collections.defaultdict(dict); last_buy={}
for f in files:
    name=f.split('/')[-1]
    for l in open(f):
        x=json.loads(l); d=x['data']
        if x['type']=='BUY':
            o=open_[name].setdefault(d['token_id'],dict(ts=x['ts'],mk=d.get('market_id'),cost=D(0),sh=D(0)))
            o['cost']+=D(d['price'])*D(d['shares']); o['sh']+=D(d['shares']); last_buy[name]=x['ts']
        elif x['type']=='SELL':
            o=open_[name].get(d['token_id'])
            if o: o['sh']-=D(d['shares'])
        elif x['type']=='SETTLE': open_[name].pop(d['token_id'],None)
mk=collections.defaultdict(lambda:[0,D(0),set()])
for n,t in open_.items():
    for tok,o in t.items():
        if o['sh']<=0: continue
        age=(now-dt.datetime.fromisoformat(o['ts'].replace('Z','+00:00'))).total_seconds()/86400
        if age>3:
            m=mk[o['mk']]; m[0]+=1; m[1]+=o['cost']; m[2].add(n)
for k,v in sorted(mk.items(),key=lambda kv:-kv[1][1]): print(k,v[0],round(v[1],1),len(v[2]))
