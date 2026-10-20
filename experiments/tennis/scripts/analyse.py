"""Piste n° 1 (tennis) : le favori d'un match gagne-t-il plus ou moins souvent que son prix ?
Prix du CLOB à J-24 h / J-6 h / J-1 h / J-10 min avant le coup d'envoi ; achats simulés du favori (ou de
l'outsider) avec les vrais frais (rate × p × (1−p)) et un écart de 1 centime ; verdict = idea_test.verdict.
Usage (depuis experiments/tennis) : ../../.venv/bin/python scripts/analyse.py"""
import json, math, sys, collections
from datetime import datetime, timezone
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import verdict

rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
cases = []
for l in open("donnees/prix.jsonl"):
    p = json.loads(l); r = rows[p["id"]]; h = p["h"]
    if len(h) < 6: continue
    # contrôle du règlement : l'issue « 0 » a gagné ssi le dernier prix de la fenêtre étendue tend vers 1 (vérifié plus bas)
    def at(lag):
        pts = [x for x in h if x[0] <= p["st"] - lag]
        return pts[-1][1] if pts and p["st"] - lag - pts[-1][0] <= 3 * 3600 else None
    pr = {lag: at(lag) for lag in (24 * 3600, 6 * 3600, 3600, 600)}
    cases.append(dict(r, st=p["st"], pr=pr, y0=1 if r["won"] == 0 else 0, month=datetime.fromtimestamp(p["st"], timezone.utc).strftime("%Y-%m")))
print("matchs avec historique", len(cases))
fee_rate = lambda c: float(c["fee"] or 0)

def price_fav(c, lag):
    p0 = c["pr"][lag]
    if p0 is None: return None
    # favori = camp au prix le plus haut ; prix du camp 1 ≈ 1 − p0
    return (0, p0, c["y0"]) if p0 >= 0.5 else (1, 1 - p0, 1 - c["y0"])

def bets(select, lag, spread=0.01, side="fav"):
    out = []
    for c in cases:
        f = price_fav(c, lag)
        if f is None or not select(c, f[1]): continue
        _, p, win = f
        if side == "dog": p, win = 1 - p, 1 - win
        cost = p + spread + fee_rate(c) * (p + spread) * (1 - p - spread)
        if cost >= 0.99: continue
        out.append({"gain": (win - cost) / cost, "evenement": c["event"], "mois": c["month"], "cout": cost, "win": win, "p": p})
    return out

def calib(sel, lag, label):
    b = bets(sel, lag, spread=0.0)
    if not b: return
    n = len(b); w = sum(x["win"] for x in b); e = sum(x["p"] for x in b); var = sum(x["p"] * (1 - x["p"]) for x in b)
    print(f"  {label:28} n={n:5} gagnés={w:5.0f} attendus={e:7.1f} écart={(w - e) / n * 100:+5.1f} pts  z={(w - e) / math.sqrt(var):+5.2f}")

bands = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 1.0)]
for lag, name in ((6 * 3600, "J-6h"), (3600, "J-1h"), (600, "J-10min")):
    print(f"\n== Favori à {name} : gagne-t-il plus souvent que son prix ? ==")
    calib(lambda c, p: True, lag, "tous")
    for circ in ("atp", "wta", "itf"):
        calib(lambda c, p, circ=circ: c["circuit"] == circ, lag, circ)
    for lo, hi in bands:
        calib(lambda c, p, lo=lo, hi=hi: lo <= p < hi, lag, f"prix {lo:.1f}-{hi:.1f}")
if "--achats" in sys.argv:
    for lag, name in ((6 * 3600, "J-6h"), (3600, "J-1h"), (600, "J-10min")):
        for side in ("fav", "dog"):
            for lo, hi in ((0.5, 0.8), (0.8, 0.95), (0.5, 0.95)):
                b = bets(lambda c, p, lo=lo, hi=hi: lo <= p < hi, lag, side=side)
                if len(b) >= 30:
                    v = verdict(b)
                    print(f"{name} {side} prix {lo}-{hi}: n={v['paris']} rendement={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} mois={v['mois_gagnants']} -> {v['verdict']}")
