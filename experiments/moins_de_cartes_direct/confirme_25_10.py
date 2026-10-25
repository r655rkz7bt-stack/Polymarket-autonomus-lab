"""Confirmation en direct de `moins_de_cartes` (25/10/2026, nuit) : les 54 paris réglés du fantôme, regroupés par MATCH réel
(identifiant d'événement Gamma = un match) et relus : question, règlement officiel, prix payé. Sortie : t par match, gagnés contre attendus."""
import sys, os, json, math, collections, requests
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger
H = {'User-Agent': 'curl/8'}
P = charger('published_data/ledger/fantome/moins_de_cartes_v1.0.0.jsonl')
info = {}
for p in P:
    r = requests.get(f"https://gamma-api.polymarket.com/markets/{p['market']}", headers=H, timeout=30).json()
    ev = (r.get('events') or [{}])[0]
    outs = json.loads(r['outcomes']) if isinstance(r.get('outcomes'), str) else r.get('outcomes')
    prices = json.loads(r['outcomePrices']) if isinstance(r.get('outcomePrices'), str) else r.get('outcomePrices')
    info[p['token']] = dict(q=r['question'], titre=ev.get('title'), closed=r.get('closed'), outs=outs, prices=prices, uma=r.get('umaResolutionStatus'))
json.dump(info, open('/tmp/claude-0/-home-user-Polymarket-autonomus-lab/4cfb3d36-d011-5723-99b7-d578e1281864/scratchpad/mdc_info.json', 'w'))
match = collections.defaultdict(list)
bad = 0
for p in P:
    i = info[p['token']]
    j = i['outs'].index(p['outcome'])
    off = float(i['prices'][j])                      # règlement officiel de la jambe achetée
    if abs(off - float(p['pay'])) > 1e-6:
        bad += 1; print('ÉCART règlement', i['q'], p['outcome'], off, p['pay'])
    match[p['event']].append(p)
print('règlements concordants :', len(P) - bad, '/', len(P))
rs = []
for t, L in match.items():
    g = sum(float(p['gain']) for p in L); m = sum(float(p['mise']) for p in L)
    rs.append(g / m)
n = len(rs); mm = sum(rs) / n; sd = (sum((x - mm) ** 2 for x in rs) / (n - 1)) ** .5
print('matchs', n, 'paris', len(P), 'rendement moyen par match', round(100 * mm, 1), 't', round(mm / (sd / math.sqrt(n)), 2))
gag = sum(float(p['pay']) for p in P); att = sum(float(p['prix']) for p in P); var = sum(float(p['prix']) * (1 - float(p['prix'])) for p in P)
print('gagnés', gag, 'attendus', round(att, 1), 'z', round((gag - att) / math.sqrt(var), 2))
for t, L in sorted(match.items(), key=lambda kv: -len(kv[1]))[:6]:
    print(len(L), t, [info[p['token']]['q'] for p in L][:2])
