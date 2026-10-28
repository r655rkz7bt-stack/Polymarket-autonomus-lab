"""Over/Under de sport : rendement par tranche de prix payé (tous côtés, h = 0,5 / 1 / 3 / 6 h avant le coup d'envoi), mêmes achats que analyse.py."""
import runpy, sys, collections, math, statistics as st
sys.argv = ["analyse.py", "0.5,1,3,6"]
import io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("experiments/props_over_under/scripts/analyse.py")
rows = g["rows"]
for lo, hi in ((0.02, 0.10), (0.10, 0.25), (0.25, 0.45), (0.45, 0.55), (0.55, 0.75), (0.75, 0.90), (0.90, 0.99)):
    R = [r for r in rows if lo <= r["px"] < hi]
    if len(R) < 30: continue
    ev = collections.defaultdict(float)
    for r in R: ev[r["ev"]] += r["g"]
    e = list(ev.values()); sd = st.pstdev(e) or 1
    print(f"prix {lo:.2f}-{hi:.2f}: {len(R):5d} paris / {len(ev):4d} événements, gagnés {sum(r['win'] for r in R):5d} pour {sum(r['px'] for r in R):7.1f}, rendement {sum(r['g'] for r in R)/sum(r['px'] for r in R):+7.2%}, t/événement {st.mean(e)/(sd/math.sqrt(len(e))):+.2f}")
