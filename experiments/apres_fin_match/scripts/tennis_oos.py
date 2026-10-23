"""Tennis en jeu, hors échantillon : favori à 0,80-0,95 à +15 / +30 min du coup d'envoi (premier échange preneur dans les 10 min), moneyline.
Matchs commencés à partir de AFTER (UTC). Même règle que experiments/tennis.md. Frais du barème du marché."""
import bisect, json, sys, datetime, collections, os
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
AFTER = datetime.datetime.fromisoformat(os.environ.get("AFTER", "2026-10-20T16:00:00+00:00")).timestamp()
BEFORE = os.environ.get("BEFORE")
ev = [json.loads(l) for l in open("donnees/events.jsonl")]
tr = {}
for l in open("donnees/echanges.jsonl"):
    o = json.loads(l); tr[o["event"]] = o["trades"]
jl = lambda x: json.loads(x) if isinstance(x, str) else x
out = collections.defaultdict(list)
for e in ev:
    if e["sport"] not in ("atp", "wta", "itf") or e["id"] not in tr: continue
    start = datetime.datetime.fromisoformat(e["start"]).timestamp()
    if start < AFTER or (BEFORE and start >= datetime.datetime.fromisoformat(BEFORE).timestamp()): continue
    srt = sorted(tr[e["id"]]); times = [t[0] for t in srt]
    for m in e["markets"]:
        if m.get("sportsMarketType") != "moneyline": continue
        pr = [str(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        if len(toks) != 2 or sorted(pr) != ["0", "1"]: continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
        for lag in (900, 1800):
            lo, hi = start + lag, start + lag + 600
            pts = []
            for t in srt[bisect.bisect_left(times, lo):bisect.bisect_right(times, hi)]:
                for i in (0, 1):
                    if t[1] == toks[i] and t[2] == "BUY": pts.append((t[0], i, t[3]))
                    elif t[1] == toks[1 - i] and t[2] == "SELL": pts.append((t[0], i, 1 - t[3]))
            if not pts: continue
            # favori = jeton au prix médian le plus haut dans la fenêtre
            mid = {i: sorted(p for _, j, p in pts if j == i) for i in (0, 1)}
            fav = max((i for i in (0, 1) if mid[i]), key=lambda i: mid[i][len(mid[i]) // 2])
            first = sorted(p for p in pts if p[1] == fav)[0]
            p = first[2]
            if not 0.80 <= p < 0.95: continue
            won = 1 if pr[fav] == "1" else 0
            out[lag].append({"evenement": e["id"], "cout": p, "gain": (won - p - fee(p, rate)) / p, "won": won, "mois": "2026-10", "sport": e["sport"]})
for lag, bets in out.items():
    won = sum(b["won"] for b in bets); exp = sum(b["cout"] for b in bets); v = verdict(bets, 30)
    print(f"+{lag//60} min: {len(bets)} paris, {won} gagnés / {exp:.1f} attendus, rendement {sum(b['gain'] for b in bets)/len(bets)*100:+.1f} %, t événement {v['confiance_evenements']}, z prix {v['z_prix']}, {dict(collections.Counter(b['sport'] for b in bets))}")
