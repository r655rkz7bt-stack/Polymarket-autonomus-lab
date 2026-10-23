# Test sur le passé de `vague_volume` (23/10/2026)

Compte rendu : `../vague_volume_backtest.md`. À lancer depuis la racine du dépôt, dans cet ordre
(données dans `donnees/`, ignoré par Git) :

| Ordre | Script | Ce qu'il fait | Durée |
|---|---|---|---|
| 1 | `PYTHONPATH=src .venv/bin/python experiments/vague_volume_backtest/releve_marches.py 2026-07-10 2026-10-15` | marchés OUI/NON réglés à ≥ 20 000 $ (Gamma `/markets`, une fenêtre par jour), gardés s'ils ont pu offrir une décision (âge ≥ 3 j, échéance réelle ≥ 48 h après) → `marches.json` | ≈ 3 min |
| 2 | `PYTHONPATH=src .venv/bin/python experiments/vague_volume_backtest/releve_echanges.py` | vrais échanges des preneurs, marché par marché, en remontant le temps avec `end` (≤ 40 pages) → `echanges/<id>.json.gz` (reprise possible : cache) | ≈ 1 h |
| 3 | `PYTHONPATH=src .venv/bin/python experiments/vague_volume_backtest/controle_reglement.py 400` | dernier échange avant la clôture contre le résultat officiel | ≈ 3 min |
| 4 | `PYTHONPATH=src .venv/bin/python experiments/vague_volume_backtest/analyse.py 0` (ou `0,12`) | règle en direct rejouée à 00:00 UTC (et 12:00), 36 réglages, détail par famille, références sans vague → `resultats_*.json` | ≈ 2 min |
