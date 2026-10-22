import sys; sys.path.insert(0, "experiments/courbe_de_risque"); sys.path.insert(0, "src")
import analyse as A
from polymarket_agent import idea_test as it
n = 0
for pmax in (0.97, 0.85):
    for H in (7, 10, 14, 21, 30, 45):
        r = A.run(H, "non", pmax=pmax); n += 1
        bets = [dict(gain=(x["win"] - x["p"] - it.fee(x["p"], x["rate"])) / (x["p"] + it.fee(x["p"], x["rate"])), evenement=x["eid"], mois=x["mois"], cout=x["p"]) for x in r]
        v = it.verdict(bets)
        print(f"NON, prix <= {pmax}, à {H:2d} j : paris={v['paris']:4d} évts={v['evenements']:4d} rendement={100*v.get('rendement_moyen',0):+5.1f}% t_évt={v.get('confiance_evenements',0):+.2f} z_prix={v.get('z_prix',0):+.2f} mois+ {v.get('mois_gagnants')} -> {v['verdict']}", flush=True)
print("réglages essayés ici:", n)
