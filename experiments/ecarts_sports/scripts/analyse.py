"""Handicaps (spreads) de sport (26/10/2026), même méthode que totaux_sports/scripts/analyse.py. Ligne principale = celle dont le jeton 0 coûte le plus près
de 0,5 ; on achète le côté qui DONNE des points (« favori », ligne négative) ou celui qui en REÇOIT (« outsider ») au premier échange preneur dans les 30 minutes
qui suivent `coup d'envoi − d heures`. 50-50 comptés 0,5. À lancer depuis experiments/ecarts_sports/."""
import json, sys, datetime, collections, os
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
jl = lambda x: json.loads(x) if isinstance(x, str) else x
tr = {}
for f in ("donnees/echanges.jsonl", "donnees/echanges_rev.jsonl"):
    if os.path.exists(f):
        for l in open(f):
            o = json.loads(l); tr[o["m"]] = o["trades"]
DELAYS = [1, 3, 6, 12, 24]
rows = []; nev = 0
for l in open("donnees/ecarts.jsonl"):
    e = json.loads(l)
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    by_type = collections.defaultdict(list)
    for m in e["markets"]:
        if m["conditionId"] not in tr or m.get("umaResolutionStatus") != "resolved" or m.get("line") is None: continue
        try:
            pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if len(toks) != 2: continue
        if sorted(pr) == [0.0, 1.0]: pay = pr
        elif pr == [0.5, 0.5]: pay = [0.5, 0.5]
        else: continue
        by_type[m["sportsMarketType"]].append((m, toks, pay))
    if not by_type: continue
    nev += 1
    for ty, mks in by_type.items():
        for d in DELAYS:
            lo_t, hi_t = start - d * 3600, start - d * 3600 + 1800
            cands = []
            for m, toks, pay in mks:
                srt = tr[m["conditionId"]]; px = []
                for i in (0, 1):
                    pts = sorted([(t[0], t[3], t[4]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[i] and t[2] == "BUY"]
                                 + [(t[0], 1 - t[3], t[4]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[1 - i] and t[2] == "SELL"])
                    px.append(pts[0] if pts else None)
                if px[0] and px[1]:
                    cands.append((abs(px[0][1] - 0.5), m, px, pay))
            if not cands: continue
            _, m, px, pay = min(cands, key=lambda c: c[0])
            fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
            rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
            line0 = float(m["line"])
            for i in (0, 1):
                ts_, p, sz = px[i]
                if not 0.05 <= p <= 0.95: continue
                gives = (line0 < 0) if i == 0 else (line0 > 0)
                rows.append({"evenement": e["id"], "sport": e["sport"], "ty": ty, "d": d, "side": "favori" if gives else "outsider", "cout": p, "won": pay[i],
                             "gain": (pay[i] - p - fee(p, rate)) / p, "taille": sz, "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")})
print("événements", nev, "paris", len(rows))
def line(label, bets):
    if len(bets) < 5: return
    m = sum(b["gain"] for b in bets) / len(bets); v = verdict(bets, min_bets=30)
    print(f"{label:34} {len(bets):5d} paris {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {sum(b['won'] for b in bets):.0f}/{sum(b['cout'] for b in bets):.0f}")
for d in DELAYS:
    for side in ("favori", "outsider"): line(f"-{d} h {side}", [r for r in rows if r["d"] == d and r["side"] == side])
print("== par type (-3 h) ==")
for ty in sorted({r["ty"] for r in rows}):
    for side in ("favori", "outsider"): line(f"{ty} {side}", [r for r in rows if r["d"] == 3 and r["ty"] == ty and r["side"] == side])
print("== par sport (spreads, -3 h) ==")
for sp in sorted({r["sport"] for r in rows}):
    for side in ("favori", "outsider"): line(f"{sp} {side}", [r for r in rows if r["d"] == 3 and r["ty"] == "spreads" and r["sport"] == sp and r["side"] == side])
json.dump(rows, open("donnees/paris.json", "w"))
