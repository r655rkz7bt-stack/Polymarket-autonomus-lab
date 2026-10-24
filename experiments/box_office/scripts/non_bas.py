"""Acheter le NON des tranches peu probables (prix du OUI 0,05-0,30), prix du dernier achat réel du NON, frais 5 %."""
import sys
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
from favori import *
def run_non(h, lo, hi, rate=0.05, win=2 * 3600):
    bets = []
    for c in C:
        t = c["end"] - h * 3600
        for m in c["ms"]:
            p0 = last_before(m["series"], t, 8 * 3600)
            if p0 is None or not (lo <= p0 < hi): continue
            px = taker_buy(c["trades"], m["tokens"][0], m["tokens"][1], t, win, 0)
            if px is None: continue
            cost = px + rate * px * (1 - px)
            bets.append({"gain": ((1 - m["win"]) - cost) / cost, "evenement": c["e"]["id"], "mois": datetime.fromtimestamp(c["end"], timezone.utc).strftime("%Y-%m"), "cout": px})
    return bets
if __name__ == "__main__":
    for h in (96, 72, 48, 36, 24, 12):
        for lo, hi in ((0.05, 0.15), (0.15, 0.30), (0.05, 0.30)):
            b = run_non(h, lo, hi)
            if len(b) < 15: continue
            v = verdict(b)
            print(f"h={h:3d} OUI {lo}-{hi}: NON n={v['paris']:3d} ({v['evenements']} ev.) rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} z_prix {v['z_prix']:+.2f} -> {v['verdict']}")
