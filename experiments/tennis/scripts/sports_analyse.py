"""E-sport (CS2, LoL, Dota 2, Valorant) : le favori gagne-t-il plus souvent que son prix, avant et pendant le match ?
Mêmes règles que le tennis (prix CLOB connus à l'instant, écart 1 ¢, frais du marché, idea_test.verdict).
Usage depuis experiments/tennis : ../../.venv/bin/python scripts/esport_analyse.py"""
import json, math, sys, collections
from datetime import datetime, timezone
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import verdict
rows = {r["id"]: r for r in json.load(open("donnees/sport_matchs.json"))}
data = [(rows[json.loads(l)["id"]], json.loads(l)) for l in open("donnees/sport_prix.jsonl")]
print("marchés", len(rows), "avec historique", len(data), collections.Counter((r["circuit"], r["type"]) for r, _ in data))
def snap(h, t, tol=1800):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= tol else None
def run(lag, lo, hi, select=lambda r: True, label=""):
    b = []
    for r, p in data:
        if not select(r): continue
        q = snap(p["h"], p["st"] + lag)
        if q is None: continue
        fav = q >= 0.5
        pr = q if fav else 1 - q
        win = 1 if (r["won"] == 0) == fav else 0
        if not lo <= pr < hi: continue
        c = pr + 0.01; c += float(r["fee"] or 0) * c * (1 - c)
        if c >= 0.99: continue
        b.append({"gain": (win - c) / c, "evenement": r["event"], "mois": datetime.fromtimestamp(p["st"], timezone.utc).strftime("%Y-%m"), "cout": c, "win": win, "p": pr})
    if len(b) < 30: return None
    n = len(b); w = sum(x["win"] for x in b); e = sum(x["p"] for x in b); var = sum(x["p"] * (1 - x["p"]) for x in b)
    v = verdict(b)
    print(f"{label:34} lag={lag // 60:4d} min prix {lo}-{hi}: n={n:5} gagnés={w} attendus={e:.0f} z={(w - e) / math.sqrt(var):+.2f} rend={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} mois={v['mois_gagnants']} -> {v['verdict']}")
    return v
for typ in ("moneyline", "child_moneyline"):
    for lag in (-3600, -600, 900, 1800, 3600):
        for lo, hi in ((0.5, 0.8), (0.8, 0.95)):
            run(lag, lo, hi, lambda r, typ=typ: r["type"] == typ, typ)
print("-- par jeu, favori 0,80-0,95, match entier")
for g in ("cs2", "lol", "dota2", "val"):
    for lag in (-3600, 1800):
        run(lag, 0.8, 0.95, lambda r, g=g: r["circuit"] == g and r["type"] == "moneyline", g)
