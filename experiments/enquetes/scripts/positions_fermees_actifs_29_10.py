import json,glob,datetime as dt,sys
from decimal import Decimal as D
S=sys.argv[1]
closed={l.split(' | ')[0]:l.split(' | ') for l in open(S+'/gamma_out.txt') if l.split(' | ')[1]=='True'}
now=dt.datetime.now(dt.timezone.utc)
for f in glob.glob('published_data/ledger/fantome/*')+['published_data/ledger/ledger.jsonl']:
    rows=[json.loads(l) for l in open(f)]
    last=dt.datetime.fromisoformat(rows[-1]['ts'].replace('Z','+00:00'))
    if (now-last).total_seconds()>86400: continue
    op={}
    for x in rows:
        d=x['data']
        if x['type']=='BUY':
            o=op.setdefault(d['token_id'],[d.get('market_id'),D(0),D(0)]); o[1]+=D(d['shares']); o[2]+=D(d['price'])*D(d['shares'])
        elif x['type']=='SELL' and d['token_id'] in op: op[d['token_id']][1]-=D(d['shares'])
        elif x['type']=='SETTLE': op.pop(d['token_id'],None)
    for t,o in op.items():
        if o[1]>0 and str(o[0]) in closed:
            g=closed[str(o[0])]; print(f.split('/')[-1][:45],o[0],round(o[2],1),g[3],g[4],g[5][:50])
