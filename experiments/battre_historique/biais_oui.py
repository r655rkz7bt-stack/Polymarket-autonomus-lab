"""Piste n° 61, suite : le OUI des « beat » est-il sous-coté en général ? Achats simulés du OUI à T-d j, prix milieu + écart,
frais du marché (feeSchedule), par tranche de prix, verdict par mois (idea_test.verdict)."""
import json, math, sys
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
for D in (1, 3, 7):
    cas = json.load(open(f"experiments/battre_historique/donnees/cas_T{D}.json"))
    for ecart in (0.01, 0.02):
        for lo, hi in ((0.30, 0.70), (0.50, 0.85), (0.70, 0.90), (0.30, 0.90)):
            bets = []
            for c in cas:
                if not lo <= c["p"] < hi: continue
                rate = float((c.get("fee") or {}).get("rate") or 0)
                cout = c["p"] + ecart
                f = rate * cout * (1 - cout)
                bets.append(dict(gain=(c["y"] - cout - f) / (cout + f), evenement=c["eid"], mois=c["mois"], cout=cout))
            v = verdict(bets)
            print(f"T-{D} écart {ecart} OUI {lo:.2f}-{hi:.2f} : {v['paris']} paris, {v.get('rendement_moyen', v.get('rendement', ''))} ", {k: v[k] for k in v if k in ('verdict', 't_evenement', 'mois_gagnants', 'mois', 'rendement_moyen')})
