# 05/11/2026, 11 h : positions « oubliées » du constat `positions_oubliees` (famille 6)

**Question** : l'enquête automatique signale des positions ouvertes 78 à 251 h après leur échéance
(`vague_volume_suivre_x5`, `detroits_marche_log`, `favori_politique*`, …). Un règlement a-t-il été manqué ?

**Contrôle** : les 33 marchés cités dans `published/rapports/enquete.md` relus un par un sur Gamma (`/markets/<id>`).

**Résultat** : 33 marchés sur 33 sont encore `closed: false` (sans `closedTime`). Exemples : Serbie (2757900,
échéance 25/10, NON 0,87), pipeline saoudien (5401795, 0,9835), séismes ≥ 5,5 (6090732, échéance 02/11, 0,9875).
Ce sont des marchés dont la date de fin Gamma est dépassée mais qui n'ont pas encore été réglés par UMA : l'argent
est bloqué parce que le marché l'est, pas à cause du journal. Aucun règlement manqué, aucun défaut de code.

**Autres vérifications** : `cdc_historique.py` relancé : toujours 2 lignes (22 et 29/10), le CDC n'a pas publié
la ligne du 04/11. Aucun changement de code, donc aucun test ajouté.
