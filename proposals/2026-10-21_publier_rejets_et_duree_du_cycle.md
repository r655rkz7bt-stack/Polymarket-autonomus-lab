# Proposition (noyau) : publier la durée du cycle, les propositions et les rejets par motif (21/10/2026, soir)

Le chercheur n'a pas pu établir pourquoi la mère `naive_favorite` n'achète plus depuis le 18/10 alors qu'elle a de l'argent (87 → 257 €) : les journaux signés ne gardent que les
achats, et la sauvegarde quotidienne (`backup/essentiel.sqlite.gz`, étape « Sauvegarde de l'essentiel » de `.github/workflows/cycle.yml`, **fichier protégé**) vide les tables
`decisions` (propositions et rejets avec leurs motifs), `cycles` (durée) et `observations`. Les abstentions du dernier cycle (clé `abstentions` de la table `kv`) n'y sont pas non plus :
`scripts/research_brief.py` les lit dans la base du cycle, mais le chercheur, lui, ne voit que ce que publie la branche `data`.

## Ce qui manque au chercheur (et qu'un cycle local ne reproduit pas)
1. **Rejets par motif et par stratégie** (table `decisions`) : « carnet périmé », « prix chuté pendant le cycle », « taille inférieure au minimum », « coût supérieur au solde ».
   Un cycle local de 2 min (20 h 14 UTC) : 158 propositions, 56 exécutions, 12 rejets « carnet périmé » (corrigés ce soir dans `main._execute`, PR du passage), 4 rejets « prix chuté ».
2. **Durée du cycle** (`cycles.started_at / finished_at`, ou le tour de chaque étape `_lap`) : tous les battements d'un cycle portent la même heure dans les journaux.
3. **Abstentions du dernier cycle** par portefeuille (`kv.abstentions`) : pourquoi une stratégie reste muette.

## Proposition
Dans l'étape de sauvegarde de `cycle.yml`, garder (au lieu de vider) un extrait léger : les 3 000 dernières lignes de `decisions` (colonnes : cycle, stratégie, accepted, reasons, fill_status),
les 300 dernières lignes de `cycles` et la clé `abstentions`. Quelques centaines de ko compressés. Sinon : écrire ces trois éléments dans un fichier `diagnostic.json` de la branche `data`,
mis à jour à chaque cycle, lisible par `scripts/fetch_data.sh`.
