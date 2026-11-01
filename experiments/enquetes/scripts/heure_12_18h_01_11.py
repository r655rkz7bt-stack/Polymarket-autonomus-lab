import sys,glob,os,math,collections
sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
from decimal import Decimal as D
seen={}
for f in sorted(glob.glob('published_data/ledger/fantome/*.jsonl')):
    n=os.path.basename(f)
    if not n.startswith('nf_sport') and not n.startswith('nf_court') and not n.startswith('naive'): continue
    if 'principal' in n: continue
    try: ps=charger(f)
    except Exception as e: continue
    for p in ps:
        seen.setdefault(p['token'],(n,p))
by=collections.defaultdict(list)
for t,(n,p) in seen.items():
    h=int(p['ts'][11:13]); by['12-18' if 12<=h<18 else 'autre'].append(p)
for k,L in by.items():
    mise=sum(p['mise'] for p in L); gain=sum(p['gain'] for p in L)
    att=sum(float(p['prix']) for p in L); g=sum(float(p['pay']) for p in L)
    var=sum(float(p['prix'])*(1-float(p['prix'])) for p in L)
    ev=len({p['event'] for p in L})
    print(k,len(L),'events',ev,'gagnés',round(g,1),'attendus',round(att,1),'z',round((g-att)/math.sqrt(var),2),'rend',round(float(gain/mise)*100,1),'%')
