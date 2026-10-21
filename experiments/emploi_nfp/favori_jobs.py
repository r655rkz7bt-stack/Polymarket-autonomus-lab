"""Jobs added : la tranche favorite (prix le plus haut à T-h) gagne-t-elle moins souvent que son prix ?
Tranches de 50k : même un bon pronostic ne dépasse guère 25-30 % sur 50k si l'écart-type de la surprise est ~75k."""
import sys, collections, math, importlib.util
sys.path.insert(0, 'src')
spec = importlib.util.spec_from_file_location('an', 'experiments/emploi_nfp/analyse.py'); an = importlib.util.module_from_spec(spec); spec.loader.exec_module(an)
from polymarket_agent.idea_test import taker_cost, verdict
D = an.D
def favoris(kind, h):
    by = collections.defaultdict(list)
    for r in D:
        if r['kind'] != kind: continue
        p, t = an.price_at(r, h)
        if p is not None: by[r['event']].append((p, r, t))
    out = []
    for e, L in by.items():
        if len(L) < 3: continue
        L.sort(key=lambda x: -x[0]); p, r, t = L[0]
        out.append((r['release'][:10], e, p, r['bucket'], r['yes_final'] > .5, r, t, sum(x[0] for x in L)))
    return sorted(out)
for kind in ('jobs', 'chomage'):
    for h in (6, 24, 72, 168):
        F = favoris(kind, h)
        w = sum(x[4] for x in F); e = sum(x[2] for x in F); n = len(F)
        v = sum(x[2] * (1 - x[2]) for x in F)
        half = n // 2
        print(f'{kind} T-{h}: {n} événements, favori gagne {w} / attendu {e:.1f} (z {(w - e) / math.sqrt(v):+.2f}); prix moyen {e / n:.2f}; 1re moitié {sum(x[4] for x in F[:half])}/{sum(x[2] for x in F[:half]):.1f}, 2e moitié {sum(x[4] for x in F[half:])}/{sum(x[2] for x in F[half:]):.1f}; somme des prix des tranches moy. {sum(x[7] for x in F) / n:.2f}')
print()
for x in favoris('jobs', 24): print(x[:5])
print('\n--- NON sur la tranche favorite, prix des vrais échanges, frais du marché')
for kind in ('jobs', 'chomage'):
    for h in (6, 24, 72, 168):
        for side in ('NON',):
            bets = []
            for d, e, p, b, win, r, t, _ in favoris(kind, h):
                yes, no = r['tokens'][:2]
                c = taker_cost(an.tr(e), no, yes, int(t), window=2 * 3600, after=True)
                if c is None: continue
                c = min(c, .99); f = an.fr(r) * c * (1 - c)
                bets.append({'gain': ((0 if win else 1) - c - f) / (c + f), 'evenement': e, 'mois': d[:7], 'cout': c})
            if len(bets) >= 8:
                v = verdict(bets, min_bets=8)
                print(f'{kind} {side} favori T-{h}: {v["paris"]} paris {v["rendement_moyen"]*100:+.1f}% t_ev={v["confiance_evenements"]:+.2f} z_prix={v["z_prix"]:+.1f} mois {v["mois_gagnants"]} coût moyen {sum(b["cout"] for b in bets)/len(bets):.2f} -> {v["verdict"]}')
