"""Piste n° 65, rejeu : tranches « <X> odds on <date> » (indice PredictionMarketOdds) contre la loi empirique des variations du
sous-jacent Polymarket sur le même horizon, apprise sur les 90 jours AVANT la décision (pas de regard vers le futur).
Prix de décision : dernier point prices-history (CLOB, fidelity 60) <= T de chaque tranche ; achat simulé à ce prix + 0,01."""
import json, os, re, math, random, sys, requests
from datetime import datetime
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
D = os.path.join(os.path.dirname(__file__), '..', 'donnees')
SOUS = {'Senate': '11328770156420933991', '2028 presidential': '49084048476353771153083262278964615095037480324537117350127265918750912547378'}
cache = {}
def hist(tok, a, b):
    k = (tok, a, b)
    if k in cache: return cache[k]
    pts = {}
    t = a
    while t < b:
        t2 = min(b, t + 13 * 86400)
        r = s.get('https://clob.polymarket.com/prices-history', params={'market': tok, 'startTs': t, 'endTs': t2, 'fidelity': 60}, timeout=30).json()
        for p in r.get('history') or []: pts[int(p['t'])] = float(p['p'])
        t = t2
    cache[k] = pts; return pts
def at(pts, T):
    ks = [k for k in pts if k <= T]
    return pts[max(ks)] if ks else None
def bornes(lab):
    n = [float(x) / 100 for x in re.findall(r'\d+(?:\.\d+)?', lab)]
    if lab.startswith('<'): return (0, n[0])
    if lab.startswith('>') or lab.endswith('+'): return (n[0], 2)
    return (n[0], n[1])
ev = json.load(open(os.path.join(D, 'evenements.json')))
# jeton complet du Sénat
e32224 = s.get('https://gamma-api.polymarket.com/events/32224', timeout=20).json()
SOUS['Senate'] = json.loads(e32224['markets'][0]['clobTokenIds'])[0]
random.seed(1)
lignes = []
for e in ev:
    if ' odds on ' not in e['title'] or not e.get('closed'): continue
    sj = next(v for k, v in SOUS.items() if k in e['title'])
    fin = int(datetime.fromisoformat(e['endDate'].replace('Z', '+00:00')).timestamp())
    under = hist(sj, fin - 100 * 86400, fin + 3600)
    trs = []
    for m in e['markets']:
        lab = m.get('groupItemTitle') or ''
        if not re.search(r'\d', lab): continue
        res = float(json.loads(m['outcomePrices'])[0])
        tok = json.loads(m['clobTokenIds'])[0]
        trs.append((lab, bornes(lab), res, hist(tok, fin - 10 * 86400, fin)))
    xfin = at(under, fin)
    gag = [t[0] for t in trs if t[2] == 1]
    proxy = [t[0] for t in trs if t[1][0] - 1e-9 <= xfin < t[1][1] - 1e-9]
    for jours in (1, 2, 3, 5):
        T = fin - jours * 86400; H = jours * 86400
        x0 = at(under, T)
        if x0 is None: continue
        ks = sorted(k for k in under if T - 90 * 86400 <= k <= T - H)
        dif = [under[k + H] - under[k] for k in ks if (k + H) in under and k + H <= T]
        if len(dif) < 100: continue
        sim = [x0 + d + random.uniform(-0.003, 0.003) for d in dif for _ in range(3)]
        for lab, (a, b), res, ph in trs:
            p = at(ph, T)
            if p is None: continue
            q = sum(1 for v in sim if a - 1e-9 <= round(v, 3) < b - 1e-9) / len(sim)
            lignes.append(dict(ev=e['id'], titre=e['title'], j=jours, lab=lab, res=res, prix=p, modele=q, x0=x0))
    print(e['title'], '| gagnant', gag, '| proxy à la fin', round(xfin, 4), proxy)
json.dump(lignes, open(os.path.join(D, 'rejeu.json'), 'w'))
def ls(p, r): p = min(max(p, 0.01), 0.99); return math.log(p if r == 1 else 1 - p)
for j in (1, 2, 3, 5):
    L = [l for l in lignes if l['j'] == j]
    if not L: continue
    nev = len({l['ev'] for l in L})
    lm = sum(ls(l['modele'], l['res']) for l in L) / nev; lp = sum(ls(l['prix'], l['res']) for l in L) / nev
    print(f"J-{j} : {nev} événements, {len(L)} tranches ; log-score (somme par événement) modèle {lm:.3f} contre prix {lp:.3f}")
    for seuil in (0.05, 0.08, 0.12):
        paris = []
        for l in L:
            if l['modele'] - l['prix'] >= seuil and l['prix'] + 0.01 < 0.97: paris.append((l['prix'] + 0.01, l['res'], l['ev']))
            if l['prix'] - l['modele'] >= seuil and (1 - l['prix']) + 0.01 < 0.97: paris.append((1 - l['prix'] + 0.01, 1 - l['res'], l['ev']))
        if paris:
            cout = sum(p for p, _, _ in paris); gain = sum(r for _, r, _ in paris)
            print(f"   seuil {seuil}: {len(paris)} paris ({len({x[2] for x in paris})} év.), gagnés {gain:.0f} pour {cout:.2f} payés, rendement {gain/cout-1:+.1%}")
