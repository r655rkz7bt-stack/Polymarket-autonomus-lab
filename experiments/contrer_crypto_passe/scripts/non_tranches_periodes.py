"""28/10/2026 (passage 27/10 matin) : les tranches fortes du NON crypto à 0,10-0,45 se répètent-elles dans CHAQUE période séparée ?
Réutilise les fonctions de baseline_non.py (tout ce qui précède la ligne « Référence »). MARCHES=marches_2024.jsonl,marches_2025.jsonl,marches_2026.jsonl"""
import datetime as dt
src = open("experiments/contrer_crypto_passe/scripts/baseline_non.py").read().split("# Référence")[0]
exec(compile(src, "baseline_non", "exec"))
base = bets_for(0.10, 0.45, 0, base_side=1)
PER = (("2024-01 à 2025-12", "2024-01", "2025-12"), ("2026-01 à 2026-05", "2026-01", "2026-05"), ("2026-06 à 2026-10", "2026-06", "2026-10"))
TR = (("tous", lambda b: True), ("payé 0,10-0,20", lambda b: b["cout"] < 0.20), ("payé 0,20-0,30", lambda b: 0.20 <= b["cout"] < 0.30),
      ("payé 0,30-0,45", lambda b: b["cout"] >= 0.30), ("fin dans ≥ 96 h", lambda b: b["h"] >= 96), ("fin dans < 96 h", lambda b: b["h"] < 96),
      ("≥ 96 h et payé < 0,30", lambda b: b["h"] >= 96 and b["cout"] < 0.30))
print("| tranche | période | paris | rendement | gagnés / attendus | z |\n|---|---|---|---|---|---|")
for nom, f in TR:
    for pn, a, z in PER:
        bs = [b for b in base if a <= b["mois"] <= z and f(b)]
        if len(bs) < 5: print(f"| {nom} | {pn} | {len(bs)} | | | |"); continue
        v = it.verdict(bs)
        print(f"| {nom} | {pn} | {len(bs)} | {v['rendement_moyen']:+.1%} | {sum(b['gagne'] for b in bs)} / {sum(b['cout'] for b in bs):.1f} | {v['z_prix']:+.2f} |", flush=True)
