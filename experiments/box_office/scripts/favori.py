"""Acheter le OUI de la tranche favorite du box-office, à h heures de la fin, au prix du dernier achat réel (preneur)."""
import sys, json
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
from analyse import *
from datetime import datetime, timezone
RATE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
C = cases()
def run(h, lo, hi, win=2 * 3600, rate=RATE, label=True):
    bets = []
    for c in C:
        t = c["end"] - h * 3600
        pr = [(last_before(m["series"], t, 8 * 3600), m) for m in c["ms"]]
        if any(p is None for p, _ in pr): continue
        p0, m = max(pr, key=lambda x: x[0])
        if not (lo <= p0 < hi): continue
        px = taker_buy(c["trades"], m["tokens"][0], m["tokens"][1], t, win, 1)
        if px is None or not (lo <= px < hi + 0.05): continue
        cost = px + rate * px * (1 - px)
        bets.append({"gain": (m["win"] - cost) / cost, "evenement": c["e"]["id"], "mois": datetime.fromtimestamp(c["end"], timezone.utc).strftime("%Y-%m"), "cout": px})
    return bets
if __name__ == "__main__":
    for h in (96, 72, 48, 36, 24, 12):
        for lo, hi in ((0.5, 1.0), (0.5, 0.8), (0.8, 1.0), (0.6, 0.9)):
            b = run(h, lo, hi)
            if len(b) < 10: continue
            v = verdict(b)
            print(f"h={h:3d} prix {lo}-{hi}: n={v['paris']:3d} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} z_prix {v['z_prix']:+.2f} mois {v['mois_gagnants']} -> {v['verdict']}")
