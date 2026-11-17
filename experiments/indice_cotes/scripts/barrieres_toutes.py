"""Piste n° 65, branche « barrières » (17/11/2026, passage de 21 h) : « <X> odds hit <b>% / dip to <b>% by <date>? » (4 valeurs
horaires consécutives de l'indice PredictionMarketOdds au-delà du seuil). Chance = fréquence, sur les trajectoires PASSÉES du
sous-jacent Polymarket (jeton lu dans les échantillons publiés par l'indice), qu'une série de 4 heures consécutives franchisse le
seuil en H heures, en partant de la valeur du moment (variations absolues ou en logit). Aucune donnée postérieure à la décision.
Entrée : histo.json (sous-jacents horaires 400 jours, barrières 90 jours ; voir histo.py) ; sortie : tableau des décisions."""
import json, math, re, sys
from datetime import datetime, timezone

H = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'histo.json'))
CLE = [('Republican House', 'Republican House|republican_party'), ('Republican Senate', 'Republican Senate|republican_party'),
       ('Talarico', 'Talarico|james_talarico'), ("Ossoff", 'Ossoff|jon_ossoff'), ('Newsom', 'Newsom|gavin_newsom'), ('Rubio', 'Rubio|marco_rubio'),
       ('Vance', 'Vance|jd_vance'), ('Democratic 2028 presidential', 'Democratic 2028 presidential|democratic_party'),
       ('AOC', 'AOC|alexandria_ocasio_cortez'), ('Carlson', 'Carlson|tucker_carlson'), ('Shapiro', 'Shapiro|josh_shapiro'),
       ('Buttigieg', 'Buttigieg|pete_buttigieg'), ('DeSantis', 'DeSantis|ron_desantis'), ('Harris', 'Harris|kamala_harris'),
       ('Trump Jr', 'Trump Jr|donald_trump_jr'), ('trifecta', 'trifecta|democratic_trifecta'), ('Le Pen', 'Le Pen|marine_le_pen'),
       ('You Can See Everything', 'You Can See Everything|you_can_see_everything')]
Q = re.compile(r'odds (hit|dip to) (\d+(?:\.\d+)?)%')


def h_of(iso):
    return int(datetime.fromisoformat(iso.replace('Z', '+00:00')).timestamp()) // 3600


def serie(pts):
    hs = sorted(int(h) for h in pts)
    v, last = {}, None
    for h in range(hs[0], hs[-1] + 1):
        last = pts.get(str(h), last); v[h] = last
    return v


def lg(x):
    x = min(max(x, 0.002), 0.998); return math.log(x / (1 - x))


def il(z):
    return 1 / (1 + math.exp(-z))


def p_hit(v, t, x0, n_h, b, haut, logit, pas=24, min_departs=20):
    """Départs tous les `pas` heures dans l'historique AVANT t (la trajectoire entière avant t)."""
    hs = [h for h in sorted(v) if h + n_h < t]
    if len(hs) < n_h + 24 * min_departs:
        return None
    ok = n = 0
    for k in hs[:len(hs) - 0:pas]:
        if k + n_h >= t:
            break
        run, hit, v0 = 0, False, v[k]
        for i in range(1, n_h + 1):
            x = il(lg(x0) + lg(v[k + i]) - lg(v0)) if logit else x0 + v[k + i] - v0
            if (x >= b - 1e-9) if haut else (x <= b + 1e-9):
                run += 1
                if run >= 4:
                    hit = True; break
            else:
                run = 0
        n += 1; ok += hit
    return ok / n if n >= min_departs else None


def prix(pts, t):
    best = None
    for h, p in pts.items():
        if int(h) <= t and (best is None or int(h) > best[0]):
            best = (int(h), p)
    return best[1] if best and t - best[0] <= 48 else None


def deja_touche(v, debut, t, b, haut):
    run = 0
    for h in range(debut, t + 1):
        x = v.get(h)
        if x is None:
            continue
        if (x >= b - 1e-9) if haut else (x <= b + 1e-9):
            run += 1
            if run >= 4:
                return True
        else:
            run = 0
    return False


maintenant = int(datetime.now(timezone.utc).timestamp()) // 3600
U = {k: serie(p) for k, p in H['U'].items() if p}
lignes = []
for mid, b in H['bar'].items():
    cle = next((c for nom, c in CLE if nom in b['titre']), None)
    m = Q.search(b['question'])
    if not cle or not m or cle not in U or not H['B'].get(mid):
        continue
    haut, seuil = m.group(1) == 'hit', float(m.group(2)) / 100
    v, debut, fin = U[cle], h_of(b['cree']), h_of(b['fin'])
    issue = None
    if b['closed'] and b['issue']:
        issue = float(json.loads(b['issue'])[0])
    temps = list(range(debut + 24, min(fin, maintenant) - 24, 72)) if b['closed'] else [maintenant - 1]
    for t in temps:
        px = prix(H['B'][mid], t)
        x0 = v.get(t)
        if b['closed'] is False:
            x0 = float(H['tokens'][cle]['valeur'])  # valeur publiée de l'indice
        if px is None or x0 is None or deja_touche(v, debut, t, seuil, haut):
            continue
        n_h = fin - t
        pa, pl = p_hit(v, t, x0, n_h, seuil, haut, False), p_hit(v, t, x0, n_h, seuil, haut, True)
        lignes.append(dict(marche=mid, q=b['question'][:70], t=t, n_h=n_h, x0=round(x0, 3), seuil=seuil, haut=haut, prix=px,
                           p_abs=pa, p_logit=pl, issue=issue, event=b['event']))
json.dump(lignes, open('decisions.json', 'w'))
print(len(lignes), 'décisions')
