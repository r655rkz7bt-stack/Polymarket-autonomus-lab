"""Relevé des marchés « What will Trump say during <rally> ? » (2024 : campagne ; 2026 : meetings de mi-mandat).
Écrit experiments/rallies_trump/donnees/marches.json (ignoré par Git) : un enregistrement par marché (mot, résultat, prix horaires du OUI).
Usage : .venv/bin/python experiments/rallies_trump/scripts/releve.py"""
import requests, json, os, re, time, concurrent.futures as cf
H = {"User-Agent": "curl/8"}
OUT = os.path.join(os.path.dirname(__file__), '..', 'donnees'); os.makedirs(OUT, exist_ok=True)
S = requests.Session(); S.headers.update(H)
def get(url, **kw):
    for i in range(4):
        try:
            r = S.get(url, timeout=40, **kw)
            if r.status_code == 200: return r.json()
            if r.status_code in (429, 503): time.sleep(2 + i * 3)
            else: return None
        except Exception: time.sleep(1 + i)
    return None
ids = {}
for q in ["Trump say Midterm Rally", "What will Trump say during his Midterm Rally", "Trump say rally", "What will Trump say during rally", "Trump say during rally Pennsylvania", "What will Trump say rally Georgia"]:
    for page in range(1, 8):
        r = get("https://gamma-api.polymarket.com/public-search", params={"q": q, "limit_per_type": 50, "page": page, "events_status": "closed"})
        if not r or not r.get('events'): break
        for e in r['events']:
            t = e['title']
            if re.search(r'rally', t, re.I) and re.search(r'what will trump', t, re.I): ids[e['id']] = t
print(len(ids), 'événements')
def hist(token, start, end):
    pts = {}
    t = start
    while t < end:
        t2 = min(t + 13 * 86400, end)
        r = get("https://clob.polymarket.com/prices-history", params={"market": token, "startTs": int(t), "endTs": int(t2), "fidelity": 60})
        for x in (r or {}).get('history', []): pts[x['t']] = x['p']
        t = t2
    return sorted(pts.items())
def one(eid):
    ev = get(f"https://gamma-api.polymarket.com/events/{eid}")
    if not ev: return []
    out = []
    for m in ev.get('markets') or []:
        try:
            op = json.loads(m['outcomePrices']) if isinstance(m.get('outcomePrices'), str) else m.get('outcomePrices')
            toks = json.loads(m['clobTokenIds']) if isinstance(m.get('clobTokenIds'), str) else m.get('clobTokenIds')
            outs = json.loads(m['outcomes']) if isinstance(m.get('outcomes'), str) else m.get('outcomes')
        except Exception: continue
        if not op or not toks or float(op[0]) not in (0.0, 1.0): continue
        iy = outs.index('Yes') if 'Yes' in outs else 0
        st = m.get('startDate') or ev.get('startDate'); en = m.get('endDate') or ev.get('endDate')
        from datetime import datetime
        f = lambda x: datetime.fromisoformat(x.replace('Z', '+00:00')).timestamp()
        s0, e0 = f(st), f(en)
        h = hist(toks[iy], s0 - 3600, min(e0 + 86400, time.time()))
        out.append(dict(event=eid, titre=ev['title'], q=m['question'], yes=float(op[iy]) == 1.0, start=s0, end=e0, closed=m.get('closedTime'), cond=m.get('conditionId'), hist=h,
                        fee=m.get('feeSchedule') or m.get('feeType'), vol=m.get('volumeNum')))
    return out
rows = []
with cf.ThreadPoolExecutor(6) as ex:
    for r in ex.map(one, list(ids)): rows += r
json.dump(rows, open(os.path.join(OUT, 'marches.json'), 'w'))
print(len(rows), 'marchés ;', sum(1 for r in rows if len(r['hist']) >= 3), 'avec historique')
