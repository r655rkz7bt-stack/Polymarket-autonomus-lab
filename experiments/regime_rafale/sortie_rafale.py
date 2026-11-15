"""15/11/2026 : la rafale quitte la fenêtre de 7 jours mais reste dans celle de 14 jours (rythme 336 h ≥ 2 × rythme 168 h).
Le mélange « actuel » (½ 168 h + ½ 336 h) prévoit-il trop haut ? Archive CNN, périodes de 7 jours (mardi et vendredi 12 h Est),
décisions à 24-144 h. Rend : log-perte par estimateur sur les seuils 50..500, total final prévu contre réel, et la chance
« total dans [lo, hi] » des tranches de 20 autour de la prévision (calibration par tranche)."""
import math
exec(open("backtest.py").read().split("NAMES =")[0])
TH = list(range(50, 501, 25))
NAMES = ["actuel", "7j+84j", "84j", "mediane", "min(actuel,72h)"]
def ratio(now): r = lambda h: n_between(now - h * H, now) / h; return r(336) / max(r(168), 1e-9)
for lo_r, hi_r in ((0, 1.5), (1.5, 2.0), (2.0, 99)):
    ll = {n: [0.0, 0] for n in NAMES}; pred = {n: [] for n in NAMES}; real = []; periods = set()
    buck = {n: [0.0, 0.0, 0] for n in NAMES}  # somme p, somme réalisé, n pour les tranches de 20
    for s in starts():
        final = n_between(s, s + 7 * 86400)
        if final == 0: continue
        for h in (24, 48, 72, 96, 120, 144):
            now = s + h * H; cnt = n_between(s, now); rem = 168 - h
            q = ratio(now)
            if not (lo_r <= q < hi_r): continue
            periods.add(s); real.append(final)
            for n in NAMES:
                m = est(n, now, s) * rem; pred[n].append(cnt + m)
                for x in TH:
                    if x <= cnt and final < x: continue
                    p = min(max(negbin_interval(x - cnt, 10 ** 9, m, 12), .005), .995); y = final >= x
                    ll[n][0] += -math.log(p if y else 1 - p); ll[n][1] += 1
                for lo in range(0, 400, 20):
                    if lo + 19 < cnt: continue
                    p = negbin_interval(lo - cnt, lo + 19 - cnt, m, 12)
                    if p < 0.02: continue
                    buck[n][0] += p; buck[n][1] += (lo <= final <= lo + 19); buck[n][2] += 1
    print(f"\nrapport 336h/168h dans [{lo_r}, {hi_r}) : {len(real)} décisions, {len(periods)} périodes ; total réel moyen {sum(real)/max(len(real),1):.1f}")
    for n in NAMES:
        if not real: break
        err = sum(p - r for p, r in zip(pred[n], real)) / len(real)
        print(f"  {n:16s} log-perte {ll[n][0]/max(ll[n][1],1):.4f} ({ll[n][1]})  total prévu − réel {err:+6.1f}  "
              f"tranches de 20 : dit {buck[n][0]/max(buck[n][2],1):.3f} réel {buck[n][1]/max(buck[n][2],1):.3f} ({buck[n][2]})")
