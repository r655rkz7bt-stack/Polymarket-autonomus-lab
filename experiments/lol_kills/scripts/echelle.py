"""27/10/2026 : cohérence des lignes d'une même partie (« Total Kills Over/Under X in Game N ») : 3 à 6 lignes par partie, donc P(Over L1) >= P(Over L2) si L1 < L2.
Pour une partie, avec L1 < L2 : acheter Over(L1) + Under(L2) coûte c et paie 1 (kills <= L1 ou >= L2... en fait au moins 1 des deux gagne toujours, 2 si L1 < kills < L2) :
si c + frais < 1, gain sûr >= 1 − c. On cherche les paires dont les deux prix réels sont observés dans la même fenêtre de 10 minutes avant le coup d'envoi.
Usage : python echelle.py [H=3]"""
import json, sys, collections
sys.path.insert(0, "experiments/lol_kills/scripts")
import analyse as A
H = float(sys.argv[1]) if len(sys.argv) > 1 else 3
ms = [json.loads(l) for l in open(A.MARCHES)]
par = collections.defaultdict(list)
for m in ms:
    if m["debut"] and m["jeu"]: par[(m["event"], m["jeu"])].append(m)
paires = []; vus = 0
for (ev, g), lst in par.items():
    if len(lst) < 2: continue
    rows = {m["id"]: A.charge(m) for m in lst}
    s = A.ts(lst[0]["debut"])
    for fen in range(int(H * 3600), 0, -600):  # fenêtres de 10 minutes jusqu'au coup d'envoi
        t0 = s - fen; fin = t0 + 600
        px = {}
        for m in lst:
            if rows[m["id"]]:
                o = A.achat(rows[m["id"]], m["over"], m["under"], t0, fin); u = A.achat(rows[m["id"]], m["under"], m["over"], t0, fin)
                if o and u: px[m["id"]] = (o[1], u[1])
        for a in lst:
            for b in lst:
                if a["ligne"] < b["ligne"] and a["id"] in px and b["id"] in px:
                    c = px[a["id"]][0] + px[b["id"]][1]
                    fee = a["taux"] * px[a["id"]][0] * (1 - px[a["id"]][0]) + b["taux"] * px[b["id"]][1] * (1 - px[b["id"]][1])
                    vus += 1
                    if c + fee < 0.99:
                        res_a = 1.0 if a["res"] == "Over" else 0.5 if a["res"] == "50-50" else 0.0
                        res_b = 1.0 if b["res"] == "Under" else 0.5 if b["res"] == "50-50" else 0.0
                        paires.append((ev, g, a["ligne"], b["ligne"], round(c, 3), round(fee, 3), res_a + res_b, fen))
print("paires comparables", vus, "; paires avec coût + frais < 0,99 :", len(paires))
for p in paires[:15]: print(p)
if paires:
    print("gain moyen (paie - coût - frais) :", sum(p[6] - p[4] - p[5] for p in paires) / len(paires))
