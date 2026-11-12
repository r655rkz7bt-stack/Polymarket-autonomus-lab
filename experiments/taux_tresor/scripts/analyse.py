"""Barrière sur clôtures quotidiennes (Trésor, « Daily Treasury Par Yield Curve Rates ») contre le prix Polymarket.
Décision chaque jour ouvré à 02 h UTC (la clôture de la veille est publiée) ; modèle : marche aléatoire sans dérive, σ = écart-type des
variations quotidiennes des 60 jours ouvrés précédents (×k), P(max des clôtures restantes ≥ niveau) par simulation (Monte-Carlo, graine fixe).
Jamais de regard vers le futur : seules les clôtures datées AVANT le jour de décision servent."""
import csv, glob, json, math, os, random, re, sys
from datetime import datetime, timedelta, timezone, date
D = os.path.join(os.path.dirname(__file__), "..", "donnees")
COL = {2: "2 Yr", 5: "5 Yr", 10: "10 Yr", 30: "30 Yr"}
par = {}
for f in glob.glob(os.path.join(D, "par_*.csv")):
    for r in csv.DictReader(open(f)):
        d = datetime.strptime(r["Date"], "%m/%d/%Y").date()
        par[d] = {k: float(r[v]) for k, v in COL.items() if r.get(v)}
days = sorted(par)
MOIS = {m: i + 1 for i, m in enumerate("January February March April May June July August September October November December".split())}
_W = re.compile(r"between (\w+ \d+, \d{4}) and (\w+ \d+, \d{4})")
K = float(os.environ.get("K", "1.0")); N = 4000
def bdays(a, b):  # jours ouvrés (hors week-end) de a à b inclus ; les fériés sont rares, ignorés (léger excès de jours)
    x, out = a, []
    while x <= b:
        if x.weekday() < 5: out.append(x)
        x += timedelta(days=1)
    return out
rows = json.load(open(os.path.join(D, "marches.json")))
res, check = [], [0, 0]
rng = random.Random(7)
for r in rows:
    w = _W.search(r["desc"])
    if not w or r["gagne"] not in (0.0, 1.0):
        continue
    a, b = (datetime.strptime(x, "%B %d, %Y").date() for x in w.groups())
    ten, lvl, up = r["duree"], r["niveau"], r["sens"] == "high"
    obs = [par[d][ten] for d in days if a <= d <= b and ten in par[d]]
    if not obs:
        continue
    hit = (max(obs) >= lvl - 1e-9) if up else (min(obs) <= lvl + 1e-9)
    check[0] += 1; check[1] += hit == (r["gagne"] == 1.0)
    pts = json.load(open(os.path.join(D, "prix", r["oui"] + ".json")))
    for dd in bdays(a, b):
        t = datetime(dd.year, dd.month, dd.day, 2, tzinfo=timezone.utc)
        known = [d for d in days if d < dd and ten in par[d]]
        if len(known) < 61:
            continue
        seen = [par[d][ten] for d in known if a <= d]
        if seen and ((max(seen) >= lvl - 1e-9) if up else (min(seen) <= lvl + 1e-9)):
            break  # déjà touché : réglé
        ch = [par[known[i]][ten] - par[known[i - 1]][ten] for i in range(len(known) - 60, len(known))]
        sd = K * math.sqrt(sum(c * c for c in ch) / len(ch))
        rest = [d for d in bdays(dd, b)]
        if not rest:
            continue
        x0 = par[known[-1]][ten]
        n = 0
        for _ in range(N):
            x = x0
            for _d in rest:
                x += rng.gauss(0, sd)
                if (x >= lvl - 0.005) if up else (x <= lvl + 0.005):  # publié au centième
                    n += 1; break
        p = (n + 0.5) / (N + 1)
        pr = [q["p"] for q in pts if q["t"] <= t.timestamp() and q["t"] > t.timestamp() - 6 * 3600]
        if not pr:
            continue
        res.append({"id": r["id"], "ev": r["event"], "jour": dd.isoformat(), "p": p, "prix": pr[-1], "y": int(r["gagne"] == 1.0),
                    "ten": ten, "sens": r["sens"], "mois": r["mois"], "jours_restants": len(rest), "dist": round(abs(lvl - x0), 3), "sd": sd})
print("règlement relu :", check[1], "/", check[0])
json.dump(res, open(os.path.join(D, f"obs_K{K}.json"), "w"))
def ls(p, y): p = min(max(p, 1e-3), 1 - 1e-3); return math.log(p if y else 1 - p)
n = len(res)
print(f"K={K} {n} observations (marché × jour) ; log-score modèle {sum(ls(o['p'], o['y']) for o in res) / n:.4f} contre prix {sum(ls(o['prix'], o['y']) for o in res) / n:.4f}")
for lab, f in (("p<0,5 côté", lambda o: True),):
    pass
