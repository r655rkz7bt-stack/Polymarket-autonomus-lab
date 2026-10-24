"""Règle jouée par le fantôme : fenêtre ancrée sur le week-end (samedi 18 h UTC → dimanche 16 h UTC), marché encore ouvert 1 h au moins ; premier moment où une favorite 0,5-0,95 a un achat réel dans les 2 h."""
import sys
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
import favori
from favori import *
from datetime import timedelta
def sat18(end):
    d = datetime.fromtimestamp(end, timezone.utc)
    sun = (d - timedelta(days=(d.weekday() + 1) % 7)).replace(hour=0, minute=0, second=0, microsecond=0)
    return int((sun - timedelta(hours=6)).timestamp())
def regle(C, start_h=0, stop_h=22, lo=0.5, hi=0.95, rate=0.05, premier=True):
    bets = []
    for c in C:
        a = sat18(c["end"])
        for k in range(start_h, stop_h + 1):
            t = a + k * 3600
            if t > c["end"] - 3600: break
            pr = [(last_before(m["series"], t, 8 * 3600), m) for m in c["ms"]]
            pr = [(p, m) for p, m in pr if p is not None]
            if len(pr) < 2: continue
            p0, m = max(pr, key=lambda x: x[0])
            if not lo <= p0 < hi or p0 < max(0.0, 1 - sum(p for p, _ in pr)) + 0.02: continue
            px = taker_buy(c["trades"], m["tokens"][0], m["tokens"][1], t, 2 * 3600, 1)
            if px is None or not lo <= px < hi + 0.03: continue
            cost = px + rate * px * (1 - px)
            bets.append({"gain": (m["win"] - cost) / cost, "evenement": c["e"]["id"], "mois": datetime.fromtimestamp(c["end"], timezone.utc).strftime("%Y-%m"), "cout": px})
            break
    return bets
if __name__ == "__main__":
    for nom, kw in (("règle du fantôme (sam. 18 h → dim. 16 h)", {}), ("sam. 18 h → dim. 8 h", {"stop_h": 14}), ("sam. 24 h → dim. 16 h", {"start_h": 6}), ("dim. 0 h → dim. 16 h", {"start_h": 6, "stop_h": 22}), ("0,5-0,8", {"hi": 0.8}), ("0,8-0,95", {"lo": 0.8})):
        b = regle(favori.C, **kw)
        if len(b) < 15: print(nom, len(b)); continue
        v = verdict(b)
        print(f"{nom}: n={v['paris']} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f} z_prix {v['z_prix']:+.2f} mois {v['mois_gagnants']}")
