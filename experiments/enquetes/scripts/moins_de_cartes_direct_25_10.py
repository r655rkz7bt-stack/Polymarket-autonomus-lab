"""moins_de_cartes en direct (23-25/10) : rendement par jeu et par BO (titre de l'événement relu sur Gamma)."""
import sys, os, collections, requests, re
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
ps = charger('published_data/ledger/fantome/moins_de_cartes_v1.0.0.jsonl')
g = collections.defaultdict(list)
for p in ps:
    e = requests.get(f"https://gamma-api.polymarket.com/events/{p['event']}", headers={'User-Agent': 'curl/8'}, timeout=30).json()
    t = e.get('title', '')
    jeu = t.split(':')[0]; bo = re.search(r'\(BO(\d)\)', t)
    p['cle'] = (jeu, 'BO' + bo.group(1) if bo else '?')
    g[p['cle'][0]].append(p); g['BO' + (bo.group(1) if bo else '?')].append(p)
for k, v in sorted(g.items()):
    m = float(sum(p['mise'] for p in v)); ga = float(sum(p['gain'] for p in v))
    print(f"{k:10} {len(v):3d} paris  gagnés {sum(float(p['pay']) for p in v):5.1f}/{sum(float(p['prix']) for p in v):5.1f}  mise {m:6.0f}  gain {ga:+6.1f} ({100*ga/m:+.1f} %)")
