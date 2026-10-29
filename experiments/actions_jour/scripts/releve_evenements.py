"""Relève les événements « <action> Up or Down on <date> ? » réglés depuis août 2026 (public-search de Gamma)."""
import requests, json, re, sys, time
H = {'User-Agent': 'curl/8'}
seen = {}
queries = ['Up or Down on October', 'Up or Down on September', 'Up or Down on August', 'Up or Down on', 'SPX Up or Down', 'NVDA Up or Down', 'TSLA Up or Down',
           'AAPL Up or Down', 'MSFT Up or Down', 'AMZN Up or Down', 'GOOGL Up or Down', 'META Up or Down', 'NFLX Up or Down', 'PLTR Up or Down', 'COIN Up or Down',
           'QQQ Up or Down', 'SPY Up or Down', 'Opens Up or Down', 'Nasdaq Up or Down', 'Dow Jones Up or Down', 'Gold Up or Down', 'Silver Up or Down', 'Crude Oil Up or Down',
           'MSTR Up or Down', 'HOOD Up or Down', 'ORCL Up or Down', 'AMD Up or Down', 'Russell Up or Down']
for q in queries:
    for status in ['closed']:
        for page in range(1, 40):
            try:
                r = requests.get('https://gamma-api.polymarket.com/public-search', params={'q': q, 'events_status': status, 'limit_per_type': 50, 'page': page}, headers=H, timeout=40).json()
            except Exception as e:
                print('err', q, page, e); break
            ev = r.get('events', [])
            for e in ev:
                t = e['title']
                if 'Up or Down' in t and e.get('closedTime', '') and e['closedTime'] >= '2026-07-25':
                    seen[e['id']] = e
            if not r.get('pagination', {}).get('hasMore'):
                break
    print(q, len(seen), flush=True)
json.dump(list(seen.values()), open('experiments/actions_jour/donnees/evenements.json', 'w'))
