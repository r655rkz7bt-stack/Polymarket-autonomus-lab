"""Famille 2 : le gain des fantômes du haut du classement résiste-t-il sans son meilleur sport / sans l'ITF ? (28/10/2026) Discipline et source relues sur Gamma."""
import sys, json, collections, requests
sys.path.insert(0, 'src'); sys.path.insert(0, 'experiments/enquetes/scripts')
from concurrent.futures import ThreadPoolExecutor
from charge_fantome import charger
from polymarket_agent.pareto import discipline
from polymarket_agent.resolution_sources import domain_of
H = {'User-Agent': 'curl/8'}
TOP = ['nf_sport_patiente_prix_850_875', 'nf_sport_18_24h', 'nf_sport_prix_haut', 'nf_sport_patiente', 'nf_sport_patiente_6_24h', 'nf_sport', 'nf_court']
data = {n: charger(f'published_data/ledger/fantome/{n}_v1.0.0.jsonl') for n in TOP}
ms = sorted({p['market'] for v in data.values() for p in v})
def q(m):
    for _ in range(3):
        try:
            r = requests.get(f'https://gamma-api.polymarket.com/markets/{m}', headers=H, timeout=30)
            if r.status_code == 200:
                j = r.json(); return m, (j.get('question') or '', j.get('resolutionSource') or '', j.get('sportsMarketType'))
        except Exception: pass
    return m, ('', '', None)
with ThreadPoolExecutor(8) as ex: info = dict(ex.map(q, ms))
def tag(p):
    qs, src, smt = info[p['market']]
    d = discipline(qs, src); dom = domain_of(src) if src else ''
    return 'tennis-ITF' if dom == 'itftennis.com' else d
for n, ps in data.items():
    tot = sum(float(p['gain']) for p in ps)
    by = collections.defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])
    for p in ps:
        b = by[tag(p)]; b[0] += 1; b[1] += float(p['gain']); b[2] += float(p['mise']); b[3] += float(p['pay']); b[4] += float(p['prix'])
    print(f"{n}: {len(ps)} paris, gain {tot:+.0f} €")
    for k, b in sorted(by.items(), key=lambda kv: -kv[1][0])[:6]:
        print(f"    {k:15s} n={b[0]:3d} gain {b[1]:+8.1f} € sur {b[2]:8.1f} € ({100*b[1]/b[2]:+.1f} %)  gagnés {b[3]:.1f}/{b[4]:.1f}")
    best = max(by.items(), key=lambda kv: kv[1][1])
    print(f"    sans son meilleur sport ({best[0]}) : {tot-best[1][1]:+.0f} €")
