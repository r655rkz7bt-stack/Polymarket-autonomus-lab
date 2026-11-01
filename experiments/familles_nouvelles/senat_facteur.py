"""01/11 : une seule corrélation entre courses (copule gaussienne à un facteur) explique-t-elle l'échelle des sièges du Sénat ?"""
import json, math
from statistics import NormalDist
N = NormalDist()
c = json.load(open('experiments/familles_nouvelles/senat_courses_01_11.json'))
P = []
for t, d in c.items():
    items = {k.strip(): v[0] for k, v in d.items()}
    r = [v for k, v in items.items() if k.endswith('(R)') or k == 'Republican' or 'Sullivan' in k]
    tot = sum(items.values())
    if r and tot: P.append(min(max(r[0] / tot, 1e-4), 1 - 1e-4))
mkt = dict(zip(['<=47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57+'], [.485, .145, .11, .095, .07, .0605, .039, .0075, .0025, .0015, .0035]))
BASE = 31
def ladder(rho):
    dist = {}
    zs = [(-6 + 12 * i / 240) for i in range(241)]; w = [N.pdf(z) for z in zs]; sw = sum(w)
    for z, wz in zip(zs, w):
        d = {BASE: 1.0}
        for p in P:
            thr = N.inv_cdf(p)  # R gagne si x < thr, x = sqrt(rho) z + sqrt(1-rho) e
            pc = N.cdf((thr - math.sqrt(rho) * z) / math.sqrt(1 - rho))
            nd = {}
            for k, v in d.items():
                nd[k + 1] = nd.get(k + 1, 0) + v * pc; nd[k] = nd.get(k, 0) + v * (1 - pc)
            d = nd
        for k, v in d.items(): dist[k] = dist.get(k, 0) + v * wz / sw
    out = {'<=47': sum(v for k, v in dist.items() if k <= 47), '57+': sum(v for k, v in dist.items() if k >= 57)}
    for k in range(48, 57): out[str(k)] = dist.get(k, 0)
    return out
best = None
for rho in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
    l = ladder(rho)
    kl = sum(m * math.log(m / max(l[k], 1e-9)) for k, m in mkt.items())
    print(f"rho {rho:.1f}  KL(marché||modèle) {kl:.3f}  P(R>=51) modèle {sum(l[str(k)] for k in range(51,57))+l['57+']:.3f} (marché 0.182)  P(R>=53) {sum(l[str(k)] for k in range(53,57))+l['57+']:.3f} (marché 0.054)")
    if best is None or kl < best[0]: best = (kl, rho, l)
print('meilleur rho', best[1]); print({k: round(v, 3) for k, v in best[2].items()}); print(mkt)
