"""Emploi américain (jobs added + taux de chômage) : les tranches sont-elles bien calibrées aux alentours de la publication ?
1) prix historique (pas de 12 h) : gagnés contre attendus par tranche de prix, OUI et NON ; 2) aux prix des vrais échanges (taker_cost)
avec les frais du marché (feesEnabled). Release corrigée par le saut de prix des échanges (voir telecharger.py)."""
import json, gzip, sys, bisect, math, collections, datetime as dt
sys.path.insert(0, 'src')
from polymarket_agent.idea_test import taker_cost, fee, verdict
D = json.load(open('experiments/emploi_nfp/donnees/marches.json'))
EXCLUS = {'42245', '42244'}                      # septembre 2025 : publication repoussée (shutdown), date inconnue ici
OVER = {'101764': '2025-12-16T13:30:00+00:00', '83746': '2025-12-16T13:30:00+00:00',   # novembre 2025
        '153683': '2026-02-11T13:30:00+00:00', '153669': '2026-02-11T13:30:00+00:00',   # janvier 2026
        '11744': '2024-08-02T12:30:00+00:00'}                                             # juillet 2024
D = [r for r in D if r['event'] not in EXCLUS]
for r in D:
    r['release'] = OVER.get(r['event'], r['release'])
trades = {}
def tr(e):
    if e not in trades: trades[e] = json.loads(gzip.decompress(open(f'experiments/emploi_nfp/donnees/echanges/echanges_{e}.json.gz', 'rb').read()))
    return trades[e]
def ts(r): return int(dt.datetime.fromisoformat(r['release']).timestamp())
def price_at(r, hours, tol=13 * 3600):
    t = ts(r) - hours * 3600; hs = [x[0] for x in r['hist']]; i = bisect.bisect_right(hs, t) - 1
    return (None, t) if i < 0 or t - hs[i] > tol else (r['hist'][i][1], t)
def fr(r): return .05 if r.get('feesEnabled') else 0.0
def table(kind, hours, bins):
    print(f'\n--- {kind}  T-{hours} h (prix historique 12 h) : OUI gagnés / attendus par tranche')
    for lo, hi in bins:
        c = [(p, r['yes_final'] > .5, r['event']) for r in D if r['kind'] == kind for p, _ in [price_at(r, hours)] if p is not None and lo <= p < hi]
        if not c: continue
        n = len(c); w = sum(x[1] for x in c); e = sum(x[0] for x in c); v = sum(x[0] * (1 - x[0]) for x in c)
        print(f'  {lo:.2f}-{hi:.2f}: n={n:3d} événements={len({x[2] for x in c}):2d} OUI gagnés {w:3d} / attendus {e:5.1f}  z={(w - e) / math.sqrt(v) if v else 0:+.2f}')
BINS = [(.02, .05), (.05, .10), (.10, .20), (.20, .35), (.35, .55), (.55, .75), (.75, .90), (.90, .98)]
if __name__ == '__main__':
    for kind in ('jobs', 'chomage'):
        for h in (6, 24, 72, 168):
            table(kind, h, BINS)
    print('\n=== achats simulés au prix des vrais échanges (premier échange 2 h après la décision), frais du marché')
    for kind in ('jobs', 'chomage', None):
        for side in ('NON', 'OUI'):
            for h in (24, 72, 168):
                for lo, hi in ((.05, .30), (.10, .25), (.03, .15), (.35, .75), (.70, .95)):
                    bets = []
                    for r in D:
                        if kind and r['kind'] != kind: continue
                        p, t = price_at(r, h)
                        if p is None or not lo <= p < hi: continue
                        yes, no = r['tokens'][:2]
                        tok, oth = (no, yes) if side == 'NON' else (yes, no)
                        c = taker_cost(tr(r['event']), tok, oth, int(t), window=2 * 3600, after=True)
                        if c is None: continue
                        c = min(c, .99); f = fr(r) * c * (1 - c)
                        win = (r['yes_final'] < .5) if side == 'NON' else (r['yes_final'] > .5)
                        bets.append({'gain': ((1 if win else 0) - c - f) / (c + f), 'evenement': r['event'], 'mois': r['release'][:7], 'cout': c})
                    if len(bets) < 10: continue
                    v = verdict(bets)
                    print(f'{kind or "tous":8s} {side} T-{h:3d}h prix {lo:.2f}-{hi:.2f}: {v["paris"]:3d} paris ({v["evenements"]} ev.) {v["rendement_moyen"]*100:+6.1f}% t_ev={v["confiance_evenements"]:+.2f} z_prix={v["z_prix"]:+.1f} mois {v["mois_gagnants"]} -> {v["verdict"]}')
