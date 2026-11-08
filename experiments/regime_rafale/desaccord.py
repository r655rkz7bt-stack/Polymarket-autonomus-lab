"""Quand 'actuel' et la médiane des 5 rythmes divergent de plus d'un facteur 1,6, qui a raison ?"""
import json,sys,math,bisect,datetime as D
exec(open("backtest.py").read().split("NAMES =")[0])
acc={}
for s in starts():
    final=n_between(s,s+7*86400)
    if final==0: continue
    for h in (24,48,72,96,120,144):
        now=s+h*H;cnt=n_between(s,now);rem=168-h
        a,m=est("actuel",now,s),est("mediane",now,s)
        k="desaccord" if a>1.6*m else ("accord" )
        for x in range(50,501,25):
            if x<=cnt and final<x: continue
            y=final>=x
            for n,r in (("actuel",a),("mediane",m)):
                p=min(max(negbin_interval(x-cnt,10**9,r*rem,12),.005),.995)
                d=acc.setdefault((k,n),[0,0,0,0]);d[0]+=-math.log(p if y else 1-p);d[1]+=1;d[2]+=p;d[3]+=y
for k,v in sorted(acc.items()):print(k,"logloss %.4f n=%d dit %.3f réel %.3f"%(v[0]/v[1],v[1],v[2]/v[1],v[3]/v[1]))
