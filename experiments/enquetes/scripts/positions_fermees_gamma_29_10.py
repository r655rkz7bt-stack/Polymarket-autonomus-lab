import json,glob,collections,datetime as dt,yaml
from decimal import Decimal as D
S='/tmp/claude-0/-home-user-Polymarket-autonomus-lab/28a98362-cd88-5449-b221-34c45d3f40d3/scratchpad'
closed=set(l.strip() for l in open(S+'/closed_ids.txt'))
now=dt.datetime.now(dt.timezone.utc)
cfg=yaml.safe_load(open('config/strategies.yaml'))
names=set()
def walk(c):
    if isinstance(c,dict):
        for k,v in c.items():
            if isinstance(v,dict) and ('version' in v or 'class' in v or 'type' in v): names.add(k)
            walk(v)
    elif isinstance(c,list):
        for v in c:
            if isinstance(v,dict) and 'name' in v: names.add(v['name'])
            walk(v)
walk(cfg)
print(len(names),list(names)[:5])
res=collections.defaultdict(lambda:[0,D(0),[]])
for f in glob.glob('published_data/ledger/fantome/*')+['published_data/ledger/ledger.jsonl']:
    n=f.split('/')[-1].replace('.jsonl','')
    op={}
    for l in open(f):
        x=json.loads(l); d=x['data']
        if x['type']=='BUY':
            o=op.setdefault(d['token_id'],[d.get('market_id'),D(0),D(0),x['ts']]); o[1]+=D(d['shares']); o[2]+=D(d['price'])*D(d['shares'])
        elif x['type']=='SELL' and d['token_id'] in op: op[d['token_id']][1]-=D(d['shares'])
        elif x['type']=='SETTLE': op.pop(d['token_id'],None)
    for t,o in op.items():
        if o[1]>0 and str(o[0]) in closed:
            r=res[n]; r[0]+=1; r[1]+=o[2]; r[2].append(o[0])
act=0
for n,r in sorted(res.items(),key=lambda kv:-kv[1][1]):
    base=n.rsplit('_v',1)[0]
    print(('ACTIVE ' if base in names or n in names else 'extinct'),n,r[0],round(r[1],1),sorted(set(r[2]))[:4])
print(len(res), sum(r[0] for r in res.values()), sum(r[1] for r in res.values()))
