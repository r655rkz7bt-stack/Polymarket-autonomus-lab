"""04/11 : les 18 paris du principal copiés de nf_court, un par un, contre ceux du fantôme (mise, gain, rapport)."""
import sys, json
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger
rows = [json.loads(l) for l in open('published_data/ledger/ledger.jsonl')]
strat = {}
for r in rows:
    if r['type'] == 'BUY': strat.setdefault(r['data']['token_id'], r['data']['strategy_id'])
P = {p['token']: p for p in charger('published_data/ledger/ledger.jsonl') if strat[p['token']] == 'nf_court'}
G = {p['token']: p for p in charger('published_data/ledger/fantome/nf_court_v1.0.0.jsonl')}
for t, p in sorted(P.items(), key=lambda kv: kv[1]['ts']):
    g = G.get(t)
    print(p['ts'][5:16], f"prix {float(p['prix']):.3f} mise P {float(p['mise']):6.1f} gain {float(p['gain']):+7.1f}",
          '| fantôme', (f"mise {float(g['mise']):6.1f} gain {float(g['gain']):+7.1f} ratio {float(p['mise']/g['mise']):.2f}" if g else 'absent/non réglé'))
