"""04/11/2026 : les échelles de sièges relevées le 31/10 contre les prix du 04/11 (lendemain de l'élection).
Pour chaque tranche : prix du 31/10, modèle (districts liés, choc 0,5), prix actuel (proxy du résultat quand il est <= 0,05 ou >= 0,95).
Mesure : le modèle des districts est-il plus proche de l'issue que le prix de l'échelle ? (écart quadratique, Brier)."""
import json, re, requests
H = {'User-Agent': 'curl/8'}
d = json.load(open('experiments/coherence_sieges/releve_echelles.json'))
tr = json.load(open('experiments/coherence_sieges/tranches.json'))
modele = {(st, t, k): (p, ms[1], liq) for st, t, k, p, ms, vol, liq in tr}
out = []
for st, o in sorted(d.items()):
    try:
        e = requests.get(f"https://gamma-api.polymarket.com/events/{o['ladder_event']}", headers=H, timeout=30).json()
    except Exception as x:
        print(st, 'erreur', x); continue
    for m in e['markets']:
        q = m['question']
        mm = re.search(r'fewer than (\d+)', q) or re.search(r'exactly (\d+)', q) or re.search(r'(\d+) or more', q)
        if not mm: continue
        t = 'lt' if 'fewer than' in q else 'eq' if 'exactly' in q else 'ge'
        key = (st, t, int(mm[1]))
        if key not in modele: continue
        pn = float(json.loads(m['outcomePrices'])[0])
        p0, mod, liq = modele[key]
        out.append((st, t, int(mm[1]), p0, mod, pn, bool(m.get('closed')), liq))
json.dump(out, open('experiments/coherence_sieges/lecture_04_11.json', 'w'))
sure = [r for r in out if r[5] <= 0.05 or r[5] >= 0.95]
print(len(out), 'tranches,', len(sure), 'dont issue quasi connue,', sum(r[6] for r in out), 'réglées')
b_prix = b_mod = 0
for st, t, k, p0, mod, pn, cl, liq in sure:
    y = 1.0 if pn >= 0.95 else 0.0
    b_prix += (p0 - y) ** 2; b_mod += (mod - y) ** 2
print(f'Brier prix 31/10 {b_prix/len(sure):.4f}   Brier modèle districts {b_mod/len(sure):.4f}   ({len(sure)} tranches)')
print('écart modèle-prix >= 0,10 :')
n = g = 0; gains = []
for st, t, k, p0, mod, pn, cl, liq in sorted(out, key=lambda r: -abs(r[4] - r[3])):
    if abs(mod - p0) < 0.10: break
    cote = 'OUI' if mod > p0 else 'NON'
    paye = p0 if cote == 'OUI' else 1 - p0
    val = pn if cote == 'OUI' else 1 - pn
    gains.append((val - paye) / paye)
    print(f'{st:15}{t}{k:>3} prix31/10 {p0:.3f} modèle {mod:.3f} prix04/11 {pn:.3f} -> {cote} payé {paye:.3f} vaut {val:.3f} ({100*(val-paye)/paye:+.0f} %) liq {int(liq)}')
print('rendement moyen (valeur au 04/11) des', len(gains), 'tranches à écart >= 0,10 :', f'{100*sum(gains)/len(gains):+.1f} %', ' médian', f'{100*sorted(gains)[len(gains)//2]:+.1f} %')
