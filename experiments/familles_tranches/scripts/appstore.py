"""App Store (classement du jour) : la favorite du marché 24 h avant la fin gagne-t-elle autant que son prix ? NON de la favorite aux prix payés."""
import sys
sys.path.insert(0, "experiments/familles_tranches/scripts"); sys.path.insert(0, "src")
from favori import *
def serie(t): return re.sub(r"\s+on .*", "", t)
def run_fav(C, h, lo, hi, side, rate=0.05, win=3 * 3600):
    bets = []
    for c in C:
        t = c["end"] - h * 3600
        pr = [(last_before(m["series"], t, 12 * 3600), m) for m in c["ms"]]
        pr = [(p, m) for p, m in pr if p is not None]
        if len(pr) < 2: continue
        p0, m = max(pr, key=lambda x: x[0])
        if p0 < max(0.0, 1 - sum(p for p, _ in pr)) + 0.02 or not lo <= p0 < hi: continue
        px = taker_buy(c["trades"], m["tokens"][0], m["tokens"][1], t, win, side)
        if px is None: continue
        cost = px + rate * px * (1 - px)
        won = m["win"] if side else 1 - m["win"]
        bets.append({"gain": (won - cost) / cost, "evenement": c["e"]["id"], "mois": datetime.fromtimestamp(c["end"], timezone.utc).strftime("%Y-%m"), "cout": px, "p0": p0, "win": m["win"]})
    return bets
if __name__ == "__main__":
    C = cases("appstore")
    groups = {"#1 Free": [c for c in C if "#1 Free" in c["e"]["title"]], "#2 Free": [c for c in C if "#2 Free" in c["e"]["title"]], "#1 Paid": [c for c in C if "#1 Paid" in c["e"]["title"]]}
    for nom, cc in groups.items():
        print(nom, len(cc), "événements")
        for h in (72, 48, 24, 12, 6):
            for lo, hi in ((0.5, 1.0), (0.5, 0.8), (0.8, 1.0)):
                b = run_fav(cc, h, lo, hi, 1)
                if len(b) < 15: continue
                n = run_fav(cc, h, lo, hi, 0)
                v, vn = verdict(b), verdict(n)
                print(f"  h={h:2d} {lo}-{hi}: favorite n={v['paris']} gagnées {sum(x['win'] for x in b)}/{sum(x['p0'] for x in b):.1f} OUI {v['rendement_moyen']:+.3f} (t {v['confiance_evenements']:+.2f}) | NON {vn['rendement_moyen']:+.3f} (t {vn['confiance_evenements']:+.2f}, z_prix {vn['z_prix']:+.2f}, n={vn['paris']})")
