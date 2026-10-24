"""NON des candidats de primaires cotés LO-HI à J-d, payé au premier échange preneur dans les 6 h qui suivent la décision (vrais prix). À lancer depuis experiments/primaires/."""
import json, bisect, sys, os, datetime, collections
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
rows = {json.loads(l)["market"]: json.loads(l) for l in open("donnees/prix.jsonl")}
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["market"]] = o
WIN = float(os.environ.get("WIN", 6)) * 3600
def run(d, lo, hi, verbose=False):
    bets = []; nosig = 0; incompl = 0
    for m, r in rows.items():
        ts = [p[0] for p in r["h"]]; T = r["endts"] - d * 86400; i = bisect.bisect_right(ts, T) - 1
        if i < 0 or T - ts[i] > 12 * 3600 or not lo <= r["h"][i][1] <= hi: continue
        o = tr.get(m)
        if o is None: continue
        if not o["complete"]: incompl += 1; continue
        yes = r["tok"]
        pts = []
        for t in o["trades"]:
            if not T <= t[0] <= T + WIN: continue
            if t[1] == yes and t[2] == "SELL": pts.append((t[0], 1 - t[3]))      # le preneur vend OUI = achète NON
            elif t[1] != yes and t[2] == "BUY": pts.append((t[0], t[3]))         # le preneur achète NON
        if not pts: nosig += 1; continue
        pts.sort(); c = pts[0][1]
        if c >= 0.995: continue
        g = ((1 - r["won"]) - c - fee(c, r["rate"])) / c
        bets.append({"evenement": r["event"], "cout": c, "gain": g, "won": 1 - r["won"], "mois": datetime.datetime.fromtimestamp(r["endts"]).strftime("%Y-%m")})
    return bets, nosig, incompl
for LO, HI in ((0.10, 0.30), (0.05, 0.15), (0.15, 0.40)):
    print(f"== NON, candidats cotés {LO}-{HI}, fenêtre {WIN/3600:g} h")
    for d in (7, 14, 21, 30):
        b, nosig, inc = run(d, LO, HI)
        if len(b) < 20: print(f" J-{d}: {len(b)} paris (sans échange {nosig}, incomplets {inc})"); continue
        v = verdict(b, min_bets=30)
        print(f" J-{d}: {len(b)} paris ({len({x['evenement'] for x in b})} événements ; sans échange dans la fenêtre {nosig}, marchés incomplets {inc}), NON gagné {sum(x['won'] for x in b)} / {sum(x['cout'] for x in b):.1f} attendus, rendement {sum(x['gain'] for x in b)/len(b)*100:+.1f} %, t événement {v['confiance_evenements']}, z prix {v['z_prix']}, mois gagnants {v['mois_gagnants']}, verdict {v['verdict']}")
