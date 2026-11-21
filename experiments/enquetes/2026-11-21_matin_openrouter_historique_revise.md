# 21/11/2026 (passage de 6 h) : OpenRouter récrit tout son historique ; refus d'`openrouter_semaine` mal nommé

## Constat (enquête automatique, « n'achète plus depuis 72 h »)
`openrouter_semaine_v2.0.0` : dernier achat le 17/11 12 h 57 ; au dernier cycle, « OpenRouter : forme de la semaine précédente
incohérente » ×3.

## Ce qui s'est passé (lu, pas supposé)
- Journal `openrouter:histo` et `historique_references` de la sauvegarde du 21/11 : jusqu'à 22 h 55 UTC le 20/11, la semaine du 9/11
  valait **211,28 T** et la projection de la semaine du 16/11 était 326 T (« 240 T+ » à p = 1,0). À **23 h 55 UTC**, la même semaine
  valait **171,21 T**, la semaine du 16/11 149,20 T au lieu de 197,25 T.
- Relu en direct le 21/11 vers 05 h 55 UTC (graphique mis en cache à 04 h 55) : TOUTES les semaines ont baissé, de 15 à 21 %
  (comparé aux copies du 13 et du 17/11 dans `tests/data/`) :

  | semaine | avant | après | rapport |
  |---|---|---|---|
  | 21/09 | 145,85 | 114,94 | 0,788 |
  | 05/10 | 171,84 | 139,26 | 0,810 |
  | 19/10 | 188,04 | 160,24 | 0,852 |
  | 26/10 | 193,58 | 162,33 | 0,839 |
  | 02/11 | 209,48 | 173,12 | 0,826 |
  | 09/11 | 211,28 | 171,21 | 0,810 |

  Les vues « 7 jours » et « 30 jours » sont révisées de la même façon (30 jours = 741,98 T, cohérent avec le graphique).
  `tencent/hy4-flash` (≈ 15,7 T le 17/11) n'a plus que 0,42 T sur 7 jours pour 768 millions de requêtes. Aucune annonce trouvée
  (recherche web) : cause inconnue (changement de méthode de comptage ou nettoyage de trafic).
- Le marché « semaine du 16/11 » est resté à « 240 T+ » 0,97-0,98 et « < 210 T » 0,01 jusque vers **03 h 50 UTC le 21/11** (échanges
  data-api v2), soit 4 h après notre lecture ; ensuite « < 210 » 0,38 / 0,89 (milieu 0,64), « 4 semaines 675-725 » 0,45 / 0,65,
  « semaine du 23/11 : < 230 » 0,39 / 0,58 contre « 260+ » 0,32 / 0,50 : la foule parie sur une annulation de la révision à 30-45 %.

## Défaut
Aucune perte et aucun achat faux : le refus était juste. Mais sa **raison était fausse** : les totaux quotidiens du journal lus
AVANT la révision (16-18/11 : 32,13 + 53,56 + 56,25 T) dépassaient le nouveau graphique, et `openrouter.detail` concluait à une
« forme de la semaine précédente incohérente ». Le passage suivant aurait cherché un défaut de forme au lieu de lire la révision.

## Correctif
`openrouter.detail` compare la « semaine précédente » gardée au journal pour la semaine en cours à celle du graphique ; au-delà de
3 % (`REVISION_MAX`) : refus « historique révisé par la source (semaine précédente 211,3 → 171,2 T) », champ `revision`. Test du cas
réel : `test_21_11_history_revised_by_source_is_named` (copie réduite des vues du 21/11 dans `tests/data/openrouter_2026-11-21.json`).
L'enquête automatique affiche la raison dans « acheteuses arrêtées » : aucun contrôle de plus nécessaire. La semaine du 23/11 repartira
d'un journal propre (points lus après la révision).

## Conviction étudiée (non écrite)
« < 210 T, semaine du 16/11 » : si la révision tient jusqu'à lundi 00 h UTC (règle : chiffre affiché quand la semaine suivante
apparaît), total ≈ 193-201 T (graphique 155,9 T le samedi matin, week-end ≈ 21-22 T/jour) → P(< 210 | tient) ≈ 0,97. Cinq estimations
0,90 / 0,88 / 0,80 (annulation avant lundi) / 0,93 / 0,88, médiane 0,88 ; rapprochée du milieu 0,64 → 0,76, sous le vendeur 0,894 :
**rien**. « 675-725 » des 4 semaines (≈ 700 T si tient) : médiane 0,87, rapprochée 0,71, borne basse ≈ 0,66 sous vendeur + 5 points
(0,70), et plus de 30 points du prix sans savoir ce que le prix sait : **rien**. Piste n° 74 ouverte (tenue des révisions).

## Famille 4 (contrôle à la main)
3 achats v2 depuis le passage de 1 h relus contre Gamma : `non_aux_drames` NON « invasion de Cuba en 2026 » 0,950 (vendeur 0,957 ce
matin, 41 jours, dans 30-120 j) ; `taux_tresor_empirique` OUI « 5 ans sous 4,56 % » 0,07 (estimé 0,178, plage 0,05-0,90) et « 10 ans
sous 4,82 % » 0,169 (avantage net 0,061 ≥ 0,06), achetés à 00 h UTC (fenêtre 00-12 h) : **3/3 conformes**.
