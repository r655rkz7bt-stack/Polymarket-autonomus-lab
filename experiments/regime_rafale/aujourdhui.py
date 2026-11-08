import json,sys,math,bisect,datetime as D
exec(open("backtest.py").read().split("NAMES =")[0])
s=D.datetime(2026,11,6,17,tzinfo=D.timezone.utc).timestamp()
now=D.datetime(2026,11,7,22,15,tzinfo=D.timezone.utc).timestamp()
cnt=n_between(s,now);h=(now-s)/H;rem=168-h
print("compte",cnt,"h",round(h,1))
for n in ("actuel","24h","72h","84j","7j+84j","mediane"):
    r=est(n,now,s);print(n,round(r,3),"/h", "P(>=200)=%.3f"%negbin_interval(200-cnt,10**9,r*rem,12))
# analogues : decisions avec cnt/h < 0.25*rythme actuel, h in 24..48
print("analogues (h 24-48, compte < 35% du rythme 'actuel' x h) :")
for s2 in starts():
    f=n_between(s2,s2+7*86400)
    for hh in (24,48):
        nw=s2+hh*H;c=n_between(s2,nw)
        if c<0.35*est("actuel",nw,s2)*hh:
            print(D.datetime.fromtimestamp(s2,D.timezone.utc).date(),hh,"compte",c,"actuel/h",round(est("actuel",nw,s2),2),"final",f,"P200=%.2f"%negbin_interval(200-c,10**9,est("actuel",nw,s2)*(168-hh),12))
