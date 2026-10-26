"""27/10/2026 : biais « favori / outsider » des marchés de totaux, TOUTES les lignes (pas seulement la ligne principale) : pour chaque marché de totaux (relevé complet,
échanges réels), chaque côté (Over / Under) et chaque délai (3 h, 12 h avant le coup d'envoi), premier échange preneur dans les 30 minutes qui suivent la décision ;
les paris sont rangés par prix payé. Un pari par (marché, côté, délai), frais du marché, règlements 0,5-0,5 comptés 0,5. Lancer depuis la racine."""
import bisect, json, sys, glob, datetime
sys.path.insert(0, "src")
from polymarket_agent.idea_test import fee, verdict
D = "experiments/totaux_sports/donnees"
jl = lambda x: json.loads(x) if isinstance(x, str) else x
COUPE = datetime.datetime(2026, 8, 15, tzinfo=datetime.timezone.utc).timestamp()
TYPES = ("totals", "tennis_set_totals", "first_half_totals", "soccer_team_totals", "tennis_match_totals")
info = {}
for l in open(f"{D}/totaux_complet.jsonl"):
    e = json.loads(l)
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    for m in e["markets"]:
        if m["sportsMarketType"] not in TYPES or m.get("umaResolutionStatus") != "resolved": continue
        try:
            outs = jl(m["outcomes"]); pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if not (len(outs) == 2 and str(outs[0]).startswith("Over") and str(outs[1]).startswith("Under")) or len(toks) != 2: continue
        if not (sorted(pr) == [0.0, 1.0] or pr == [0.5, 0.5]): continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        info[m["conditionId"]] = (e["id"], e["sport"], start, toks, pr, float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0, m["sportsMarketType"])
rows = []
for f in sorted(glob.glob(f"{D}/echanges_complet_*.jsonl")):
    for l in open(f):
        o = json.loads(l)
        if o["m"] not in info: continue
        ev, sport, start, toks, pay, rate, ty = info[o["m"]]
        # prix « acheter le jeton i » = achat de i au prix p, ou vente de l'autre à 1 − p ; triés par heure
        series = []
        for i in (0, 1):
            series.append(sorted([(t[0], t[3]) for t in o["trades"] if t[1] == toks[i] and t[2] == "BUY"]
                                 + [(t[0], 1 - t[3]) for t in o["trades"] if t[1] == toks[1 - i] and t[2] == "SELL"]))
        keys = [[x[0] for x in s] for s in series]
        for d in (3, 12):
            lo, hi = start - d * 3600, start - d * 3600 + 1800
            for i in (0, 1):
                j = bisect.bisect_left(keys[i], lo)
                if j < len(keys[i]) and keys[i][j] <= hi:
                    p = series[i][j][1]
                    if not 0.03 <= p <= 0.97: continue
                    rows.append({"evenement": ev, "sport": sport, "ty": ty, "d": d, "side": "Over" if i == 0 else "Under", "cout": p, "won": pay[i], "start": start,
                                 "gain": (pay[i] - p - fee(p, rate)) / p,
                                 "mois": datetime.datetime.fromtimestamp(series[i][j][0], datetime.timezone.utc).strftime("%Y-%m")})
print(len(rows), "paris", flush=True)
json.dump(rows, open(f"{D}/paris_lignes.json", "w"))
BANDES = [(0.03, 0.15), (0.15, 0.30), (0.30, 0.45), (0.45, 0.55), (0.55, 0.70), (0.70, 0.85), (0.85, 0.97)]
def line(label, bets):
    if len(bets) < 30: return
    m = sum(b["gain"] for b in bets) / len(bets); v = verdict(bets, min_bets=30)
    print(f"{label:44} {len(bets):6d} paris  {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {sum(b['won'] for b in bets):.0f}/{sum(b['cout'] for b in bets):.0f}")
for per, f in (("février-août", lambda r: r["start"] < COUPE), ("août-octobre", lambda r: r["start"] >= COUPE)):
    for d in (3, 12):
        for lo, hi in BANDES:
            line(f"{per} -{d} h prix {lo:.2f}-{hi:.2f}", [r for r in rows if f(r) and r["d"] == d and lo <= r["cout"] < hi])
