"""28/10/2026 : marchés de football « premier à marquer », « buteur à tout moment », corners d'équipe, totaux d'équipe de la 1re mi-temps :
chaque issue est achetée au premier échange preneur qui suit la décision (T = coup d'envoi − d heures, fenêtre de 30 min), prix de 0,05 à 0,95,
frais du marché, 50-50 compté 0,5. Même méthode que experiments/totaux_sports/scripts/analyse_complet.py. Sortie : lignes par type × issue × délai × tranche de prix."""
import json, sys, datetime, collections, os
sys.path.insert(0, "src")
from polymarket_agent.idea_test import fee, verdict
D = "experiments/props_football/donnees"
jl = lambda x: json.loads(x) if isinstance(x, str) else x
tr = {}
for l in open(f"{D}/echanges_props.jsonl"):
    o = json.loads(l); tr[o["m"]] = o["trades"]
DELAYS = [1, 3, 6, 12, 24]
rows = []
for l in open(f"{D}/props_evenements.jsonl"):
    e = json.loads(l)
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    for m in e["markets"]:
        if m["conditionId"] not in tr or m.get("umaResolutionStatus") != "resolved": continue
        try:
            outs = jl(m["outcomes"]); pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if len(outs) != 2 or len(toks) != 2: continue
        if sorted(pr) == [0.0, 1.0]: pay = pr
        elif pr == [0.5, 0.5]: pay = pr
        else: continue
        srt = tr[m["conditionId"]]
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
        for d in DELAYS:
            lo_t, hi_t = start - d * 3600, start - d * 3600 + 1800
            for i in (0, 1):
                pts = sorted([(t[0], t[3], t[4]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[i] and t[2] == "BUY"]
                             + [(t[0], 1 - t[3], t[4]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[1 - i] and t[2] == "SELL"])
                if not pts: continue
                ts_, p, sz = pts[0]
                if not 0.05 <= p <= 0.95: continue
                rows.append({"evenement": e["id"], "sport": e["sport"], "ty": m["sportsMarketType"], "d": d, "side": str(outs[i]), "cout": p, "won": pay[i], "ts": ts_,
                             "taille": sz, "gain": (pay[i] - p - fee(p, rate)) / p, "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")})
print("paris", len(rows), "événements", len({r['evenement'] for r in rows}))
def line(label, bets, mini=30):
    if len(bets) < mini: return
    m = sum(b["gain"] for b in bets) / len(bets)
    v = verdict(bets, min_bets=30)
    print(f"{label:52} {len(bets):5d} paris {len({b['evenement'] for b in bets}):4d} év {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {sum(b['won'] for b in bets):.0f}/{sum(b['cout'] for b in bets):.0f}")
for ty in sorted({r["ty"] for r in rows}):
    print("==", ty)
    for side in sorted({r["side"] for r in rows if r["ty"] == ty}):
        for d in DELAYS:
            line(f"{side} -{d} h", [r for r in rows if r["ty"] == ty and r["side"] == side and r["d"] == d])
        for lo, hi in ((0.05, 0.15), (0.15, 0.30), (0.30, 0.50), (0.50, 0.70), (0.70, 0.95)):
            line(f"{side} tranche {lo}-{hi} (tous délais 3 h)", [r for r in rows if r["ty"] == ty and r["side"] == side and r["d"] == 3 and lo <= r["cout"] < hi])
json.dump(rows, open(f"{D}/paris_props.json", "w"))
