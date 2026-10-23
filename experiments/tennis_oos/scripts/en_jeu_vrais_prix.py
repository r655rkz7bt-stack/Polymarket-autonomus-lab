"""Tennis en jeu, aux PRIX RÉELLEMENT PAYÉS : décision à +T min (favori à 0,80-0,95 d'après l'historique connu à cet
instant), prix payé = premier échange d'achat de ce camp dans les 10 minutes qui suivent (idea_test.taker_cost,
after=True), frais = rate × p × (1−p). Verdict idea_test.verdict ; moitiés de période séparées."""
import json, sys
from datetime import datetime, timezone
sys.path.insert(0, "../../../src")
from polymarket_agent.idea_test import verdict, taker_cost, fee
rows = {r["id"]: r for r in json.load(open("donnees/matchs.json"))}
trades = {json.loads(l)["event"]: json.loads(l)["trades"] for l in open("donnees/echanges.jsonl")}
hist = {json.loads(l)["id"]: json.loads(l) for l in open("donnees/prix.jsonl")}
def snap(h, t):
    pts = [x for x in h if x[0] <= t]
    return pts[-1][1] if pts and t - pts[-1][0] <= 1800 else None
for lag in (900, 1800):
    for lo, hi in ((0.80, 0.95), (0.875, 0.95)):
        b = []
        for mid, p in hist.items():
            r = rows[mid]
            if r["event"] not in trades: continue
            q = snap(p["h"], p["st"] + lag)
            if q is None: continue
            fav = 0 if q >= 0.5 else 1
            pr = q if fav == 0 else 1 - q
            if not lo <= pr < hi: continue
            paid = taker_cost(trades[r["event"]], r["toks"][fav], r["toks"][1 - fav], p["st"] + lag, window=600, after=True)
            if paid is None or not 0.5 < paid < 0.99: continue
            c = paid + fee(paid, float(r["fee"] or 0))
            win = 1 if r["won"] == fav else 0
            b.append({"gain": (win - c) / c, "evenement": r["event"], "mois": datetime.fromtimestamp(p["st"], timezone.utc).strftime("%Y-%m"), "cout": c,
                      "win": win, "paid": paid, "pr": pr, "st": p["st"], "circ": r["circuit"]})
        if len(b) < 30: print(lag, lo, hi, "n =", len(b)); continue
        b.sort(key=lambda x: x["st"]); h = len(b) // 2
        v = verdict(b)
        print(f"+{lag // 60} min, prix connu {lo}-{hi}: n={v['paris']} (sur {len(b)}) payé moyen={sum(x['paid'] for x in b) / len(b):.3f} vs prix connu={sum(x['pr'] for x in b) / len(b):.3f} "
              f"gagnés={sum(x['win'] for x in b)} rend={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} mois={v['mois']} -> {v['verdict']}")
        print(f"      1re moitié rend={sum(x['gain'] for x in b[:h]) / h:+.3f}  2e moitié rend={sum(x['gain'] for x in b[h:]) / (len(b) - h):+.3f}")
        for c in ("atp", "wta", "itf"):
            s = [x for x in b if x["circ"] == c]
            if len(s) >= 30: print(f"      {c}: n={len(s)} rend={sum(x['gain'] for x in s) / len(s):+.3f}")
