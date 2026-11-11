"""11/11/2026 : table de climatologie de `tornades_mois` (src/polymarket_agent/tornades_climat.json) : base finale SPC 1995-2024
(experiments/tornades/donnees/actual.csv, `www.spc.noaa.gov/wcm/data/1950-2024_actual_tornadoes.csv`), nombre de tornades par jour,
pour chaque mois : 30 listes (une par année) de 31 comptes. Usage : .venv/bin/python experiments/tornades/climat.py"""
import csv, json, collections
from pathlib import Path
seen, daily = set(), collections.Counter()
for r in csv.DictReader(open("experiments/tornades/donnees/actual.csv")):
    if r["sg"] == "2" or (r["yr"], r["om"]) in seen:
        continue
    seen.add((r["yr"], r["om"])); daily[(int(r["yr"]), int(r["mo"]), int(r["dy"]))] += 1
table = {f"{mo:02d}": [[daily[(y, mo, d)] for d in range(1, 32)] for y in range(1995, 2025)] for mo in range(1, 13)}
Path("src/polymarket_agent/tornades_climat.json").write_text(json.dumps({"source": "SPC base finale 1995-2024, tornades par jour", "annees": [1995, 2024], "mois": table}, separators=(",", ":")))
print("ok", sum(sum(map(sum, v)) for v in table.values()))
