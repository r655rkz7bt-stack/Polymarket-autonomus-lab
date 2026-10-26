"""27/10/2026 : « acheter le favori d'un match avant le coup d'envoi » sur un ÉCHANTILLON ALÉATOIRE de marchés « vainqueur du match » du relevé complet
(releve_complet.py ; releve_echanges_ml.py : 6 000 marchés tirés avec une graine fixe parmi 59 760 > 2 000 $). Pour chaque marché et chaque délai d (1, 3, 6, 12, 24 h avant le
coup d'envoi) : premier échange preneur dans les 30 minutes qui suivent la décision, pour chaque issue ; on achète le FAVORI (prix le plus haut) s'il vaut 0,55-0,97 ;
frais du marché ; règlements 0,5-0,5 comptés 0,5. Un pari par (marché, délai). Lancer depuis la racine ; sortie : lignes de résultats + donnees/paris_favoris.json."""
import json, sys, glob, datetime, collections
sys.path.insert(0, "src")
from polymarket_agent.idea_test import fee, verdict
D = "experiments/totaux_sports/donnees"
jl = lambda x: json.loads(x) if isinstance(x, str) else x
DELAYS = [1, 3, 6, 12, 24]
COUPE = datetime.datetime(2026, 8, 15, tzinfo=datetime.timezone.utc).timestamp()
GROUPES = {"tennis": {"atp", "wta", "itf"}, "esport": {"cs2", "lol", "dota2", "val"}, "basket": {"nba", "wnba", "euroleague", "ncaab", "cbb"},
           "football US": {"nfl", "cfb"}, "baseball": {"mlb", "npb", "kbo"}, "hockey": {"nhl", "ahl", "khl"}}
def groupe(sport):
    return next((g for g, s in GROUPES.items() if sport in s), "football")
info = {}
for l in open(f"{D}/totaux_complet.jsonl"):
    e = json.loads(l)
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    for m in e["markets"]:
        if m["sportsMarketType"] != "moneyline" or m.get("umaResolutionStatus") != "resolved": continue
        try:
            pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: continue
        if len(toks) != 2 or not (sorted(pr) == [0.0, 1.0] or pr == [0.5, 0.5]): continue
        fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
        info[m["conditionId"]] = (e["id"], e["sport"], start, toks, pr, float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0)
rows, n = [], 0
for f in sorted(glob.glob(f"{D}/echanges_ml_*.jsonl")):
    for l in open(f):
        o = json.loads(l)
        if o["m"] not in info: continue
        ev, sport, start, toks, pay, rate = info[o["m"]]
        n += 1
        for d in DELAYS:
            lo, hi = start - d * 3600, start - d * 3600 + 1800
            px = []
            for i in (0, 1):
                pts = sorted([(t[0], t[3]) for t in o["trades"] if lo <= t[0] <= hi and t[1] == toks[i] and t[2] == "BUY"]
                             + [(t[0], 1 - t[3]) for t in o["trades"] if lo <= t[0] <= hi and t[1] == toks[1 - i] and t[2] == "SELL"])
                px.append(pts[0] if pts else None)
            ok = [i for i in (0, 1) if px[i] is not None]
            if not ok: continue
            i = max(ok, key=lambda j: px[j][1])      # le favori du marché ; l'autre issue n'est pas jouée
            p = px[i][1]
            if not 0.55 <= p <= 0.97: continue
            rows.append({"evenement": ev, "sport": sport, "groupe": groupe(sport), "d": d, "cout": p, "won": pay[i], "start": start,
                         "gain": (pay[i] - p - fee(p, rate)) / p,
                         "mois": datetime.datetime.fromtimestamp(px[i][0], datetime.timezone.utc).strftime("%Y-%m")})
print(n, "marchés avec échanges,", len(rows), "paris", flush=True)
json.dump(rows, open(f"{D}/paris_favoris.json", "w"))
def line(label, bets, mini=30):
    if len(bets) < mini: return
    m = sum(b["gain"] for b in bets) / len(bets); v = verdict(bets, min_bets=30)
    print(f"{label:46} {len(bets):5d} paris  {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {sum(b['won'] for b in bets):.0f}/{sum(b['cout'] for b in bets):.0f}")
BANDES = [(0.55, 0.70), (0.70, 0.80), (0.80, 0.85), (0.85, 0.875), (0.875, 0.90), (0.90, 0.95), (0.95, 0.97)]
print("== tous sports, par délai et tranche de prix ==")
for d in DELAYS:
    for lo, hi in BANDES:
        line(f"-{d} h  {lo:.3f}-{hi:.3f}", [r for r in rows if r["d"] == d and lo <= r["cout"] < hi])
print("== 0,80-0,95, par groupe de sport, par délai ==")
for g in list(GROUPES) + ["football"]:
    for d in (1, 3, 6, 12):
        line(f"{g} -{d} h", [r for r in rows if r["groupe"] == g and r["d"] == d and 0.80 <= r["cout"] < 0.95], 20)
print("== 0,85-0,875 (la tranche de nf_sport_patiente_prix_850_875), par délai et période ==")
for d in DELAYS:
    for per, f in (("février-août", lambda r: r["start"] < COUPE), ("août-octobre", lambda r: r["start"] >= COUPE)):
        line(f"-{d} h {per}", [r for r in rows if r["d"] == d and 0.85 <= r["cout"] < 0.875 and f(r)], 20)
