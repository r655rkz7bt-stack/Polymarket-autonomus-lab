"""Favoris d'e-sport 0,65-0,80, H-3/H-6 : le gain vient-il des petits marchés ? Volume = notionnel échangé AVANT T (aucun regard vers le futur ; `volumeNum` de Gamma
compte aussi l'après). Terciles du volume avant T, puis seuils fixes. 28/10/2026."""
import sys, os, bisect, collections
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
groups = tuple((sys.argv[1] if len(sys.argv) > 1 else "cs2,lol,dota2,val").split(","))
LO, HI = 0.65, 0.80
MS = a.load(groups); byid = {M["e"]["id"]: M for M in MS}
def vol_before(M, T):
    return sum(t[3] * t[4] for t in M["trades"] if t[0] < T)
tout = {}
for delta in (3, 6):
    r = [x for x in o.run(MS, delta) if LO <= x["cout"] < HI]
    for x in r:
        M = byid[x["evenement"]]; x["vavant"] = vol_before(M, M["start"] - delta * 3600)
    tout[delta] = r
    vs = sorted(x["vavant"] for x in r); q1, q2 = vs[len(vs) // 3], vs[2 * len(vs) // 3]
    print(f"=== H-{delta} ({len(r)} paris) ; terciles du volume avant T : {q1:.0f} $ / {q2:.0f} $")
    print("  tercile bas ", o.fmt([x for x in r if x["vavant"] < q1]))
    print("  tercile mil.", o.fmt([x for x in r if q1 <= x["vavant"] < q2]))
    print("  tercile haut", o.fmt([x for x in r if x["vavant"] >= q2]))
    for seuil in (1000, 3000, 10000, 30000):
        print(f"  volume avant T < {seuil:6d} $", o.fmt([x for x in r if x["vavant"] < seuil]))
    for sp in groups:
        sub = [x for x in r if x["sport"] == sp and x["vavant"] < q1 * 1.0]
        print(f"  tercile bas, {sp}", o.fmt(sub))
