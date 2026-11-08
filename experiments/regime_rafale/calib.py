import json,sys,math,bisect,datetime as D
exec(open("backtest.py").read().split("NAMES =")[0])
rows=[]
for s in starts():
    final=n_between(s,s+7*86400)
    if final==0: continue
    for h in (24,48,72,96,120,144):
        now=s+h*H;cnt=n_between(s,now);rem=168-h
        ms={n:est(n,now,s)*rem for n in ("actuel","7j+84j","84j","72h")}
        for x in (100,150,200,250,300):
            if x<=cnt: continue
            rows.append((s,h,x,final>=x,{n:negbin_interval(x-cnt,10**9,m,12) for n,m in ms.items()}))
for n in ("actuel","7j+84j","84j"):
    print(n)
    for lo,hi in ((0,.1),(.1,.3),(.3,.5),(.5,.7),(.7,.9),(.9,.99),(.99,1.01)):
        b=[r for r in rows if lo<=r[4][n]<hi]
        if b:
            # par fenêtre : 1 tirage
            ev={(r[0],r[2]) for r in b}
            print(f"  {lo:.2f}-{hi:.2f} n={len(b)} fenêtres-seuils={len(ev)} dit {sum(r[4][n] for r in b)/len(b):.2f} réel {sum(r[3] for r in b)/len(b):.2f}")
