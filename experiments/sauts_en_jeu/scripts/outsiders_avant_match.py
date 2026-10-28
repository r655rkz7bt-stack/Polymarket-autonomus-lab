"""Outsiders avant le match, tennis et e-sport (28/10/2026) : à T = coup d'envoi − Δ, on achète le côté dont le prix est < 0,5 (un pari par match ; COTE=favoris : le côté ≥ 0,5), au prix du premier échange de
preneur dans l'heure qui suit (frais du marché inclus). Même données que analyse.py. Règlements 50-50 comptés à 0,5 (INCLURE_50_50) ou écartés."""
import sys, math, os, json
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
from polymarket_agent import idea_test as it
INCL = os.environ.get("INCLURE_50_50") == "1"
FAV = os.environ.get("COTE") == "favoris"
BANDS = [(0.55, 0.65), (0.65, 0.80), (0.80, 0.90), (0.90, 0.97)] if FAV else [(0.05, 0.10), (0.10, 0.20), (0.20, 0.30), (0.30, 0.45)]
def run(MS, delta, side_mode="outsider"):
    res = []
    for M in MS:
        prs = M["prs"]
        if sorted(prs) == [0.0, 1.0]: pay = prs
        elif INCL and sorted(prs) == [0.5, 0.5]: pay = prs
        else: continue
        T = M["start"] - delta * 3600
        p0 = a.price_at(M, T, fresh=3 * 3600)
        if p0 is None: continue
        buy0 = (p0 >= 0.5) if FAV else (p0 < 0.5)
        tok, oth = (M["toks"][0], M["toks"][1]) if buy0 else (M["toks"][1], M["toks"][0])
        c = it.taker_cost(M["trades"], tok, oth, T, window=3600, after=True)
        if c is None or c < 0.03 or c > 0.97: continue
        rate = (M["m"].get("feeSchedule") or {}).get("rate") if M["m"].get("feesEnabled") else 0
        cost = c + it.fee(c, rate or 0)
        py = pay[0 if buy0 else 1]
        res.append(dict(evenement=M["e"]["id"], mois=__import__("datetime").datetime.fromtimestamp(T, __import__("datetime").timezone.utc).strftime("%Y-%m"), cout=c,
                        win=py == 1.0, pay=py, gain=(py - cost) / cost, sport=M["e"]["sport"]))
    return res
def fmt(r):
    if not r: return "0 cas"
    n = len(r); ex = sum(x["cout"] for x in r); w = sum(x["pay"] for x in r)
    var = sum(x["cout"] * (1 - x["cout"]) for x in r)
    v = it.verdict(r)
    return f"n={n:4d} gagnés={w:6.1f} attendus={ex:6.1f} z={(w-ex)/math.sqrt(var):+.2f} rendement={100*sum(x['gain'] for x in r)/n:+.1f}% t_event={v['confiance_evenements']:+.2f} {v['verdict']}"
if __name__ == "__main__":
    for group in (("atp", "wta"), ("cs2", "lol", "dota2", "val")):
        MS = a.load(group)
        print(group, len(MS), "matchs", flush=True)
        for delta in (1, 3, 6, 12):
            r = run(MS, delta)
            print(f"  H-{delta:2d} tous outsiders", fmt(r), flush=True)
            for lo, hi in BANDS:
                print(f"       prix {lo:.2f}-{hi:.2f}", fmt([x for x in r if lo <= x["cout"] < hi]), flush=True)
