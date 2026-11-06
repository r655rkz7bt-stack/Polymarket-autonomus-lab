import json,collections
from decimal import Decimal as D
rows=[json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
buy=collections.defaultdict(lambda:[D(0),D(0),None]);st={}
sett={}
for x in rows:
    d=x['data']
    if x['type']=='BUY':
        b=buy[d['token_id']];b[0]+=D(d['shares']);b[1]+=D(d['price'])*D(d['shares'])+D(d['fee']);b[2]=d['strategy_id']
    elif x['type']=='SETTLE': sett[d['token_id']]=D(d['payout_per_share'])
g=collections.defaultdict(lambda:[0,D(0),D(0),0.0,0.0])
for t,(sh,c,s) in buy.items():
    if t not in sett: continue
    r=g[s];r[0]+=1;r[1]+=sh*sett[t]-c;r[2]+=c;r[3]+=float(sett[t]);r[4]+=float(c/sh)
for s,r in sorted(g.items(),key=lambda x:x[1][1]):
    print(f"{s[:36]:36} n={r[0]:3} gain={float(r[1]):7.1f} mise={float(r[2]):7.1f} rend={float(r[1]/r[2])*100:6.1f}% gagnes={r[3]:.1f} att={r[4]:.1f}")
