"""Tennis en jeu : le favori à 0,80-0,95 PENDANT le match gagne-t-il plus souvent que son prix ?
(la championne nf_sport_patiente achète 84 % de ses paris après le coup d'envoi). Un instantané par match et par
retard après le coup d'envoi ; décision = prix connu à cet instant seulement (jamais de regard vers l'avenir)."""
import json, math, sys, collections
from datetime import datetime, timezone
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import verdict
rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
data = [(rows[json.loads(l)["id"]], json.loads(l)) for l in open("donnees/prix.jsonl")]
def snap(h, t):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= 1800 else None
for lag in (900, 1800, 3600, 5400, 7200):
    for lo, hi in ((0.80, 0.95), (0.80, 0.875), (0.875, 0.95)):
        b = []
        for r, p in data:
            q = snap(p["h"], p["st"] + lag)
            if q is None: continue
            side0 = q >= 0.5
            pr, win = (q, 1 if r["won"] == 0 else 0) if side0 else (1 - q, 1 if r["won"] == 1 else 0)
            if not lo <= pr < hi: continue
            c = pr + 0.01; c += float(r["fee"] or 0) * c * (1 - c)
            if c >= 0.99: continue
            b.append({"gain": (win - c) / c, "evenement": r["event"], "mois": datetime.fromtimestamp(p["st"], timezone.utc).strftime("%Y-%m"), "cout": c,
                      "win": win, "p": pr, "circ": r["circuit"]})
        if len(b) < 30: continue
        n = len(b); w = sum(x["win"] for x in b); e = sum(x["p"] for x in b); var = sum(x["p"] * (1 - x["p"]) for x in b)
        v = verdict(b)
        print(f"+{lag // 60:3d} min prix {lo}-{hi}: n={n:4} gagnés={w} attendus={e:.1f} z={(w - e) / math.sqrt(var):+.2f} | après frais+écart rend={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} mois={v['mois_gagnants']} -> {v['verdict']}")
        if (lo, hi) == (0.80, 0.95):
            for c in ("atp", "wta", "itf"):
                s = [x for x in b if x["circ"] == c]
                if len(s) >= 30: print(f"      {c}: n={len(s)} rend={sum(x['gain'] for x in s) / len(s):+.3f} gagnés={sum(x['win'] for x in s)} attendus={sum(x['p'] for x in s):.1f}")
