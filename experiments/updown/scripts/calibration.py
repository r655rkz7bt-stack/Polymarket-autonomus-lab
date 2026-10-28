"""Up or Down : les prix payés (premier achat d'un preneur dans la minute) battent-ils leurs prix ? Par minute et par tranche de prix, sans modèle.
Usage : python calibration.py <5m|15m>"""
import pickle, sys, os, math, collections, statistics as st
ICI = os.path.dirname(os.path.abspath(__file__)); pas = sys.argv[1]; W = 300 if pas == "5m" else 900
rows = pickle.load(open(os.path.join(ICI, "..", "donnees", f"{pas}_lignes.pkl"), "rb"))
def fee(p): return 0.07 * p * (1 - p)
def blocs(ks, lo, hi, smin=20):
    R = []
    for r in rows:
        if r["k"] not in ks: continue
        for side, (px, sz) in r["ach"].items():
            if sz >= smin and lo <= px < hi:
                win = r["up"] if side == "Up" else not r["up"]
                R.append((r["ev"], px, win, (1.0 if win else 0.0) - px - fee(px)))
    return R
def aff(nom, R):
    if len(R) < 40: return
    ev = collections.defaultdict(float)
    for e, px, w, g in R: ev[e] += g
    evs = list(ev.values()); sd = st.pstdev(evs) or 1
    tot = sum(g for *_, g in R); mise = sum(px for _, px, *_ in R)
    print(f"{nom:34s} {len(R):6d} paris / {len(ev):5d} marchés  gagnés {sum(w for _,_,w,_ in R):6d} pour {sum(px for _,px,_,_ in R):8.1f}  rendement {tot/mise:+7.2%}  t/marché {st.mean(evs)/(sd/math.sqrt(len(evs))):+.2f}")
n = W // 60
for nom, ks in (("toutes minutes", list(range(1, n))), (f"minute {n-1}", [n-1]), (f"minutes {n-3}-{n-2}", [n-3, n-2]), ("minutes 1-3", [1, 2, 3])):
    print("==", nom)
    for lo, hi in ((0.02, 0.10), (0.10, 0.25), (0.25, 0.45), (0.45, 0.55), (0.55, 0.75), (0.75, 0.90), (0.90, 0.98)):
        aff(f"  prix {lo:.2f}-{hi:.2f}", blocs(ks, lo, hi))
