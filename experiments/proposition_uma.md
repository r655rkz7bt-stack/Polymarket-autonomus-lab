# Piste n° 14 (vingt-cinq pistes) : `proposition_uma`, acheter l'issue proposée à 0,90-0,98

**Verdict : écartée (relevé en direct du 22/10/2026, 05 h UTC).** Idée : quand Gamma indique `umaResolutionStatus: proposed`,
un résultat est proposé et sera payé dans environ 2 h sauf contestation ; si l'issue proposée coûte encore 0,90-0,98, l'acheter.

## Relevé
Les 2 500 marchés ouverts les plus actifs (Gamma, tri par volume 24 h), ceux dont le statut n'est ni vide ni `resolved` :
**36 marchés « proposed »**, tous des matchs du soir (NBA, Liga MX, UFC, tennis ITF, CS2…).
- 33 sur 36 : prix **0,9995 / 0,0005** (tick minimum) pour les deux issues ; le gain possible est de 0,05 %, inférieur aux frais.
- 1 marché d'exception (« Guangzhou 2 : Cruz Hewitt contre Tristan Schoolkate », 0,495 / 0,505, volume 15 k$) : prix proche de 0,50 sans cause
  relevée (non vérifié : pas de règlement visible, donc pas une décote prouvée) ; 1 marché de propriétés de joueur à 0,10 / 0,90 (« AJ Dybantsa : Points O/U 13,5 »).
- Le seul cas de marge connu est le litige UMA 5167158 (« Russia target Kyiv ? »), statut `disputed`, pas `proposed` : bloque
  5 portefeuilles depuis 78 h (enquête du 21/10).

## Pourquoi pas de test sur le passé
Gamma ne garde pas la date de la proposition ; `prices-history` montrerait seulement que les prix finaux sont déjà à 0,99+. Le relevé
en direct suffit : la fenêtre « proposé » est arbitrée par les robots avant que la stratégie n'agisse (cycle de 5 minutes). Si un jour
un marché « proposed » se négocie sous 0,97, c'est qu'un litige est probable : le risque (perte totale) dépasse alors la marge de 3 %.
Pas de stratégie, pas de fantôme. À ne pas refaire sans un relevé horodaté des propositions (seule manière de mesurer la marge restante).
