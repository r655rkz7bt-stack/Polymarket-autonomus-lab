import json,collections,sys,glob
sys.path.insert(0,'experiments/enquetes/scripts')
from decimal import Decimal as D
rows=[json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
P=collections.OrderedDict(); S={}
for r in rows:
    d=r['data']
    if r['type']=='BUY':
        k=(d['strategy_id'],d['strategy_version'],d['token_id'])
        p=P.setdefault(k,dict(sh=D(0),cout=D(0),ts=r['ts'],px=[],outcome=d['outcome']))
        p['sh']+=D(d['shares']);p['cout']+=D(d['price'])*D(d['shares'])+D(d['fee']);p['px'].append(float(d['price']))
    elif r['type']=='SETTLE': S[d['token_id']]=D(d['payout_per_share'])
import charge_fantome as cf
by=collections.defaultdict(list)
for (sid,v,t),p in P.items(): by[(sid,v)].append((t,p))
tot_p=tot_g=0
print("strat n_princ settled gain_p cout_p | ghost same tokens gain_g cout_g | ghost prix moy / princ prix moy")
for (sid,v),lst in sorted(by.items(), key=lambda x:-len(x[1])):
    f=f'published_data/ledger/fantome/{sid}_v{v}.jsonl'
    try: g={x['token']:x for x in cf.charger(f)}
    except Exception as e: print(sid,'no ghost',e); continue
    gp=gg=cp=cg=0;n=0;dpx=[];
    for t,p in lst:
        if t in S and t in g:
            n+=1
            gp+=p['sh']*S[t]-p['cout']; cp+=p['cout']
            gg+=g[t]['gain']; cg+=g[t]['cout']
            dpx.append(sum(p['px'])/len(p['px'])-float(g[t]['prix']))
    m=[t for t,p in lst if t not in g]
    if n or m: print(f"{sid[:34]:34} princ={len(lst):3} regl_communs={n:3} P:{float(gp):7.2f}/{float(cp):7.1f} ({float(gp/cp)*100 if cp else 0:5.1f}%)  G:{float(gg):7.2f}/{float(cg):8.1f} ({float(gg/cg)*100 if cg else 0:5.1f}%) ecart_px_moy={sum(dpx)/len(dpx) if dpx else 0:+.4f} sans_fantome={len(m)}")
    tot_p+=gp
print('total gain principal sur tous reglés', float(tot_p))

print('---- nf_sport sans fantome')
import os
gh={}
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r['type']=='BUY': gh.setdefault(r['data']['token_id'],[]).append((os.path.basename(f)[:30],r['ts'][:16],r['data']['price'],r['data']['shares']))
for (sid,v,t),p in P.items():
    if sid=='nf_sport':
        f=f'published_data/ledger/fantome/{sid}_v{v}.jsonl'
        mine=[x for x in gh.get(t,[]) if x[0].startswith('nf_sport_v1')]
        if not mine: print(p['ts'][:16], float(p['sh']), p['px'][:1], 'ghost nf_sport:',mine, 'autres:', [(a[0],a[1]) for a in gh.get(t,[])][:3])

print('---- nf_court par jeton')
g={x['token']:x for x in cf.charger('published_data/ledger/fantome/nf_court_v1.0.0.jsonl')}
for (sid,v,t),p in P.items():
    if sid=='nf_court' and t in S and t in g:
        x=g[t]
        print(p['ts'][5:16], 'P px %.3f sh %6.2f mise %6.2f gain %7.2f | G px %.3f sh %7.2f mise %7.1f gain %7.1f | ratio mise P/G %.3f pay %s'%(sum(p['px'])/len(p['px']),p['sh'],p['cout'],p['sh']*S[t]-p['cout'],x['prix'],x['sh'],x['cout'],x['gain'],p['cout']/x['cout'],S[t]))

print('---- depuis 21/10: tous reglés ou non, principal vs fantome (mise relative au capital)')
import statistics as st
for (sid,v,t),p in P.items(): pass
cap_p=None
res=collections.defaultdict(list)
miss=collections.Counter(); tot=collections.Counter()
for (sid,v,t),p in P.items():
    if p['ts']<'2026-10-21': continue
    tot[sid]+=1
    f=f'published_data/ledger/fantome/{sid}_v{v}.jsonl'
    if not os.path.exists(f): miss[sid]+=1; continue
    gb=[json.loads(l) for l in open(f)]
    gb=[r['data'] for r in gb if r['type']=='BUY' and r['data']['token_id']==t]
    if not gb: miss[sid]+=1; continue
    gc=sum(D(x['price'])*D(x['shares']) for x in gb); pc=sum(D(x['price'])*D(x['shares']) for x in gb)*0+p['cout']
    res[sid].append(float(pc/gc))
for sid,l in res.items(): print(sid, len(l), 'ratio mise P/G médian %.3f min %.3f max %.3f'%(st.median(l),min(l),max(l)))
print('sans jumeau', dict(miss), 'total', dict(tot))
