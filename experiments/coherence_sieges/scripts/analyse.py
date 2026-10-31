"""Compare, par État, le nombre moyen de sièges démocrates de l'échelle (ses tranches) à la somme des prix démocrates des districts (la moyenne ne dépend pas de la corrélation)."""
import json, re, math
d = json.load(open('experiments/coherence_sieges/releve_echelles.json'))
def pb(ps):
    dist = [1.0]
    for p in ps:
        new = [0.0] * (len(dist) + 1)
        for k, v in enumerate(dist):
            new[k] += v * (1 - p); new[k + 1] += v * p
        dist = new
    return dist
print(f"{'État':15}{'dist.':>6}{'Σ districts':>12}{'E échelle':>10}{'Σ tranches':>11}{'écart':>7}  vol/liq min district")
for st, o in sorted(d.items()):
    ps = [v[0] for v in o['districts'].values() if v]
    n = len(o['districts'])
    lad = {}
    for q, p, vol, liq in o['ladder']:
        m = re.search(r'fewer than (\d+)', q)
        if m: lad[('lt', int(m[1]))] = p; continue
        m = re.search(r'exactly (\d+)', q)
        if m: lad[('eq', int(m[1]))] = p; continue
        m = re.search(r'(\d+) or more', q)
        if m: lad[('ge', int(m[1]))] = p
    tot = sum(lad.values())
    # espérance : fewer than k -> on suppose k-1 ; k or more -> k (borne basse : tranches ouvertes)
    e = sum(p * ({'lt': k - 1, 'eq': k, 'ge': k}[t]) for (t, k), p in lad.items())
    s = sum(ps)
    flag = '' if len(ps) == n else f' ({len(ps)}/{n} districts)'
    print(f"{st:15}{n:>6}{s:>12.2f}{e:>10.2f}{tot:>11.3f}{e - s:>+7.2f}{flag}")
