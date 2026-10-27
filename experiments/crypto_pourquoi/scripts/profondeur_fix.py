"""28/10/2026 : profondeur de la règle R1 (NON de la tranche centrale à H−3/6) : parts de NON achetées par des preneurs à ≤ prix payé + 2 centimes dans l'heure qui suit l'instant de décision,
et rendement par seuil de profondeur (≥ 20, 50, 100, 200 parts). Même sélection que regle_fix.py (un pari par marché, le plus ancien des H−3/6). Usage : PYTHONPATH=src python profondeur_fix.py"""
import bisect, gzip, json, statistics, datetime as dt
from collections import defaultdict
from pathlib import Path
from polymarket_agent import idea_test as it
D = Path("experiments/contrer_crypto_passe/donnees"); SP = Path("experiments/crypto_pourquoi/donnees")
S = json.load(open(SP / "snaps_saison.json"))
mk = {}
for nom in ("marches_a.jsonl", "marches_e.jsonl"):
    for l in open(D / nom):
        m = json.loads(l); mk[m["id"]] = m
def ts(s):
    s = str(s or "").replace(" ", "T")
    if s.endswith("+00"): s += ":00"
    return int(dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp())
par = defaultdict(list)
for s in S:
    if s["kind"] == "between" and s["h"] in (3, 6) and s["pn"] is not None and 0.03 <= s["pn"] <= 0.45: par[s["id"]].append(s)
rows = []
for mid, v in par.items():
    s = max(v, key=lambda x: x["h"]); m = mk[mid]; end = ts(m["end"]); T = end - s["h"] * 3600
    tr = sorted(json.loads(gzip.decompress((D / "echanges" / f"{mid}.json.gz").read_bytes()))["echanges"])
    no = m["no"]; yes = m["yes"]
    achats = [(t[0], t[3] if t[1] == no else 1 - t[3], t[4]) for t in tr if (t[1] == no and t[2] == "BUY") or (t[1] == yes and t[2] == "SELL")]
    j = bisect.bisect_left([a[0] for a in achats], T)
    if j >= len(achats) or achats[j][0] > T + 3600: continue
    paid = achats[j][1]; first = achats[j][2]
    dispo = sum(a[2] for a in achats[j:] if a[0] <= T + 3600 and a[1] <= paid + 0.02)
    w = 1 - s["won"]; fee = s["rate"] * paid * (1 - paid)
    rows.append(dict(gain=(w - paid - fee) / paid, cout=paid, evenement=s["ev"], mois=s["mois"], gagne=w, premier=first, dispo=dispo))
print(len(rows), "paris ; taille du premier échange : médiane", round(statistics.median(r["premier"] for r in rows), 1), "parts ; parts achetées par les preneurs à ≤ prix + 2 c dans l'heure : médiane",
      round(statistics.median(r["dispo"] for r in rows), 1), "quartiles", [round(x, 1) for x in statistics.quantiles([r["dispo"] for r in rows], n=4)])
print("| profondeur dans l'heure | paris | évén. | rendement | t | gagnés/attendus |")
for seuil in (0, 20, 50, 100, 200, 400):
    b = [r for r in rows if r["dispo"] >= seuil]
    if len(b) < 15: continue
    v = it.verdict(b); g = sum(x["gagne"] for x in b); a = sum(x["cout"] for x in b)
    print(f"| ≥ {seuil} parts | {v['paris']} | {v['evenements']} | {v['rendement_moyen']:+.1%} | t évén. {v['confiance_evenements']:+.2f} | {g:g} / {a:.1f} (z {v['z_prix']:+.2f}) |")
print("mise en euros achetable médiane (parts × prix) :", round(statistics.median(r["dispo"] * r["cout"] for r in rows), 1), "€")
