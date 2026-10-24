"""Outsider (jeton à bas prix) acheté d heures AVANT le coup d envoi, 50-50 INCLUS : un 50-50 paie 0,5 par part, soit 3 à 10 fois le prix d un outsider. À lancer depuis experiments/avant_match_50_50/."""
import bisect, json, sys, datetime, collections, os
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
LO, HI = float(os.environ.get("LO", 0.05)), float(os.environ.get("HI", 0.20))
ev = [json.loads(l) for l in open("donnees/events.jsonl")]
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["event"]] = o["trades"]
jl = lambda x: json.loads(x) if isinstance(x, str) else x
GROUP = {"atp": "tennis", "wta": "tennis", "itf": "tennis", "cs2": "esport", "lol": "esport", "dota2": "esport", "val": "esport"}
DELAYS = [1, 3, 6, 12, 24]
rows = []
for e in ev:
    if e["id"] not in tr: continue
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    srt = sorted(tr[e["id"]]); times = [t[0] for t in srt]
    cands = []
    for m in e["markets"]:
        if m.get("sportsMarketType") != "moneyline": continue
        try:
            pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if len(toks) != 2 or len(pr) != 2: continue
        if m.get("umaResolutionStatus") not in (None, "", "resolved"): continue
        if sorted(pr) == [0.0, 1.0]: pay = pr
        elif pr == [0.5, 0.5]: pay = [0.5, 0.5]
        else: continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
        for i in (0, 1): cands.append((toks[i], toks[1 - i], pay[i], rate, pr == [0.5, 0.5]))
    for d in DELAYS:
        lo_t, hi_t = start - d * 3600, start - d * 3600 + 1800
        i0 = bisect.bisect_left(times, lo_t); i1 = bisect.bisect_right(times, hi_t)
        best = None
        for tok, oth, pay, rate, void in cands:
            pts = sorted([(t[0], t[3]) for t in srt[i0:i1] if t[1] == tok and t[2] == "BUY"] + [(t[0], 1 - t[3]) for t in srt[i0:i1] if t[1] == oth and t[2] == "SELL"])
            if not pts: continue
            ts_, p = pts[0]
            if not LO <= p <= HI: continue
            rec = {"evenement": e["id"], "sport": e["sport"], "d": d, "cout": p, "won": pay, "void": void, "ts": ts_,
                   "gain": (pay - p - fee(p, rate)) / p, "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")}
            if best is None or ts_ < best["ts"]: best = rec
        if best: rows.append(best)
def line(label, bets):
    if not bets: print(f"{label}: 0 paris"); return
    nov = [b for b in bets if not b["void"]]
    nv = len(bets) - len(nov)
    m = sum(b["gain"] for b in bets) / len(bets); m0 = sum(b["gain"] for b in nov) / max(1, len(nov))
    v = verdict(bets, min_bets=30)
    exp = sum(b["cout"] for b in nov); won = sum(1 for b in nov if b["won"] == 1)
    print(f"{label}: {len(bets)} paris dont {nv} à 50-50 ({nv/len(bets):.1%}) ; avec 50-50 {m*100:+.1f} % (t {v['confiance_evenements']}, z prix {v['z_prix']}) ; sans {m0*100:+.1f} % ; {won} gagnés / {exp:.1f} attendus")
print("événements avec échanges", len(tr), "fourchette", LO, HI)
for d in DELAYS: line(f"-{d} h tous sports", [r for r in rows if r["d"] == d])
print("== PAR GROUPE (-1 h … -24 h cumulés ne sont pas indépendants : un délai à la fois) ==")
for d in DELAYS:
    for g in ("tennis", "esport", "autre"):
        line(f"-{d} h {g}", [r for r in rows if r["d"] == d and (GROUP.get(r["sport"], "autre") == g)])
print("== PAR LIGUE à -6 h ==")
by = collections.defaultdict(list)
for r in rows:
    if r["d"] == 6: by[r["sport"]].append(r)
for k, v in sorted(by.items(), key=lambda kv: -len(kv[1]))[:14]: line(k, v)
json.dump(rows, open("donnees/rows_outsiders.json", "w"))
