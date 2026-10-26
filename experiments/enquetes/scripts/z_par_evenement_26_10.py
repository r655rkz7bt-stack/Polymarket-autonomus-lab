"""26/10/2026 (soir) : t par pari contre t par événement, sur les stratégies qui reçoivent une part du capital principal.
Lancer depuis la racine du dépôt après `bash scripts/fetch_data.sh` et `bash scripts/fetch_published.sh`."""
import json, sys, math, collections
sys.path.insert(0, 'experiments/enquetes/scripts')
from charge_fantome import charger

d = json.load(open('published/data.json'))


def t(x):
    k = len(x); mu = sum(x) / k; sd = (sum((a - mu) ** 2 for a in x) / (k - 1)) ** .5
    return mu, (mu / (sd / math.sqrt(k)) if sd > 0 else 0.0)


for a in d['arene']:
    if not a.get('part_principal'):
        continue
    ps = charger(f"published_data/ledger/fantome/{a['nom']}.jsonl")
    ev = collections.defaultdict(lambda: [0., 0.])
    for p in ps:
        ev[p['event']][0] += float(p['gain']); ev[p['event']][1] += float(p['mise'])
    rb = [float(p['gain']) / float(p['mise']) for p in ps]
    re_ = [g / m for g, m in ev.values() if m > 0]
    print(a['nom'], 'part', a['part_principal'], 'paris', len(ps), 't par pari %.2f' % t(rb)[1],
          '| événements', len(ev), 't par événement %.2f (moy %.3f)' % (t(re_)[1], t(re_)[0]))
