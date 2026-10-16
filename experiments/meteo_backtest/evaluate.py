"""Backtest météo, étape 2 : modèle (prévision passée + flou) contre le marché, hors échantillon."""
import json, math, sys, statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
SP = sys.argv[1]; sys.path.insert(0, sys.argv[2])
from polymarket_agent import weather_model as wm
D = json.load(open(f"{SP}/bt/data.json")); fc = D["fc"]
LEAD = sys.argv[3] if len(sys.argv) > 3 else "day1"   # day1 : prix au début du jour local ; day2 : 24 h avant

def daily(station, date, kind, model):
    f = fc.get(station)
    if not f: return None
    h = f["hourly"]; key = f"temperature_2m_previous_{LEAD}_{model}"
    vals = [v for t, v in zip(h["time"], h.get(key, [])) if t.startswith(date) and v is not None]
    if len(vals) < 20: return None
    return max(vals) if kind == "max" else min(vals)

rows = []
for r in D["rows"]:
    p = r.get("p0") if LEAD == "day1" else r.get("p_1")
    if p is None or not (0.005 < p < 0.995): continue
    q = wm.parse_question(r["q"])
    g, e = daily(r["station"], r["date"], q.kind, "gfs_seamless"), daily(r["station"], r["date"], q.kind, "ecmwf_ifs025")
    if g is None or e is None: continue
    rows.append(dict(r, p=p, q=q, members=[g, e]))
print(len(rows), "marchés avec prix et prévisions", "(", LEAD, ")")
dates = sorted({r["date"] for r in rows}); cut = dates[len(dates) // 2]
train = [r for r in rows if r["date"] < cut]; test = [r for r in rows if r["date"] >= cut]
print("apprentissage", len(train), "dates <", cut, "; test", len(test))

def P(r, sigma, bias):
    return min(0.999, max(0.001, wm.probability(r["q"], r["members"], sigma, bias)))
def brier(rs, f): return sum((f(r) - r["won"]) ** 2 for r in rs) / len(rs)
def logloss(rs, f): return -sum(math.log(f(r) if r["won"] else 1 - f(r)) for r in rs) / len(rs)
# biais moyen par type (prévision - réel inconnu : on l'ajuste sur la vraisemblance)
best = None
for kind in ("max", "min"):
    tr = [r for r in train if r["q"].kind == kind]
    cands = [(logloss(tr, lambda r, s=s, b=b: P(r, s, b)), s, b) for s in (0.6, 0.8, 1.0, 1.2, 1.5, 1.8, 2.2) for b in (-1.5, -1, -0.5, 0, 0.5, 1, 1.5)]
    ll, s, b = min(cands)
    print(f"[{kind}] réglage : sigma={s} °C, biais={b} °C, logloss apprentissage {ll:.4f}")
    best = best or {}; best[kind] = (s, b)
f_model = lambda r: P(r, *best[r["q"].kind])
f_mkt = lambda r: r["p"]
print(f"TEST Brier : modèle {brier(test, f_model):.4f} | marché {brier(test, f_mkt):.4f} | mélange 50/50 {brier(test, lambda r: (f_model(r)+r['p'])/2):.4f}")
print(f"TEST logloss : modèle {logloss(test, f_model):.4f} | marché {logloss(test, f_mkt):.4f}")
# Simulation : 1 part par pari, prix = dernier prix + 0,01 (écart achat-vente) + frais.
def fee(p): return 0.05 * p * (1 - p)
for edge in (0.03, 0.05, 0.08, 0.12):
    pnl = n = wins = 0; stakes = 0
    for r in test:
        pm = f_model(r); y = r["p"] + 0.01; no = (1 - r["p"]) + 0.01
        if pm - y - fee(y) > edge:
            n += 1; stakes += y; g = r["won"] - y - fee(y); pnl += g; wins += g > 0
        elif (1 - pm) - no - fee(no) > edge:
            n += 1; stakes += no; g = (1 - r["won"]) - no - fee(no); pnl += g; wins += g > 0
    print(f"seuil {edge:.2f} : {n} paris, gagnants {wins}, résultat {pnl:+.2f} pour {stakes:.2f} misés ({(pnl / stakes * 100 if stakes else 0):+.1f} %)")
# Par jour du test, pour voir la régularité (seuil 0,05)
byday = defaultdict(float)
for r in test:
    pm = f_model(r); y = r["p"] + 0.01; no = (1 - r["p"]) + 0.01
    if pm - y - fee(y) > 0.05: byday[r["date"]] += r["won"] - y - fee(y)
    elif (1 - pm) - no - fee(no) > 0.05: byday[r["date"]] += (1 - r["won"]) - no - fee(no)
print("par jour (seuil 0,05) :", {d: round(v, 2) for d, v in sorted(byday.items())})
