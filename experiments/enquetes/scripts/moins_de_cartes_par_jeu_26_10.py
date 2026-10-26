"""26/10 : les 57 paris réglés de `moins_de_cartes` (direct), par jeu (titre Gamma du marché) : le morceau LoL/Dota/CS2 tient-il ?"""
import sys, os, collections, math, requests
sys.path.insert(0, os.path.dirname(__file__))
from charge_fantome import charger
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
par = collections.defaultdict(list)
for p in charger('published_data/ledger/fantome/moins_de_cartes_v1.0.0.jsonl'):
    ev = s.get(f"https://gamma-api.polymarket.com/events/{p['event']}", timeout=30).json(); q = (ev.get('title') or '') + ' ' + ' '.join(t.get('label', '') for t in ev.get('tags') or [])
    jeu = next((j for k, j in (('Counter-Strike', 'CS2'), ('Dota', 'Dota 2'), ('League of Legends', 'LoL'), ('Valorant', 'Valorant')) if k.lower() in q.lower()), 'autre:' + q[:30])
    par[jeu].append(p)
for jeu, v in sorted(par.items(), key=lambda kv: -len(kv[1])):
    mise = sum(p['mise'] for p in v); g = sum(p['gain'] for p in v)
    e = sum(float(p['prix']) for p in v); w = sum(float(p['pay']) for p in v)
    var = sum(float(p['prix']) * (1 - float(p['prix'])) for p in v)
    print(f"{jeu:14s} {len(v):3d} paris  rendement {float(g/mise)*100:+6.1f} %  gagnés {w:.1f}/{e:.1f}  z {(w-e)/math.sqrt(var):+.2f}")
