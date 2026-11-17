"""Piste n° 65, barrières (17/11/2026) : historiques horaires (prices-history) des sous-jacents (400 j) et des barrières (90 j) -> histo.json."""
import json, requests, time, concurrent.futures as cf
s = requests.Session(); s.headers['User-Agent'] = 'polymarket-autonomous-lab'
def hist(tok, jours=400):
    fin=int(time.time()); t=fin-jours*86400; pts={}
    while t<fin:
        t2=min(fin,t+13*86400)
        for _ in range(3):
            try:
                for p in s.get('https://clob.polymarket.com/prices-history',params={'market':tok,'startTs':t,'endTs':t2,'fidelity':60},timeout=30).json().get('history') or []:
                    pts[int(p['t'])//3600]=float(p['p'])
                break
            except Exception: time.sleep(1)
        t=t2
    return pts
toks=json.load(open('tokens.json'))
evs=json.load(open('barr.json'))
und={}
for k,v in toks.items():
    tok=v['token']
    if not tok:
        m=s.get(f"https://gamma-api.polymarket.com/markets/{v['market']}",timeout=30).json(); tok=json.loads(m['clobTokenIds'])[0]; v['token']=tok
    und[k]=tok
bar={}
for e in evs:
    t=e['title']
    if not (' hit ' in t or ' dip ' in t): continue
    for m in e['markets']:
        try: tk=json.loads(m['clobTokenIds'])[0]
        except Exception: continue
        bar[m['id']]={'event':e['id'],'titre':t,'question':m['question'],'token':tk,'cree':m.get('createdAt') or e.get('createdAt'),'fin':m.get('endDate') or e.get('endDate'),
                      'closed':m.get('closed'),'issue':m.get('outcomePrices'),'bid':m.get('bestBid'),'ask':m.get('bestAsk')}
jobs={('U',k):t for k,t in und.items()}; jobs.update({('B',k):v['token'] for k,v in bar.items()})
res={}
with cf.ThreadPoolExecutor(6) as ex:
    fut={ex.submit(hist,t,400 if k[0]=='U' else 90):k for k,t in jobs.items()}
    for f in cf.as_completed(fut): res[fut[f]]=f.result()
json.dump({'tokens':toks,'bar':bar,'U':{k[1]:v for k,v in res.items() if k[0]=='U'},'B':{k[1]:v for k,v in res.items() if k[0]=='B'}},open('histo.json','w'))
print(len(und),'sous-jacents',len(bar),'barrières', sum(len(v) for v in res.values()),'points')
