"""PIB et ISM : la tranche favorite (prix le plus haut à T-h) gagne-t-elle moins que son prix ? (prix historique, 14 événements avec heure de publication)"""
import json, bisect, math, collections
D = json.load(open('experiments/emploi_nfp/donnees/macro/marches.json'))
by = collections.defaultdict(list)
for r in D:
    if r['release_ts']: by[r['event']].append(r)
for h in (6, 24, 72, 168):
    F = []
    for e, ms in by.items():
        c = []
        for r in ms:
            hs = [x[0] for x in r['hist']]; t = r['release_ts'] - h * 3600; i = bisect.bisect_right(hs, t) - 1
            if i >= 0 and t - hs[i] < 13 * 3600: c.append((r['hist'][i][1], r['yes_final'] > .5, r['title']))
        if len(c) >= 4: F.append(max(c))
    n = len(F); w = sum(x[1] for x in F); e_ = sum(x[0] for x in F); v = sum(x[0] * (1 - x[0]) for x in F)
    kinds = collections.Counter('ISM' if 'ISM' in x[2] else 'PIB' for x in F)
    print(f'T-{h}: {n} événements {dict(kinds)} ; favori gagne {w} / attendu {e_:.1f} (z {(w - e_) / math.sqrt(v):+.2f}) ; prix moyen {e_ / n:.2f}')
