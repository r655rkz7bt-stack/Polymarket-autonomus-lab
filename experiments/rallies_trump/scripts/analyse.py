"""Rallies de Trump : le OUI d'un mot est-il mal coté par rapport à la fréquence du même mot dans les rallies précédents de la même campagne ?
Sans regard vers le futur : taux du mot sur les rallies PASSÉS (fin avant le début du marché), lissé vers le taux de tous les mots.
Usage : analyse.py [marge=0.05] [k=2] [min_prec=3] [delai_h=6] [prix_min=0] [campagne=toutes|2024|2026]"""
import json, os, re, sys, math, bisect, collections, statistics as st
D = os.path.join(os.path.dirname(__file__), '..', 'donnees', 'marches.json')
rows = json.load(open(D))
MARGIN = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
K = float(sys.argv[2]) if len(sys.argv) > 2 else 2
MINP = int(sys.argv[3]) if len(sys.argv) > 3 else 3
DELAY = float(sys.argv[4]) if len(sys.argv) > 4 else 6
PMIN = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
CAMP = sys.argv[6] if len(sys.argv) > 6 else 'toutes'
def key(q):
    m = re.search(r'say (.*?) (during|at|in|on)\b', q.strip(), re.I)
    s = (m.group(1) if m else q).lower()
    s = re.sub(r'\s+', ' ', s).strip(' "“”')
    return s
def campagne(r): return '2024' if r['end'] < 1.73e9 else '2026'
rows = [r for r in rows if len(r['hist']) >= 3]
for r in rows: r['w'] = key(r['q']); r['c'] = campagne(r)
if CAMP != 'toutes': rows = [r for r in rows if r['c'] == CAMP]
evs = collections.defaultdict(list)
for r in rows: evs[r['event']].append(r)
order = sorted(evs, key=lambda e: evs[e][0]['end'])
ll_m = ll_q = n = 0; trades = []
for e in order:
    ms = evs[e]; end = ms[0]['end']
    prior_ev = [x for x in order if evs[x][0]['end'] < ms[0]['start'] and evs[x][0]['c'] == ms[0]['c']]
    prior = [r for x in prior_ev for r in evs[x]]
    if len(prior_ev) < 2: continue
    g = (sum(r['yes'] for r in prior) + 1) / (len(prior) + 2)
    for r in ms:
        same = [x for x in prior if x['w'] == r['w']]
        if len(same) < MINP: continue
        t_ref = min(r['start'] + DELAY * 3600, r['end'] - 3 * 3600)
        if t_ref <= r['start']: continue
        ts = [t for t, p in r['hist']]; i = bisect.bisect_right(ts, t_ref) - 1
        if i < 0: continue
        p = r['hist'][i][1]
        if not 0.03 < p < 0.97: continue
        q = (sum(x['yes'] for x in same) + K * g) / (len(same) + K)
        y = r['yes']
        ll_m += math.log(p if y else 1 - p); ll_q += math.log(q if y else 1 - q); n += 1
        for side, qq, cost in ((0, q, p + 0.02), (1, 1 - q, 1 - p + 0.02)):
            if qq - MARGIN > cost and PMIN <= cost < 0.98:
                won = y if side == 0 else not y
                fee = 0.04 * cost * (1 - cost)
                trades.append((r['w'], side, cost, qq, ((1 if won else 0) - cost - fee) / cost, e, 1 if won else 0, r['c']))
print(f"log-score : marché {ll_m / n:.4f}  modèle {ll_q / n:.4f}  n {n}  (marge {MARGIN}, k {K}, min {MINP}, délai {DELAY} h, prix ≥ {PMIN}, {CAMP})")
def summ(t, label):
    if not t: print(label, 'aucun'); return
    by = collections.defaultdict(list)
    for x in t: by[x[5]].append(x[4])
    ev = [st.mean(v) for v in by.values()]
    tt = st.mean(ev) / (st.stdev(ev) / math.sqrt(len(ev))) if len(ev) > 2 and st.stdev(ev) > 0 else float('nan')
    w = sum(x[6] for x in t); e = sum(1 - x[2] + 0.02 if False else x[2] - 0.02 for x in t)
    print(f"{label:14s} {len(t):4d} achats  rendement {st.mean(x[4] for x in t) * 100:+6.1f} %  par événement {st.mean(ev) * 100:+6.1f} % (t {tt:+.2f}, {len(ev)} événements)  gagnés {w} pour {e:.1f} attendus par les prix")
summ(trades, 'tous')
summ([t for t in trades if t[1] == 0], 'OUI'); summ([t for t in trades if t[1] == 1], 'NON')
for c in ('2024', '2026'): summ([t for t in trades if t[7] == c], 'campagne ' + c)
