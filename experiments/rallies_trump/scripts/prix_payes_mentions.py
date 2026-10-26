"""Vérification aux prix réellement payés : pour un tirage d'événements « What will X say », le NON d'un mot dont le OUI vaut 0,40-0,70 (prix horaire du CLOB) à `délai` h après l'ouverture,
acheté au premier échange réel d'un preneur qui ACHÈTE le NON dans les 2 heures suivantes (prix de cet échange, plus rien d'autre ; pas de frais : feesEnabled false).
Usage : prix_payes_mentions.py [nb_evenements=150] [delai=24] [graine=1]"""
import json, os, sys, random, bisect, collections, time, requests, concurrent.futures as cf
D = os.path.join(os.path.dirname(__file__), '..', 'donnees')
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
DELAY = float(sys.argv[2]) if len(sys.argv) > 2 else 24
random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
import re
SIMPLE = os.environ.get('SIMPLE') == '1'   # SIMPLE=1 : sans les seuils « N+ times »
rows = [r for r in json.load(open(os.path.join(D, 'mentions.json'))) if len(r['hist']) >= 3 and not (SIMPLE and re.search(r'\d+\+', r['q']))]
S = requests.Session(); S.headers['User-Agent'] = 'curl/8'
def get(url, **kw):
    for i in range(4):
        try:
            r = S.get(url, timeout=40, **kw)
            if r.status_code == 200: return r.json()
            if r.status_code in (429, 503): time.sleep(2 + 3 * i)
            else: return None
        except Exception: time.sleep(1 + i)
byev = collections.defaultdict(list)
for r in rows: byev[r['event']].append(r)
evs = random.sample(sorted(byev), min(N, len(byev)))
def one(eid):
    ev = get(f"https://gamma-api.polymarket.com/events/{eid}")
    if not ev: return []
    cond = {}
    for m in ev.get('markets') or []:
        try:
            toks = json.loads(m['clobTokenIds']) if isinstance(m['clobTokenIds'], str) else m['clobTokenIds']
            outs = json.loads(m['outcomes']) if isinstance(m['outcomes'], str) else m['outcomes']
            cond[m['question']] = (m['conditionId'], toks[1 - outs.index('Yes')] if 'Yes' in outs else None)
        except Exception: pass
    out = []
    for r in byev[eid]:
        t = min(r['start'] + DELAY * 3600, r['end'] - 3 * 3600)
        if t <= r['start']: continue
        ts = [a for a, b in r['hist']]; i = bisect.bisect_right(ts, t) - 1
        if i < 0: continue
        p = r['hist'][i][1]
        if not 0.40 <= p < 0.70 or r['q'] not in cond: continue
        c, notok = cond[r['q']]
        trades = []
        for off in range(0, 3000, 500):
            b = get("https://data-api.polymarket.com/trades", params={"market": c, "limit": 500, "offset": off})
            if not b: break
            trades += b
            if len(b) < 500 or min(x['timestamp'] for x in b) < t: break
        fills = sorted((x['timestamp'], x['price']) for x in trades if x['asset'] == notok and x['side'] == 'BUY' and t <= x['timestamp'] <= t + 7200)
        out.append(dict(event=eid, p=p, y=r['yes'], fill=fills[0][1] if fills else None, nfills=len(fills)))
    return out
res = []
with cf.ThreadPoolExecutor(6) as ex:
    for k, o in enumerate(ex.map(one, evs)):
        res += o
        if k % 25 == 0: print(k, len(res), flush=True)
json.dump(res, open(os.path.join(D, f'prix_payes_{int(DELAY)}{"_simple" if SIMPLE else ""}.json'), 'w'))
ok = [x for x in res if x['fill'] is not None]
print(len(res), 'paris candidats ;', len(ok), 'avec un échange réel du NON dans les 2 h')
