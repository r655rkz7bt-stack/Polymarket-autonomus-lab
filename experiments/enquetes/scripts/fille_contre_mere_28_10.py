import sys; sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
from decimal import Decimal as D
import glob
def ch(n):
    return charger(f'published_data/ledger/fantome/{n}_v1.0.0.jsonl')
m=ch('nf_sport_patiente'); f=ch('nf_sport_patiente_prix_850_875')
t0=min(p['ts'] for p in f)
print('fille depuis',t0,len(f),sum(p['gain'] for p in f), sum(p['mise'] for p in f))
mm=[p for p in m if p['ts']>=t0]
print('mere depuis',len(mm),sum(p['gain'] for p in mm),sum(p['mise'] for p in mm))
mr=[p for p in mm if D('0.85')<=p['prix']<=D('0.875')]
print('mere dans plage',len(mr),sum(p['gain'] for p in mr),sum(p['mise'] for p in mr))
fs={p['token'] for p in f}; ms={p['token'] for p in mr}
print('communs',len(fs&ms),'fille seule',len(fs-ms),'mere seule',len(ms-fs))
def r(ps): 
    return sum(p['gain'] for p in ps)/sum(p['mise'] for p in ps) if ps else None
for nm,s in (('communs',fs&ms),('fille seule',fs-ms),('mere seule',ms-fs)):
    a=[p for p in f+mr if p['token'] in s]
    # dedupe
    print(nm, len(s), 'fille', [round(float(p['mise']),0) for p in f if p['token'] in s][:6], 'mere',[round(float(p['mise']),0) for p in mr if p['token'] in s][:6])
for nm,s,src in (('fille seule',fs-ms,f),('mere seule',ms-fs,mr),('communs fille',fs&ms,f),('communs mere',fs&ms,mr)):
    ps=[p for p in src if p['token'] in s]
    print(nm,len(ps),float(sum(p['gain'] for p in ps)),float(sum(p['mise'] for p in ps)), float(r(ps) or 0))
import math, collections
def z(ps):
    exp=sum(float(p['prix']) for p in ps); won=sum(float(p['pay']) for p in ps)
    var=sum(float(p['prix'])*(1-float(p['prix'])) for p in ps)
    return len(ps),round(won,1),round(exp,1),round((won-exp)/math.sqrt(var),2)
print('fille',z(f)); print('fille seule',z([p for p in f if p['token'] in fs-ms]))
print('mere hors plage', z([p for p in mm if not (D('0.85')<=p['prix']<=D('0.875'))]))
# par jour de reglement
d=collections.defaultdict(lambda:[0,0.0])
for p in f: k=str(p['reglé_ts'])[:10]; d[k][0]+=1; d[k][1]+=float(p['gain'])
print(sorted(d.items()))
# retire les 3 plus gros gains
g=sorted(f,key=lambda p:-p['gain']); print('sans top3', float(sum(p['gain'] for p in g[3:])), [round(float(p['gain'])) for p in g[:5]])
# paris par cycle (ts arrondi minute) de la fille vs mere
cy=collections.Counter(p['ts'][:16] for p in f); print('fille paris/cycle', collections.Counter(cy.values()))
cm=collections.Counter(p['ts'][:16] for p in mm); print('mere paris/cycle', collections.Counter(cm.values()))
