"""Calibration de compteur_tweets* : gagnés contre estimés et contre prix, par délai, côté et événement (28/10/2026). bash scripts/fetch_data.sh d abord."""
import sys, glob, collections
sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
seen={}
for f in sorted(glob.glob('published_data/ledger/fantome/compteur_tweets*_v1.0.0.jsonl')):
    for p in charger(f):
        if p['token'] in seen: continue
        a=p['achats'][0]
        seen[p['token']]=dict(ev=p['event'],out=p['outcome'],prix=float(p['prix']),est=float(a[3]['est_probability']),edge=float(a[3].get('net_edge',0)),pay=float(p['pay']),mise=float(p['mise']),gain=float(p['gain']),ts=p['ts'][:10],h=float(a[3].get('horizon_hours',0)))
R=list(seen.values())
def tab(name,sel):
    v=[r for r in R if sel(r)]
    if not v: return
    print(f"{name:28s} n={len(v):3d} ev={len({r['ev'] for r in v}):2d} gagnés={sum(r['pay'] for r in v):5.1f} prix={sum(r['prix'] for r in v):5.1f} est={sum(r['est'] for r in v):5.1f} mise={sum(r['mise'] for r in v):7.1f} gain={sum(r['gain'] for r in v):7.1f} rend={sum(r['gain'] for r in v)/sum(r['mise'] for r in v):+.2f}")
tab('tout',lambda r:True)
for lo,hi in [(0,.1),(.1,.2),(.2,.3),(.3,1)]: tab(f'edge {lo}-{hi}',lambda r,lo=lo,hi=hi:lo<=r['edge']<hi)
tab('Yes',lambda r:r['out']=='Yes'); tab('No',lambda r:r['out']=='No')
for lo,hi in [(0,.3),(.3,.5),(.5,.7),(.7,.9),(.9,1)]: tab(f'prix {lo}-{hi}',lambda r,lo=lo,hi=hi:lo<=r['prix']<hi)
for lo,hi in [(0,48),(48,100),(100,400)]: tab(f'horizon {lo}-{hi}h',lambda r,lo=lo,hi=hi:lo<=r['h']<hi)
# par événement : gain
ev=collections.defaultdict(float)
for r in R: ev[r['ev']]+=r['gain']
print(sorted(round(v,1) for v in ev.values()))
