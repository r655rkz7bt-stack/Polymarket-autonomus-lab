"""Piste n° 17 : « battre ses résultats » : calibration du prix du OUI à T-k jours et achats simulés (prix du CLOB, à confirmer aux vrais échanges)."""
import json, sys, bisect, math, datetime as dt, collections
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
R = json.load(open("experiments/battre_resultats/donnees/earnings.json"))
def ts(s):
    try: return int(dt.datetime.fromisoformat(str(s).replace("Z", "+00:00").replace(" ", "T")).timestamp())
    except Exception: return None
def price_at(h, t, maxgap=12 * 3600):
    tt = [x[0] for x in h]; i = bisect.bisect_right(tt, t) - 1
    return h[i][1] if i >= 0 and t - tt[i] <= maxgap else None
def cases(days):
    out = []
    for r in R:
        e = ts(r["end"]); 
        if not e or not r["hist"]: continue
        p = price_at(r["hist"], e - days * 86400)
        if p is None or not 0.03 < p < 0.97: continue
        out.append((r, p))
    return out
print(len(R), "marchés réglés ;", f"taux de OUI {sum(r['won'] for r in R)/len(R):.3f}")
for days in (1, 3, 7):
    C = cases(days)
    print(f"--- prix du OUI à T-{days} j : {len(C)} marchés")
    bins = collections.defaultdict(list)
    for r, p in C:
        b = "< 0,50" if p < .5 else "0,50-0,65" if p < .65 else "0,65-0,80" if p < .8 else "0,80-0,90" if p < .9 else "≥ 0,90"
        bins[b].append((p, r["won"]))
    for b in ("< 0,50", "0,50-0,65", "0,65-0,80", "0,80-0,90", "≥ 0,90"):
        v = bins.get(b, [])
        if v: print(f"   {b:>10} : {len(v):>4} marchés, prix moyen {sum(p for p,_ in v)/len(v):.3f}, OUI réalisés {sum(w for _,w in v)/len(v):.3f}")
    for lo, hi, side in ((0.0, 0.65, "OUI"), (0.65, 0.80, "OUI"), (0.80, 0.90, "OUI"), (0.90, 1.0, "NON"), (0.0, 0.50, "OUI")):
        for sp in (0.01, 0.02):
            bets = []
            for r, p in C:
                if not lo <= p < hi: continue
                rate = float((r["fs"] or {}).get("rate") or 0) if r["fees"] else 0.0
                cost = (p if side == "OUI" else 1 - p) + sp
                fee = rate * cost * (1 - cost)
                won = r["won"] if side == "OUI" else 1 - r["won"]
                bets.append(dict(gain=(won - cost - fee) / (cost + fee), evenement=r["id"], mois=dt.datetime.utcfromtimestamp(ts(r["end"])).strftime("%Y-%m"), cout=cost))
            v = verdict(bets) if bets else None
            if v and v["paris"] >= 30: print(f"   {side} {lo:.2f}-{hi:.2f}, écart {sp}: {v['paris']} paris, rendement {v['rendement_moyen']:+.3f}, t {v['confiance_evenements']:+.2f}, z prix {v['z_prix']:+.2f}, mois {v['mois_gagnants']}, {v['verdict']}")
