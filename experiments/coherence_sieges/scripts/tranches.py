"""Probabilité de chaque tranche de l'échelle d'un État sous deux modèles : districts indépendants, et districts liés par un choc commun (logit + N(0, s²), s = 0 / 0,5 / 1,0).
La moyenne des districts ne change pas avec le choc ; les queues oui. Écart = modèle − prix de l'échelle (positif = tranche bon marché)."""
import json, re, math, random
random.seed(1)
d = json.load(open('experiments/coherence_sieges/releve_echelles.json'))
def logit(p): p = min(max(p, 1e-4), 1 - 1e-4); return math.log(p / (1 - p))
def sig(x): return 1 / (1 + math.exp(-x))
def sim(ps, s, n=20000):
    L = [logit(p) for p in ps]; cnt = {}
    for _ in range(n):
        z = random.gauss(0, s)
        k = sum(1 for l in L if random.random() < sig(l + z))
        cnt[k] = cnt.get(k, 0) + 1
    return {k: v / n for k, v in cnt.items()}
def prob(dist, t, k):
    if t == 'lt': return sum(v for j, v in dist.items() if j < k)
    if t == 'eq': return dist.get(k, 0)
    return sum(v for j, v in dist.items() if j >= k)
rows = []
for st, o in sorted(d.items()):
    ds = [v for v in o['districts'].values() if v]
    if len(ds) != len(o['districts']):
        continue
    ps = [v[0] for v in ds]
    # le choc doit conserver la moyenne de chaque district : on recalibre l'ordonnée à l'origine pour que Σ P = Σ p
    models = {}
    for s in (0.0, 0.5, 1.0):
        models[s] = sim(ps, s)
    for q, p, vol, liq in o['ladder']:
        m = re.search(r'fewer than (\d+)', q) or re.search(r'exactly (\d+)', q) or re.search(r'(\d+) or more', q)
        t = 'lt' if 'fewer than' in q else 'eq' if 'exactly' in q else 'ge'
        k = int(m[1])
        rows.append((st, t, k, p, [prob(models[s], t, k) for s in (0.0, 0.5, 1.0)], vol, liq))
json.dump(rows, open('experiments/coherence_sieges/tranches.json', 'w'))
big = sorted(rows, key=lambda r: -(abs(r[4][1] - r[3])))
print('plus gros écarts (modèle choc 0,5 − prix) :')
for st, t, k, p, ms, vol, liq in big[:25]:
    print(f"{st:15}{t}{k:>3} prix {p:.3f}  indép {ms[0]:.3f}  choc0,5 {ms[1]:.3f}  choc1 {ms[2]:.3f}  vol {int(vol)}  liq {int(liq)}")
