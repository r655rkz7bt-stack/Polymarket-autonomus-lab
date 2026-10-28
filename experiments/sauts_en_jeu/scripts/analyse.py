"""Sauts de prix en match, tennis et e-sport (28/10/2026). Prix = échanges réels des preneurs (data-api). Saut = variation >= J du prix du joueur 1 en
`back` secondes, mesuré APRÈS le coup d'envoi (gameStartTime), prix de moins de 4 min. Un seul saut par match (le premier). Entrée = prix du premier échange
de preneur dans les 5 min qui suivent (saut + délai), plus les frais du marché. Contrarien : on achète le côté qui vient de BAISSER ; suiveur : l'inverse.
Aucun regard vers le futur. Règlement : prix final 1/0 (50-50 écartés ET comptés à part)."""
import json, gzip, sys, math, bisect, datetime as dt, collections
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent import idea_test as it
D = Path("experiments/sauts_en_jeu/donnees")
def parse(s):
    s = s.replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s).timestamp())
def load(sports):
    out = []
    for e in json.load(open(D / "evenements.json")):
        if e["sport"] not in sports: continue
        p = D / "echanges" / f"{e['id']}.json.gz"
        if not p.exists(): continue
        trades = json.loads(gzip.decompress(p.read_bytes()))
        m = e["markets"][0]
        try: toks = json.loads(m["clobTokenIds"]); prs = [float(x) for x in json.loads(m["outcomePrices"])]
        except Exception: continue
        if len(toks) != 2 or not trades: continue
        try: start = parse(m.get("gameStartTime") or e["start"])
        except Exception: continue
        pts = sorted((t[0], t[3] if t[1] == toks[0] else 1 - t[3]) for t in trades if t[1] in toks)
        if len(pts) < 20: continue
        out.append(dict(e=e, m=m, toks=toks, prs=prs, start=start, trades=trades, pts=pts, times=[p[0] for p in pts]))
    return out
def price_at(M, t, fresh=240):
    i = bisect.bisect_right(M["times"], t) - 1
    if i < 0 or t - M["times"][i] > fresh: return None
    return M["pts"][i][1]
def run(MS, J, back, delay, side, maxmin, pmin=0.0, pmax=1.0, W=300):
    res = []
    for M in MS:
        prs = M["prs"]
        if sorted(prs) != [0.0, 1.0]: continue
        found = None
        for minute in range(max(back // 60, 1), maxmin + 1):
            t = M["start"] + minute * 60
            a = price_at(M, t); b = price_at(M, t - back)
            if a is None or b is None: continue
            if abs(a - b) >= J: found = (t, a - b, a, b); break
        if not found: continue
        t, dlt, pnow, pbef = found
        buy0 = (dlt < 0) if side == "contre" else (dlt > 0)
        tok, oth = (M["toks"][0], M["toks"][1]) if buy0 else (M["toks"][1], M["toks"][0])
        c = it.taker_cost(M["trades"], tok, oth, t + delay, window=W, after=True)
        if c is None or c < 0.03 or c > 0.97 or not (pmin <= c < pmax): continue
        rate = ((M["m"].get("feeSchedule") or {}).get("rate")) if M["m"].get("feesEnabled") else 0
        rate = rate or 0
        win = prs[0 if buy0 else 1] == 1.0
        cost = c + it.fee(c, rate)
        res.append(dict(evenement=M["e"]["id"], mois=dt.datetime.fromtimestamp(t, dt.timezone.utc).strftime("%Y-%m"), cout=c, win=win,
                        gain=((1.0 if win else 0.0) - cost) / cost, minute=(t - M["start"]) // 60, dlt=dlt, sport=M["e"]["sport"]))
    return res
def resume(res):
    n = len(res)
    if n == 0: return "0 cas"
    w = sum(r["win"] for r in res); ex = sum(r["cout"] for r in res); var = sum(r["cout"] * (1 - r["cout"]) for r in res)
    z = (w - ex) / math.sqrt(var) if var else 0
    v = it.verdict(res)
    return f"n={n:4d} gagnés={w:4d} attendus={ex:6.1f} z={z:+.2f} rendement={100*sum(r['gain'] for r in res)/n:+.1f}% t_event={v['confiance_evenements']:+.2f} {v['verdict']}"
if __name__ == "__main__":
    sports = sys.argv[1].split(",")
    maxmin = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    MS = load(sports)
    print(sports, "matchs chargés", len(MS), flush=True)
    for side in ("contre", "suiveur"):
        for J in (0.10, 0.15, 0.20, 0.30):
            for back, delay in ((300, 60), (300, 180), (900, 60)):
                r = run(MS, J, back, delay, side, maxmin)
                print(side, f"J={J} regard={back//60}min délai={delay//60}min", resume(r), flush=True)
