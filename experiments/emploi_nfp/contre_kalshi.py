"""Emploi américain : Polymarket (tranches) contre Kalshi (seuils « plus de X »), mêmes publications.
Probabilité Kalshi d'une tranche Polymarket [a, b[ = P(> a) − P(> b) (milieu acheteur-vendeur de la dernière bougie horaire avant T-h) ;
elle n'existe que si Kalshi cote les deux seuils. Question : la tranche favorite de Polymarket est-elle plus chère que chez Kalshi, et qui a raison ?"""
import sys, re, json, math, bisect, collections, importlib.util, datetime as dt
sys.path.insert(0, 'src')
spec = importlib.util.spec_from_file_location('an', 'experiments/emploi_nfp/analyse.py'); an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
from polymarket_agent.idea_test import taker_cost, verdict
K = json.load(open('experiments/emploi_nfp/donnees/kalshi_bougies.json'))
byev = collections.defaultdict(dict)
for tk, m in K.items():
    ev = tk.rsplit('-T', 1)[0]
    if m['floor'] is not None: byev[ev][float(m['floor'])] = m
MON = {m: i + 1 for i, m in enumerate(['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'])}
ref2ev = {}
for ev in byev:
    mm = re.search(r'(\d\d)([A-Z]{3})(?:B)?$', ev)
    if mm: ref2ev[(2000 + int(mm.group(1)), MON[mm.group(2)])] = ev
def kprob(m, t):
    c = [x for x in m['c'] if x[0] <= t and x[1] is not None and x[2] is not None]
    if not c: return None
    _, b, a = c[-1]; b, a = float(b), float(a)
    return (a + b) / 2 if a - b <= 0.15 else None
def bornes(b):
    s = b.replace(',', '').replace('–', '-').replace('−', '-').lower().replace(' ', '').replace('to', '-')
    nums = [float(x) * 1000 for x in re.findall(r'\d+(?:\.\d+)?', s)]
    if s.startswith('<') and nums: return (None, nums[0])
    if (s.startswith(('>', '≥')) or s.endswith('+')) and nums: return (nums[0], None)
    if len(nums) == 2: return (nums[0], nums[1])
    return None
def kalshi_bucket(ev, a, b, t):
    th = byev[ev]; pa = pb = None
    if a is None: pa = 1.0
    elif a in th: pa = kprob(th[a], t)
    if b is None: pb = 0.0
    elif b in th: pb = kprob(th[b], t)
    if pa is None or pb is None: return None
    return max(pa - pb, 0.0)
rows = []   # (event, h, bucket, p_poly, q_kalshi, win, release)
for r in an.D:
    if r['kind'] != 'jobs' or tuple(r['ref']) not in ref2ev: continue
    bo = bornes(r['bucket'])
    if bo is None: continue
    for h in (6, 24, 72, 168):
        p, t = an.price_at(r, h)
        if p is None: continue
        q = kalshi_bucket(ref2ev[tuple(r['ref'])], bo[0], bo[1], int(t))
        if q is None: continue
        rows.append((r['event'], h, r['bucket'], p, q, r['yes_final'] > .5, r))
print(len(rows), 'tranches Polymarket avec probabilité Kalshi équivalente ;', len({x[0] for x in rows}), 'événements')
for h in (6, 24, 72, 168):
    R = [x for x in rows if x[1] == h]
    if not R: continue
    n = len(R); diff = sum(x[3] - x[4] for x in R) / n
    wp = sum((x[5] - x[3]) ** 2 for x in R) / n; wk = sum((x[5] - x[4]) ** 2 for x in R) / n
    print(f'T-{h}: {n} tranches, Polymarket − Kalshi = {diff:+.3f} ; Brier Polymarket {wp:.4f} contre Kalshi {wk:.4f}')
    # favoris de Polymarket
    by = collections.defaultdict(list)
    for x in R: by[x[0]].append(x)
    F = [max(v, key=lambda x: x[3]) for v in by.values() if len(v) >= 3]
    if F:
        print(f'   favori Polymarket ({len(F)} ev.) : prix {sum(x[3] for x in F)/len(F):.3f}, Kalshi {sum(x[4] for x in F)/len(F):.3f}, gagne {sum(x[5] for x in F)} ; attendu Poly {sum(x[3] for x in F):.1f} / Kalshi {sum(x[4] for x in F):.1f}')
print('\n--- NON si Polymarket > Kalshi + seuil (prix des vrais échanges)')
for h in (6, 24, 72):
    for thr in (0.03, 0.05, 0.08):
        bets = []
        for ev, hh, b, p, q, win, r in rows:
            if hh != h or p - q < thr or not 0.05 <= p <= 0.8: continue
            _, t = an.price_at(r, h); yes, no = r['tokens'][:2]
            c = taker_cost(an.tr(ev), no, yes, int(t), window=2 * 3600, after=True)
            if c is None: continue
            c = min(c, .99); f = an.fr(r) * c * (1 - c)
            bets.append({'gain': ((0 if win else 1) - c - f) / (c + f), 'evenement': ev, 'mois': r['release'][:7], 'cout': c})
        if len(bets) >= 8:
            v = verdict(bets, min_bets=8)
            print(f'T-{h} écart ≥ {thr:.2f}: {v["paris"]} paris ({v["evenements"]} ev.) {v["rendement_moyen"]*100:+.1f}% t_ev={v["confiance_evenements"]:+.2f} z_prix={v["z_prix"]:+.1f} -> {v["verdict"]}')
