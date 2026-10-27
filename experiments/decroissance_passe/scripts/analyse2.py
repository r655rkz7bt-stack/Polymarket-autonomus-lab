"""Suite de analyse.py : étalonnage de l'estimation, réglages voisins, côté OUI, robustesse (moitiés, horizons, sans les 5 meilleurs événements)."""
import sys, json, collections
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/decroissance_passe/scripts")
import analyse as a
from polymarket_agent import idea_test as it
EV = a.charge(); R = a.paris(EV)
print("estimation moyenne du NON %.3f, gagnés réels %.3f, prix moyen payé %.3f" % (sum(1 - r["fair"] for r in R) / len(R), sum(r["win"] for r in R) / len(R), sum(r["pay"] for r in R) / len(R)))
for lab, kw in [("NON, règle de la stratégie", {}), ("NON sans règle de gap (OUI 3-35 %)", dict(gap_min=-1)), ("NON gap >= 0,05", dict(gap_min=0.05)), ("NON OUI 0,03-0,15", dict(ymax=0.15)),
                ("NON OUI 0,15-0,35", dict(ymin=0.15)), ("NON p6 sur 6 h", dict(fen_p6=6 * 3600)), ("NON tous horizons (paris liés)", dict(un_par_marche=False)),
                ("NON OUI 0,35-0,65", dict(gap_min=-1, ymin=0.35, ymax=0.65)),
                ("OUI 3-35 %", dict(gap_min=-1, cote="oui")), ("OUI 3-15 %", dict(gap_min=-1, cote="oui", ymax=0.15)), ("OUI 15-35 %", dict(gap_min=-1, cote="oui", ymin=0.15)),
                ("OUI 20-35 %", dict(gap_min=-1, cote="oui", ymin=0.20)), ("OUI 15-45 %", dict(gap_min=-1, cote="oui", ymin=0.15, ymax=0.45)), ("OUI 10-30 %", dict(gap_min=-1, cote="oui", ymin=0.10, ymax=0.30))]:
    r = a.paris(EV, **kw); print(lab.ljust(36), a.resume(r), flush=True)
print("sauts >= 1,5x :", a.resume([r for r in R if r["ratio"] >= 1.5])); print("sauts < 1,5x  :", a.resume([r for r in R if r["ratio"] < 1.5]))
r = a.paris(EV, gap_min=-1, cote="oui", ymin=0.15)
v = it.verdict([dict(gain=x["gain"], evenement=x["eid"], mois=x["mois"], cout=x["pay"] + x["fee"]) for x in r])
print("OUI 15-35 % : moitié 1", v["moitie_1"]["rendement"], "(", v["moitie_1"]["paris"], "paris) moitié 2", v["moitie_2"]["rendement"], "(", v["moitie_2"]["paris"], ")")
for H in (30, 14, 7, 3, 1): print("   OUI 15-35 %, premier déclenchement à", H, "j :", a.resume([x for x in r if x["H"] == H]))
g = collections.defaultdict(float)
for x in r: g[x["eid"]] += x["win"] - x["pay"] - x["fee"]
top = sorted(g, key=g.get, reverse=True)[:5]; print("   OUI 15-35 % sans ses 5 meilleurs événements :", a.resume([x for x in r if x["eid"] not in top]))
