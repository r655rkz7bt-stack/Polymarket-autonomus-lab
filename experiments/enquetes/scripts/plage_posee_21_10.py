"""Contrôle à la main du 21/10 : les achats posés SOUS la plage de prix (< 0,80) de la famille nf_sport_patiente
rapportent-ils autant que les achats dans la plage ? Un ordre posé servi bien plus bas que l'écart habituel = vendeur
qui sait quelque chose (sélection adverse). Lecture seule des journaux signés (published_data/)."""
import json, glob, sys, collections, math
rows = []
for p in glob.glob('published_data/ledger/fantome/nf_sport_patiente*.jsonl') + glob.glob('published_data/ledger/fantome/nf_tennis*.jsonl'):
    buys, settles = [], {}
    for l in open(p):
        d = json.loads(l)
        if d['type'] == 'BUY':
            buys.append(d)
        elif d['type'] == 'SETTLE':
            settles[d['data']['token_id']] = float(d['data']['payout_per_share'])
    for b in buys:  # un jeton réglé : tous ses achats comptent
        t = b['data']['token_id']
        if t in settles:
            sh, pr, fee = float(b['data']['shares']), float(b['data']['price']), float(b['data'].get('fee') or 0)
            rows.append((p.split('/')[-1], pr, sh * pr + fee, sh * settles[t] - sh * pr - fee, t))
print(len(rows), 'opérations réglées (toutes stratégies de la famille, paris communs comptés plusieurs fois)')
uniq = {}
for x in rows: uniq.setdefault((x[4], round(x[1], 2)), x)
rows_all = rows; rows = list(uniq.values())
print(len(rows), 'paris distincts (jeton, prix arrondi)')
def agg(name, sel):
    r = [x for x in rows if sel(x)]
    if not r: return
    mis = sum(x[2] for x in r); pnl = sum(x[3] for x in r)
    rets = [x[3] / x[2] for x in r if x[2] > 0]
    m = sum(rets) / len(rets); sd = (sum((v - m) ** 2 for v in rets) / max(len(rets) - 1, 1)) ** .5
    print(f'{name:28s} n={len(r):3d} misé={mis:8.0f} pnl={pnl:7.1f} rend={pnl/mis*100:6.1f}% t={m/(sd/math.sqrt(len(rets))+1e-9):5.2f}')
agg('prix < 0,80', lambda x: x[1] < .80)
agg('0,80 - 0,875', lambda x: .80 <= x[1] < .875)
agg('0,875 - 0,95', lambda x: .875 <= x[1] <= .95)
agg('> 0,95', lambda x: x[1] > .95)
