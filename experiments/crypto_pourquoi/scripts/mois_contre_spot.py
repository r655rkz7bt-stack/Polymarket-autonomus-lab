"""28/10/2026 : le rendement mensuel du « NON crypto 0,10-0,45 » (contrer_crypto_passe/resultats_baseline_non_2024_2026.txt, 33 mois) suit-il le rendement du mois
du Bitcoin / de l'Ethereum (barres Binance, donnees/spot_*.json) ? Un NON sur un « au-dessus de X » qui coûte 0,10-0,45 est un pari à la BAISSE : s'il gagne les mois où
le cours baisse et perd quand il monte, c'est de la tendance (bêta) et pas une erreur de prix. Usage : python mois_contre_spot.py"""
import json, re, math, datetime as dt
rows = {}
for l in open("experiments/contrer_crypto_passe/resultats_baseline_non_2024_2026.txt"):
    m = re.match(r"\| NON 0,10-0,45 mois (\d{4}-\d\d) \| (\d+) \| \d+ \| ([+-][\d.]+)% ", l)
    if m: rows[m[1]] = (int(m[2]), float(m[3]))
def mensuel(a):
    r = json.load(open(f"experiments/crypto_pourquoi/donnees/spot_{a}.json")); by = {}
    for t, o, h, l, c in r:
        k = dt.datetime.utcfromtimestamp(t).strftime("%Y-%m"); by.setdefault(k, [o, c]); by[k][1] = c
    return {k: (c / o - 1) * 100 for k, (o, c) in by.items()}
def corr(x, y):
    n = len(x); mx, my = sum(x) / n, sum(y) / n
    sx = math.sqrt(sum((a - mx) ** 2 for a in x)); sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sx * sy)
def rang(v): o = sorted(range(len(v)), key=lambda i: v[i]); r = [0] * len(v); [r.__setitem__(i, k) for k, i in enumerate(o)]; return r
for a in ("BTC", "ETH"):
    mo = mensuel(a)
    for nmin in (1, 30, 100):
        ks = [k for k, (n, g) in sorted(rows.items()) if n >= nmin and k in mo]
        x = [mo[k] for k in ks]; y = [rows[k][1] for k in ks]
        sg = sum(1 for a_, b_ in zip(x, y) if a_ * b_ < 0)
        print(f"{a} mois ≥ {nmin:3d} paris : {len(ks)} mois, corrélation {corr(x, y):+.2f} (rang {corr(rang(x), rang(y)):+.2f}), gain de signe opposé au cours : {sg}/{len(ks)}")
        if nmin == 100:
            n = len(ks); mx, my = sum(x) / n, sum(y) / n
            b = sum((a_ - mx) * (b_ - my) for a_, b_ in zip(x, y)) / sum((a_ - mx) ** 2 for a_ in x)
            print(f"   pente {b:+.2f} point de rendement par point de cours ; ordonnée (rendement quand le cours est stable) {my - b * mx:+.1f} % ; cours moyen des mois {mx:+.1f} %")
    if a == "BTC":
        print("   détail : " + " ".join(f"{k[2:]}:{mo[k]:+.0f}/{rows[k][1]:+.0f}" for k in sorted(rows) if rows[k][0] >= 100 and k in mo))
# Régression pondérée par le nombre de paris : rendement du mois = a + b × cours du mois (BTC, ETH, et la moyenne des deux). a = ce qui reste quand le cours est stable.
def mco(x, y, w):
    W = sum(w); mx = sum(a * c for a, c in zip(x, w)) / W; my = sum(a * c for a, c in zip(y, w)) / W
    sxx = sum(c * (a - mx) ** 2 for a, c in zip(x, w)); b = sum(c * (a - mx) * (d - my) for a, c, d in zip(x, w, y)) / sxx
    a0 = my - b * mx; res = [d - a0 - b * a for a, d in zip(x, y)]
    n = len(x); s2 = sum(c * r * r for c, r in zip(w, res)) / (W - W / n * 2) if n > 2 else float("nan")  # variance résiduelle approchée
    s2 = sum(r * r for r in res) / (n - 2)
    se_a = math.sqrt(s2 * (1 / n + (sum(x) / n) ** 2 / sum((a - sum(x) / n) ** 2 for a in x)))
    r2 = 1 - sum(r * r for r in res) / sum((d - sum(y) / n) ** 2 for d in y)
    return a0, se_a, b, r2
for nmin in (30, 100):
    for a in ("BTC", "ETH"):
        mo = mensuel(a); ks = [k for k, (n, g) in sorted(rows.items()) if n >= nmin and k in mo]
        a0, se, b, r2 = mco([mo[k] for k in ks], [rows[k][1] for k in ks], [rows[k][0] for k in ks])
        print(f"régression {a}, mois ≥ {nmin} paris ({len(ks)} mois) : rendement stable a = {a0:+.1f} % (± {se:.1f}), pente {b:+.2f}, R² {r2:.2f}")
tot = sum(n for n, g in rows.values()); print(f"rendement moyen pondéré des {len(rows)} mois : {sum(n * g for n, g in rows.values()) / tot:+.1f} % ; cours BTC moyen des mêmes mois {sum(mensuel('BTC')[k] for k in rows) / len(rows):+.1f} %")
