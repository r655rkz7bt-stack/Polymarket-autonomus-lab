"""Distribution empirique des variations d'un sous-jacent (prix Polymarket) sur un horizon donné, à partir de prices-history
du CLOB (fidelity 60, tranches de 14 jours). Usage : vol_sousjacent.py <token_id> <jours d'historique> <horizon en heures>"""
import sys, time, requests, statistics as st, json, os
s = requests.Session(); s.headers['User-Agent'] = 'curl/8'
tok, jours, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
fin = int(time.time()); deb = fin - jours * 86400
pts = {}
t = deb
while t < fin:
    t2 = min(fin, t + 13 * 86400)
    r = s.get('https://clob.polymarket.com/prices-history', params={'market': tok, 'startTs': t, 'endTs': t2, 'fidelity': 60}, timeout=30).json()
    for p in r.get('history') or []:
        pts[int(p['t']) // 3600] = float(p['p'])
    t = t2
hs = sorted(pts)
print(len(hs), 'heures', 'de', time.strftime('%Y-%m-%d', time.gmtime(hs[0] * 3600)), 'à', time.strftime('%Y-%m-%d %H', time.gmtime(hs[-1] * 3600)))
dif = [pts[h + H] - pts[h] for h in hs if h + H in pts]
dif.sort()
n = len(dif)
q = lambda f: dif[int(f * (n - 1))]
print('horizon', H, 'h :', n, 'variations ; sd', round(st.pstdev(dif), 4), '; quantiles 1/5/25/50/75/95/99 %',
      [round(q(f), 4) for f in (.01, .05, .25, .5, .75, .95, .99)])
json.dump({'dif': dif, 'dernier': pts[hs[-1]]}, open(os.path.join(os.path.dirname(__file__), '..', 'donnees', f'dif_{tok[:8]}_{H}.json'), 'w'))
