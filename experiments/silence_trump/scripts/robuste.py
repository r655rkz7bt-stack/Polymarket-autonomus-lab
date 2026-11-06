"""Rythme robuste aux rafales : médiane des semaines passées au lieu de la moyenne des 14 derniers jours (Brier de « N ≥ seuil »)."""
import json, bisect, statistics, sys
from datetime import datetime, timezone
from polymarket_agent.references import negbin_interval
ts = sorted(datetime.fromisoformat(t.replace("Z", "+00:00")).timestamp() for t in json.load(open("experiments/silence_trump/donnees/trump_posts.json")))
H = 3600; W = 168 * H
n_between = lambda a, b: bisect.bisect_left(ts, b) - bisect.bisect_left(ts, a)
def weeks_before(T, k): return [n_between(T - (i + 1) * W, T - i * W) for i in range(k)]
rate_h = lambda T, h: n_between(T - h * H, T) / h
disp = 12
P = {
 "modele actuel (168h+336h)": lambda T, thr: negbin_interval(thr, 10**6, (.5 * rate_h(T, 168) + .5 * rate_h(T, 336)) * 168, disp),
 "168h + 84 j": lambda T, thr: negbin_interval(thr, 10**6, (.5 * rate_h(T, 168) + .5 * rate_h(T, 2016)) * 168, disp),
 "frequence 8 semaines passees": lambda T, thr: (sum(x >= thr for x in weeks_before(T, 8)) + .5) / 9,
 "frequence 12 semaines": lambda T, thr: (sum(x >= thr for x in weeks_before(T, 12)) + .5) / 13,
 "frequence 20 semaines": lambda T, thr: (sum(x >= thr for x in weeks_before(T, 20)) + .5) / 21,
 "negbin mediane 12 sem": lambda T, thr: negbin_interval(thr, 10**6, statistics.median(weeks_before(T, 12)), disp),
 "negbin mediane 12 sem, disp 6": lambda T, thr: negbin_interval(thr, 10**6, statistics.median(weeks_before(T, 12)), 6),
 "negbin mediane 20 sem, disp 6": lambda T, thr: negbin_interval(thr, 10**6, statistics.median(weeks_before(T, 20)), 6),
}
T = datetime(2026, 5, 1, tzinfo=timezone.utc).timestamp(); end = ts[-1] - W; S = {k: [0, 0] for k in P}; cnt = 0; ndec = 0
while T <= end:
    y = n_between(T, T + W); ndec += 1
    for thr in (100, 150, 200, 250, 300):
        o = 1.0 if y >= thr else 0.0
        for k, f in P.items():
            S[k][0] += (f(T, thr) - o) ** 2; S[k][1] += 1
    T += 6 * H
print("décisions", ndec, "(≈", ndec // 28, "semaines indépendantes)")
for k, (b, m) in sorted(S.items(), key=lambda kv: kv[1][0] / kv[1][1]): print(f"{k:34s} Brier {b / m:.4f}")
# Brier par seuil 200 seulement
T = datetime(2026, 5, 1, tzinfo=timezone.utc).timestamp(); S2 = {k: 0 for k in P}; c = 0
while T <= end:
    o = 1.0 if n_between(T, T + W) >= 200 else 0.0
    for k, f in P.items(): S2[k] += (f(T, 200) - o) ** 2
    c += 1; T += 6 * H
print("seuil 200 seul :", {k: round(v / c, 4) for k, v in S2.items()})

# Calibration du modèle actuel : quand il dit ≥ 0,9 pour « ≥ 200 », que se passe-t-il ?
T = datetime(2026, 2, 1, tzinfo=timezone.utc).timestamp(); rows = []
while T <= end:
    rows.append((P["modele actuel (168h+336h)"](T, 200), n_between(T, T + W) >= 200, T)); T += 6 * H
for lo, hi in ((0, .1), (.1, .5), (.5, .9), (.9, .99), (.99, 1.01)):
    s = [r for r in rows if lo <= r[0] < hi]
    if s: print(f"modèle {lo:.2f}-{hi:.2f}: {len(s)} décisions, {len({int(r[2] // 86400 // 7) for r in s})} semaines distinctes, ≥200 dans {sum(r[1] for r in s) / len(s):.0%}, moyenne dite {sum(r[0] for r in s) / len(s):.0%}")
