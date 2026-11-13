"""Rejeu du 13/11/2026 (leçon de Freddie Mac, experiments/taux_immobilier.md) : la marche aléatoire × K de `taux_tresor_barriere`
contre des TRAJECTOIRES RÉELLES de clôtures du Trésor.

Mêmes observations que analyse.py (chaque jour ouvré de la fenêtre, décision à 02 h UTC, clôtures datées d'avant le jour seulement, prix
horaire du marché dans les 6 h d'avant). Modèles :
- `rw<K>` : marche aléatoire gaussienne, σ = écart-type des 60 dernières variations × K (le module en production, K = 1,3) ;
- `abs` : part des fenêtres historiques de n jours ouvrés (même durée, clôtures 1990 → 31/07/2026) dont le maximum (ou minimum) depuis le
  début dépasse l'écart demandé, en points ;
- `vol` : idem, chaque trajectoire divisée par l'écart-type de ses 60 jours d'avant et multipliée par celui d'aujourd'hui.
Sortie : log-score de chaque modèle et du prix, par mois et par sens."""
import csv, glob, json, math, os, random, re, statistics
from bisect import bisect_left
from datetime import datetime, timedelta, timezone, date
D = os.path.join(os.path.dirname(__file__), "..", "donnees")
COL = {2: "2 Yr", 5: "5 Yr", 10: "10 Yr", 30: "30 Yr"}
par = {}
for f in glob.glob(os.path.join(D, "par_*.csv")):
    for r in csv.DictReader(open(f)):
        try:
            d = datetime.strptime(r["Date"], "%m/%d/%Y").date()
        except (KeyError, ValueError):
            continue
        par[d] = {k: float(r[v]) for k, v in COL.items() if r.get(v) not in (None, "", "N/A")}
days = sorted(par)
COUPURE = date(2026, 8, 1)
NMAX = 25
hist = {}
for ten in COL:
    s = [par[d][ten] for d in days if d < COUPURE and ten in par[d]]
    sd60 = [None] * len(s)
    for i in range(60, len(s)):
        ch = [s[j] - s[j - 1] for j in range(i - 59, i + 1)]
        sd60[i] = math.sqrt(sum(c * c for c in ch) / 60)
    up = {n: [] for n in range(1, NMAX + 1)}
    dn = {n: [] for n in range(1, NMAX + 1)}
    upv = {n: [] for n in range(1, NMAX + 1)}
    dnv = {n: [] for n in range(1, NMAX + 1)}
    for i in range(60, len(s) - NMAX):
        hi = lo = 0.0
        for n in range(1, NMAX + 1):
            mv = s[i + n] - s[i]
            hi, lo = max(hi, mv), min(lo, mv)
            up[n].append(hi); dn[n].append(-lo)
            if sd60[i] and sd60[i] > 0:
                upv[n].append(hi / sd60[i]); dnv[n].append(-lo / sd60[i])
    hist[ten] = {n: (sorted(up[n]), sorted(dn[n]), sorted(upv[n]), sorted(dnv[n])) for n in up}
    print(ten, "ans :", len(s), "clôtures avant la coupure", flush=True)


def part(sorted_vals, seuil):
    return (len(sorted_vals) - bisect_left(sorted_vals, seuil - 1e-9) + 0.5) / (len(sorted_vals) + 1)


_W = re.compile(r"between (\w+ \d+, \d{4}) and (\w+ \d+, \d{4})")
def bdays(a, b):
    x, out = a, []
    while x <= b:
        if x.weekday() < 5 and x not in (date(2026, 9, 7), date(2026, 10, 12), date(2026, 11, 11), date(2026, 11, 26)):
            out.append(x)
        x += timedelta(days=1)
    return out
rows = json.load(open(os.path.join(D, "marches.json")))
rng = random.Random(7)
res = []
for r in rows:
    w = _W.search(r["desc"])
    if not w or r["gagne"] not in (0.0, 1.0):
        continue
    a, b = (datetime.strptime(x, "%B %d, %Y").date() for x in w.groups())
    ten, lvl, up = r["duree"], r["niveau"], r["sens"] == "high"
    pf = os.path.join(D, "prix", r["oui"] + ".json")
    if not os.path.exists(pf):
        continue
    pts = json.load(open(pf))
    for dd in bdays(a, b):
        t = datetime(dd.year, dd.month, dd.day, 2, tzinfo=timezone.utc).timestamp()
        known = [d for d in days if d < dd and ten in par[d]]
        seen = [par[d][ten] for d in known if a <= d]
        if seen and ((max(seen) >= lvl - 1e-9) if up else (min(seen) <= lvl + 1e-9)):
            break
        rest = bdays(dd, b)
        if not rest or len(rest) > NMAX:
            continue
        x0 = par[known[-1]][ten]
        ch = [par[known[i]][ten] - par[known[i - 1]][ten] for i in range(len(known) - 60, len(known))]
        sd = math.sqrt(sum(c * c for c in ch) / 60)
        dist = (lvl - 0.005 - x0) if up else (x0 - lvl - 0.005)   # publié au centième
        n = len(rest)
        u, dn_, uv, dv = hist[ten][n]
        p_abs = part(u if up else dn_, dist)
        p_vol = part(uv if up else dv, dist / sd)
        rw = {}
        for K in (1.0, 1.3):
            z = dist / (K * sd * math.sqrt(n))
            # barrière continue (principe de réflexion), corrigée du pas discret (Broadie-Glasserman : +0,5826 σ)
            zc = (dist + 0.5826 * K * sd) / (K * sd * math.sqrt(n))
            rw[K] = min(1.0, 2 * (1 - statistics.NormalDist().cdf(zc)))
        pr = [q["p"] for q in pts if t - 6 * 3600 < q["t"] <= t]
        if not pr:
            continue
        res.append({"ev": r["event"], "mois": r["mois"], "sens": r["sens"], "ten": ten, "y": int(r["gagne"] == 1.0), "prix": pr[-1],
                    "abs": p_abs, "vol": p_vol, "rw1.0": rw[1.0], "rw1.3": rw[1.3], "n": n, "jour": dd.isoformat()})
json.dump(res, open(os.path.join(D, "obs_trajectoires.json"), "w"))
def ls(p, y):
    p = min(max(p, 1e-3), 1 - 1e-3)
    return math.log(p if y else 1 - p)
def tableau(obs, titre):
    if not obs:
        return
    cols = ("prix", "rw1.0", "rw1.3", "abs", "vol")
    print(f"{titre:28s} n={len(obs):5d} " + " ".join(f"{c} {sum(ls(o[c], o['y']) for o in obs) / len(obs):+.3f}" for c in cols))
tableau(res, "toutes")
for m in sorted({o["mois"] for o in res}):
    for s in ("high", "low"):
        tableau([o for o in res if o["mois"] == m and o["sens"] == s], f"{m} {s}")
for ten in COL:
    tableau([o for o in res if o["ten"] == ten], f"{ten} ans")
