"""Piste n° 61 : achat du OUI des « beat » AUX VRAIS ÉCHANGES. Décision à T0 = fermeture − D j sur le prix milieu connu (CLOB) ;
achat = premiers échanges de preneurs qui achètent le OUI (ou vendent le NON) dans les `FEN` heures après T0, à un prix
≤ milieu + 0,03, jusqu'à `PARTS` parts (prix moyen pondéré ; marché écarté s'il n'y a pas `PARTS` parts). Frais du marché."""
import json, sys
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
E = json.load(open("experiments/battre_historique/donnees/echanges.json"))
def run(D, lo, hi, parts, fen=12, marge=0.03, quiet=False):
    bets = []
    for c in json.load(open(f"experiments/battre_historique/donnees/cas_T{D}.json")):
        if not lo <= c["p"] < hi: continue
        t0 = c["tc"] - D * 86400
        pts = sorted((t, p if o == "Yes" else 1 - p, s) for t, sd, o, p, s in E.get(c["cond"], [])
                     if t0 <= t <= t0 + fen * 3600 and ((o == "Yes" and sd == "BUY") or (o == "No" and sd == "SELL")))
        got, cost = 0.0, 0.0
        for t, p, s in pts:
            if p > c["p"] + marge: continue
            q = min(s, parts - got); got += q; cost += q * p
            if got >= parts - 1e-9: break
        if got < parts - 1e-9: continue
        px = cost / got
        rate = float((c.get("fee") or {}).get("rate") or 0)
        f = rate * px * (1 - px)
        bets.append(dict(gain=(c["y"] - px - f) / (px + f), evenement=c["eid"], mois=c["mois"], cout=px, y=c["y"], p=c["p"]))
    v = verdict(bets)
    n = len(bets); y = sum(b["y"] for b in bets); e = sum(b["cout"] for b in bets)
    if not quiet:
        print(f"T-{D} OUI {lo:.2f}-{hi:.2f} ≥{parts} parts en {fen} h : {n} paris, {y} gagnés pour {e:.1f} payés, rendement {v.get('rendement_moyen')}, "
              f"mois gagnants {v.get('mois_gagnants')}, verdict {v.get('verdict')}, t évén. {v.get('t_evenement', v.get('confiance_evenement'))}")
    return v, bets
if __name__ == "__main__":
    for D in (1, 3, 7):
        for lo, hi in ((0.30, 0.70), (0.50, 0.85), (0.30, 0.90)):
            for parts in (10, 50, 200):
                run(D, lo, hi, parts)
