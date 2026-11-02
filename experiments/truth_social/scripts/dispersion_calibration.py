"""Calibre la dispersion de la loi binomiale négative sur les semaines de posts Trump (archive trumpstruth.org) : log-score par tranche à 54, 120 et 220 h avant le début de la fenêtre. Lancer depuis la racine du dépôt (02/11/2026)."""
import csv,bisect,sys,math
sys.path.insert(0,'src')
from datetime import datetime,timedelta
from polymarket_agent.references import negbin_interval
ts=sorted(datetime.fromisoformat(r['ts_utc']) for r in csv.DictReader(open('experiments/truth_social/releves/posts.csv')))
def cnt(a,b): return bisect.bisect_left(ts,b)-bisect.bisect_left(ts,a)
BUCKETS=[(0,19),(20,39),(40,59),(60,79),(80,99),(100,119),(120,139),(140,159),(160,179),(180,199),(200,10**9)]
def run(lead,rw,disp,rh=168,lh=336,shrink=0.0,mu_long=None):
    ll=0;n=0;ls=[]
    s=ts[0]+timedelta(days=15+ (lh//24 -14 if lh>336 else 0))
    while s+timedelta(days=7)<=ts[-1]:
        T=s-timedelta(hours=lead)
        rec=cnt(T-timedelta(hours=rh),T)/rh; lon=cnt(T-timedelta(hours=lh),T)/lh
        fc=(rw*rec+(1-rw)*lon)*168
        if shrink and mu_long: fc=(1-shrink)*fc+shrink*mu_long
        act=cnt(s,s+timedelta(days=7))
        for lo,hi in BUCKETS:
            if lo<=act<=hi:
                p=negbin_interval(lo,hi,fc,disp); ll+=math.log(max(p,1e-6)); n+=1
        s+=timedelta(hours=12)
    return ll/n
if __name__=='__main__':
    for lead in (54,120,220):
        print('lead',lead,'actuel',round(run(lead,0.5,12),4))
        best=[]
        for rw in (0,0.2,0.35,0.5):
            for disp in (3,5,8,12):
                for lh in (336,672):
                    best.append((run(lead,rw,disp,168,lh),rw,disp,lh))
        best.sort(reverse=True)
        print(' meilleurs',[(round(a,4),b,c,d) for a,b,c,d in best[:5]])
