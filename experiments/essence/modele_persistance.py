"""Piste n° 4 (04/11/2026) : le prix AAA du jour J tient-il son niveau de la veille ? Modèle : normale centrée sur la tranche gagnante de la
veille, écart-type estimé sur les jours AVANT J (aucun regard vers le futur) ; comparé au prix du marché (normalisé) à 24 h et 12 h avant la fin."""
import csv, json, re, math
def bornes(lbl):
    n = [float(x) for x in re.findall(r'\d+\.\d+', lbl)]
    if lbl.startswith('<'): return (-1e9, n[0])
    if lbl.endswith('+'): return (n[0], 1e9)
    return (n[0], n[0] + 0.01)
def cdf(x, mu, s): return 0.5 * (1 + math.erf((x - mu) / (s * math.sqrt(2))))
rows = [r for r in csv.DictReader(open('experiments/essence/releve.csv')) if r['date'] >= '2026-10-16']
rows.sort(key=lambda r: r['date'])
mid = {}
for r in rows:
    lo, hi = bornes(r['gagnante'])
    mid[r['date']] = (lo + hi) / 2 if abs(hi - lo) < 1 else None
print('milieux connus', {k: round(v, 3) if v else None for k, v in mid.items()})
res = []
for i, r in enumerate(rows[1:], 1):
    prev = mid.get(rows[i - 1]['date'])
    if prev is None: continue
    d = [mid[rows[j]['date']] - mid[rows[j - 1]['date']] for j in range(1, i) if mid.get(rows[j]['date']) and mid.get(rows[j - 1]['date'])]
    s = max(0.012, (sum(x * x for x in d) / len(d)) ** 0.5) if len(d) >= 3 else 0.025
    t = json.loads(r['tranches']); out = {}
    for h, k in (('24h', 1), ('12h', 2)):
        px = [x[k] for x in t]
        if any(p == '' for p in px): continue
        tot = sum(px)
        pm = [p / tot for p in px]
        pmod = []
        for x in t:
            lo, hi = bornes(x[0]); pmod.append(max(1e-3, cdf(hi, prev, s) - cdf(lo, prev, s)))
        z = sum(pmod); pmod = [p / z for p in pmod]
        w = [j for j, x in enumerate(t) if x[0] == r['gagnante']][0]
        out[h] = (math.log(pmod[w]), math.log(max(pm[w], 1e-3)), tot)
    res.append((r['date'], round(s, 3), out))
for x in res: print(x[0], x[1], {k: (round(v[0], 2), round(v[1], 2), round(v[2], 2)) for k, v in x[2].items()})
for h in ('24h', '12h'):
    v = [x[2][h] for x in res if h in x[2]]
    if not v: print(h, "aucun prix lisible (carnets vides à 24 h)"); continue
    liq = [a for a in v if 0.9 <= a[2] <= 1.25]
    print(h, 'jours', len(v), 'log-score modèle', round(sum(a[0] for a in v) / len(v), 3), 'marché', round(sum(a[1] for a in v) / len(v), 3),
          '| jours à somme des prix 0,9-1,25 :', len(liq), round(sum(a[0] for a in liq) / max(1, len(liq)), 3), round(sum(a[1] for a in liq) / max(1, len(liq)), 3))
