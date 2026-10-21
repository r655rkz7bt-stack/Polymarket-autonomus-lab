"""Piste n° 3 (CPI) : acheter NON sur les tranches « improbables » d'un événement CPI. Prix horaire + écart 0,01 + frais 5 %·p(1-p)."""
import json, collections, datetime as dt, bisect, sys
sys.path.insert(0, 'src')
from polymarket_agent.idea_test import verdict, fee
D = json.load(open('experiments/cpi_nowcast/donnees/marches.json'))
def price_at(r, hours):
    rel = dt.datetime.fromisoformat(r['release'].replace('Z', '+00:00')).timestamp() - hours * 3600
    ts = [t for t, p in r['hist']]; i = bisect.bisect_right(ts, rel) - 1
    return None if i < 0 or rel - ts[i] > 6 * 3600 else r['hist'][i][1]
def run(H, lo, hi, kind=None, spread=0.01):
    bets = []
    for r in D:
        if kind and kind not in r['title']: continue
        p = price_at(r, H)
        if p is None or not lo <= p < hi: continue
        cost = min(1 - p + spread, .99)           # prix payé pour le NON
        win = 0 if r['yes_final'] > .5 else 1
        gain = (win - cost - fee(cost, .05)) / (cost + fee(cost, .05))
        bets.append({'gain': gain, 'evenement': r['event'], 'mois': r['release'][:7], 'cout': cost})
    return verdict(bets)
print('réglage | paris | rend | t_par_événement | mois gagnants | verdict')
for H in (24, 72, 168):
    for lo, hi in ((.03, .25), (.05, .30), (.10, .25), (.03, .10)):
        v = run(H, lo, hi)
        print(f'T-{H:3d}h NON {lo:.2f}-{hi:.2f}: {v["paris"]:3d} {v.get("rendement_moyen",0)*100:+6.1f}% t_ev={v.get("confiance_evenements",0):+.2f} mois {v.get("mois_gagnants")} -> {v["verdict"]}')
print('\nPar type, T-24h NON 0,05-0,30')
for kind in ('Annual', 'Monthly', 'YoY', 'MoM'):
    v = run(24, .05, .30, kind); print(kind, v['paris'], f'{v.get("rendement_moyen",0)*100:+.1f}%', v.get('confiance_evenements'), v['verdict'])
v = run(24, .05, .30); print(json.dumps(v, ensure_ascii=False)[:900])
