# Après la fin du match (23/10/2026) : ordre de lancement

Depuis ce dossier (`cd experiments/apres_fin_match`), avec `../../.venv/bin/python` :
1. `scripts/releve.py` : événements réglés de 37 ligues depuis le 30/09 (Gamma) et leurs échanges (data-api) → `donnees/events.jsonl`, `donnees/echanges.jsonl` (≈ 10 min ; lancer un second
   processus avec `REV=1` pour aller deux fois plus vite, puis dédoublonner `echanges.jsonl`).
2. `scripts/analyse.py` : favori acheté d heures après le coup d'envoi (`LO`/`HI` = fourchette de prix) → `resultats_*.txt` ; écrit `donnees/rows.json`.
3. `scripts/tennis_oos.py` : relecture de l'« indice » du tennis en jeu (`AFTER`/`BEFORE` = dates).
Compte rendu : `experiments/apres_fin_match.md`.
