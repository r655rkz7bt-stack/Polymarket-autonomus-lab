"""Charge un journal signé de fantôme et rend un pari par jeton (prix moyen, mise, gain, règlement)."""
import json, collections, sys
from decimal import Decimal as D

def charger(chemin):
    rows = [json.loads(l) for l in open(chemin)]
    paris = collections.OrderedDict()
    reglé = {}
    for x in rows:
        d = x['data']
        if x['type'] == 'BUY':
            p = paris.setdefault(d['token_id'], dict(token=d['token_id'], sh=D(0), cout=D(0), ts=x['ts'], outcome=d['outcome'],
                                                      event=d.get('event_id'), market=d.get('market_id'), achats=[], vente=D(0)))
            p['sh'] += D(d['shares']); p['cout'] += D(d['price']) * D(d['shares']) + D(d['fee'])
            p['achats'].append((x['ts'], D(d['price']), D(d['shares']), d.get('extra', {})))
        elif x['type'] == 'SELL':
            p = paris.get(d['token_id'])
            if p:
                p['sh'] -= D(d['shares']); p['vente'] += D(d['price']) * D(d['shares']) - D(d['fee'])
        elif x['type'] == 'SETTLE':
            reglé[d['token_id']] = (D(d['payout_per_share']), x['ts'], d.get('resolution'))
    out = []
    for t, p in paris.items():
        if t in reglé:
            pay, ts, res = reglé[t]
            p['gain'] = p['sh'] * pay + p['vente'] - p['cout']; p['gagne'] = pay > 0; p['reglé_ts'] = ts
            p['prix'] = sum(a[1] * a[2] for a in p['achats']) / sum(a[2] for a in p['achats'])
            p['mise'] = p['cout']
            out.append(p)
    return out

if __name__ == '__main__':
    ps = charger(sys.argv[1])
    print(len(ps), sum(p['gain'] for p in ps))
