"""Piste « sous-marchés du football » (26/10/2026) : quels types de marchés (sportsMarketType) autour d'un match, combien, quel volume ?"""
import requests, collections, sys
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
SERIES = {"epl": 10188, "ucl": 10204, "lal": 10193, "bun": 10194, "fl1": 10195, "sea": 10203}
cnt = collections.Counter(); vol = collections.defaultdict(list); resolved = collections.Counter()
for nm, sid in SERIES.items():
    for off in range(0, 600, 100):
        b = s.get('https://gamma-api.polymarket.com/events', params=dict(series_id=sid, closed='true', order='endDate', ascending='false', limit=100, offset=off), timeout=60).json()
        for e in b:
            for m in e.get('markets') or []:
                t = m.get('sportsMarketType'); cnt[t] += 1; vol[t].append(m.get('volumeNum') or 0)
                if m.get('umaResolutionStatus') == 'resolved': resolved[t] += 1
for t, n in cnt.most_common(40):
    v = sorted(vol[t]); print(f'{t!s:42s} {n:5d} marchés, médiane {v[len(v)//2]:8.0f} $, >1000$: {sum(x>1000 for x in v)}')
