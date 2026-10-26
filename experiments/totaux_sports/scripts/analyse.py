"""Piste « Under des totaux de sport » (26/10/2026). À lancer depuis experiments/totaux_sports/.
Pour chaque événement, type de marché et délai d (heures avant le coup d'envoi), on prend la ligne dont le prix du « Over »
est le plus proche de 0,5 (la ligne principale) puis on achète « Over » et « Under » (deux séries de paris, jugées séparément) au
premier échange preneur dans les 30 minutes qui suivent l'instant de décision (prix réel, frais du marché). Les règlements à 0,5-0,5
(ligne entière, match annulé) sont comptés 0,5. Un pari par (événement, type, délai, côté)."""
import bisect, json, sys, datetime, collections, os
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
jl = lambda x: json.loads(x) if isinstance(x, str) else x
tr = {}
for f in ("donnees/echanges.jsonl", "donnees/echanges_rev.jsonl"):
    if os.path.exists(f):
        for l in open(f):
            o = json.loads(l); tr[o["m"]] = o["trades"]
DELAYS = [int(x) for x in os.environ.get("DELAYS", "1,3,6,12,24").split(",")]
GROUP = {"atp": "tennis", "wta": "tennis", "itf": "tennis", "cs2": "esport", "lol": "esport", "dota2": "esport", "val": "esport",
         "nba": "basket", "wnba": "basket", "euroleague": "basket", "ncaab": "basket", "cbb": "basket", "nfl": "football_us", "cfb": "football_us",
         "mlb": "baseball", "npb": "baseball", "kbo": "baseball", "nhl": "hockey", "ahl": "hockey", "khl": "hockey"}
rows = []
nev = 0
for l in open("donnees/totaux.jsonl"):
    e = json.loads(l)
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    by_type = collections.defaultdict(list)
    for m in e["markets"]:
        if m["conditionId"] not in tr or m.get("umaResolutionStatus") != "resolved": continue
        try:
            outs = jl(m["outcomes"]); pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if outs != ["Over", "Under"] or len(toks) != 2: continue
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
                srt = tr[m["conditionId"]]
                px = []
                for i in (0, 1):
                    pts = sorted([(t[0], t[3]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[i] and t[2] == "BUY"]
                                 + [(t[0], 1 - t[3]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[1 - i] and t[2] == "SELL"])
                    px.append(pts[0] if pts else None)
                if px[0] and px[1]:
                    cands.append((abs(px[0][1] - 0.5), m, px, pay))
            if not cands: continue
            _, m, px, pay = min(cands, key=lambda c: c[0])
            fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
            rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
            for i, side in ((0, "Over"), (1, "Under")):
                ts_, p = px[i]
                if not 0.05 <= p <= 0.95: continue
                rows.append({"evenement": e["id"], "sport": e["sport"], "ty": ty, "d": d, "side": side, "cout": p, "won": pay[i], "void": pay[i] == 0.5, "ts": ts_,
                             "gain": (pay[i] - p - fee(p, rate)) / p, "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")})
print("événements avec totaux et échanges", nev, "paris", len(rows))
def line(label, bets):
    if len(bets) < 5: return
    m = sum(b["gain"] for b in bets) / len(bets)
    v = verdict(bets, min_bets=30)
    exp = sum(b["cout"] for b in bets); won = sum(b["won"] for b in bets)
    print(f"{label:46} {len(bets):5d} paris  {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {won:.0f}/{exp:.0f}")
for d in DELAYS:
    for side in ("Over", "Under"):
        line(f"-{d} h {side} tous", [r for r in rows if r["d"] == d and r["side"] == side])
print("== par type de marché (-3 h) ==")
for ty in sorted({r["ty"] for r in rows}):
    for side in ("Over", "Under"):
        line(f"{ty} {side}", [r for r in rows if r["d"] == 3 and r["ty"] == ty and r["side"] == side])
print("== par sport (type totals, -3 h) ==")
for sp in sorted({r["sport"] for r in rows}):
    for side in ("Over", "Under"):
        line(f"{sp} {side}", [r for r in rows if r["d"] == 3 and r["ty"] == "totals" and r["sport"] == sp and r["side"] == side])
json.dump(rows, open("donnees/paris.json", "w"))
