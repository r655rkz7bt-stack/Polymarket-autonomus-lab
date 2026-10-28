"""Favoris d'e-sport 0,65-0,80 à H-3/H-6, découpés (exploratoire, 28/10/2026) : format (BO1/BO3/BO5), volume du marché, équipe/jeu. À ne pas lire comme des réglages gagnants."""
import sys, os, re, collections
os.environ["COTE"] = "favoris"
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
import outsiders_avant_match as o
groups = tuple((sys.argv[1] if len(sys.argv) > 1 else "cs2,lol,dota2,val").split(","))
MS = a.load(groups); byid = {M["e"]["id"]: M for M in MS}
for delta in (3, 6):
    r = [x for x in o.run(MS, delta) if 0.65 <= x["cout"] < 0.80]
    for x in r:
        M = byid[x["evenement"]]; t = M["e"].get("title") or ""
        g = re.search(r"\(BO(\d)\)", t); x["bo"] = g.group(1) if g else "?"
        x["vol"] = float(M["m"].get("volumeNum") or 0)
    print(f"=== H-{delta} ({len(r)} paris)")
    for bo in ("1", "3", "5", "?"):
        print(f"  BO{bo}", o.fmt([x for x in r if x["bo"] == bo]))
    vs = sorted(x["vol"] for x in r); q1, q2 = vs[len(vs)//3], vs[2*len(vs)//3]
    print(f"  volume < {q1:.0f} $", o.fmt([x for x in r if x["vol"] < q1])); print(f"  volume {q1:.0f}-{q2:.0f} $", o.fmt([x for x in r if q1 <= x["vol"] < q2])); print(f"  volume >= {q2:.0f} $", o.fmt([x for x in r if x["vol"] >= q2]))
