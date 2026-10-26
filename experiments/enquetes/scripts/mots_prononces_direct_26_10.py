"""26/10 : `mots_prononces` (retenue le 20/10 : +19 à +27 % aux vrais prix) fait +0,1 % sur 50 paris réglés en direct (21 gagnés pour 23,4 attendus).
Dissection : type d'événement, prix, estimation, délai, et ce que le test passé faisait (billets ≥ 0,30)."""
import sys, os, json, math, collections, requests
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
v = charger('published_data/ledger/fantome/mots_prononces_v1.0.0.jsonl')
rows = []
for p in v:
    m = s.get(f"https://gamma-api.polymarket.com/markets/{p['market']}", timeout=30).json()
    ev = s.get(f"https://gamma-api.polymarket.com/events/{p['event']}", timeout=30).json()
    est = p['achats'][0][3].get('est_probability')
    rows.append(dict(ts=p['ts'][:16], titre=(ev.get('title') or '')[:60], q=(m.get('question') or '')[:60], out=p['outcome'], prix=float(p['prix']), est=float(est) if est else None,
                     pay=float(p['pay']), mise=float(p['mise']), gain=float(p['gain'])))
json.dump(rows, open('/tmp/claude-0/sp/mots.json', 'w'))
for r in sorted(rows, key=lambda r: r['ts']): print(r['ts'], f"{r['prix']:.2f} est {r['est']} pay {r['pay']:.0f} {r['gain']:+6.1f}", r['out'], '|', r['titre'], '|', r['q'])
