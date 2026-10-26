"""Contre-épreuve : le biais du OUI existe-t-il dans TOUS les marchés « What will X say … » (pas seulement les meetings) ?
Écrit donnees/mentions.json (même format que marches.json). Une seule fenêtre de prix par marché (ouverture → +4 jours)."""
import requests, json, os, re, time, sys, concurrent.futures as cf
from datetime import datetime
S = requests.Session(); S.headers.update({"User-Agent": "curl/8"})
OUT = os.path.join(os.path.dirname(__file__), '..', 'donnees'); os.makedirs(OUT, exist_ok=True)
def get(url, **kw):
    for i in range(4):
        try:
            r = S.get(url, timeout=40, **kw)
            if r.status_code == 200: return r.json()
            if r.status_code in (429, 503): time.sleep(2 + i * 3)
            else: return None
        except Exception: time.sleep(1 + i)
    return None
known = {r['event'] for r in json.load(open(os.path.join(OUT, 'marches.json')))}
ids = {}
qs = ["What will Trump say this week", "What will Trump say during", "What will Powell say during press conference", "What will Vance say during", "What will Trump say in his speech", "What will Trump say during interview",
      "What will Biden say", "What will Harris say", "What will Zelensky say", "What will Netanyahu say", "What will Putin say", "What will Musk say", "What will Starmer say", "What will Lagarde say",
      "What will Trump say during press conference", "What will Trump say at", "What will the announcers say", "What will Trump say on Truth Social", "What will Trump say during State of the Union", "mention earnings call say"]
for q in qs:
    for page in range(1, 11):
        r = get("https://gamma-api.polymarket.com/public-search", params={"q": q, "limit_per_type": 50, "page": page, "events_status": "closed"})
        if not r or not r.get('events'): break
        for e in r['events']:
            t = e['title']
            if re.match(r'\s*what will .* (say|mention)', t, re.I) and not re.search(r'rally', t, re.I) and e['id'] not in known: ids[e['id']] = t
print(len(ids), 'événements', flush=True)
def one(eid):
    try:
        return _one(eid)
    except Exception as exc:  # un événement mal formé ne perd pas le relevé
        print('ignoré', eid, repr(exc), flush=True)
        return []


def _one(eid):
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
        f = lambda x: datetime.fromisoformat(x.replace('Z', '+00:00')).timestamp()
        s0, e0 = f(m.get('startDate') or ev['startDate']), f(m.get('endDate') or ev.get('endDate') or m.get('startDate') or ev['startDate'])
        r = get("https://clob.polymarket.com/prices-history", params={"market": toks[iy], "startTs": int(s0 - 3600), "endTs": int(min(s0 + 4 * 86400, e0 + 3600, time.time())), "fidelity": 60})
        out.append(dict(event=eid, titre=ev['title'], q=m['question'], yes=float(op[iy]) == 1.0, start=s0, end=e0, hist=[(x['t'], x['p']) for x in (r or {}).get('history', [])]))
    return out
rows = []
with cf.ThreadPoolExecutor(6) as ex:
    for k, r in enumerate(ex.map(one, list(ids))):
        rows += r
        if k % 50 == 0: print(k, len(rows), flush=True)
json.dump(rows, open(os.path.join(OUT, 'mentions.json'), 'w'))
print(len(rows), 'marchés')
