import requests,sys,concurrent.futures as cf
ids=[l.strip() for l in open(sys.argv[1]) if l.strip()]
def get(i):
    try:
        r=requests.get(f'https://gamma-api.polymarket.com/markets/{i}',headers={'User-Agent':'curl/8'},timeout=20)
        m=r.json(); return i,m.get('closed'),m.get('active'),m.get('endDate'),m.get('umaResolutionStatus'),(m.get('question') or '')[:60]
    except Exception as e: return i,'ERR',str(e)[:40],None,None,''
with cf.ThreadPoolExecutor(8) as ex:
    for r in ex.map(get,ids): print(*r,sep=' | ')
