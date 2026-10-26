"""« Les deux équipes marquent » (BTTS), 26/10/2026 : OUI ou NON acheté d heures avant le coup d'envoi (premier échange preneur dans les 30 min), frais du marché,
50-50 comptés 0,5. Un pari par événement, type, délai et côté. À lancer depuis experiments/btts/."""
import json, sys, datetime, os, collections
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
jl = lambda x: json.loads(x) if isinstance(x, str) else x
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["m"]] = o["trades"]
rows = []
for l in open("donnees/btts.jsonl"):
    e = json.loads(l); start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    for m in e["markets"]:
        if m["conditionId"] not in tr or m.get("umaResolutionStatus") != "resolved": continue
        try: outs = jl(m["outcomes"]); pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if outs != ["Yes", "No"] or len(toks) != 2: continue
        pay = pr if sorted(pr) == [0.0, 1.0] else [0.5, 0.5] if pr == [0.5, 0.5] else None
        if pay is None: continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
        srt = tr[m["conditionId"]]
        for d in (1, 3, 6, 12, 24):
            lo_t, hi_t = start - d * 3600, start - d * 3600 + 1800
            for i, side in ((0, "Yes"), (1, "No")):
                pts = sorted([(t[0], t[3]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[i] and t[2] == "BUY"]
                             + [(t[0], 1 - t[3]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[1 - i] and t[2] == "SELL"])
                if not pts or not 0.05 <= pts[0][1] <= 0.95: continue
                ts_, p = pts[0]
                rows.append({"evenement": e["id"], "sport": e["sport"], "ty": m["sportsMarketType"], "d": d, "side": side, "cout": p, "won": pay[i],
                             "gain": (pay[i] - p - fee(p, rate)) / p, "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")})
print("paris", len(rows), "événements", len({r['evenement'] for r in rows}))
def line(label, bets):
    if len(bets) < 5: return
    m = sum(b["gain"] for b in bets) / len(bets); v = verdict(bets, min_bets=30)
    print(f"{label:38} {len(bets):5d} paris {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {sum(b['won'] for b in bets):.0f}/{sum(b['cout'] for b in bets):.0f}")
for ty in ("both_teams_to_score", "both_teams_to_score_first_half", "both_teams_to_score_second_half"):
    for d in (1, 3, 6, 12, 24):
        for side in ("Yes", "No"): line(f"{ty[-22:]} -{d} h {side}", [r for r in rows if r["ty"] == ty and r["d"] == d and r["side"] == side])
print("== match entier, par tranche de prix, -3 h ==")
for lo, hi in ((0.05, .3), (.3, .45), (.45, .6), (.6, .8), (.8, .95)):
    for side in ("Yes", "No"): line(f"{lo}-{hi} {side}", [r for r in rows if r["ty"] == "both_teams_to_score" and r["d"] == 3 and r["side"] == side and lo <= r["cout"] < hi])
