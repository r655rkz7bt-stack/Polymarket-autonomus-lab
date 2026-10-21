import requests, json
H={'User-Agent':'curl/8'}
out={}
for q in ['CPI','inflation','inflation monthly','CPI August','CPI September','core inflation','Fed rate decision']:
    for page in range(1,8):
        r=requests.get('https://gamma-api.polymarket.com/public-search',params={'q':q,'page':page,'limit_per_type':50,'events_status':'closed' if page%2 else 'open'},headers=H,timeout=30)
        if r.status_code!=200: print(q,page,r.status_code); break
        for e in r.json().get('events',[]): out[e['id']]=e
print(len(out))
for e in sorted(out.values(), key=lambda e:e.get('endDate') or ''):
    t=e['title']
    if any(k in t.lower() for k in ('cpi','inflation')): print(e['id'],(e.get('endDate') or '')[:10],e['closed'],len(e.get('markets',[])),t[:90])
json.dump(out,open('experiments/cpi_nowcast/donnees/events.json','w'))
