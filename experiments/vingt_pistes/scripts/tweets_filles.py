"""Filles du compteur de tweets (piste n° 1, 21/10/2026) : lit les achats écrits par tweets_contre_marche.py
(donnees/xt/trades_<dispersion>_<marge>_<prix min>.json) et les découpe : sans NYC Mayor, Elon seul,
48 dernières heures, NON seul. Rendement = gain par euro misé (frais et écart déjà comptés)."""
import json, math, statistics as st, sys
from collections import defaultdict
from datetime import datetime
D = "donnees/xt"
fin = {e["slug"]: datetime.fromisoformat(e["fin"]) for e in json.load(open(f"{D}/marches.json"))}
def load(cfg):
    out = []
    for h, slug, hh, b, side, cost, q, gain in json.load(open(f"{D}/trades_{cfg}.json")):
        t = datetime.fromisoformat(hh + ":00:00+00:00")
        out.append(dict(h=h, slug=slug, t=t, b=b, side=side, cost=cost, q=q, gain=gain, left=(fin[slug] - t).total_seconds() / 3600))
    return out
def summ(rows, label):
    if len(rows) < 5: print(f"  {label:34} {len(rows)} achats"); return None
    g = [r["gain"] for r in rows]
    ev = defaultdict(list)
    for r in rows: ev[r["slug"]].append(r["gain"])
    pg = [st.mean(v) for v in ev.values()]
    tp = st.mean(pg) / st.stdev(pg) * math.sqrt(len(pg)) if len(pg) > 2 and st.stdev(pg) > 0 else float("nan")
    mo = defaultdict(list)
    for r in rows: mo[r["t"].strftime("%m")].append(r["gain"])
    months = " ".join(f"{k}:{st.mean(v):+.2f}" for k, v in sorted(mo.items()))
    # 3 plus gros gains retirés (par période)
    top = sorted(pg)[:-3]
    print(f"  {label:34} {len(g):5} achats, {len(pg):3} périodes | par achat {st.mean(g):+.3f} | par période {st.mean(pg):+.3f} (t {tp:+.2f}) | sans 3 meilleures périodes {st.mean(top):+.3f} | {months}")
    return st.mean(pg), tp
cfgs = sys.argv[1:] or ["12.0_0.03_0.1"]
for cfg in cfgs:
    print("réglage", cfg)
    T = load(cfg)
    summ(T, "toutes (référence)")
    summ([r for r in T if r["h"] != "NYCMayor"], "fille A : sans NYC Mayor")
    summ([r for r in T if r["h"] == "elonmusk"], "fille B : Elon seul")
    summ([r for r in T if r["left"] <= 48], "fille C : 48 dernières heures")
    summ([r for r in T if r["left"] > 48], "   (les 5 premiers jours)")
    summ([r for r in T if r["side"] == 1], "fille D : NON seulement")
    summ([r for r in T if r["side"] == 1 and r["h"] != "NYCMayor"], "A+D : NON sans NYC")
    summ([r for r in T if r["side"] == 1 and r["h"] != "NYCMayor" and r["left"] <= 48], "A+C+D")
    summ([r for r in T if r["h"] != "NYCMayor" and r["left"] <= 48], "A+C")
