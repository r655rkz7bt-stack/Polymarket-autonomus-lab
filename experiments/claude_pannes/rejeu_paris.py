"""Rejeu de paris (14/11/2026) : à plusieurs jours du mois (5, 10, 14, 18, 22, 26 ; 21 h UTC), Poisson au taux des
60 jours d'avant ; achat du OUI d'une tranche (ou du NON) si chance − prix − 0,02 (écart) − frais ≥ seuil.
Frais tech_fees 4 % × p(1−p). Prix = dernier point prices-history (fidelity 60) avant l'instant. Règlement = compte final
des cases (8/8 conformes aux règlements Gamma). Paris d'un même mois = un événement (verdict par mois)."""
import statistics, csv, os, json, math, datetime as dt, requests, calendar, collections, sys
H = {'User-Agent': 'curl/8'}
D = os.path.dirname(__file__)
jours = {x['date']: x['couleur'].lower() != '#76ad2a' for x in csv.DictReader(open(os.path.join(D, 'releves', 'jours.csv'))) if x['couleur'] != '#EAEAEA'}
EVTS = {'2026-03': 230853, '2026-04': 301324, '2026-05': 326334, '2026-06': 528220, '2026-07': 652128, '2026-08': 769586,
        '2026-09': 917980, '2026-10': 1111195}
def bornes(t):
    t = t.replace(' ', '')
    if t.startswith('<'): return 0, int(t[1:]) - 1
    if t.endswith('+'): return int(t[:-1]), 99
    if '-' in t: a, b = t.split('-'); return int(a), int(b)
    return int(t), int(t)
def pois(mu, k): return math.exp(-mu) * mu ** k / math.factorial(k) if k >= 0 else 0.0
cache = {}
def prix(tok, ts):
    if tok not in cache:
        y = []
        for a in range(ts - 30 * 86400, ts + 86400, 13 * 86400):
            y += requests.get('https://clob.polymarket.com/prices-history', params=dict(market=tok, startTs=a, endTs=a + 13 * 86400, fidelity=60), headers=H, timeout=30).json().get('history') or []
        cache[tok] = sorted({(p['t'], p['p']) for p in y})
    h = [p for t, p in cache[tok] if ts - 6 * 3600 <= t <= ts]
    return h[-1] if h else None
paris = []
for ym, eid in EVTS.items():
    y, m = map(int, ym.split('-')); nj = calendar.monthrange(y, m)[1]
    total = sum(jours[f'{ym}-{d:02d}'] for d in range(1, nj + 1))
    mk = requests.get(f'https://gamma-api.polymarket.com/events/{eid}', headers=H, timeout=30).json()['markets']
    for jour in (5, 10, 14, 18, 22, 26):
        t0 = dt.datetime(y, m, jour, 21, tzinfo=dt.timezone.utc); ts = int(t0.timestamp())
        vus = sum(jours[f'{ym}-{d:02d}'] for d in range(1, jour))
        deb = dt.date(y, m, jour)
        lam = sum(jours[(deb - dt.timedelta(days=i)).isoformat()] for i in range(1, 61)) / 60
        mu = lam * (nj - jour + 1)
        for x in mk:
            a, b = bornes(x['groupItemTitle'])
            p = sum(pois(mu, k - vus) for k in range(max(a, vus), min(b, 60) + 1))
            tok = json.loads(x['clobTokenIds'])[0]
            q = prix(tok, ts)
            if q is None or not 0.02 <= q <= 0.98: continue
            g = a <= total <= b
            for cote, ch, pr, gain in (('OUI', p, q, g), ('NON', 1 - p, 1 - q, not g)):
                pr = min(pr + 0.02, 0.99); f = 0.04 * pr * (1 - pr)
                paris.append(dict(mois=ym, jour=jour, tranche=x['groupItemTitle'], cote=cote, chance=ch, prix=pr, frais=f, gagne=gain,
                                  edge=ch - pr - f))
json.dump(paris, open(os.path.join(D, 'releves', 'rejeu_paris.json'), 'w'))
for seuil in (0.04, 0.06, 0.08, 0.12):
    for plage in ((0.05, 0.95), (0.10, 0.45), (0.45, 0.95)):
        s = [p for p in paris if p['edge'] >= seuil and plage[0] <= p['prix'] <= plage[1]]
        if not s: continue
        r = [((1 if p['gagne'] else 0) - p['prix'] - p['frais']) / p['prix'] for p in s]
        pm = collections.defaultdict(list)
        for p, x in zip(s, r): pm[p['mois']].append(x)
        mm = [sum(v) / len(v) for v in pm.values()]
        t = (sum(mm) / len(mm)) / (statistics.stdev(mm) / math.sqrt(len(mm))) if len(mm) > 2 and statistics.stdev(mm) > 0 else 0
        w = sum(p['gagne'] for p in s); e = sum(p['prix'] for p in s)
        print(f"seuil {seuil} prix {plage}: {len(s):3d} paris, {len(pm)} mois, rendement {sum(r)/len(r):+.1%}, t par mois {t:+.2f}, gagnés {w} pour {e:.1f}, mois positifs {sum(x>0 for x in mm)}/{len(mm)}")
