"""Robustesse de « NON sur la tranche favorite des emplois » : par moitié de période, sans les tranches ouvertes (« <x », « >x »), sans le meilleur événement."""
import sys, importlib.util, statistics
sys.path.insert(0, 'src')
spec = importlib.util.spec_from_file_location('fj', 'experiments/emploi_nfp/favori_jobs.py')
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    fj = importlib.util.module_from_spec(spec); spec.loader.exec_module(fj)
from polymarket_agent.idea_test import taker_cost, verdict
an = fj.an
for h in (6, 24, 72):
    F = fj.favoris('jobs', h)
    def gains(sel):
        out = []
        for d, e, p, b, win, r, t, _ in sel:
            yes, no = r['tokens'][:2]
            c = taker_cost(an.tr(e), no, yes, int(t), window=2 * 3600, after=True)
            if c is None: continue
            c = min(c, .99); f = an.fr(r) * c * (1 - c)
            out.append({'gain': ((0 if win else 1) - c - f) / (c + f), 'evenement': e, 'mois': d[:7], 'cout': c, 'd': d})
        return out
    n = len(F); half = n // 2
    tail = lambda x: x[3].strip().startswith(('<', '>', '≥', '≤')) or x[3].strip().endswith(('+', 'k+'))
    for name, sel in (('tous', F), ('1re moitié', F[:half]), ('2e moitié', F[half:]), ('sans tranches ouvertes', [x for x in F if not tail(x)])):
        g = gains(sel)
        if len(g) < 5: print(f'T-{h} {name}: {len(g)} paris'); continue
        v = verdict(g, min_bets=5)
        wins = sum(1 for x in sel if not x[4])
        print(f'T-{h:3d} {name:22s}: {len(g):2d} paris  {v["rendement_moyen"]*100:+6.1f}%  t_ev {v["confiance_evenements"]:+.2f}  (favori perd {wins}/{len(sel)})')
    g = gains(F)
    if len(g) > 6:
        best = max(g, key=lambda x: x['gain'])
        rest = [x for x in g if x is not best]
        print(f'T-{h:3d} sans le meilleur pari : {sum(x["gain"] for x in rest)/len(rest)*100:+.1f}% sur {len(rest)} paris')
