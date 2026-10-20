import json, math, sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "src")
from polymarket_agent.references import negbin_interval
D = "donnees/xt"
H = ("elonmusk", "WhiteHouse", "realDonaldTrump", "tedcruz", "ZelenskyyUa", "NYCMayor", "cz_binance")
T0 = datetime(2025, 10, 1, tzinfo=timezone.utc)

def hourly(h):
    ts = json.load(open(f"{D}/{h}.json"))
    first = datetime.fromisoformat(ts[0].replace("Z", "+00:00"))
    n = int((datetime(2026, 10, 20, 11, tzinfo=timezone.utc) - T0).total_seconds() // 3600)
    c = [0] * n
    for t in ts:
        i = int((datetime.fromisoformat(t.replace("Z", "+00:00")) - T0).total_seconds() // 3600)
        if 0 <= i < n: c[i] += 1
    return c, int((first - T0).total_seconds() // 3600)

def periods(start_idx, n):
    # vendredi 16:00 UTC
    d = T0
    while d.weekday() != 4: d += timedelta(days=1)
    d = d.replace(hour=16)
    out = []
    while True:
        i = int((d - T0).total_seconds() // 3600)
        if i + 168 > n: break
        if i - 336 >= start_idx: out.append(i)
        d += timedelta(days=7)
    return out

def model_mean(c, i, k, w, R, L, prof):
    rec = sum(c[i + k - R:i + k]) / R
    lng = sum(c[i + k - L:i + k]) / L
    rate = w * rec + (1 - w) * lng
    rem = 168 - k
    if not prof:
        return rate * rem
    # profil heure de la semaine des 4 semaines passées, mis à l'échelle du rythme
    base = [sum(c[i + k - 168 * j + h] for j in range(1, 5)) / 4 for h in range(rem)]
    tot = sum(sum(c[i + k - 168 * j: i + k - 168 * (j - 1)]) for j in range(1, 5)) / 4 / 168
    return sum(base) * (rate / tot) if tot > 0 else rate * rem

def run(w, R, L, disp, prof, width=20, checks=range(12, 168, 6), quiet=True):
    ll, n, cov50, cov90 = 0.0, 0, 0, 0
    per = {}
    for h in H:
        c, s = hourly(h)
        for i in periods(s, len(c)):
            final = sum(c[i:i + 168])
            for k in checks:
                so_far = sum(c[i:i + k])
                mu = model_mean(c, i, k, w, R, L, prof)
                lo = (final // width) * width
                p = negbin_interval(lo - so_far, lo + width - 1 - so_far, mu, disp)
                ll += math.log(max(p, 1e-4)); n += 1
                per.setdefault(h, [0, 0]); per[h][0] += math.log(max(p, 1e-4)); per[h][1] += 1
                # couverture : P(X <= final - so_far)
                cdf = negbin_interval(0, final - so_far, mu, disp)
                cdf_lo = negbin_interval(0, final - so_far - 1, mu, disp) if final - so_far > 0 else 0
                pit = (cdf + cdf_lo) / 2
                cov50 += 0.25 <= pit <= 0.75; cov90 += 0.05 <= pit <= 0.95
    return ll / n, n, cov50 / n, cov90 / n, {h: v[0] / v[1] for h, v in per.items()}

if __name__ == "__main__":
    best = []
    for prof in (False, True):
        for w in (0, 0.5, 1):
            for R in (24, 72, 168):
                if w == 0 and R != 72: continue
                for disp in (2, 4, 8, 16, 32):
                    r = run(w, R, 336, disp, prof)
                    best.append((r[0], prof, w, R, disp, r[1], r[2], r[3]))
    best.sort(reverse=True)
    for b in best[:12]:
        print(f"log {b[0]:.3f}  profil {b[1]!s:5} w {b[2]} R {b[3]:3} disp {b[4]:2}  n {b[5]}  cov50 {b[6]:.2f} cov90 {b[7]:.2f}")
    cur = run(0.5, 72, 336, 4, False)
    print("actuel (w .5, R 72, disp 4):", f"{cur[0]:.3f}", f"cov50 {cur[2]:.2f} cov90 {cur[3]:.2f}")
