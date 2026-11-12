# 12/11/2026 (passage de 6 h) : raison d'abstention de `suivre_inities`, copie du principal, prix payés des 142 achats v2

Familles 1 (copie du principal, jour 12 → 12 mod 6 + 1) et 4 (prix payé contre prix cru) à la main ; constats « à regarder »
`muettes` et `positions_oubliees` de l'enquête automatique (05 h 55 UTC). Aucune « Enquête obligatoire ».

## Constat « à regarder » : `suivre_inities` muette « raison non notée par la stratégie » ×229

Cause : `strategies_v3.SuivreInities.propose` sautait sans rien noter les marchés sans référence `inities` (le cas normal : aucune
grappe de comptes neufs et concentrés n'est relevée) ; `main._raison_par_defaut` affichait alors le message générique « aucun
marché vu n'a la référence ou la forme demandée (raison non notée) », que l'enquête et le tableau de bord ne peuvent pas
distinguer d'une stratégie sourde. La muette elle-même est déjà élucidée (09/11 : aucune grappe suspecte).
**Correctif** : abstention nommée « aucune grappe de comptes neufs et concentrés relevée sur ce marché » ; test
(`tests/test_inities.py`, marché du Ballon d'Or sans référence). Aucun euro en jeu.

## `positions_oubliees` : 5 positions de `favori_politique_quasi_certain`

Relues sur Gamma à 05 h 58 UTC : marchés 2118145, 2116493, 2117123… (élection néo-zélandaise), `closed: false`,
`umaResolutionStatus` vide, prix 0,9355-0,993 : résultats officiels le 27/11, déjà noté le 11/11. Rien à corriger.

## Famille 1 : copie du principal

Journal signé du principal (9 297 lignes) : dernier achat le 07/11 15 h 17, depuis seulement des règlements v1 et des
battements (`HEARTBEAT` 05 h 52 : 582,87 € disponibles, 653,44 € estimés). Aucune stratégie v2 n'a encore 12 opérations
closes (meilleure : `compteur_tweets` 18 achats réglés mais portefeuille en test 4,5 jours, croissance −0,041) : champion
« aucun », 0 copie attendue. Conforme.

## Famille 2 (au passage) : les fantômes v2 contre leurs prix

| fantôme | achats | réglés | événements | payés | attendus par les prix | gain |
|---|---|---|---|---|---|---|
| compteur_tweets | 36 | 18 | 6 | 10,0 | 11,2 | −40,1 € |
| compteur_truth | 10 | 4 | 1 | 3,0 | 3,3 | −11,6 € |
| seismes_marche | 8 | 3 | 2 | 0,0 | 2,4 | −144,5 € |
| favori_politique_quasi_certain | 24 | 2 | 1 | 2,0 | 2,0 | +0,7 € |
| convictions_claude | 4 | 1 | 1 | 0,0 | 0,5 | −14,6 € |

Rien d'anormal : chaque écart tient en un ou deux événements (la perte de `seismes_marche` est déjà expliquée le 11/11).

## Famille 4 : prix payé contre prix cru, 142 achats v2

Pour chaque `BUY` des journaux `fantome_v2` : prix moyen contre niveaux du carnet relus (`extra.levels`), plage
`min_price`/`max_price` de la stratégie (`config/strategies.yaml`), avantage net `prob_low − prix − frais/part` contre
`min_net_edge`. **0 écart sur 142** : aucun achat hors plage, aucun au-dessus du carnet relu, aucun sous l'avantage minimum
(le 11/11, `favori_politique_quasi_certain` avait 3 achats à 0,961-0,969 sous son plancher 0,97 ; aucun nouveau depuis).

## Pas de nouveau contrôle automatique

Le contrôle `muettes` a joué son rôle (il a montré la phrase générique) ; le correctif est dans la stratégie.
