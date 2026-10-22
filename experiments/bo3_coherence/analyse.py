"""Piste n° 4 : le prix du match (BO3/BO5) est-il cohérent avec le prix de la carte 1 (loi binomiale, cartes équiprobables) ?
Prix = dernier échange réel avant T0 = coup d'envoi − retard (A-équivalent : achat de A ou vente de B)."""
import json, sys, math, datetime as dt, bisect
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
M = json.load(open("experiments/bo3_coherence/donnees/matchs.json"))
def ts(s):
    try: return int(dt.datetime.fromisoformat(str(s).replace("Z", "+00:00").replace(" ", "T")).timestamp())
    except Exception: return None
def last_before(trades, tokA, tokB, t, win):
    pts = sorted((x[0], x[3] if x[1] == tokA else 1 - x[3]) for x in trades if x[1] in (tokA, tokB))
    sel = [p for w, p in pts if t - win <= w <= t]
    return sel[-1] if sel else None
def series(q, bo):
    if bo == 3: return q * q * (3 - 2 * q)
    return q ** 3 * (10 - 15 * q + 6 * q * q)
def inv(m, bo):
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if series(mid, bo) < m: lo = mid
        else: hi = mid
    return (lo + hi) / 2
def cases(delay_min, win_min=120):
    out = []
    for r in M:
        if r["bo"] not in (3, 5) or not r["start"]: continue
        st = ts(r["start"])
        if not st: continue
        t0 = st - delay_min * 60
        tm, tg = r["tm"], r["tg"]
        m = last_before(r["trades"], tm[0], tm[1], t0, win_min * 60)
        g = last_before(r["trades"], tg[0], tg[1], t0, win_min * 60)
        if m is None or g is None or not (0.02 < m < 0.98) or not (0.02 < g < 0.98): continue
        out.append(dict(r=r, m=m, g=g, a_won=1 - r["win_m"], bo=r["bo"], month=dt.datetime.utcfromtimestamp(st).strftime("%Y-%m")))
    return out
def ll(p, y): p = min(max(p, 1e-4), 1 - 1e-4); return -(y * math.log(p) + (1 - y) * math.log(1 - p))
def report(delay):
    C = cases(delay)
    if not C: print("aucun cas"); return
    lm = sum(ll(c["m"], c["a_won"]) for c in C) / len(C)
    ls = sum(ll(series(c["g"], c["bo"]), c["a_won"]) for c in C) / len(C)
    lq = sum(ll(0.5 * (c["m"] + series(c["g"], c["bo"])), c["a_won"]) for c in C) / len(C)
    gaps = [c["m"] - series(c["g"], c["bo"]) for c in C]
    print(f"retard {delay:>3} min : {len(C)} matchs, log-score match {lm:.4f} ; modèle (carte 1 → match) {ls:.4f} ; moyenne {lq:.4f} ; écart moyen |m − m*| {sum(abs(x) for x in gaps)/len(gaps):.3f}")
    for thr in (0.03, 0.05, 0.08):
        bets = []
        for c in C:
            fs = c["r"]["fs"] or {}; rate = float(fs.get("rate") or 0) if c["r"]["fees"] else 0.0
            d = c["m"] - series(c["g"], c["bo"])
            if abs(d) < thr: continue
            buyA = d < 0
            cost = (c["m"] if buyA else 1 - c["m"]) + 0.01
            fee = rate * cost * (1 - cost)
            won = c["a_won"] if buyA else 1 - c["a_won"]
            bets.append(dict(gain=(won - cost - fee) / (cost + fee), evenement=c["r"]["id"], mois=c["month"], cout=cost))
        v = verdict(bets) if bets else {"paris": 0, "verdict": "-"}
        if v["paris"]: print(f"   seuil {thr}: {v['paris']} paris, rendement {v['rendement_moyen']:+.3f}, t {v['confiance_evenements']:+.2f}, z prix {v['z_prix']:+.2f}, mois {v['mois_gagnants']}, {v['verdict']}")
if __name__ == "__main__":
    print(len(M), "matchs relevés,", sum(1 for r in M if r["bo"] in (3, 5)), "BO3/BO5")
    for d in (0, 30, 60, 180): report(d)
