"""NON des candidats à 0,10-0,30 (marchés de gagnant de saison) : un seul horizon à la fois, paris regroupés par événement,
par année, sans les 3 meilleurs événements, selon l'écart. Usage : PYTHONPATH=../../src python scripts/analyse2.py"""
import json, collections, math
from datetime import datetime, timezone
from polymarket_agent.idea_test import verdict, fee
ev = {e["id"]: e for e in json.load(open("donnees/evenements.json"))}
mk = {m["id"]: (m, e) for e in ev.values() for m in e["markets"]}
rows = [json.loads(l) for l in open("donnees/prix.jsonl")]
def dec(r):
    pts = [p for p in r["hist"] if p[0] <= r["t"]]
    return pts[-1][1] if pts and r["t"] - pts[-1][0] <= 43200 else None
cases = []
for r in rows:
    p = dec(r)
    if p is None: continue
    m, e = mk[r["id"]]
    cases.append({"h": r["h"], "p": p, "yes": m["yes_won"], "ev": e["id"], "title": e["title"], "rate": float(m["fee"] or 0),
                  "an": datetime.fromtimestamp(r["t"], timezone.utc).strftime("%Y"), "mois": datetime.fromtimestamp(r["t"], timezone.utc).strftime("%Y-%m")})
def run(h, lo, hi, sp, only=None, drop=0):
    b = []
    for c in cases:
        if c["h"] != h or not lo <= c["p"] < hi or (only and c["an"] != only): continue
        pay = min(0.99, 1 - c["p"] + sp); cost = pay + fee(pay, c["rate"])
        b.append({"gain": ((0.0 if c["yes"] else 1.0) - cost) / cost, "evenement": c["ev"], "mois": c["mois"], "cout": pay, "win": not c["yes"], "t": c["title"]})
    if drop:
        tot = collections.defaultdict(float)
        for x in b: tot[x["evenement"]] += x["gain"]
        top = {k for k, _ in sorted(tot.items(), key=lambda kv: -kv[1])[:drop]}
        b = [x for x in b if x["evenement"] not in top]
    if len(b) < 20: return None
    v = verdict(b)
    return len(b), len({x["evenement"] for x in b}), v["rendement_moyen"], v["confiance_evenements"], v["verdict"], sum(x["win"] for x in b), sum(x["cout"] for x in b)
n = 0
for h in (7, 14, 30):
    for lo, hi in ((0.10, 0.20), (0.10, 0.30), (0.15, 0.30)):
        for sp in (0.01, 0.02):
            for only, drop in ((None, 0), (None, 3), ("2025", 0), ("2026", 0)):
                r = run(h, lo, hi, sp, only, drop); n += 1
                if r: print(f"H={h:>2} p {lo:.2f}-{hi:.2f} écart {sp} {only or 'tous'} sans top{drop}: n={r[0]} ev={r[1]} rend {r[2]:+.3f} t_ev {r[3]:+.2f} gagnés {r[5]} / {r[6]:.1f} -> {r[4]}")
print("réglages", n)
