# 02/11/2026 (matin) : positions « oubliées » après l'échéance, vrai blocage ou règlement manqué ?

Famille 3 (jour 2 mod 6 + 1) : positions jamais réglées. Constat de l'enquête automatique : `positions_oubliees`
(nm_prix_bas 5, vague_volume_suivre 3, nf_court 5… « échéance dépassée de 122 à 174 h »).

## Vérifié
- Les marchés cités (Israël 682705/682708/2109956/5939176/5939179, Serbie 2757891/4961853) sont lus sur Gamma
  `/markets/<id>` : `closed: false`, `active: true`, prix vivants (ex. Eizenkot PM 0,4385). La date de fin est
  une date placeholder d'élection ; le marché n'est simplement pas clos. Pas un règlement manqué.
- Contrôle large : 434 marchés où une stratégie ENCORE ACTIVE (journal écrit aujourd'hui) a un jeton acheté avant le
  30/10 et jamais réglé, relus sur Gamma : **0 marché fermé**. Aucun règlement manquant côté stratégies actives
  (`scripts/reglements_manquants_02_11.py`).
- Les 528 marchés « fermés mais non réglés » vus dans tous les journaux (19 178 € misés) ne concernent que des stratégies
  éliminées ou retirées (journal arrêté : `market_structure`, `market_maker*`, `news_momentum*`, `reversion`…) :
  leur journal ne reçoit plus de règlement, c'est normal.
- Contrôle croisé : `nf_court` a bien réglé le jeton du marché 608545 (Ballon d'Or) le 27/10 à 02 h 01, 12 s après `closedTime`.

## Résultat
Pas de défaut de code. Argent immobilisé réellement : paris sur des marchés d'élection dont Gamma ne clôt pas le marché
après le scrutin (résultat israélien encore en cours de formation du gouvernement). Le constat `positions_oubliees` reste utile
mais ne doit pas déclencher d'obligation tant que le marché est ouvert.
