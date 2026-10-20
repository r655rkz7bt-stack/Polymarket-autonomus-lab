"""Fatigue NBA contre le marché : le prix tient-il compte du dos-à-dos / du repos ? (lancer depuis la racine du dépôt)"""
import json, math, statistics as st, sys
from collections import defaultdict
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
rows = json.load(open("experiments/nba/donnees/rows.json"))
RATE = 0.05
def price(r, h=1.0):
    pts = [x for x in r["hist"] if x["t"] <= r["st"] - h * 3600]
    return pts[-1]["p"] if pts else None
data = []
for r in rows:
    p = price(r)
    if p is None or not 0.05 < p < 0.95: continue
    data.append(dict(r, p=p, aw=1.0 if r["away_win"] else 0.0, mois=r["date"][:7]))
print("matchs", len(data))
# calibration générale
print("prix moyen visiteur %.3f, gagnés %.3f" % (st.mean(d["p"] for d in data), st.mean(d["aw"] for d in data)))
def gain(c, win):  # rendement par euro misé en achetant au prix c + 0,01 (écart) avec frais
    c = c + 0.01
    return (win - c - RATE * c * (1 - c)) / c
def cases():
    for d in data:
        ra, na = d["rest_away"]; rh, nh = d["rest_home"]
        yield d, ra, rh, na, nh
groups = {
    "visiteur dos-à-dos, domicile reposé (≥2 j)": lambda ra, rh, na, nh: ra == 1 and rh >= 2,
    "domicile dos-à-dos, visiteur reposé (≥2 j)": lambda ra, rh, na, nh: rh == 1 and ra >= 2,
    "les deux dos-à-dos": lambda ra, rh, na, nh: ra == 1 and rh == 1,
    "visiteur 3 matchs en 4 soirs (n4≥2), domicile pas": lambda ra, rh, na, nh: na >= 2 and nh < 2,
    "domicile 3 matchs en 4 soirs (n4≥2), visiteur pas": lambda ra, rh, na, nh: nh >= 2 and na < 2,
    "visiteur ≥ 3 jours de plus de repos que le domicile": lambda ra, rh, na, nh: ra - rh >= 2,
    "domicile ≥ 3 jours de plus de repos": lambda ra, rh, na, nh: rh - ra >= 2,
}
out = {}
for k, f in groups.items():
    tired, rested = [], []
    for d, ra, rh, na, nh in cases():
        if not f(ra, rh, na, nh): continue
        # « fatigué » = l'équipe qui a le moins de repos
        away_tired = ra < rh or (ra == rh and na > nh)
        p_t = d["p"] if away_tired else 1 - d["p"]
        w_t = d["aw"] if away_tired else 1 - d["aw"]
        tired.append((p_t, w_t, d))
    if not tired: continue
    n = len(tired); exp = sum(p for p, _, _ in tired); won = sum(w for _, w, _ in tired)
    # statistique : gagnés - attendus (variance Bernoulli)
    z = (won - exp) / math.sqrt(sum(p * (1 - p) for p, _, _ in tired))
    bets = [{"gain": gain(1 - p, 1 - w), "evenement": d["slug"], "mois": d["mois"], "cout": 1 - p + 0.01} for p, w, d in tired]
    v = verdict(bets) if n >= 30 else None
    print(f"{k:55} n {n:4} prix de l'équipe fatiguée {exp/n:.3f} gagnés {won/n:.3f} z {z:+.2f} | acheter le reposé : {sum(b['gain'] for b in bets)/n:+.3f}"
          + (f" t_evt {v['confiance_evenements']:+.2f} mois {v['mois_gagnants']} → {v['verdict']}" if v else ""))
# régression : résultat - prix sur (repos domicile - repos visiteur), plafonné à 4 jours
xs = [(min(d["rest_home"][0], 4) - min(d["rest_away"][0], 4), d["aw"] - d["p"]) for d in data]
mx = st.mean(x for x, _ in xs); my = st.mean(y for _, y in xs)
b = sum((x - mx) * (y - my) for x, y in xs) / sum((x - mx) ** 2 for x, _ in xs)
res = [y - my - b * (x - mx) for x, y in xs]
se = math.sqrt(st.pvariance(res) / sum((x - mx) ** 2 for x, _ in xs))
print(f"pente (résultat visiteur − prix) par jour de repos en plus au DOMICILE : {b:+.4f} (t {b/se:+.2f}), n {len(xs)}")
# par moitié de saison
half = sorted(d["date"] for d in data)[len(data) // 2]
for nom, f in (("1re moitié", lambda d: d["date"] < half), ("2e moitié", lambda d: d["date"] >= half)):
    sub = [(min(d["rest_home"][0], 4) - min(d["rest_away"][0], 4), d["aw"] - d["p"]) for d in data if f(d)]
    mx2 = st.mean(x for x, _ in sub); my2 = st.mean(y for _, y in sub)
    b2 = sum((x - mx2) * (y - my2) for x, y in sub) / sum((x - mx2) ** 2 for x, _ in sub)
    print(f"  {nom}: pente {b2:+.4f} (n {len(sub)})")
# favoris : le favori gagne-t-il plus que son prix ? (rappel, piste « autres sports »)
for lo, hi in ((0.5, 0.65), (0.65, 0.8), (0.8, 0.95)):
    sub = [(max(d["p"], 1 - d["p"]), d["aw"] if d["p"] >= .5 else 1 - d["aw"]) for d in data if lo <= max(d["p"], 1 - d["p"]) < hi]
    if sub: print(f"favori {lo:.2f}-{hi:.2f}: n {len(sub)} prix {st.mean(p for p,_ in sub):.3f} gagnés {st.mean(w for _,w in sub):.3f}")
