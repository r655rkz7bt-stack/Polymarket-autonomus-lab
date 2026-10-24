"""Calibration des candidats de primaires : prix (historique horaire) à J-d contre résultat. À lancer depuis experiments/primaires/."""
import json, bisect, collections, math
rows = [json.loads(l) for l in open("donnees/prix.jsonl")]
BINS = [0, .02, .05, .10, .20, .40, .60, .80, .90, .97, 1.0001]
def price_at(r, d):
    T = r["endts"] - d * 86400
    ts = [p[0] for p in r["h"]]
    i = bisect.bisect_right(ts, T) - 1
    if i < 0 or T - ts[i] > 12 * 3600: return None
    return r["h"][i][1]
for d in (1, 3, 7, 14, 30):
    print(f"== J-{d}")
    B = collections.defaultdict(lambda: [0, 0.0, 0, set()])
    for r in rows:
        p = price_at(r, d)
        if p is None: continue
        k = bisect.bisect_right(BINS, p) - 1
        b = B[k]; b[0] += 1; b[1] += p; b[2] += r["won"]; b[3].add(r["event"])
    for k in sorted(B):
        n, sp, w, evs = B[k]
        sd = math.sqrt(max(1e-9, sum(0 for _ in [])) + 1e-9)
        var = None
        print(f"  {BINS[k]:.2f}-{BINS[k+1]:.2f}: n={n:4d} événements={len(evs):3d} prix moyen {sp/n:.3f} gagné {w/n:.3f}  ({w} / {sp:.1f} attendus)")
