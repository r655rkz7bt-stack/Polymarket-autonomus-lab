"""Elon Musk : le rythme des dernières semaines prolongé (production : 7 j / 14 j, poids 0,5, dispersion 12) ou ramené vers une moyenne plus longue ?
Log-score moyen de la tranche de 20 posts contenant le total réel de la semaine (7 jours, départs toutes les 12 h), décision `lead` heures avant le début.
Aucun regard vers le futur : le rythme n'utilise que les posts antérieurs à la décision. Lancer depuis la racine : .venv/bin/python experiments/elon_rythme_long/scripts/calibration.py"""
import csv, bisect, sys, math
sys.path.insert(0, 'src')
from datetime import datetime, timedelta
from polymarket_agent.references import negbin_interval
ts = sorted(datetime.fromisoformat(r['ts_utc']) for r in csv.DictReader(open('experiments/elon_rythme_long/releves/posts_elon.csv')))
def cnt(a, b): return bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)
def run(lead, rw, disp, rh=168, lh=336, debut=None, fin=None, step=12):
    out = []
    s = ts[0] + timedelta(days=max(15, lh // 24 + 1))
    while s + timedelta(days=7) <= ts[-1]:
        T = s - timedelta(hours=lead)
        if (debut is None or s >= debut) and (fin is None or s < fin):
            rec = cnt(T - timedelta(hours=rh), T) / rh; lon = cnt(T - timedelta(hours=lh), T) / lh
            fc = (rw * rec + (1 - rw) * lon) * 168
            act = cnt(s, s + timedelta(days=7)); lo = act // 20 * 20
            out.append((math.log(max(negbin_interval(lo, lo + 19, fc, disp), 1e-6)), fc, act))
        s += timedelta(hours=step)
    return out
def moy(o): return sum(x[0] for x in o) / len(o)
if __name__ == '__main__':
    base = ts[0] + timedelta(days=15)
    # même départs pour toutes les lignes : on part du plus long retour (12 semaines)
    D0 = ts[0] + timedelta(days=85)
    sem = [x[2] for x in run(0, 0.5, 12, debut=D0, step=168)]
    print('semaines réelles (un départ par 7 j) n =', len(sem), 'moyenne', round(sum(sem) / len(sem)), 'min', min(sem), 'max', max(sem))
    for lead in (54, 120, 220):
        print('--- décision', lead, 'h avant le début ; mêmes départs depuis le', D0.date())
        res = []
        for rw in (0.5, 0.35, 0.2, 0.0):
            for lh in (336, 672, 1344, 2016):
                if lh == 336 and rw != 0.5 and rw != 0.0: pass
                for disp in (5, 8, 12, 20):
                    o = run(lead, rw, disp, 168, lh, debut=D0)
                    res.append((moy(o), rw, lh, disp, len(o)))
        prod = [r for r in res if r[1] == 0.5 and r[2] == 336 and r[3] == 12][0]
        print('production (0,5 ; 336 h ; d 12) :', round(prod[0], 3), 'n', prod[4])
        for r in sorted(res, reverse=True)[:6]: print('  ', [round(r[0], 3)] + list(r[1:]))
