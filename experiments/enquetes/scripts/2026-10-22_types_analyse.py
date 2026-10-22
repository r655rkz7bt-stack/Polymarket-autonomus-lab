import pickle,re,collections,math
bets=pickle.load(open('/tmp/bets.pkl','rb'));mk=pickle.load(open('/tmp/mk.pkl','rb'))
def kind(b):
    m=mk.get(b['mid']) or {}
    q=m.get('q') or ''
    if q.startswith('Exact Score'):return 'exact_score'
    if re.match(r'Will .* win on \d{4}',q):return 'win_on_date(%s)'%b['out']
    if 'above' in q and 'price of' in q: return 'crypto_above'
    if q.startswith('Spread') or 'Spread' in q: return 'spread'
    if 'O/U' in q or 'Total' in q: return 'total'
    return (m.get('type') or 'autre')
agg=collections.defaultdict(lambda:[0,0,0,0,0,0.0,0.0])
for (sid,tok),b in bets.items():
    if b.get('pay') is None: continue
    p=b['cost']/b['sh']; k=kind(b)
    a=agg[k]; a[0]+=1; a[1]+=b['cost']; a[2]+=b['sh']*b['pay']-b['cost']-b['fee']; a[3]+= (b['pay']>0.5); a[4]+=p; a[5]+= (b['est'] or p); 
for k,a in sorted(agg.items(),key=lambda x:-x[1][1]):
    n=a[0]
    print(f"{k:28s} n={n:4d} mise={a[1]:8.0f} gain={a[2]:7.0f} ({100*a[2]/a[1]:+5.1f}%) gagnés={a[3]:4d} attendus_prix={a[4]:6.1f} annoncés={a[5]:6.1f}")
print("---- dédoublonné par jeton (un jeton = un pari)")
tok=collections.defaultdict(list)
for (sid,t),b in bets.items():
    if b.get('pay') is not None: tok[t].append(b)
agg=collections.defaultdict(lambda:[0,0.0,0.0,0,0.0,0.0,0.0])
for t,L in tok.items():
    b=L[0]; k=kind(b)
    p=sum(x['cost'] for x in L)/sum(x['sh'] for x in L)
    win=b['pay']>0.5; a=agg[k]
    a[0]+=1;a[3]+=win;a[4]+=p;a[5]+= (win-p)**2*0 ; a[1]+= (b['pay']-p) ; a[6]+=p*(1-p)
for k,a in sorted(agg.items(),key=lambda x:-x[1][0]):
    if a[0]<10: continue
    z=(a[3]-a[4])/math.sqrt(a[6]) if a[6] else 0
    print(f"{k:24s} jetons={a[0]:4d} gagnés={a[3]:4d} attendus={a[4]:6.1f} z={z:+.2f} rendement_moyen/part={100*a[1]/a[0]:+.1f}c")
print("---- gros paris de fantômes (mise > seuil), un par (stratégie,jeton)")
for lo,hi in [(0,50),(50,100),(100,200),(200,1e9)]:
    L=[b for b in bets.values() if b.get('pay') is not None and lo<=b['cost']<hi]
    n=len(L);w=sum(b['pay']>0.5 for b in L);ex=sum(b['cost']/b['sh'] for b in L);g=sum(b['sh']*b['pay']-b['cost']-b['fee'] for b in L);c=sum(b['cost'] for b in L)
    est=sum(b['est'] or b['cost']/b['sh'] for b in L)
    print(f"mise {lo:>4}-{hi:<6.0f} n={n:4d} gagnés={w:4d} attendus_prix={ex:6.1f} annoncés={est:6.1f} gain={g:7.0f} ({100*g/c:+.1f}%)")
