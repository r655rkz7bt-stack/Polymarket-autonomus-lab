import json
from decimal import Decimal as D
def load(n):
    return [json.loads(l) for l in open(f'published_data/ledger/fantome/{n}_v1.0.0.jsonl')]
m=load('nf_sport_patiente'); f=load('nf_sport_patiente_prix_850_875')
print(set(x['type'] for x in m))
print([x for x in m if x['type'] not in('BUY','SELL','SETTLE')][:2])
# solde disponible dans mere au moment de chaque achat de fille seule
import bisect
def timeline(rows):
    cash=None; tl=[]
    for x in rows:
        d=x['data']
        if 'cash_after' in d: tl.append((x['ts'],d['cash_after']))
    return tl
print(m[0]); print(m[5])
import sys; sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
mh=[(x['ts'],D(x['data']['cash']),D(x['data']['total_estimated'])) for x in m if x['type']=='HEARTBEAT']
fp=charger('published_data/ledger/fantome/nf_sport_patiente_prix_850_875_v1.0.0.jsonl')
mp=charger('published_data/ledger/fantome/nf_sport_patiente_v1.0.0.jsonl')
mtok={p['token'] for p in mp}
rows=[]
for p in fp:
    if p['token'] in mtok: continue
    ts=p['ts']; c=[h for h in mh if h[0]<=ts]
    if not c: continue
    cash,tot=c[-1][1],c[-1][2]
    rows.append((ts[:16],float(p['mise']),float(cash),float(tot)))
print(len(rows),'paris fille seule; mere cash < mise fille:',sum(1 for r in rows if r[2]<r[1]),'; cash < 2x mise:',sum(1 for r in rows if r[2]<2*r[1]))
import statistics
print('cash mere median',statistics.median(r[2] for r in rows),'mise fille median',statistics.median(r[1] for r in rows))
for r in rows[:12]: print(r)
print('----')
mev={}
for p in mp: mev.setdefault(p['event'],[]).append(p)
n_same_event=0; n_mother_bet_same_cycle=0; tot=0
for p in fp:
    if p['token'] in mtok: continue
    tot+=1
    if p['event'] in mev: n_same_event+=1
    near=[q for q in mp if abs((__import__('datetime').datetime.fromisoformat(q['ts'])-__import__('datetime').datetime.fromisoformat(p['ts'])).total_seconds())<900]
    if near: n_mother_bet_same_cycle+=1
print(tot,'fille seule; mere a deja/aussi un pari sur le meme evenement:',n_same_event,'; mere a parie dans les 15 min:',n_mother_bet_same_cycle)
# prix de la mere dans ces cycles
