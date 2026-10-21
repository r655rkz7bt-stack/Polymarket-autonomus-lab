"""Taux de chômage américain : le taux du mois précédent (connu, tiré de l'événement précédent, aucun regard vers le futur)
reste-t-il plus souvent que le prix de sa tranche ? Tranches : « même », « +0,1 », « −0,1 ». Prix historiques 12 h."""
import sys, re, math, collections, importlib.util
sys.path.insert(0, 'src')
spec = importlib.util.spec_from_file_location('an', 'experiments/emploi_nfp/analyse.py'); an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
ev = collections.defaultdict(list)
for r in an.D:
    if r['kind'] == 'chomage' and r['bucket'].endswith('%') and len(r['bucket']) < 8: ev[r['event']].append(r)
def val(b):
    m = re.match(r'^(≤|≥)?(\d\.\d)%$', b); return (m.group(1), float(m.group(2))) if m else None
order = sorted(ev, key=lambda e: ev[e][0]['release'])
exact = {}
for e in order:
    w = [r for r in ev[e] if r['yes_final'] > .5]
    if w:
        v = val(w[0]['bucket'])
        if v and v[0] is None: exact[e] = v[1]
res = collections.defaultdict(list)
for a, b in zip(order, order[1:]):
    if a not in exact: continue
    prev = exact[a]
    ra, rb = ev[a][0]['ref'], ev[b][0]['ref']
    if not (rb[0] * 12 + rb[1]) - (ra[0] * 12 + ra[1]) == 1: continue
    for lab, d in (('même', 0), ('+0,1', .1), ('−0,1', -.1)):
        for r in ev[b]:
            v = val(r['bucket'])
            if v and v[0] is None and abs(v[1] - (prev + d)) < 1e-6:
                for h in (6, 24, 72, 168):
                    p, _ = an.price_at(r, h)
                    if p is not None: res[(lab, h)].append((p, r['yes_final'] > .5))
for (lab, h), L in sorted(res.items(), key=lambda x: (x[0][1], x[0][0])):
    n = len(L); w = sum(x[1] for x in L); e = sum(x[0] for x in L); v = sum(x[0] * (1 - x[0]) for x in L)
    print(f'T-{h:3d} {lab:5s}: n={n:2d} gagnés {w:2d} / attendus {e:5.1f} z={(w - e) / math.sqrt(v):+.2f}  prix moyen {e / n:.2f}')
