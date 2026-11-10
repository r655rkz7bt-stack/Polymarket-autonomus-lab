import json,sys
sys.path.insert(0,'/home/user/Polymarket-autonomus-lab/src')
from polymarket_agent.idea_test import verdict
D=json.load(open('donnees/lid_data.json'))
def sim(h,lo,hi,spread=0.015):
    bets=[]
    for r in D:
        p=r.get(str(h)) if str(h) in r else r.get(h)
        if p is None or not (lo<=p<hi): continue
        c=p+spread; c+=0.04*c*(1-c)
        g=(1.0 if r['y'] else 0.0)/c-1
        bets.append(dict(gain=g,evenement=r['d'],mois=r['d'][:7],cout=c))
    return bets
n=0
for h in [72,48,24,12]:
    for lo,hi in [(0.30,0.60),(0.40,0.60),(0.35,0.55),(0.20,0.70)]:
        b=sim(h,lo,hi); n+=1
        v=verdict(b)
        print(h,lo,hi,v['paris'],v.get('rendement_moyen'),'t_ev',v.get('confiance_evenements'),'z',v.get('z_prix'),v.get('mois_gagnants'),v.get('verdict'))
print('réglages essayés',n)
v=verdict(sim(24,0.30,0.60)); print(json.dumps(v,ensure_ascii=False,indent=0)[:1500])
