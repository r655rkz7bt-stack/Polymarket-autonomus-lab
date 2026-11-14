"""Rejeu sur les 8 mois réglés (mars-octobre 2026) : au 14 du mois 21 h UTC, prix du marché contre deux modèles,
log-score de la tranche gagnante. Modèle P : Poisson au taux des 60 jours d'avant, pour les jours restants (jour 14 compté
entier). Modèle E : comptes « jour 15 → fin » des 12 mois d'avant (fréquence empirique). Aucun regard vers le futur :
seuls les jours ≤ 14 du mois et les mois finis d'avant."""
import csv, os, json, math, datetime as dt, requests, collections, re, calendar
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
def pois(mu, k): return math.exp(-mu) * mu ** k / math.factorial(k)
def fin_par_mois():
    c = collections.defaultdict(int)
    for d, b in jours.items():
        if int(d[8:10]) >= 15: c[d[:7]] += b
    return c
FIN = fin_par_mois()
res = []
for ym, eid in EVTS.items():
    y, m = map(int, ym.split('-')); nj = calendar.monthrange(y, m)[1]
    t0 = dt.datetime(y, m, 14, 21, tzinfo=dt.timezone.utc)
    vus = sum(jours[f'{ym}-{d:02d}'] for d in range(1, 14))  # jours 1-13 finis
    deb = dt.date(y, m, 14)
    passe = [jours[(deb - dt.timedelta(days=i)).isoformat()] for i in range(1, 61)]
    lam = sum(passe) / 60; reste = nj - 13  # jour 14 + jours 15..fin
    mois_av = [k for k in sorted(FIN) if k < ym][-12:]
    emp = collections.Counter(FIN[k] for k in mois_av)
    total = sum(jours[f'{ym}-{d:02d}'] for d in range(1, nj + 1))
    e = requests.get(f'https://gamma-api.polymarket.com/events/{eid}', headers=H, timeout=30).json()
    for mk in e['markets']:
        a, b = bornes(mk['groupItemTitle'])
        pP = sum(pois(lam * reste, k - vus) for k in range(max(a, vus), min(b, 60) + 1))
        # E : jours 15..fin empiriques ; le jour 14 ajouté au taux des 60 jours
        pE = 0
        for x, n in emp.items():
            for j14 in (0, 1):
                pj = lam if j14 else 1 - lam
                if a <= vus + j14 + x <= b: pE += n / len(mois_av) * pj
        tok = json.loads(mk['clobTokenIds'])[0]
        h = requests.get('https://clob.polymarket.com/prices-history', params=dict(market=tok, startTs=int(t0.timestamp()) - 6 * 3600, endTs=int(t0.timestamp()), fidelity=60), headers=H, timeout=30).json().get('history') or []
        prix = h[-1]['p'] if h else None
        gagne = a <= total <= b
        res.append((ym, mk['groupItemTitle'], vus, round(lam, 3), prix, round(pP, 3), round(pE, 3), gagne))
for r in res: print(*r)
ls = collections.defaultdict(float); n = 0
for r in res:
    if r[7] and r[4] is not None:
        n += 1
        for nom, p in (('marché', r[4]), ('Poisson 60 j', r[5]), ('empirique 12 mois', r[6]), ('moitié marché/P', (r[4] + r[5]) / 2)):
            ls[nom] += math.log(min(max(p, 0.01), 0.99))
print('log-score moyen de la tranche gagnante sur', n, 'mois :', {k: round(v / n, 3) for k, v in ls.items()})
