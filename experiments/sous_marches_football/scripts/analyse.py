"""Piste « sous-marchés du football » (26/10/2026) : 1X2 (moneyline) et résultat à la mi-temps. À lancer depuis experiments/sous_marches_football/.
Un pari = un marché Oui/Non (victoire A, nul, victoire B), côté Oui ou Non, acheté au premier échange preneur dans les 30 minutes qui suivent
T − d (prix réel, frais du marché). Règlements 0,5-0,5 comptés 0,5. Un pari par (marché, délai, côté). Rôle : « nul » ou « equipe ».
PERIODE=avant : coups d'envoi avant le 15/08 ; PERIODE=apres : à partir du 15/08 ; sinon tout."""
import json, sys, datetime, collections, os
sys.path.insert(0, "../../src")
from polymarket_agent.idea_test import fee, verdict
jl = lambda x: json.loads(x) if isinstance(x, str) else x
tr = {}
for f in ("donnees/echanges.jsonl", "donnees/echanges_rev.jsonl"):
    if os.path.exists(f):
        for l in open(f):
            o = json.loads(l); tr[o["m"]] = o["trades"]
DELAYS = [int(x) for x in os.environ.get("DELAYS", "1,3,6,12,24").split(",")]
PER = os.environ.get("PERIODE", "")
CUT = int(datetime.datetime(2026, 8, 15, tzinfo=datetime.timezone.utc).timestamp())
rows = []; nev = 0; ecart = collections.Counter()
for l in open("donnees/events.jsonl"):
    e = json.loads(l)
    start = int(datetime.datetime.fromisoformat(e["start"]).timestamp())
    if PER == "avant" and start >= CUT: continue
    if PER == "apres" and start < CUT: continue
    mks = []
    for m in e["markets"]:
        if m["conditionId"] not in tr or m.get("umaResolutionStatus") != "resolved": ecart["sans échange/non réglé"] += 1; continue
        try:
            outs = jl(m["outcomes"]); pr = [float(p) for p in jl(m["outcomePrices"])]; toks = jl(m["clobTokenIds"])
        except Exception: ecart["illisible"] += 1; continue
        if outs != ["Yes", "No"] or len(toks) != 2: ecart["pas Oui/Non"] += 1; continue
        if sorted(pr) == [0.0, 1.0]: pay = pr
        elif pr == [0.5, 0.5]: pay = [0.5, 0.5]
        else: ecart["prix final étrange"] += 1; continue
        q = ((m.get("groupItemTitle") or "") + " " + (m.get("question") or "")).lower()
        mks.append((m, toks, pay, "nul" if "draw" in q else "equipe"))
    if len(mks) < 2: continue
    nev += 1
    for d in DELAYS:
        lo_t, hi_t = start - d * 3600, start - d * 3600 + 1800
        for m, toks, pay, role in mks:
            srt = tr[m["conditionId"]]
            fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
            rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
            for i, side in ((0, "Oui"), (1, "Non")):
                pts = sorted([(t[0], t[3], t[4]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[i] and t[2] == "BUY"]
                             + [(t[0], 1 - t[3], t[4]) for t in srt if lo_t <= t[0] <= hi_t and t[1] == toks[1 - i] and t[2] == "SELL"])
                if not pts: continue
                ts_, p, sz = pts[0]
                if not 0.05 <= p <= 0.95: continue
                rows.append({"evenement": e["id"], "sport": e["sport"], "ty": m["sportsMarketType"], "role": role, "d": d, "side": side, "cout": p,
                             "won": pay[i], "ts": ts_, "taille": sz, "gain": (pay[i] - p - fee(p, rate)) / p,
                             "mois": datetime.datetime.fromtimestamp(ts_, datetime.timezone.utc).strftime("%Y-%m")})
print("événements", nev, "paris", len(rows), "écartés", dict(ecart))
def line(label, bets):
    if len(bets) < 10: return
    m = sum(b["gain"] for b in bets) / len(bets)
    v = verdict(bets, min_bets=30)
    exp = sum(b["cout"] for b in bets); won = sum(b["won"] for b in bets)
    print(f"{label:46} {len(bets):5d} paris  {m*100:+6.1f} %  t/év {v['confiance_evenements']:+.2f}  z prix {v['z_prix']:+.2f}  gagnés {won:.0f}/{exp:.0f}")
for ty in ("moneyline", "soccer_halftime_result"):
    print("=====", ty)
    for role in ("nul", "equipe"):
        for side in ("Oui", "Non"):
            for d in DELAYS:
                line(f"{role} {side} -{d} h", [r for r in rows if r["ty"] == ty and r["role"] == role and r["side"] == side and r["d"] == d])
print("===== par bande de prix (1X2, -3 h)")
for role in ("nul", "equipe"):
    for side in ("Oui", "Non"):
        for lo, hi in [(.05, .15), (.15, .25), (.25, .35), (.35, .5), (.5, .65), (.65, .8), (.8, .95)]:
            line(f"{role} {side} prix {lo:.2f}-{hi:.2f}", [r for r in rows if r["ty"] == "moneyline" and r["role"] == role and r["side"] == side and r["d"] == 3 and lo <= r["cout"] < hi])
json.dump(rows, open("donnees/paris%s.json" % ("_" + PER if PER else ""), "w"))
