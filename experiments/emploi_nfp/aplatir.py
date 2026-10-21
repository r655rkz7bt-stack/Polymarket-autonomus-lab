"""Jobs added : le marché est-il trop sûr de lui ? On aplatit ses prix (q ∝ p^g, g<1), on règle g sur la 1re moitié des événements
(dans l'ordre du temps) et on regarde le log-score sur la 2e (jamais de regard vers le futur). Tranches normalisées à somme 1."""
import sys, math, collections, importlib.util
sys.path.insert(0, 'src')
spec = importlib.util.spec_from_file_location('an', 'experiments/emploi_nfp/analyse.py'); an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
def evenements(kind, h):
    by = collections.defaultdict(list)
    for r in an.D:
        if r['kind'] != kind or len(r['bucket']) > 14 and kind == 'chomage': continue
        p, t = an.price_at(r, h)
        if p is not None: by[r['event']].append((max(p, .005), r['yes_final'] > .5, r['release']))
    return sorted((v[0][2], v) for v in by.values() if len(v) >= 4 and sum(x[1] for x in v) == 1)
def ls(evs, g):
    tot = 0
    for _, v in evs:
        w = [p ** g for p, _, _ in v]; z = sum(w)
        tot += math.log(next(wi for wi, (_, win, _) in zip(w, v) if win) / z)
    return tot / len(evs)
for kind in ('jobs', 'chomage'):
    for h in (6, 24, 72, 168):
        E = evenements(kind, h); n = len(E); a, b = E[:n // 2], E[n // 2:]
        gs = [i / 20 for i in range(6, 25)]
        gstar = max(gs, key=lambda g: ls(a, g))
        print(f'{kind} T-{h}: {n} événements ; g* (1re moitié) = {gstar:.2f} ; log-score 2e moitié : marché brut {ls(b, 1):.3f} contre aplati {ls(b, gstar):.3f} ; tout : g=1 {ls(E, 1):.3f}, meilleur g={max(gs, key=lambda g: ls(E, g)):.2f} {max(ls(E, g) for g in gs):.3f}')
