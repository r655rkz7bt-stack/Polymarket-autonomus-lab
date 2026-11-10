import json,sys,re,datetime as dt
from zoneinfo import ZoneInfo
sys.path.insert(0,'/home/user/Polymarket-autonomus-lab/src')
from polymarket_agent.idea_test import verdict, taker_cost
ET=ZoneInfo('America/New_York')
T=json.load(open('donnees/lid_trades.json')); H={m['id']:m for m in json.load(open('donnees/lid_hist.json'))}
D={r['d']:r for r in json.load(open('donnees/lid_data.json'))}
MON={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
bad=sum(1 for i,d in T.items() if any(t[1] not in d['toks'] for t in d['trades'])); print('marchés avec jetons étrangers',bad)
import bisect
def run(h,lo,hi,win=3*3600,minsh=0):
    bets=[]; miss=0
    for i,m in H.items():
        g=re.search(r"on (\w+) (\d+)",m['q'])
        if not g or g.group(1) not in MON or not m['closed']: continue
        yr=int(m['end'][:4]); d=dt.date(yr,MON[g.group(1)],int(g.group(2)))
        if d>dt.date.fromisoformat(m['end'][:10]): d=d.replace(year=yr-1)
        r=D.get(d.isoformat()); 
        if not r: continue
        p=r.get(str(h))
        if p is None or not(lo<=p<hi): continue
        dl=int(dt.datetime(d.year,d.month,d.day,18,30,tzinfo=ET).timestamp()); ts=dl-h*3600
        tr=T[i]['trades']; yes,no=T[i]['toks']
        c=taker_cost(tr,yes,no,ts,window=win,after=True)
        if c is None: miss+=1; continue
        if minsh:
            sh=sum(t[4] for t in tr if ts<=t[0]<=ts+win and ((t[1]==yes and t[2]=='BUY' and t[3]<=c+0.02) or (t[1]==no and t[2]=='SELL' and 1-t[3]<=c+0.02)))
            if sh<minsh: miss+=1; continue
        cc=c+0.04*c*(1-c)
        bets.append(dict(gain=(1.0 if r['y'] else 0.0)/cc-1,evenement=r['d'],mois=r['d'][:7],cout=cc,p=p,c=c))
    return bets,miss
for h in [72,48,24,12]:
    for lo,hi in [(0.30,0.60),(0.40,0.60)]:
        for minsh in [0,50]:
            b,miss=run(h,lo,hi,minsh=minsh); v=verdict(b)
            import statistics
            print(h,lo,hi,'min parts',minsh,'paris',len(b),'sans échange',miss,'prix histo moyen %.3f payé moyen %.3f'%(statistics.mean(x['p'] for x in b),statistics.mean(x['c'] for x in b)) if b else '', v.get('rendement_moyen'),'t',v.get('confiance_evenements'),'z',v.get('z_prix'),v.get('mois_gagnants'),v['verdict'])
b,_=run(24,0.30,0.60); v=verdict(b); print(v['mois'], v.get('moitie_1'), v.get('moitie_2'))
