import json,sys,concurrent.futures as cf,requests
sys.path.insert(0,'/home/user/Polymarket-autonomus-lab/src')
from polymarket_agent import data_api
class Http:
    def get_json(self,url,params=None):
        r=requests.get(url,params=params,headers={'User-Agent':'curl/8'},timeout=60); r.raise_for_status(); return r.json()
H=json.load(open('donnees/lid_hist.json'))
def one(m):
    g=requests.get('https://gamma-api.polymarket.com/markets/'+m['id'],headers={'User-Agent':'curl/8'},timeout=60).json()
    try:
        rows=data_api.lire(Http(),data_api.TRADES,{'condition':g['conditionId']},pages=10)
    except Exception as e:
        return m['id'],None,str(e)
    toks=json.loads(g['clobTokenIds'])
    return m['id'],dict(toks=toks,trades=[[int(t['timestamp']),str(t['asset']),str(t['side']),float(t['price']),float(t['size'])] for t in rows]),None
with cf.ThreadPoolExecutor(6) as ex: out=list(ex.map(one,H))
res={i:d for i,d,e in out if d}
print(len(res),'erreurs',[e for _,_,e in out if e][:3])
json.dump(res,open('donnees/lid_trades.json','w'))
print(sum(len(d['trades']) for d in res.values()))
