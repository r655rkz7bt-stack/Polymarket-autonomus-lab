"""Quel rythme prévoit le mieux les posts de Trump sur les 168 h suivantes ? (log-score binomiale négative, Brier de « 200+ »)."""
import json, math, bisect
from datetime import datetime, timedelta, timezone
from polymarket_agent.references import negbin_interval
ts = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() for t in json.load(open("experiments/silence_trump/donnees/trump_posts.json")))
def n_between(a, b): return bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)
H = 3600
t0 = datetime(2026, 2, 1, tzinfo=timezone.utc).timestamp(); t1 = ts[-1] - 168 * H
def rate(T, hrs): return n_between(T - hrs * H, T) / hrs
preds = {"recent168": lambda T: rate(T, 168), "recent72": lambda T: rate(T, 72), "recent48": lambda T: rate(T, 48),
         "long336": lambda T: rate(T, 336), "long84j": lambda T: rate(T, 84 * 24),
         "modele(0.5*168+0.5*336)": lambda T: .5 * rate(T, 168) + .5 * rate(T, 336),
         "modele_long(0.5*168+0.5*84j)": lambda T: .5 * rate(T, 168) + .5 * rate(T, 84 * 24),
         "mediane_jour_84j": None,
         "72h+84j": lambda T: .5 * rate(T, 72) + .5 * rate(T, 84 * 24),
         "min(168,72)+84j": lambda T: .5 * min(rate(T, 168), rate(T, 72)) + .5 * rate(T, 84 * 24)}
def daily_median(T):
    d = sorted(n_between(T - (k + 1) * 24 * H, T - k * 24 * H) for k in range(28)); return d[14] / 24
preds["mediane_jour_84j"] = lambda T: .5 * daily_median(T) + .5 * rate(T, 84 * 24)
import sys
disp = float(sys.argv[1]) if len(sys.argv) > 1 else 12
res = {k: [0, 0, 0] for k in preds}; n = 0
T = t0
while T <= t1:
    y = n_between(T, T + 168 * H); n += 1
    for k, f in preds.items():
        mu = f(T) * 168
        if mu <= 0: mu = 0.5
        p = negbin_interval(y, y, mu, disp) or 1e-9
        res[k][0] += math.log(max(p, 1e-12))
        for thr in (100, 150, 200, 250, 300):
            q = negbin_interval(thr, 10**6, mu, disp); o = 1.0 if y >= thr else 0.0
            res[k][1] += (q - o) ** 2; res[k][2] += 1
    T += 6 * H
print("décisions (toutes les 6 h, fenêtres chevauchantes) :", n, "semaines indépendantes ≈", n // 28, "dispersion", disp)
for k, (ll, br, m) in sorted(res.items(), key=lambda kv: -kv[1][0]):
    print(f"{k:34s} logvraisemblance moy {ll / n:8.3f}  Brier seuils 100-300 {br / m:.4f}")

# Cas de « silence » : rythme des 72 h dernières < 30 % du rythme des 84 jours
print("\nSILENCE (72 h < 30 % du rythme 84 j) : semaines suivantes")
T = t0; rows = []
while T <= t1:
    r72, r84 = rate(T, 72), rate(T, 84 * 24)
    if r72 < 0.3 * r84:
        rows.append((T, n_between(T, T + 168 * H), r84 * 168, r72 * 168))
    T += 6 * H
import statistics
print("décisions", len(rows), "jours distincts", len({int(r[0] // 86400) for r in rows}))
for r in rows[::4]:
    print(datetime.fromtimestamp(r[0], timezone.utc).strftime("%m-%d %Hh"), "suivante", r[1], "attendu long", round(r[2]), "72h x(168/72)", round(r[3]))
if rows:
    print("médiane suivante", statistics.median(r[1] for r in rows), "médiane attendu long", round(statistics.median(r[2] for r in rows)))
