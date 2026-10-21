import json, collections, math, datetime as dt, bisect
D = json.load(open('experiments/cpi_nowcast/donnees/marches.json'))
ev = collections.defaultdict(list)
for r in D: ev[r['event']].append(r)
# 1. règlement : un seul OUI par événement
bad = [(k, round(sum(x['yes_final'] for x in v), 2), v[0]['title']) for k, v in ev.items() if abs(sum(x['yes_final'] for x in v) - 1) > .01]
print('événements', len(ev), 'dont règlement incohérent:', len(bad), bad[:6])
print('uma:', collections.Counter(r['uma'] for r in D))
def price_at(r, hours):
    rel = dt.datetime.fromisoformat(r['release'].replace('Z', '+00:00')).timestamp() - hours * 3600
    ts = [t for t, p in r['hist']]
    i = bisect.bisect_right(ts, rel) - 1
    if i < 0 or rel - ts[i] > 6 * 3600: return None
    return r['hist'][i][1]
for H in (24, 72, 168):
    rows = []
    for k, v in ev.items():
        ps = [(price_at(r, H), r) for r in v]
        if any(p is None for p, _ in ps): continue
        s = sum(p for p, _ in ps)
        for p, r in ps: rows.append((p, 1 if r['yes_final'] > .5 else 0, r, s))
    n_ev = len({r['event'] for _, _, r, _ in rows})
    print(f'\n== T-{H} h : {n_ev} événements, {len(rows)} tranches ; somme des prix médiane {sorted(x[3] for x in rows)[len(rows)//2]:.2f}')
    ls_m = sum(-math.log(max(p if y else 1 - p, 1e-3)) for p, y, _, _ in rows) / len(rows)
    print(f'log-score marché {ls_m:.4f}')
    for lo, hi in ((0, .03), (.03, .1), (.1, .25), (.25, .5), (.5, .75), (.75, 1.01)):
        b = [x for x in rows if lo <= x[0] < hi]
        if not b: continue
        f = sum(x[1] for x in b) / len(b); mp = sum(x[0] for x in b) / len(b)
        # acheter OUI (prix+0,01 d'écart) / acheter NON
        yes = sum((x[1] - min(x[0] + .01, .99)) / min(x[0] + .01, .99) for x in b) / len(b)
        no = sum(((1 - x[1]) - min(1 - x[0] + .01, .99)) / min(1 - x[0] + .01, .99) for x in b) / len(b)
        print(f'  prix {lo:.2f}-{hi:.2f}: n={len(b):3d} gagne {f:.3f} vs prix {mp:.3f}  | OUI {yes*100:+6.1f}%  NON {no*100:+6.1f}% (sans frais)')
