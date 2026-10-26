"""Rallies de Trump : le prix du OUI à `délai` heures après l'ouverture est-il calibré ? Rendement du OUI et du NON par tranche de prix (frais 0,04·p(1−p) + 0,02 d'écart)."""
import json, os, sys, math, bisect, collections, statistics as st
rows = [r for r in json.load(open(os.path.join(os.path.dirname(__file__), '..', 'donnees', 'marches.json'))) if len(r['hist']) >= 3]
DELAY = float(sys.argv[1]) if len(sys.argv) > 1 else 6
CAMP = sys.argv[2] if len(sys.argv) > 2 else 'toutes'
pts = []
for r in rows:
    c = '2024' if r['end'] < 1.73e9 else '2026'
    if CAMP != 'toutes' and c != CAMP: continue
    t_ref = min(r['start'] + DELAY * 3600, r['end'] - 3 * 3600)
    if t_ref <= r['start']: continue
    ts = [t for t, p in r['hist']]; i = bisect.bisect_right(ts, t_ref) - 1
    if i < 0: continue
    p = r['hist'][i][1]
    pts.append((p, r['yes'], r['event'], c))
print(len(pts), 'marchés', 'délai', DELAY, 'h', CAMP, ' taux de OUI global', round(sum(y for _, y, *_ in pts) / len(pts), 3), 'prix moyen', round(st.mean(p for p, *_ in pts), 3))
bins = [(0.03, 0.15), (0.15, 0.30), (0.30, 0.45), (0.45, 0.60), (0.60, 0.75), (0.75, 0.97)]
for lo, hi in bins:
    v = [x for x in pts if lo <= x[0] < hi]
    if len(v) < 10: continue
    ry = st.mean(((1 if y else 0) - (p + 0.02) - 0.04 * (p + 0.02) * (1 - p - 0.02)) / (p + 0.02) for p, y, *_ in v)
    rn = st.mean(((0 if y else 1) - (1 - p + 0.02) - 0.04 * (1 - p + 0.02) * (p - 0.02)) / (1 - p + 0.02) for p, y, *_ in v)
    byev = collections.defaultdict(list)
    for p, y, e, c in v: byev[e].append(((0 if y else 1) - (1 - p + 0.02) - 0.04 * (1 - p + 0.02) * (p - 0.02)) / (1 - p + 0.02))
    evm = [st.mean(x) for x in byev.values()]
    tt = st.mean(evm) / (st.stdev(evm) / math.sqrt(len(evm))) if len(evm) > 2 and st.stdev(evm) > 0 else float('nan')
    print(f"prix {lo:.2f}-{hi:.2f} n={len(v):4d} prix moyen {st.mean(p for p, *_ in v):.3f} OUI réalisé {st.mean(1 if y else 0 for _, y, *_ in v):.3f}  rend OUI {ry*100:+6.1f} %  rend NON {rn*100:+6.1f} % (t par événement {tt:+.2f})")
