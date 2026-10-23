"""Détail du NON à 0,10-0,30 (H = 7 et 14 j) : par événement (les 8 plus gros gains/pertes), part du gain portée par les 5 meilleurs événements."""
import json, collections
from polymarket_agent.idea_test import fee
ev = {e["id"]: e for e in json.load(open("donnees/evenements.json"))}
mk = {m["id"]: (m, e) for e in ev.values() for m in e["markets"]}
tot = collections.defaultdict(lambda: [0, 0.0, 0, 0.0])
for l in open("donnees/prix.jsonl"):
    r = json.loads(l)
    if r["h"] not in (7, 14): continue
    pts = [p for p in r["hist"] if p[0] <= r["t"]]
    if not pts or r["t"] - pts[-1][0] > 43200 or not 0.10 <= pts[-1][1] < 0.30: continue
    m, e = mk[r["id"]]; pay = 1 - pts[-1][1] + 0.01; c = pay + fee(pay, float(m["fee"] or 0))
    a = tot[(e["title"].strip(), r["h"])]; a[0] += 1; a[1] += ((0 if m["yes_won"] else 1) - c) / c; a[2] += not m["yes_won"]; a[3] += pay
rows = sorted(tot.items(), key=lambda kv: -kv[1][1])
for (t, h), a in rows[:6] + rows[-6:]: print(f"{t[:48]:48} H={h:>2} n={a[0]} gain {a[1]:+.2f} gagnés {a[2]}/{a[3]:.1f}")
g = sum(a[1] for _, a in rows); top = sum(a[1] for _, a in rows[:5])
print("gain total", round(g, 2), "5 meilleurs (événement, horizon)", round(top, 2), "n", sum(a[0] for _, a in rows), "couples", len(rows))
