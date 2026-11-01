import sys, glob, collections
sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
import math
for name in ['nf_sport_patiente_6_24h_6_12h','nf_sport_patiente_6_24h','nf_sport_patiente_avant_match']:
    f=glob.glob(f'published_data/ledger/fantome/{name}*/ledger.jsonl') or glob.glob(f'published_data/ledger/fantome/*{name}*')
    print(name,f[:2])
    if not f: continue
    ps=charger(f[0])
    gain=sum(p['gain'] for p in ps); mise=sum(p['mise'] for p in ps)
    att=sum(float(p['prix']) for p in ps); gag=sum(float(p['pay']) for p in ps)
    var=sum(float(p['prix'])*(1-float(p['prix'])) for p in ps)
    z=(gag-att)/math.sqrt(var) if var else 0
    print(' n',len(ps),'gain',round(float(gain),1),'mise',round(float(mise),1),'rend',round(float(gain/mise)*100,1),'gagnés',gag,'attendus',round(att,1),'z',round(z,2))
    ev=collections.defaultdict(float)
    for p in ps: ev[p['event']]+=float(p['gain'])
    print(' événements',len(ev),'sans 3 plus gros paris', round(float(gain)-sum(sorted([float(p['gain']) for p in ps])[-3:]),1))
    for p in sorted(ps,key=lambda p:-p['gain'])[:4]: print('  ',p['outcome'],round(float(p['prix']),3),round(float(p['mise']),1),round(float(p['gain']),1))
    for p in sorted(ps,key=lambda p:p['gain'])[:3]: print('  perte',p['outcome'],round(float(p['prix']),3),round(float(p['mise']),1),round(float(p['gain']),1))
