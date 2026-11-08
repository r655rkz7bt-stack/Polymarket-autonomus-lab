"""Ajoute le rythme observé DANS la période au mélange (poids h/(h+k)). 11 réglages essayés au total (voir compte rendu)."""
import json,sys,math,bisect,datetime as D
exec(open("backtest.py").read().split("NAMES =")[0])
def rate(name,now,s,cnt,h):
    r=lambda hh:n_between(now-hh*H,now)/hh
    base={"actuel":.5*r(168)+.5*r(336),"7j+84j":.5*r(168)+.5*r(84*24),"84j":r(84*24)}
    if name in base: return base[name]
    b,k=name.split("@");k=float(k)
    ref={"A":base["actuel"],"B":base["7j+84j"],"C":base["84j"]}[b]
    w=h/(h+k); return (1-w)*ref+w*cnt/h
NAMES=["actuel","7j+84j","84j"]+[f"{b}@{k}" for b in "ABC" for k in (24,48,96)]
tot={n:[0,0] for n in NAMES};ext={n:[0,0] for n in NAMES}
first={}; second={}
for s in starts():
    final=n_between(s,s+7*86400)
    if final==0: continue
    for h in (24,48,72,96,120,144):
        now=s+h*H;cnt=n_between(s,now);rem=168-h
        x_ = est("actuel",now,s)>1.5
        for n in NAMES:
            m=rate(n,now,s,cnt,h)*rem
            for x in range(50,501,25):
                if x<=cnt and final<x: continue
                p=min(max(negbin_interval(x-cnt,10**9,m,12),.005),.995);y=final>=x
                ll=-math.log(p if y else 1-p)
                tot[n][0]+=ll;tot[n][1]+=1
                (first if s<D.datetime(2025,7,1).timestamp() else second).setdefault(n,[0,0]);
                d=(first if s<D.datetime(2025,7,1).timestamp() else second)[n];d[0]+=ll;d[1]+=1
                if x_: ext[n][0]+=ll;ext[n][1]+=1
for n in NAMES:
    print(f"{n:8s} tout {tot[n][0]/tot[n][1]:.4f}  avant7/2025 {first[n][0]/first[n][1]:.4f}  après {second[n][0]/second[n][1]:.4f}  rythme>1,5/h {ext[n][0]/max(ext[n][1],1):.4f} ({ext[n][1]})")
