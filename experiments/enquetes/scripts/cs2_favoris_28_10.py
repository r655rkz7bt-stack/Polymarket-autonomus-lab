"""Les favoris de Counter-Strike perdent dans l'arène (nf_sport_patiente : 43 paris −25,6 %) alors que le rejeu les trouve équilibrés : posés / immédiats, avant / pendant le match, un compte par jeton. 28/10/2026."""
import sys, json, glob, os, math, collections, requests
sys.path.insert(0, 'src')
from concurrent.futures import ThreadPoolExecutor
from polymarket_agent.enquete import _posted
from polymarket_agent.pareto import discipline
from polymarket_agent.resolution_sources import domain_of
H = {'User-Agent': 'curl/8'}
tok = {}
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    sett = {}; first = {}
    for l in open(f):
        x = json.loads(l); d = x['data']
        if x['type'] == 'BUY' and d['token_id'] not in first: first[d['token_id']] = (x['ts'], d)
        elif x['type'] == 'SETTLE': sett[d['token_id']] = float(d['payout_per_share'])
    for t, (ts, d) in first.items():
        if t not in sett: continue
        e = d.get('extra') or {}
        try: h = float(e.get('depuis_coup_d_envoi_h'))
        except (TypeError, ValueError): continue
        key = (t, _posted(e), h >= 0)
        if key not in tok or ts < tok[key]['ts']: tok[key] = dict(ts=ts, h=h, price=float(d['price']), pay=sett[t], m=d['market_id'], posted=_posted(e), live=h >= 0, ev=d.get('event_id'))
def q(m):
    for _ in range(3):
        try:
            r = requests.get(f'https://gamma-api.polymarket.com/markets/{m}', headers=H, timeout=30)
            if r.status_code == 200:
                j = r.json(); return m, (j.get('question') or '', j.get('resolutionSource') or '', j.get('sportsMarketType'))
        except Exception: pass
    return m, ('', '', None)
ms = sorted({p['m'] for p in tok.values()})
with ThreadPoolExecutor(8) as ex: info = dict(ex.map(q, ms))
def fmt(ps):
    if not ps: return 'aucun'
    w = sum(p['pay'] for p in ps); ex_ = sum(p['price'] for p in ps); var = sum(p['price'] * (1 - p['price']) for p in ps)
    return f"n={len(ps):3d} gagnés {w:5.1f}/{ex_:5.1f} z {(w - ex_) / math.sqrt(var) if var else 0:+.2f} par pari {100 * sum(p['pay'] / p['price'] - 1 for p in ps) / len(ps):+.1f} %"
for disc in ('counter-strike', 'tennis', 'dota', 'lol', 'football', 'autre'):
    sel = [p for p in tok.values() if discipline(info[p['m']][0], info[p['m']][1]) == disc and info[p['m']][2] == 'moneyline' and p['price'] >= 0.78]
    print(f"== {disc} (vainqueur, prix ≥ 0,78) : {len(sel)} jetons-modes")
    for posted in (True, False):
        for live in (False, True):
            print(f"   {'posés   ' if posted else 'immédiats'} {'en match ' if live else 'avant    '}", fmt([p for p in sel if p['posted'] == posted and p['live'] == live]))
