import json,re,datetime as dt,collections,math,bisect
from zoneinfo import ZoneInfo
ET=ZoneInfo('America/New_York')
rows=json.load(open('donnees/cal.json'))
days=collections.defaultdict(list)
for r in rows: days[r['date']].append(r)
def first_lid(d):
    ls=sorted(r['time'] for r in days.get(d,[]) if 'travel/photo lid called' in (r['details'] or '').lower() and r['time'] and r['time']>='06:00:00' and 'local' not in (r['details'] or '').lower())
    return ls[0] if ls else None
alld=sorted(d for d in days if d>='2025-02-01')
outc={d:(first_lid(d) is not None and first_lid(d)<='18:30:00') for d in alld}
MON={m:i for i,m in enumerate(['January','February','March','April','May','June','July','August','September','October','November','December'],1)}
H=json.load(open('donnees/lid_hist.json'))
data=[]
for m in H:
    if not m['closed']: continue
    g=re.search(r"on (\w+) (\d+)",m["q"])
    if not g or g.group(1) not in MON: continue
    yr=int(m["end"][:4])
    d=dt.date(yr,MON[g.group(1)],int(g.group(2)))
    if d>dt.date.fromisoformat(m['end'][:10]): d=d.replace(year=yr-1)
    y=json.loads(m['op'])[0]=='1'
    dl=dt.datetime(d.year,d.month,d.day,18,30,tzinfo=ET).timestamp()
    hs=sorted((p['t'],p['p']) for p in m['hist']); ts=[t for t,_ in hs]
    # base rate: same weekday, prior 182 days of rollcall
    wd=d.weekday()
    prior=[outc[x] for x in alld if x<d.isoformat() and x>=(d-dt.timedelta(days=182)).isoformat() and dt.date.fromisoformat(x).weekday()==wd]
    prior_all=[outc[x] for x in alld if x<d.isoformat() and x>=(d-dt.timedelta(days=60)).isoformat()]
    if len(prior)<8: continue
    b=(sum(prior)+1)/(len(prior)+2); b2=(sum(prior_all)+1)/(len(prior_all)+2)
    row=dict(d=d.isoformat(),y=y,b=b,b2=b2,fee=m['fee'])
    for h in [96,72,48,24,12,6,3]:
        T=dl-h*3600; i=bisect.bisect_right(ts,T)-1
        row[h]=hs[i][1] if i>=0 and T-ts[i]<6*3600 else None
    data.append(row)
print('n',len(data), collections.Counter(r['fee'] for r in data))
def ll(p,y): p=min(max(p,0.01),0.99); return math.log(p if y else 1-p)
for h in [96,72,48,24,12,6,3]:
    s=[r for r in data if r[h] is not None]
    if not s: continue
    lm=sum(ll(r[h],r['y']) for r in s)/len(s); lb=sum(ll(r['b'],r['y']) for r in s)/len(s); lb2=sum(ll(r['b2'],r['y']) for r in s)/len(s)
    mix=sum(ll(0.5*r[h]+0.5*r['b'],r['y']) for r in s)/len(s)
    yr=sum(r['y'] for r in s)/len(s); mp=sum(r[h] for r in s)/len(s)
    print(f'h={h:3} n={len(s):3} taux OUI {yr:.3f} prix moyen {mp:.3f} | log marché {lm:.3f} base jour {lb:.3f} base 60j {lb2:.3f} mélange {mix:.3f}')
    # calibration bins
    bins=collections.defaultdict(lambda:[0,0,0])
    for r in s:
        k=min(int(r[h]*5),4); bins[k][0]+=1; bins[k][1]+=r['y']; bins[k][2]+=r[h]
    print('    ', ' '.join(f'[{k/5:.1f}-{(k+1)/5:.1f}) n{v[0]} oui {v[1]/v[0]:.2f} prix {v[2]/v[0]:.2f}' for k,v in sorted(bins.items())))
json.dump(data,open('donnees/lid_data.json','w'))
