import json, math, statistics as st
from datetime import datetime
D = "donnees/nhl"
rows = json.load(open(f"{D}/rows.json"))
def price(r, before_h=1.0):
    st_ = datetime.fromisoformat(r["start"].replace("Z", "+00:00")).timestamp()
    pts = [x for x in r["hist"] if x["t"] <= st_ - before_h * 3600]
    return pts[-1]["p"] if pts else None
cases = {"fatigué dehors, adversaire reposé": [], "fatigué à domicile, adversaire reposé": [], "les deux": [], "aucun": []}
allp = []
for r in rows:
    p = price(r)
    if p is None or not 0.05 < p < 0.95: continue
    aw = 1.0 if r["away_win"] else 0.0
    allp.append((p, aw))
    if r["b2b_away"] and not r["b2b_home"]: cases["fatigué dehors, adversaire reposé"].append((p, aw))  # p = prix de l'équipe fatiguée
    elif r["b2b_home"] and not r["b2b_away"]: cases["fatigué à domicile, adversaire reposé"].append((1 - p, 1 - aw))
    elif r["b2b_home"] and r["b2b_away"]: cases["les deux"].append((p, aw))
    else: cases["aucun"].append((p, aw))
print("matchs avec prix", len(allp))
for k, v in cases.items():
    if not v: continue
    exp = sum(p for p, _ in v); won = sum(w for _, w in v)
    # rendement de l'achat de l'ADVERSAIRE reposé (et de l'équipe fatiguée) au prix + 0,01, frais sport ~0,03·p(1-p)
    def ret(side):
        g = []
        for p, w in v:
            c = (1 - p if side else p) + 0.01; win = (1 - w) if side else w
            g.append((win - c - 0.05 * c * (1 - c)) / c)
        m = st.mean(g); return m, m / st.stdev(g) * math.sqrt(len(g))
    print(f"{k:40} n {len(v):4}  prix moyen {exp / len(v):.3f}  gagnés {won / len(v):.3f}  écart {(won - exp) / len(v):+.3f}"
          f"  | acheter l'adversaire : {ret(1)[0]:+.3f} (t {ret(1)[1]:+.2f})")
