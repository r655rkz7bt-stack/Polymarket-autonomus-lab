"""CPI : même simulation que simuler.py mais au prix RÉELLEMENT payé (échanges des preneurs, idea_test.taker_cost).
NON acheté = acheter le jeton NON (ou vendre le OUI) ; prix = dernier échange dans les 2 h avant la décision (cas "avant"),
ou premier échange dans les 2 h APRÈS (prix qu'on aurait payé, cas "après")."""
import json, sys, datetime as dt
from pathlib import Path
sys.path.insert(0, 'src')
from polymarket_agent.http_client import HttpClient
from polymarket_agent.idea_test import fetch_event_trades, taker_cost, verdict, fee
D = json.load(open('experiments/cpi_nowcast/donnees/marches.json'))
ev = json.load(open('experiments/cpi_nowcast/donnees/events.json'))
toks = {m['id']: json.loads(m['clobTokenIds']) for e in ev.values() for m in e['markets'] if m.get('clobTokenIds')}
http = HttpClient(timeout=40, min_interval=0.15)
cache = Path('experiments/cpi_nowcast/donnees/echanges')
trades = {}
for eid in sorted({r['event'] for r in D}):
    trades[eid] = fetch_event_trades(http, cache, eid)
print('échanges:', {k: len(v) for k, v in list(trades.items())[:5]}, '... total', sum(len(v) for v in trades.values()))
import bisect
def price_at(r, hours):
    rel = dt.datetime.fromisoformat(r['release'].replace('Z', '+00:00')).timestamp() - hours * 3600
    ts = [t for t, p in r['hist']]; i = bisect.bisect_right(ts, rel) - 1
    return (None, rel) if i < 0 or rel - ts[i] > 6 * 3600 else (r['hist'][i][1], rel)
def run(H, lo, hi, mode):
    bets, nof = [], 0
    for r in D:
        p, ts = price_at(r, H)
        if p is None or not lo <= p < hi: continue
        yes, no = toks[r['market']]
        c = taker_cost(trades[r['event']], no, yes, int(ts), window=2 * 3600, after=(mode == 'après'))
        if c is None: nof += 1; continue
        c = min(c + 0.0, .99)
        win = 0 if r['yes_final'] > .5 else 1
        g = (win - c - fee(c, .05)) / (c + fee(c, .05))
        bets.append({'gain': g, 'evenement': r['event'], 'mois': r['release'][:7], 'cout': c})
    v = verdict(bets); v['sans_echange'] = nof; return v
for mode in ('avant', 'après'):
    print('\n==', mode)
    for H in (24, 72, 168):
        for lo, hi in ((.03, .25), (.05, .30), (.10, .25), (.03, .10)):
            v = run(H, lo, hi, mode)
            print(f'T-{H:3d}h NON {lo:.2f}-{hi:.2f}: {v["paris"]:3d} paris (sans échange {v["sans_echange"]:3d}) {v.get("rendement_moyen",0)*100:+6.1f}% t_ev={v.get("confiance_evenements",0):+.2f} mois {v.get("mois_gagnants")} -> {v["verdict"]}')
