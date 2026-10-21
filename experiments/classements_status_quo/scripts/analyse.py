"""Le leader d'un classement garde-t-il sa place plus souvent que son prix ne le dit ?
Pour chaque événement, à J-k avant la fin : le marché 'Oui' au prix le plus haut (le leader) ; il a gagné ou non (prix final 1).
Contrôle de règlement : exactement un 'Oui' à 1 par événement (sinon l'événement est écarté).
Prix historique (CLOB, pas de 12 h) : PAS exécutable ; la vérification aux vrais échanges vient après."""
import json, math, statistics, sys
from datetime import datetime
D = "donnees"
ev = json.load(open(f"{D}/events.json")); H = json.load(open(f"{D}/hist.json"))
ts = lambda s: int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
def at(hist, t):
    last = None
    for a, p in hist:
        if a > t: break
        last = p
    return last
rows, bad = [], 0
for o in ev:
    wins = [m for m in o["markets"] if m["final"] > 0.99]
    if len(wins) != 1: bad += 1; continue
    if not o["end"]: bad += 1; continue
    end = ts(o["end"])
    for k in (30, 14, 7, 3, 1):
        t = end - k * 86400
        if o["start"] and ts(o["start"]) > t: continue
        px = [(at(H.get(m["tok"], []), t), m) for m in o["markets"] if H.get(m["tok"])]
        px = [(p, m) for p, m in px if p is not None]
        if len(px) < 3: continue
        px.sort(key=lambda x: -x[0])
        p, m = px[0]
        rows.append({"fam": o["fam"], "ev": o["slug"], "k": k, "p": p, "win": m["final"] > 0.99, "name": m["name"], "end": o["end"][:10],
                     "second": px[1][0], "somme": sum(x[0] for x in px)})
print("événements", len(ev), "écartés (règlement non unique)", bad, "lignes", len(rows))
def tr(p):  # rendement d'un achat du leader à p+0,01 de spread (frais ignorés pour ce premier regard)
    return None
def resume(sel, label):
    if len(sel) < 5: return
    n = len(sel); w = sum(r["win"] for r in sel); e = sum(r["p"] for r in sel)
    var = sum(r["p"] * (1 - r["p"]) for r in sel)
    z = (w - e) / math.sqrt(var) if var > 0 else 0
    ret = [(1.0 if r["win"] else 0) / min(0.999, r["p"] + 0.01) - 1 for r in sel]
    print(f"{label:34s} n={n:3d} gagnés={w:3d} attendus={e:5.1f} z={z:+.2f} rendement moyen={statistics.mean(ret):+.3f}")
for fam in sorted({r["fam"] for r in rows}):
    for k in (30, 14, 7, 3, 1):
        resume([r for r in rows if r["fam"] == fam and r["k"] == k], f"{fam} J-{k}")
print()
for k in (30, 14, 7, 3, 1):
    resume([r for r in rows if r["k"] == k], f"TOUTES J-{k}")
    resume([r for r in rows if r["k"] == k and r["p"] >= 0.5], f"TOUTES J-{k}, p>=0,5")
    resume([r for r in rows if r["k"] == k and r["p"] < 0.5], f"TOUTES J-{k}, p<0,5")
json.dump(rows, open(f"{D}/lignes.json", "w"))
