"""Piste n° 1, suite : mêmes matchs, mêmes ajustements Poisson (1X2 + O/U 2,5), mais on teste les AUTRES lignes de buts
(O/U 0,5, 1,5, 3,5, 4,5, 5,5) et « les deux équipes marquent » du `-more-markets`, aux prix des vrais échanges.
usage : analyse_totaux.py [DECAL_h=3] [FENETRE_h=3]"""
import json, sys, re, math, collections, datetime as dt
sys.path.insert(0, "experiments/score_exact"); sys.path.insert(0, "src")
import analyse as A
from polymarket_agent import idea_test as it
DEC, FEN = A.DECAL, A.FEN
rows = []
stat = collections.Counter()
for e, m, mm, te, tm, tmm in A.charge():
    if len(tm) >= 10000 or len(tmm) >= 10000: continue
    ms = e["markets"]
    try: K = A.ts_of(ms[0]["gameStartTime"])
    except Exception: continue
    T0 = K - int(DEC * 3600)
    mt = re.match(r"Exact Score: (.+?) (\d+) - (\d+) (.+?)\?$", ms[0]["question"])
    if not mt: continue
    home, away = mt.group(1).strip(), mt.group(4).strip()
    px = {}
    for x in m["markets"]:
        if x.get("sportsMarketType") != "moneyline": continue
        g = (x.get("groupItemTitle") or "").strip(); tok = json.loads(x["clobTokenIds"])[0]
        lab = "draw" if "Draw" in g else "home" if g == home else "away" if g == away else None
        p = A.dernier(tm, tok, T0 - 6 * 3600, T0)
        if lab is None or p is None: break
        px[lab] = p
    if len(px) != 3: continue
    s = sum(px.values()); tgt = (px["home"] / s, px["draw"] / s, px["away"] / s)
    over = None
    for x in mm["markets"]:
        if x.get("sportsMarketType") == "totals" and str(x.get("line")) == "2.5":
            toks = json.loads(x["clobTokenIds"]); ov = A.dernier(tmm, toks[0], T0 - 6 * 3600, T0); un = A.dernier(tmm, toks[1], T0 - 6 * 3600, T0)
            if ov is not None and un is not None: over = ov / (ov + un)
    if over is None: stat["sans_ou25"] += 1; continue
    lh, la, resid = A.ajuster(tgt, over)
    ph, pa = A.grille(lh, la)
    mois = dt.datetime.fromtimestamp(K, dt.timezone.utc).strftime("%Y-%m")
    for x in mm["markets"]:
        typ = x.get("sportsMarketType")
        if typ == "totals": line = float(x.get("line")); 
        elif typ == "both_teams_to_score": line = None
        else: continue
        if typ == "totals" and str(x.get("line")) == "2.5": continue
        pr = json.loads(x["outcomePrices"])
        if sorted(pr) != ["0", "1"]: continue
        toks = json.loads(x["clobTokenIds"])
        if typ == "totals":
            p1 = sum(ph[i] * pa[j] for i in range(A.GRID) for j in range(A.GRID) if i + j > line)  # Over
            lab = f"O/U {line}"
        else:
            p1 = (1 - ph[0]) * (1 - pa[0]); lab = "BTTS"
        rate = float((x.get("feeSchedule") or {}).get("rate") or 0) if x.get("feesEnabled") else 0.0
        for k, (tok, other, pm) in enumerate(((toks[0], toks[1], p1), (toks[1], toks[0], 1 - p1))):
            c = it.taker_cost(tmm, tok, other, T0, window=int(FEN * 3600), after=True)
            if c is None or c <= 0.005 or c >= 0.995: continue
            got = pr[k] == "1"
            rows.append(dict(match=e["slug"], mois=mois, ligne=lab, cote=("1er" if k == 0 else "2e"), cout=c, modele=pm, gain_brut=1.0 if got else 0.0, fee=it.fee(c, rate)))
json.dump(rows, open(f"experiments/score_exact/donnees/totaux_{DEC:g}_{FEN:g}.json", "w"))
print(len(rows), "paris,", len({r["match"] for r in rows}), "matchs", dict(stat))
by = collections.defaultdict(list)
for r in rows: by[(r["ligne"], r["cote"])].append(r)
print("\n== Calibrage du modèle (moyenne des probabilités prévues contre fréquence) et rendement aux prix payés ==")
for k in sorted(by):
    v = by[k]; n = len(v)
    print(f"{k[0]:8s} {k[1]:4s} n={n:5d} modèle={sum(r['modele'] for r in v)/n:.3f} prix payé={sum(r['cout'] for r in v)/n:.3f} gagnés={sum(r['gain_brut'] for r in v)/n:.3f} rend={sum(r['gain_brut']/(r['cout']+r['fee'])-1 for r in v)/n:+.3f}")
print("\n== Modèle contre marché : achat si modèle − (prix + frais) > écart ==")
for ecart in (0.03, 0.05, 0.08):
    bets = [dict(gain=r["gain_brut"] / (r["cout"] + r["fee"]) - 1, evenement=r["match"], mois=r["mois"], cout=r["cout"]) for r in rows if (r["modele"] - r["cout"] - r["fee"]) > ecart]
    if bets:
        v = it.verdict(bets); print(f"écart {ecart:.2f}: n={v['paris']:5d} matchs={v['evenements']:4d} rend={v['rendement_moyen']:+.3f} t_ev={v['confiance_evenements']:+.2f} z_prix={v['z_prix']:+.2f} mois={v['mois_gagnants']} -> {v['verdict']}")
