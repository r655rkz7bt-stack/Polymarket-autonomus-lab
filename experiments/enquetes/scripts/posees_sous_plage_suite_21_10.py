import json,glob,collections
rows=[]
for p in glob.glob('published_data/ledger/fantome/nf_*.jsonl'):
    buys=[];st={}
    for l in open(p):
        d=json.loads(l)
        if d['type']=='BUY': buys.append(d)
        elif d['type']=='SETTLE': st[d['data']['token_id']]=float(d['data']['payout_per_share'])
    for b in buys:
        t=b['data']['token_id']
        if t in st:
            sh=float(b['data']['shares']);pr=float(b['data']['price']);fee=float(b['data'].get('fee') or 0)
            rows.append((p.split('/')[-1][:-12],pr,sh*pr+fee,sh*st[t]-sh*pr-fee,t,b['ts'][:10],b['data']['event_id']))
u={}
for r in rows:u.setdefault((r[4],round(r[1],2)),r)
lo=[r for r in u.values() if r[1]<.8]
byev=collections.defaultdict(lambda:[0,0.0,0.0])
for r in lo:
    e=byev[r[6]];e[0]+=1;e[1]+=r[2];e[2]+=r[3]
print(len(lo),'paris <0.80,',len(byev),'événements')
for k,v in sorted(byev.items(),key=lambda x:x[1][2])[:8]:print(k,v)
bj=collections.Counter();pj=collections.defaultdict(float)
for r in lo:pj[r[5]]+=r[3];bj[r[5]]+=1
print(dict(bj),{k:round(v) for k,v in pj.items()})
# sans les 3 plus gros perdants
s=sorted(lo,key=lambda r:r[3]);print('sans 3 pires pnl',sum(r[3] for r in s[3:]),'misé',sum(r[2] for r in s[3:]))
# par événement : rend moyen
import statistics
ev=[v[2]/v[1] for v in byev.values()];print('rend moyen par événement',statistics.mean(ev),'n',len(ev),'t',statistics.mean(ev)/(statistics.stdev(ev)/len(ev)**.5))
