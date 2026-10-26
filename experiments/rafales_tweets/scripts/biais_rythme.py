"""27/10/2026 : le rythme de `compteur_tweets` (moyenne des 168 h et 336 h) est-il gonflé par les journées de rafale ?
Posts Truth Social de Trump (archive trumpstruth.org, experiments/truth_social/releves/posts.csv). Fenêtres de 7 jours du mardi 16 h UTC.
Décision à S - 28 h (le cas du 26/10 : OUI « 200+ » estimé 0,78 pour un prix de 0,42) : total prédit par (a) la moyenne de production,
(b) des rythmes robustes (médiane des journées, journées écrêtées), contre le total réalisé."""
import sys, bisect, math, statistics as st
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "experiments/truth_social/scripts")
import reglement as rg
posts = rg.lire_posts(); ts = [p.timestamp() for p in posts]
def n(a, b): return bisect.bisect_left(ts, b.timestamp()) - bisect.bisect_left(ts, a.timestamp())
first = posts[0] + timedelta(days=30)
S = datetime(2026, 10, 27, 16, tzinfo=timezone.utc)
while S - timedelta(days=7) > first: S -= timedelta(days=7)
rows = []
while S + timedelta(days=7) <= posts[-1]:
    T = S - timedelta(hours=int(sys.argv[1]) if len(sys.argv) > 1 else 28)
    h = T.replace(minute=0, second=0, microsecond=0)
    days = [n(h - timedelta(days=k + 1), h - timedelta(days=k)) for k in range(14)]  # 24 h glissantes, 0 = la plus récente
    r168 = sum(days[:7]) / 168; r336 = sum(days) / 336
    prod = 7 * 24 * (0.5 * r168 + 0.5 * r336)
    med = 7 * st.median(days)                       # médiane des 14 journées glissantes
    cap = 2 * st.median(days)                       # journées écrêtées à 2 × la médiane
    wins = 7 * sum(min(d, cap) for d in days) / 14
    trim = 7 * st.mean(sorted(days)[2:-2])          # moyenne tronquée (2 plus petites et 2 plus grandes retirées)
    real = n(S, S + timedelta(days=7))
    rows.append((S, prod, med, wins, trim, real, max(days) / max(st.median(days), 1)))
    S += timedelta(days=7)
print(len(rows), "fenêtres")
for name, i in [("production (moyenne)", 1), ("médiane ×7", 2), ("écrêtée 2×méd", 3), ("tronquée", 4)]:
    le = [math.log(r[i] / r[5]) for r in rows]
    print(f"{name:22s} biais log {st.mean(le):+.3f}  écart-type {st.pstdev(le):.3f}  RMSE {math.sqrt(st.mean(x*x for x in le)):.3f}  sur-prédit {sum(x > 0 for x in le)}/{len(le)}")
burst = [r for r in rows if r[6] > 3]
print("fenêtres après une journée > 3 × médiane :", len(burst))
for name, i in [("production", 1), ("médiane", 2), ("écrêtée", 3), ("tronquée", 4)]:
    le = [math.log(r[i] / r[5]) for r in burst]
    print(f"  {name:12s} biais log {st.mean(le):+.3f}  sur-prédit {sum(x > 0 for x in le)}/{len(le)}")
