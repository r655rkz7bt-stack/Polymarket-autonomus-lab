"""Rythme de Trump : quelle estimation du rythme prévoit le mieux le total d'une période de 7 jours ?
Archive CNN (posts de @realDonaldTrump). Décisions à 24/48/72/96/120/144 h du début ; seuils 50..500."""
import json, sys, math, bisect, datetime as D
from zoneinfo import ZoneInfo
sys.path.insert(0, "../../src")
from polymarket_agent.references import negbin_interval
E_ = ZoneInfo("America/New_York")
arch = json.load(open(sys.argv[1]))
T = sorted(D.datetime.fromisoformat(x["created_at"].replace("Z", "+00:00")).timestamp() for x in arch)
def n_between(a, b): return bisect.bisect_right(T, b) - bisect.bisect_right(T, a)
H = 3600
def starts():
    d = D.date(2023, 6, 1)
    while d < D.date(2026, 11, 1):
        if d.weekday() in (1, 4):
            s = D.datetime(d.year, d.month, d.day, 12, tzinfo=E_).timestamp()
            if s + 7 * 86400 < T[-1]: yield s
        d += D.timedelta(days=1)
def est(name, now, s):
    r = lambda h: n_between(now - h * H, now) / h
    if name == "actuel": return .5 * r(168) + .5 * r(336)
    if name == "72h": return r(72)
    if name == "24h": return r(24)
    if name == "7j+84j": return .5 * r(168) + .5 * r(84 * 24)
    if name == "84j": return r(84 * 24)
    if name == "min(72,168)": return min(r(72), r(168))
    if name == "min(actuel,72h)": return min(.5 * r(168) + .5 * r(336), r(72))
    if name == "72h+84j": return .5 * r(72) + .5 * r(84 * 24)
    if name == "mediane": return sorted([r(24), r(72), r(168), r(336), r(84 * 24)])[2]
NAMES = ["actuel", "24h", "72h", "84j", "7j+84j", "72h+84j", "min(72,168)", "min(actuel,72h)", "mediane"]
TH = list(range(50, 501, 25))
res = {n: [0.0, 0] for n in NAMES}; drop = {n: [0.0, 0] for n in NAMES}; ndrop = 0
big = {n: [0.0, 0] for n in NAMES}
for s in starts():
    final = n_between(s, s + 7 * 86400)
    if final == 0: continue
    for h in (24, 48, 72, 96, 120, 144):
        now = s + h * H; cnt = n_between(s, now); rem = 168 - h
        is_drop = est("72h", now, s) < 0.4 * est("actuel", now, s)
        ndrop += is_drop
        for n in NAMES:
            m = est(n, now, s) * rem
            for x in TH:
                p = negbin_interval(x - cnt, 10 ** 9, m, 12)
                p = min(max(p, .005), .995)
                y = final >= x
                if x <= cnt and not y: continue
                ll = -math.log(p if y else 1 - p)
                res[n][0] += ll; res[n][1] += 1
                if is_drop: drop[n][0] += ll; drop[n][1] += 1
print("fenêtres décisions en baisse de régime:", ndrop)
for n in NAMES:
    print(f"{n:18s} tout {res[n][0]/res[n][1]:.4f} ({res[n][1]})   régime en baisse {drop[n][0]/max(drop[n][1],1):.4f} ({drop[n][1]})")
