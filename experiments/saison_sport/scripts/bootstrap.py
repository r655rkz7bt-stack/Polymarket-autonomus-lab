"""Bootstrap par événement (2 000 tirages) du NON à 0,10-0,30 à 7, 14 et 30 jours, sport et hors sport : probabilité que le rendement moyen soit ≤ 0.
(Un test par permutation du gagnant dans l'événement a été essayé puis écarté : son hypothèse « gagnant tiré au hasard » n'est pas « les prix sont justes ».)"""
import json, random, os
from polymarket_agent.idea_test import fee
random.seed(7)
def load(nom):
    ev = {e["id"]: e for e in json.load(open(f"donnees/evenements{nom}.json"))}
    mk = {m["id"]: (m, e) for e in ev.values() for m in e["markets"]}
    cases = {}
    for l in open(f"donnees/prix{nom}.jsonl"):
        r = json.loads(l)
        pts = [p for p in r["hist"] if p[0] <= r["t"]]
        if not pts or r["t"] - pts[-1][0] > 43200 or not 0.10 <= pts[-1][1] < 0.30: continue
        m, e = mk[r["id"]]
        cases.setdefault((r["h"], e["id"]), []).append((pts[-1][1], bool(m["yes_won"]), float(m["fee"] or 0), m["id"]))
    return cases
def mean_gain(items, perm=False):
    g = []
    for evid, lst in items:
        wins = [y for _, y, _, _ in lst]
        if perm: random.shuffle(wins)   # le gagnant est tiré au hasard parmi les candidats de l'événement (nombre de OUI conservé)
        for (p, _, rate, _), y in zip(lst, wins):
            pay = 1 - p + 0.01; c = pay + fee(pay, rate); g.append(((0 if y else 1) - c) / c)
    return sum(g) / len(g) if g else 0
for nom, label in (("", "sport"), ("_candidats", "hors sport")):
    cases = load(nom)
    for h in (7, 14, 30):
        items = [(k[1], v) for k, v in cases.items() if k[0] == h]
        if len(items) < 10: continue
        obs = mean_gain(items)
        boots = []
        for _ in range(2000):
            samp = [random.choice(items) for _ in items]; boots.append(mean_gain(samp))
        print(f"{label:10} H={h:>2} n_ev={len(items)} rend {obs:+.3f}  P(bootstrap ≤ 0) = {sum(b <= 0 for b in boots)/len(boots):.3f}")
