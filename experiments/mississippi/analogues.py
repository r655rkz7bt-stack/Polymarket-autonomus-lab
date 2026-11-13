"""Mississippi à Saint-Louis (USGS 07010000, relevé de 8 h, stat 30800) : analogues historiques (13/11/2026, chercheur).

Question : sachant le niveau du jour J (décrue après une onde) et le plus bas déjà vu dans la fenêtre du marché, quelle est la
chance que le plus bas relevé de J+1 à J+H passe sous un seuil ? Analogues : jours de septembre à décembre 1990-2025 où le
niveau est à ±tol du niveau du jour ET baisse (variation sur 3 jours dans [dmin, dmax]). Chaque année compte une fois au plus
par fenêtre de 10 jours (analogues liés). Sortie : distribution de (plus bas futur − niveau du jour) et de (plus bas futur −
plus bas des 30 jours d'avant).
Usage : python analogues.py donnees/stl_8h.json NIVEAU VAR3J H [tol]
"""
import json, sys, datetime as dt, statistics

f, niveau, var3, H = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
tol = float(sys.argv[5]) if len(sys.argv) > 5 else 2.0
v = json.load(open(f))['value']['timeSeries'][0]['values'][0]['value']
s = {dt.date.fromisoformat(x['dateTime'][:10]): float(x['value']) for x in v if x['value'] not in ('', '-999999')}
cas = []
last = {}
for d, x in sorted(s.items()):
    if d.year >= 2026 or not (d.month in (10, 11) or (d.month == 12 and d.day <= 10)):
        continue
    d3 = d - dt.timedelta(days=3)
    if d3 not in s or abs(x - niveau) > tol:
        continue
    ch = x - s[d3]
    if not (var3 - 1.0 <= ch <= var3 + 1.0):
        continue
    if d.year in last and (d - last[d.year]).days < 10:
        continue
    fut = [s[d + dt.timedelta(days=k)] for k in range(1, H + 1) if d + dt.timedelta(days=k) in s]
    avant = [s[d - dt.timedelta(days=k)] for k in range(1, 31) if d - dt.timedelta(days=k) in s]
    if len(fut) < H - 2 or not avant:
        continue
    last[d.year] = d
    cas.append((d, x, ch, min(fut), min(fut) - x, min(avant), min(fut) - min(avant)))
print(f"{len(cas)} analogues (niveau {niveau}±{tol}, variation 3 j {var3}±1, horizon {H} j)")
for c in cas:
    print(f"  {c[0]} niveau {c[1]:6.2f} var3 {c[2]:+5.2f} plus bas futur {c[3]:6.2f} (baisse {c[4]:+6.2f}) ; plus bas 30 j avant {c[5]:6.2f} → écart {c[6]:+6.2f}")
drops = sorted(c[4] for c in cas)
rel = sorted(c[6] for c in cas)
if drops:
    q = lambda xs, p: xs[min(len(xs) - 1, int(p * len(xs)))]
    print("baisse (plus bas futur − niveau du jour) : médiane %.2f, q10 %.2f, q25 %.2f, q75 %.2f, q90 %.2f" % (statistics.median(drops), q(drops, .1), q(drops, .25), q(drops, .75), q(drops, .9)))
    print("plus bas futur − plus bas des 30 j d'avant : médiane %.2f, q10 %.2f, q25 %.2f, q75 %.2f, q90 %.2f" % (statistics.median(rel), q(rel, .1), q(rel, .25), q(rel, .75), q(rel, .9)))
    for seuil in (0.995, -0.995):
        print(f"  part des analogues dont le plus bas futur passerait sous {seuil:+.2f} si on part du niveau du jour : "
              f"{sum(niveau + c[4] < seuil for c in cas) / len(cas):.3f}")
