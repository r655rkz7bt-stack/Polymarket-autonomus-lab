"""Piste « k gagnants » (23/10/2026) : dans un événement où exactement k marchés finissent OUI, la somme des prix OUI vaut k.
1) la somme réelle s'écarte-t-elle de k, à J-1, J-3, J-7, J-14, J-30 ? 2) les prix sont-ils calibrés par tranche ? 3) renormaliser
p' = p·k/Σp bat-il le prix (log-score) ? 4) achats simulés au milieu (à vérifier ensuite aux vrais échanges).
Usage : python experiments/k_gagnants/scripts/analyse.py   (depuis la racine du dépôt)"""
import bisect, json, math, sys
from collections import defaultdict
rows = [json.loads(l) for l in open("experiments/k_gagnants/donnees/prix.jsonl")]
evs = {e["id"]: e for e in json.load(open("experiments/k_gagnants/donnees/evs.json"))} if len(sys.argv) < 2 else {}
by = defaultdict(list)
for r in rows:
    if r["h"]:
        by[r["event"]].append(r)
DAY = 86400
def price_at(h, t):
    ts = [x[0] for x in h]
    i = bisect.bisect_right(ts, t) - 1
    return h[i][1] if i >= 0 and t - h[i][0] <= 2 * DAY else None
def ll(p, y):
    p = min(max(p, 0.001), 0.999)
    return math.log(p if y else 1 - p)
OFFS = (1, 3, 7, 14, 30)
res = {}
for ev, ms in by.items():
    n_all = len(ms)
    if n_all < 4:
        continue
    k = int(sum(m["y"] for m in ms))
    R = max(m["h"][-1][0] for m in ms)
    for d in OFFS:
        pr = [price_at(m["h"], R - d * DAY) for m in ms]
        if any(p is None for p in pr):  # marché pas encore né à cette date : on saute l'événement à ce point
            continue
        res[(ev, d)] = (k, [(p, m["y"], m["q"]) for p, m in zip(pr, ms)], R)
print(len(by), "événements avec prix ;", len({e for e, _ in res}), "avec au moins un point complet")
print("\n1) somme des prix OUI / k  (k = nombre réel de OUI)")
for d in OFFS:
    xs = [(sum(p for p, _, _ in v[1]), v[0], len(v[1])) for (e, dd), v in res.items() if dd == d]
    if not xs: continue
    ratio = [s / k for s, k, n in xs]
    ratio.sort()
    print(f"J-{d:>2} : {len(xs)} événements, Σp/k moyen {sum(ratio)/len(ratio):.3f}, médian {ratio[len(ratio)//2]:.3f}, "
          f"min {ratio[0]:.2f}, max {ratio[-1]:.2f}, part > 1,05 : {sum(r > 1.05 for r in ratio)/len(ratio):.0%}, < 0,95 : {sum(r < 0.95 for r in ratio)/len(ratio):.0%}")
BINS = [0, .02, .05, .10, .20, .40, .60, .80, .95, 1.0001]
print("\n2) calibration par tranche de prix (OUI) : n, gagnés, attendus par les prix, écart relatif ; z par les prix")
for d in (3, 7, 14):
    print(f" -- J-{d}")
    for lo, hi in zip(BINS, BINS[1:]):
        sel = [(p, y) for (e, dd), v in res.items() if dd == d for p, y, _ in v[1] if lo <= p < hi]
        if not sel: continue
        w = sum(y for _, y in sel); ex = sum(p for p, _ in sel); var = sum(p * (1 - p) for p, _ in sel)
        print(f"   [{lo:.2f},{hi:.2f}) n {len(sel):>5} gagnés {w:>5.0f} attendus {ex:>7.1f}  ({(w-ex)/ex:+.1%})  z {(w-ex)/math.sqrt(var):+.2f}")
print("\n3) log-score : prix contre prix renormalisé p·k/Σp (k connu à l'avance seulement pour les formats fixes : borne haute de l'information)")
for d in OFFS:
    a = b = n = 0
    for (e, dd), v in res.items():
        if dd != d: continue
        s = sum(p for p, _, _ in v[1]); k = v[0]
        for p, y, _ in v[1]:
            a += ll(p, y); b += ll(p * k / s, y); n += 1
    if n: print(f"J-{d:>2} : prix {a/n:+.4f}  renormalisé {b/n:+.4f}  ({n} marchés)")
