"""Piste n° 9 (lissage_tranches), sur les mêmes données : une tranche dont le prix OUI fait un creux (moins que ses deux
voisines) ou un pic isolé (plus que ses deux voisines sans être la plus chère de l'événement) est-elle mal cotée ?
Tranches ordonnées par le premier nombre de leur libellé ; événements d'au moins 6 tranches numérotées ; prix à T-72 h."""
import json, math, re, sys, datetime as dt
from collections import defaultdict
sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict
ev = {e["id"]: e for e in json.load(open("experiments/queues_tranches/donnees/evenements.json"))}
px = {}
for l in open("experiments/queues_tranches/donnees/prix.jsonl"):
    r = json.loads(l); px[r["market"]] = r
HRS = int(sys.argv[1]) if len(sys.argv) > 1 else 72
# 22/10 : des « pics » à 0,49-0,50 étaient des carnets VIDES (le CLOB affiche le milieu 0,50) : 1 gagnant sur 69 ; on écarte 0,44-0,56.
EXCLURE_MILIEU = (0.44, 0.56) if "--garder-milieu" not in sys.argv else (2, 3)
def num(m):
    s = (m.get("item") or m.get("q") or "").replace(",", "")
    g = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(g.group()) if g else None
def price(r):
    ts = r["end"] - HRS * 3600
    pts = [(t, p) for t, p in r["hist"] if t <= ts]
    return pts[-1][1] if pts and ts - pts[-1][0] <= 6 * 3600 else None
dips, spikes, n_ev = [], [], 0
for e in ev.values():
    ms = [(num(m), m) for m in e["markets"] if m["id"] in px and px[m["id"]]["final"] in (0.0, 1.0)]
    if len(ms) < 6 or any(n is None for n, _ in ms) or len(ms) != len(e["markets"]): continue
    ms.sort(key=lambda x: x[0])
    ps = [price(px[m["id"]]) for _, m in ms]
    if any(p is None for p in ps) or sum(px[m["id"]]["final"] for _, m in ms) != 1: continue
    n_ev += 1
    top = max(range(len(ps)), key=lambda i: ps[i])
    month = dt.datetime.fromtimestamp(px[ms[0][1]["id"]]["end"], dt.timezone.utc).strftime("%Y-%m")
    for i in range(1, len(ps) - 1):
        p, a, b = ps[i], ps[i - 1], ps[i + 1]
        yes = int(px[ms[i][1]["id"]]["final"] == 1.0)
        if 0.03 <= p <= 0.30 and p < 0.6 * min(a, b) and i != top and not (EXCLURE_MILIEU[0] <= min(a, b) <= EXCLURE_MILIEU[1]):
            dips.append(dict(p=p, yes=yes, ev=e["id"], month=month))
        if 0.05 <= p <= 0.70 and p > 1.6 * max(a, b) and i != top and not (EXCLURE_MILIEU[0] <= p <= EXCLURE_MILIEU[1]):
            spikes.append(dict(p=p, yes=yes, ev=e["id"], month=month))
print(n_ev, "événements ordonnés complets")
def report(name, cs):
    if not cs: print(name, "aucun"); return
    w = sum(c["yes"] for c in cs); ex = sum(c["p"] for c in cs); var = sum(c["p"] * (1 - c["p"]) for c in cs)
    print(f"{name}: {len(cs)} cas, {len({c['ev'] for c in cs})} événements, OUI gagnés {w} pour {ex:.1f} attendus (z {(w-ex)/math.sqrt(var):+.2f})")
report("creux (OUI à moins de 0,6 × la plus basse voisine)", dips)
report("pic isolé (OUI à plus de 1,6 × la plus haute voisine, pas le favori)", spikes)
for sp in (0.01, 0.02):
    bets = []
    for c in dips:   # achat du OUI du creux
        cost = c["p"] + sp; cost += 0.0
        bets.append(dict(gain=c["yes"] / cost - 1, evenement=c["ev"], mois=c["month"], cout=cost))
    v = verdict(bets); print(f"achat OUI des creux, écart {sp}: {v['paris']} paris rend {v.get('rendement_moyen')} t évts {v.get('confiance_evenements')} -> {v['verdict']}")
    bets = [dict(gain=(0 if c["yes"] else 1) / (1 - c["p"] + sp) - 1, evenement=c["ev"], mois=c["month"], cout=1 - c["p"] + sp) for c in spikes]
    v = verdict(bets); print(f"achat NON des pics, écart {sp}: {v['paris']} paris rend {v.get('rendement_moyen')} t évts {v.get('confiance_evenements')} -> {v['verdict']}")
