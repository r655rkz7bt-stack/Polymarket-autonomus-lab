"""Quelle chance de voir un « t » aussi bon par hasard parmi les 24 réglages (6 horizons × 4 plages de prix) ?
Hypothèse nulle : le marché est calibré à 24 h (le gagnant est tiré selon les prix normalisés à 24 h). Mêmes événements, mêmes prix payés, mêmes frais."""
import sys, random, math
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
import favori
from favori import *
HS = (96, 72, 48, 36, 24, 12); RANGES = ((0.5, 1.0), (0.5, 0.8), (0.8, 1.0), (0.6, 0.9)); RATE = 0.05
pre = []  # par événement : prix à 24 h normalisés, et pour chaque horizon la favorite (index, prix payé)
for c in favori.C:
    t24 = c["end"] - 24 * 3600
    p24 = [last_before(m["series"], t24, 8 * 3600) for m in c["ms"]]
    if any(p is None for p in p24): continue
    s = sum(p24); probs = [p / s for p in p24]
    per_h = {}
    for h in HS:
        t = c["end"] - h * 3600
        pr = [(last_before(m["series"], t, 8 * 3600), i) for i, m in enumerate(c["ms"])]
        if any(p is None for p, _ in pr): continue
        p0, i = max(pr)
        px = taker_buy(c["trades"], c["ms"][i]["tokens"][0], c["ms"][i]["tokens"][1], t, 2 * 3600, 1)
        if px is not None: per_h[h] = (i, p0, px)
    real = [m["win"] for m in c["ms"]].index(1)
    pre.append((probs, per_h, real, c["e"]["id"]))
print(len(pre), "événements avec prix à 24 h pour toutes les tranches")
def tstat(vals):
    """Statistique = rendement moyen par pari (au moins 30 paris) : le t de Student explose quand presque tous les paris gagnent (0,8-1,0)."""
    return sum(vals) / len(vals) if len(vals) >= 30 else None
def grid(winners):
    best, res = -9, {}
    for h in HS:
        for lo, hi in RANGES:
            g = []
            for (probs, per_h, real, eid), w in zip(pre, winners):
                if h not in per_h: continue
                i, p0, px = per_h[h]
                if not (lo <= p0 < hi and lo <= px < hi + 0.05): continue
                cost = px + RATE * px * (1 - px)
                g.append(((1.0 if i == w else 0.0) - cost) / cost)
            t = tstat(g)
            res[(h, lo, hi)] = (t, len(g), sum(g) / len(g) if g else None)
            if t is not None: best = max(best, t)
    return best, res
obs_best, obs = grid([x[2] for x in pre])
print("observé : meilleur rendement moyen =", round(obs_best, 2), "; (24 h, 0,5-1) =", round(obs[(24, 0.5, 1.0)][0], 2))
random.seed(24102026)
N = 2000; ge = 0; tops = []
for _ in range(N):
    winners = [random.choices(range(len(x[0])), weights=x[0])[0] for x in pre]
    b, _ = grid(winners); tops.append(b); ge += b >= obs_best
tops.sort()
print(f"sous l'hypothèse nulle : médiane du meilleur rendement {tops[N//2]:.2f}, 95e centile {tops[int(N*0.95)]:.2f} ; P(meilleur rendement >= observé) = {ge/N:.3f}")
top = sorted(((v[2], k, v[1]) for k, v in obs.items() if v[0] is not None), reverse=True)[:4]
print("meilleures cases observées (rendement, (h, plage), paris) :", [(round(a, 3), k, n) for a, k, n in top])
