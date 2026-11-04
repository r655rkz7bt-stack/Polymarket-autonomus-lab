import json,collections,sys,os
sys.path.insert(0,'experiments/enquetes/scripts')
from decimal import Decimal as D
rows=[json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
P=collections.OrderedDict(); S={}
for r in rows:
    d=r['data']
    if r['type']=='BUY' and r['ts']>='2026-10-28':
        k=(d['strategy_id'],d['strategy_version'],d['token_id'])
        p=P.setdefault(k,dict(sh=D(0),cout=D(0),ts=r['ts'],px=[]))
        p['sh']+=D(d['shares']);p['cout']+=D(d['price'])*D(d['shares'])+D(d['fee']);p['px'].append(float(d['price']))
    elif r['type']=='SETTLE': S[d['token_id']]=D(d['payout_per_share'])
print('paris principal depuis 28/10:',len(P))
c=collections.Counter(); sansf=collections.Counter(); ratio=collections.defaultdict(list); pxd=collections.defaultdict(list); plus_tot=0
ghost_tot=collections.Counter()
for (sid,v,t),p in P.items():
    f=f'published_data/ledger/fantome/{sid}_v{v}.jsonl'
    c[sid]+=1
    if not os.path.exists(f): sansf[sid]+=1; continue
    gb=[json.loads(l)['data'] for l in open(f) if '"BUY"' in l]
    gb=[x for x in gb if x['token_id']==t]
    if not gb: sansf[sid]+=1; continue
    gc=sum(D(x['price'])*D(x['shares']) for x in gb); gsh=sum(D(x['shares']) for x in gb)
    gpx=float(gc/gsh)
    pxd[sid].append(sum(p['px'])/len(p['px'])-gpx)
    ratio[sid].append(float(p['cout']/gc))
for sid in c:
    r=ratio[sid]; d=pxd[sid]
    print(f"{sid[:32]:32} n={c[sid]:3} sans_fantome={sansf[sid]:2} prix P-G moy={sum(d)/len(d) if d else 0:+.4f} max={max(d) if d else 0:+.3f} ratio mise med={sorted(r)[len(r)//2] if r else 0:.3f}")
