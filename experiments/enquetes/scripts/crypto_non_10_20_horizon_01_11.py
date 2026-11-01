import sys,math,json
sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
from datetime import datetime
ps=charger('published_data/ledger/fantome/crypto_non_10_20_v1.0.0.jsonl')
print(len(ps))
def stats(L,lab):
    if not L: print(lab,0); return
    mise=sum(p['mise'] for p in L); gain=sum(p['gain'] for p in L)
    att=sum(float(p['prix']) for p in L); g=sum(float(p['pay']) for p in L)
    var=sum(float(p['prix'])*(1-float(p['prix'])) for p in L)
    print(lab,len(L),'ev',len({p['event'] for p in L}),'gagnés',round(g,1),'att',round(att,1),'z',round((g-att)/math.sqrt(var),2),'rend',round(float(gain/mise)*100,1),'%','gain',round(float(gain),1))
stats(ps,'tous')
print(ps[0]['achats'][0][3])
for lo,hi in((0,24),(24,72),(72,168),(168,999)):
    stats([p for p in ps if lo<=float(p['achats'][0][3].get('horizon_hours',-1))<hi],f'h{lo}-{hi}')
# jours de règlement
import collections
d=collections.Counter(p['reglé_ts'][:10] for p in ps if 24<=float(p['achats'][0][3].get('horizon_hours',-1))<72)
print(d)
print(sorted((str(p['prix'])[:5],int(p['pay']),p['reglé_ts'][:10]) for p in ps if 24<=float(p['achats'][0][3].get('horizon_hours',-1))<72))
