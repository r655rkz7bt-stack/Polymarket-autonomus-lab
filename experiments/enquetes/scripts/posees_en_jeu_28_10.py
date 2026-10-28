"""Ordres posés servis en match : euros, hors échantillon, par stratégie (28/10 soir)."""
import json, glob, os, math, collections, sys
sys.path.insert(0, 'src')
from decimal import Decimal as D
from polymarket_agent.enquete import _posted

seen = {}  # token -> (ts, price, posted, live, strategy, shares)
pay = {}
per = collections.defaultdict(list)
for f in glob.glob('published_data/ledger/fantome/*.jsonl'):
    name = os.path.basename(f)[:-6]
    firsts = {}
    sett = {}
    for l in open(f):
        x = json.loads(l); d = x['data']
        if x['type'] == 'BUY' and d['token_id'] not in firsts:
            firsts[d['token_id']] = (x['ts'], d)
        elif x['type'] == 'SETTLE':
            sett[d['token_id']] = float(d['payout_per_share'])
    # cout total par jeton
    cost = collections.defaultdict(float); sh = collections.defaultdict(float)
    for l in open(f):
        x = json.loads(l); d = x['data']
        if x['type'] == 'BUY':
            cost[d['token_id']] += float(d['price']) * float(d['shares']) + float(d['fee']); sh[d['token_id']] += float(d['shares'])
    for t, (ts, d) in firsts.items():
        if t not in sett: continue
        e = d.get('extra') or {}
        try: live = float(e.get('depuis_coup_d_envoi_h')) >= 0
        except (TypeError, ValueError): continue
        per[name].append(dict(ts=ts, live=live, posted=_posted(e), price=float(d['price']), pay=sett[t], gain=sh[t] * sett[t] - cost[t], mise=cost[t]))
allp = [p for v in per.values() for p in v]
def resume(ps, titre):
    if not ps: print(titre, 'aucun'); return
    n = len(ps); won = sum(p['pay'] for p in ps); exp = sum(p['price'] for p in ps)
    var = sum(p['price'] * (1 - p['price']) for p in ps)
    z = (won - exp) / math.sqrt(var) if var else 0
    print('%-48s n=%4d gagnés %.1f/%.1f attendus z %+.2f  gain %+8.1f € sur %8.1f € (%+.1f %%)' % (titre, n, won, exp, z, sum(p['gain'] for p in ps), sum(p['mise'] for p in ps), 100 * sum(p['gain'] for p in ps) / max(1, sum(p['mise'] for p in ps))))
# jeton compté par stratégie (tous les fantômes : un fantôme = un pari)
resume([p for p in allp if p['live'] and p['posted']], 'en match, posés (tous fantômes, par fantôme)')
resume([p for p in allp if p['live'] and not p['posted']], 'en match, immédiats')
resume([p for p in allp if not p['live'] and p['posted']], 'avant match, posés')
resume([p for p in allp if not p['live'] and not p['posted']], 'avant match, immédiats')
for cut in ('2026-10-22', '2026-10-25'):
    resume([p for p in allp if p['live'] and p['posted'] and p['ts'] < cut], f'en match, posés avant {cut}')
    resume([p for p in allp if p['live'] and p['posted'] and p['ts'] >= cut], f'en match, posés depuis {cut}')
print()
for n in ('nf_sport_patiente_v1.0.0', 'nf_sport_patiente_avant_match_v1.0.0', 'nf_sport_patiente_prix_850_875_v1.0.0', 'nf_sport_18_24h_v1.0.0', 'nf_sport_prix_haut_v1.0.0', 'nf_sport_v1.0.0'):
    ps = per[n]
    resume([p for p in ps if p['live'] and p['posted']], n + ' en match posés')
    resume([p for p in ps if not (p['live'] and p['posted'])], n + ' le reste')

print('\n--- dédoublonné par jeton (premier fantôme) et par événement ---')
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
        try: live = float(e.get('depuis_coup_d_envoi_h')) >= 0
        except (TypeError, ValueError): continue
        key = (t, live and _posted(e))
        if key not in tok or ts < tok[key]['ts']:
            tok[key] = dict(ts=ts, live=live, posted=_posted(e), price=float(d['price']), pay=sett[t], ev=d.get('event_id'), sport=e.get('sport') or e.get('league'))
def r2(ps, titre):
    if not ps: print(titre, 'aucun'); return
    # par événement : somme (pay - price) / sqrt(somme var) par événement
    ev = collections.defaultdict(lambda: [0.0, 0.0])
    for p in ps:
        ev[p['ev']][0] += p['pay'] - p['price']; ev[p['ev']][1] += p['price'] * (1 - p['price'])
    n = len(ps); won = sum(p['pay'] for p in ps); exp = sum(p['price'] for p in ps)
    z = (won - exp) / math.sqrt(sum(p['price'] * (1 - p['price']) for p in ps))
    unit = sum(p['pay'] / p['price'] - 1 for p in ps) / n
    zev = [a / math.sqrt(b) for a, b in ev.values() if b > 0]
    print('%-40s n=%4d jetons, %3d événements, gagnés %.1f/%.1f, z %+.2f, par pari %+.1f %%, z par événement (somme/√n) %+.2f' % (titre, n, len(ev), won, exp, z, 100 * unit, sum(zev) / math.sqrt(len(zev))))
vals = list(tok.values())
r2([p for p in vals if p['live'] and p['posted']], 'match posés')
r2([p for p in vals if p['live'] and not p['posted']], 'match immédiats')
r2([p for p in vals if p['live'] and p['posted'] and p['ts'] >= '2026-10-25'], 'match posés depuis 25/10')
r2([p for p in vals if p['live'] and p['posted'] and p['ts'] < '2026-10-25'], 'match posés avant 25/10')
r2([p for p in vals if not p['live'] and p['posted']], 'avant match posés')
r2([p for p in vals if not p['live'] and not p['posted']], 'avant match immédiats')
