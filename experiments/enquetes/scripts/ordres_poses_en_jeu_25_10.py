import sys,glob,os,math,collections
sys.path.insert(0,'experiments/enquetes/scripts')
from charge_fantome import charger
tok={}
for f in sorted(glob.glob('published_data/ledger/fantome/*.jsonl'))+['published_data/ledger/ledger.jsonl']:
    nom=os.path.basename(f)
    if not (nom.startswith('nf_') or nom.startswith('naive') or nom=='ledger.jsonl'): continue
    for p in charger(f):
        t=p['token']
        if t in tok: continue
        tok[t]=p
def mode(p): return p['achats'][0][3].get('order_type') or 'marche'
def stats(L):
    n=len(L); 
    if not n: return
    mise=sum(float(p['mise']) for p in L); g=sum(float(p['gain']) for p in L)
    gag=sum(float(p['pay']) for p in L); att=sum(float(p['prix']) for p in L)
    var=sum(float(p['prix'])*(1-float(p['prix'])) for p in L)
    # rendement par pari (mise unitaire) pour t
    r=[ (float(p['pay'])/float(p['prix'])-1) for p in L]
    m=sum(r)/n; sd=(sum((x-m)**2 for x in r)/(n-1))**.5 if n>1 else 0
    return f"n={n:4d} gain={g:7.0f} rend={100*g/mise:6.1f}% unit={100*m:6.1f}% t={m/(sd/math.sqrt(n)) if sd else 0:5.2f} gag/att={gag:6.1f}/{att:6.1f} z={(gag-att)/math.sqrt(var):5.2f}"
L=list(tok.values())
print('total',stats(L))
for m in ('limite','marche'):
    print(m,stats([p for p in L if mode(p)==m]))
for lo,hi in [(0,.8),(.8,.85),(.85,.9),(.9,.95),(.95,1)]:
    for m in ('limite','marche'):
        print(f'{lo}-{hi}',m,stats([p for p in L if mode(p)==m and lo<=float(p['prix'])<hi]))
print('--- robustesse')
lim=[p for p in L if mode(p)=='limite']
byd=collections.defaultdict(list)
for p in lim: byd[p['ts'][:10]].append(p)
for d in sorted(byd): print(d,stats(byd[d]))
# par événement
ev=collections.defaultdict(list)
for p in lim: ev[p['event'] or p['token']].append(float(p['pay'])/float(p['prix'])-1)
r=[sum(v)/len(v) for v in ev.values()]; n=len(r); m=sum(r)/n; sd=(sum((x-m)**2 for x in r)/(n-1))**.5
print('par événement limite: n',n,'moy',round(100*m,1),'t',round(m/(sd/n**.5),2))
ev=collections.defaultdict(list)
for p in L:
    if mode(p)=='marche': ev[p['event'] or p['token']].append(float(p['pay'])/float(p['prix'])-1)
r=[sum(v)/len(v) for v in ev.values()]; n=len(r); m=sum(r)/n; sd=(sum((x-m)**2 for x in r)/(n-1))**.5
print('par événement marché: n',n,'moy',round(100*m,1),'t',round(m/(sd/n**.5),2))
# depuis coup d'envoi (avant / pendant)
for nom,f in [('avant match (h<0)',lambda p: float(p['achats'][0][3].get('depuis_coup_d_envoi_h') or 99)<0),('en cours (h>=0)',lambda p: 0<=float(p['achats'][0][3].get('depuis_coup_d_envoi_h') or -99)),]:
    for m in ('limite','marche'):
        print(nom,m,stats([p for p in L if mode(p)==m and f(p)]))
# sans les 3 plus gros pertes
s=sorted(lim,key=lambda p:float(p['gain']))
print('limite sans 3 pires paris:', round(sum(float(p['gain']) for p in s[3:])), 'sur', round(sum(float(p['mise']) for p in s[3:])))
# premier achat posé, écart entre prix de l'ordre et ask du moment ? champs
print(lim[0]['achats'][0][3])
print('--- hors échantillon (>= 22/10)')
for m in ('limite','marche'):
    print(m,stats([p for p in L if mode(p)==m and p['ts']>='2026-10-22']))
    print(m,'en cours',stats([p for p in L if mode(p)==m and p['ts']>='2026-10-22' and float(p['achats'][0][3].get('depuis_coup_d_envoi_h') or -99)>=0]))
print('avant 22/10')
for m in ('limite','marche'):
    print(m,stats([p for p in L if mode(p)==m and p['ts']<'2026-10-22']))
# sélection adverse directe: prix de l'ordre posé vs meilleur ask à la pose ? champs disponibles
import json
