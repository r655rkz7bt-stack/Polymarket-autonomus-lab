import requests,json,re,datetime as dt,concurrent.futures as cf
H={'User-Agent':'curl/8'}
mk=json.load(open('donnees/lid_markets.json'))
def get(m):
    g=requests.get('https://gamma-api.polymarket.com/markets/'+m['id'],headers=H,timeout=60).json()
    tok=json.loads(g['clobTokenIds'])[0]
    start=int(dt.datetime.fromisoformat(g['createdAt'].replace('Z','+00:00')).timestamp())
    end=int(dt.datetime.fromisoformat(g['endDate'].replace('Z','+00:00')).timestamp())+86400
    hist=[]
    t=start
    while t<end:
        r=requests.get('https://clob.polymarket.com/prices-history',params=dict(market=tok,startTs=t,endTs=min(t+13*86400,end),fidelity=60),headers=H,timeout=60).json()
        hist+=r.get('history',[]); t+=13*86400
    return dict(id=m['id'],q=m['q'],created=g['createdAt'],end=g['endDate'],op=g['outcomePrices'],closed=g.get('closed'),fee=g.get('feeType'),umaRes=g.get('umaResolutionStatus'),hist=hist,vol=g.get('volume'))
with cf.ThreadPoolExecutor(8) as ex: out=list(ex.map(get,mk))
json.dump(out,open('donnees/lid_hist.json','w')); print(len(out), sum(1 for o in out if o['hist']))
