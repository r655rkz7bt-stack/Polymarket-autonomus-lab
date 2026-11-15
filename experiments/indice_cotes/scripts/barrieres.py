"""Piste n° 65 (barrières) : P(4 valeurs horaires consécutives >= seuil (ou <=) d'ici la fin) pour l'indice, par les trajectoires
passées du sous-jacent Polymarket (variations relatives au point de départ, avec et sans la dérive moyenne).
Usage : barrieres.py <token> <jours d'historique> <x0> <heures restantes> <seuil:sens>..."""
import sys, time, requests, statistics as st
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
tok, jours, x0, H = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
fin = int(time.time()); t = fin - jours * 86400; pts = {}
while t < fin:
    t2 = min(fin, t + 13 * 86400)
    for p in s.get('https://clob.polymarket.com/prices-history', params={'market': tok, 'startTs': t, 'endTs': t2, 'fidelity': 60}, timeout=30).json().get('history') or []:
        pts[int(p['t']) // 3600] = float(p['p'])
    t = t2
hs = sorted(pts); v = []; last = None
for h in range(hs[0], hs[-1] + 1):
    last = pts.get(h, last); v.append(last)
print(len(v), 'heures depuis', time.strftime('%Y-%m-%d', time.gmtime(hs[0] * 3600)))
derive = (v[-1] - v[0]) / len(v)
for arg in sys.argv[5:]:
    b, sens = arg.split(':'); b = float(b)
    for dd in (0, derive):
        n = ok = 0
        for k in range(0, len(v) - H, 24):
            run = 0; hit = False
            for i in range(1, H + 1):
                x = x0 + (v[k + i] - v[k]) - dd * i
                if (x >= b - 1e-9) if sens == 'haut' else (x <= b + 1e-9):
                    run += 1
                    if run >= 4: hit = True; break
                else: run = 0
            n += 1; ok += hit
        print(f"seuil {b} {sens} {'sans dérive' if dd else 'brut'} : {ok}/{n} = {ok/n:.3f}")
