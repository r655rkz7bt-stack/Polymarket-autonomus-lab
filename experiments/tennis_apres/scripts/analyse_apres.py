"""« Après l'échéance » au tennis : le favori à 0,94-0,985 quelques heures après le coup d'envoi (match fini ou presque, règlement pas encore payé)
gagne-t-il aussi souvent que son prix ? Prix de l'historique horaire + écart ; Usage : PYTHONPATH=../../src python scripts/analyse_apres.py"""
import json, collections
from datetime import datetime, timezone
from polymarket_agent.idea_test import verdict, fee
rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
hist = {json.loads(l)["id"]: json.loads(l) for l in open("donnees/prix.jsonl")}
def snap(h, t):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= 1800 else None
print("matchs", len(hist))
for lag in (2, 3, 4, 5, 6):
    for lo, hi in ((0.94, 0.985), (0.90, 0.94), (0.97, 0.995)):
        for sp in (0.01,):
            b = []
            for mid, p in hist.items():
                r = rows[mid]; q = snap(p["h"], p["st"] + lag * 3600)
                if q is None: continue
                fav = 0 if q >= 0.5 else 1; pr = q if fav == 0 else 1 - q
                if not lo <= pr < hi: continue
                pay = min(0.995, pr + sp); c = pay + fee(pay, float(r["fee"] or 0)); win = r["won"] == fav
                b.append({"gain": ((1 if win else 0) - c) / c, "evenement": r["event"], "mois": datetime.fromtimestamp(p["st"], timezone.utc).strftime("%Y-%m-%d")[:7], "cout": pay, "win": win, "circ": r["circuit"]})
            if len(b) < 30: continue
            v = verdict(b)
            print(f"+{lag} h  {lo}-{hi}: n={len(b)} payé {sum(x['cout'] for x in b)/len(b):.3f} gagnés {sum(x['win'] for x in b)}/{sum(x['cout'] for x in b):.1f} perdus {sum(not x['win'] for x in b)} rend {v['rendement_moyen']:+.4f} t_ev {v['confiance_evenements']:+.2f} -> {v['verdict']}")
