"""Météo : biais et flou par station appris sur les jours PRÉCÉDENTS (tranche gagnante = valeur réelle)."""
import json, sys, statistics
from collections import defaultdict
SP = sys.argv[1]; sys.path.insert(0, sys.argv[2])
from polymarket_agent import weather_model as wm, idea_test as it
D = json.load(open(f"{SP}/bt/data.json")); fc = D["fc"]
LEAD = "day1"
def daily(st, date, kind, model):
    f = fc.get(st)
    if not f: return None
    h = f["hourly"]; vals = [v for t, v in zip(h["time"], h.get(f"temperature_2m_previous_{LEAD}_{model}", [])) if t.startswith(date) and v is not None]
    if len(vals) < 20: return None
    return max(vals) if kind == "max" else min(vals)
# valeur réelle (°C) d'après la tranche gagnante de chaque événement
truth = {}
for r in D["rows"]:
    if r["won"] != 1: continue
    q = wm.parse_question(r["q"])
    lo, hi = q.low, q.high
    v = (lo + hi) / 2 if lo != -wm.INF and hi != wm.INF else (lo + 0.5 if hi == wm.INF else hi - 0.5)
    truth[(r["station"], r["date"], q.kind)] = (v - 32) / 1.8 if q.unit == "F" else v
cases = []
for r in D["rows"]:
    p = r.get("p0")
    if p is None or not (0.005 < p < 0.995): continue
    q = wm.parse_question(r["q"])
    g, e = daily(r["station"], r["date"], q.kind, "gfs_seamless"), daily(r["station"], r["date"], q.kind, "ecmwf_ifs025")
    if g is None or e is None: continue
    row = it.Resolved(r["yes"], r["event"], r["event"], r["q"], r["yes"], int(r["won"]), 0, fee_rate=0.05)
    c = it.Case(row, p, r["station"], r["date"]); c.q = q; c.members = [g, e]; c.key = (r["station"], q.kind)
    cases.append(c)
# erreurs passées par (station, type) : réel − moyenne des modèles, jour par jour
err = defaultdict(dict)
for c in cases:
    t = truth.get((c.group, c.day, c.q.kind))
    if t is not None: err[c.key][c.day] = t - sum(c.members) / len(c.members)
GLOBAL = {"max": (1.5, 0.5), "min": (1.8, 0.0)}
def station_params(c, window=7, min_days=3, shrink=3.0, sigma_floor=0.8):
    past = [v for d, v in sorted(err[c.key].items()) if d < c.day][-window:]
    s0, b0 = GLOBAL[c.q.kind]
    if len(past) < min_days: return s0, b0
    n = len(past); b = (sum(past) + shrink * b0) / (n + shrink)            # moyenne tirée vers le biais global
    sd = statistics.pstdev(past) if n > 1 else s0
    s = max(sigma_floor, ((n * sd * sd + shrink * s0 * s0) / (n + shrink)) ** 0.5)
    return s, b
def prob(c, mode):
    s, b = GLOBAL[c.q.kind] if mode == "global" else station_params(c)
    if mode == "bias_only": s = GLOBAL[c.q.kind][0]
    return min(0.999, max(0.001, wm.probability(c.q, c.members, s, b)))
for mode in ("global", "bias_only", "station"):
    rep = it.evaluate(cases, lambda c: prob(c, mode), edges=(0.05, 0.08), spreads=(0.01, 0.02), sides=("NON",))
    print(f"== {mode} : Brier {rep['brier_modele']} (marché {rep['brier_marche']}), logloss {rep['logloss_modele']} ({rep['logloss_marche']})")
    for k, sim in rep["simulations"].items():
        t = sim["total"]; print(f"   {k}: {t['paris']} paris, {t['rendement_pct']} %, jours gagnants {sum(v > 0 for v in sim['par_jour'].values())}/{len(sim['par_jour'])}, stations gagnantes {sim['groupes_gagnants']}/{sim['groupes']}")
