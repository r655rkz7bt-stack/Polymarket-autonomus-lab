"""Suivre l'argent : la tranche (parmi celles à 0,10-0,85) dont les achats nets des `fen` dernières heures sont les plus gros gagne-t-elle plus que son prix ?"""
import sys
sys.path.insert(0, "experiments/box_office/scripts"); sys.path.insert(0, "src")
from favori import *
def net_flow(trades, tok, other, a, b):
    f = 0.0
    for t in trades:
        if a <= t[0] < b:
            if t[1] == tok: f += (1 if t[2] == "BUY" else -1) * t[3] * t[4]
            elif t[1] == other: f += (-1 if t[2] == "BUY" else 1) * (1 - t[3]) * t[4]
    return f
def run_flux(h, fen, lo=0.10, hi=0.85, rate=0.05, win=2 * 3600):
    bets = []
    for c in C:
        t = c["end"] - h * 3600
        best = None
        for m in c["ms"]:
            p0 = last_before(m["series"], t, 8 * 3600)
            if p0 is None or not lo <= p0 < hi: continue
            fl = net_flow(c["trades"], m["tokens"][0], m["tokens"][1], t - fen * 3600, t)
            if best is None or fl > best[0]: best = (fl, m)
        if best is None or best[0] < 20: continue  # au moins 20 $ d'achats nets
        m = best[1]
        px = taker_buy(c["trades"], m["tokens"][0], m["tokens"][1], t, win, 1)
        if px is None: continue
        cost = px + rate * px * (1 - px)
        bets.append({"gain": (m["win"] - cost) / cost, "evenement": c["e"]["id"], "mois": datetime.fromtimestamp(c["end"], timezone.utc).strftime("%Y-%m"), "cout": px})
    return bets
if __name__ == "__main__":
    for h in (72, 48, 24):
        for fen in (6, 12, 24):
            b = run_flux(h, fen)
            if len(b) < 15: continue
            v = verdict(b)
            print(f"h={h} fenêtre {fen} h: n={v['paris']} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} z_prix {v['z_prix']:+.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f} -> {v['verdict']}")
