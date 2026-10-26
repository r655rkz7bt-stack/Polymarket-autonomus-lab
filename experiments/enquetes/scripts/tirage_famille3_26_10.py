"""Famille 3 (26/10) : paris à donnée externe tirés au hasard (graine 26), marché relu sur Gamma, règlement comparé."""
import sys, os, random, requests, json, glob
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
STRATS = ['compteur_tweets', 'compteur_tweets_non', 'mots_prononces', 'fatigue_nhl', 'box_office_favori',
          'seismes_marche', 'toucher_metaux', 'cpi_tranches', 'moins_de_cartes', 'crypto_threshold_prix_bas']
pool = []
for s in STRATS:
    f = f'published_data/ledger/fantome/{s}_v1.0.0.jsonl'
    if os.path.exists(f):
        for p in charger(f):
            p['strat'] = s; pool.append(p)
print(len(pool), 'paris réglés dans', len(STRATS), 'stratégies à donnée externe')
random.seed(26)
for p in random.sample(pool, 12):
    m = requests.get(f"https://gamma-api.polymarket.com/markets/{p['market']}", headers={'User-Agent': 'curl/8'}, timeout=30).json()
    prices = json.loads(m.get('outcomePrices', '[]')); outs = json.loads(m.get('outcomes', '[]'))
    gagnant = [o for o, x in zip(outs, prices) if float(x) > 0.99]
    ok = (p['outcome'] in gagnant) == bool(p['gagne'])
    print(f"{p['strat']:22} {p['ts'][5:16]} {p['outcome']:>5} @{float(p['prix']):.3f} gain {float(p['gain']):+6.1f} | journal gagné={p['gagne']} Gamma gagnant={gagnant} {'OK' if ok else '<<< DIFFÉRENT'}")
    print('     ', m.get('question', '')[:110], '| source:', (m.get('resolutionSource') or '')[:60])
