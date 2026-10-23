"""Un favori à 0,94-0,985 acheté d heures après le coup d'envoi (premier échange preneur dans les 30 min) : gagné plus souvent que son prix ?
Règlement : marchés réglés net à 1/0. Frais : barème du marché. Un seul pari par événement (le premier acheté), comme apres_echeance corrigé."""
import bisect, json, sys, datetime, collections, math, os
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
LO, HI = float(os.environ.get("LO", 0.94)), float(os.environ.get("HI", 0.985))
ev = [json.loads(l) for l in open("donnees/events.jsonl")]
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["event"]] = o["trades"]
jl = lambda x: json.loads(x) if isinstance(x, str) else x
DELAYS = [1, 2, 3, 4, 6, 8]
rows = []  # un enregistrement par (événement, délai) : le premier achat éligible
legs_all = collections.defaultdict(list)
for e in ev:
    if e["id"] not in tr: continue
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    srt = sorted(tr[e["id"]]); times = [t[0] for t in srt]
    cands = []
    for m in e["markets"]:
        try:
            pr = [str(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"]); outs = jl(m["outcomes"])
        except Exception: continue
        if len(toks) != 2 or sorted(pr) != ["0", "1"] or m.get("umaResolutionStatus") not in (None, "", "resolved"): continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
        for i in (0, 1):
            cands.append((m, toks[i], toks[1 - i], 1 if pr[i] == "1" else 0, rate, m.get("sportsMarketType") or "autre"))
    for d in DELAYS:
        lo_t, hi_t = start + d * 3600, start + d * 3600 + 1800
        best = None
        for m, tok, oth, won, rate, typ in cands:
            i0 = bisect.bisect_left(times, lo_t); i1 = bisect.bisect_right(times, hi_t)
            pts = []
            for t in srt[i0:i1]:
                if t[1] == tok and t[2] == "BUY": pts.append((t[0], t[3]))
                elif t[1] == oth and t[2] == "SELL": pts.append((t[0], 1 - t[3]))
            pts.sort()
            if not pts: continue
            ts_, p = pts[0]
            if not LO <= p <= HI: continue
            g = (won - p - fee(p, rate)) / p   # rendement par euro misé
            rec = {"evenement": e["id"], "sport": e["sport"], "d": d, "cout": p, "gain": g, "ts": ts_, "typ": typ, "won": won, "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")}
            legs_all[d].append(rec)
            if best is None or ts_ < best["ts"]: best = rec
        if best: rows.append(best)
def line(label, bets):
    if not bets: print(f"{label}: 0 paris"); return
    won = sum(b["won"] for b in bets); exp = sum(b["cout"] for b in bets)
    mean = sum(b["gain"] for b in bets) / len(bets)
    v = verdict(bets, min_bets=30)
    print(f"{label}: {len(bets)} paris, {won} gagnés / {exp:.1f} attendus, rendement {mean*100:+.1f} %, t événement {v['confiance_evenements']}, z prix {v['z_prix']}, verdict {v['verdict']}")
print("événements avec échanges", len(tr), "fourchette", LO, HI)
print("== UN PARI PAR ÉVÉNEMENT (le premier acheté) ==")
for d in DELAYS: line(f"+{d} h", [r for r in rows if r["d"] == d])
print("== TOUTES LES JAMBES ==")
for d in DELAYS: line(f"+{d} h", legs_all[d])
print("== PAR SPORT (un pari par événement, +3 h et plus) ==")
by = collections.defaultdict(list)
for r in rows:
    if r["d"] >= 3: by[r["sport"]].append(r)
for k, v in sorted(by.items(), key=lambda kv: -len(kv[1])): line(k, v)
print("== PAR TYPE DE PARI (+3 h et plus, toutes jambes) ==")
byt = collections.defaultdict(list)
for d in DELAYS:
    if d >= 3:
        for r in legs_all[d]: byt[r["typ"]].append(r)
for k, v in sorted(byt.items(), key=lambda kv: -len(kv[1])): line(k, v)
json.dump(rows, open("donnees/rows.json", "w"))
