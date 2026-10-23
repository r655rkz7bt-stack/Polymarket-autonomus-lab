"""« Après l'échéance » au tennis, aux PRIX RÉELLEMENT PAYÉS : décision à +L h (favori 0,90-0,985 connu), prix = premier achat du favori
dans les W minutes qui suivent (idea_test.taker_cost). Un match sans échange dans la fenêtre n'est pas exécutable : compté à part."""
import json
from datetime import datetime, timezone
from polymarket_agent.idea_test import verdict, taker_cost, fee
rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
trades = {json.loads(l)["event"]: json.loads(l)["trades"] for l in open("donnees/echanges.jsonl")}
hist = {json.loads(l)["id"]: json.loads(l) for l in open("donnees/prix.jsonl")}
def snap(h, t):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= 1800 else None
for lag in (3, 4, 5, 6):
    for lo, hi in ((0.90, 0.94), (0.94, 0.985), (0.90, 0.985)):
        for W in (10, 30):
            b, seen, nofill = [], 0, 0
            for mid, p in hist.items():
                r = rows[mid]
                if r["event"] not in trades: continue
                q = snap(p["h"], p["st"] + lag * 3600)
                if q is None: continue
                fav = 0 if q >= 0.5 else 1; pr = q if fav == 0 else 1 - q
                if not lo <= pr < hi: continue
                seen += 1
                paid = taker_cost(trades[r["event"]], r["toks"][fav], r["toks"][1 - fav], p["st"] + lag * 3600, window=W * 60, after=True)
                if paid is None or not 0.5 < paid < 0.999: nofill += 1; continue
                c = paid + fee(paid, float(r["fee"] or 0)); win = r["won"] == fav
                b.append({"gain": ((1 if win else 0) - c) / c, "evenement": r["event"], "mois": "x", "cout": paid, "win": win, "pr": pr, "circ": r["circuit"]})
            if len(b) < 30: print(f"+{lag}h {lo}-{hi} W={W}: n={len(b)} (vus {seen}, sans échange {nofill})"); continue
            v = verdict(b)
            print(f"+{lag}h {lo}-{hi} W={W}min: vus {seen}, servis {len(b)} payé {sum(x['cout'] for x in b)/len(b):.3f} (histo {sum(x['pr'] for x in b)/len(b):.3f}) gagnés {sum(x['win'] for x in b)}/{sum(x['cout'] for x in b):.1f} perdus {sum(not x['win'] for x in b)} rend {v['rendement_moyen']:+.4f} t_ev {v['confiance_evenements']:+.2f} -> {v['verdict']}")
