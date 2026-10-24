# 24/10/2026 (soir) : les seuils d'une étiquette étaient ignorés pour tout marché déjà lu dans les pages normales

Famille 6 (« ce qui ne tourne plus ») : `seismes_marche` affichait « abstentions {} » (aucun marché) et `box_office_favori` « moins de deux tranches visibles » malgré les étiquettes `tag_pages` censées les montrer.

## Constat
- `scanner._add_tag_markets` lit les marchés d'une étiquette avec les seuils propres à l'étiquette (séismes : liquidité 200 $, écart 0,15 ; box-office : liquidité 0, écart 0,60). Mais `if market.market_id in seen: continue` : un marché déjà lu par les pages normales (triées par volume, 1 500 marchés)
  y avait été jugé avec les seuils GÉNÉRAUX (liquidité 1 000 $, écart 0,05) et restait « inexploitable » : l'étiquette ne servait que pour les marchés que les pages normales n'avaient pas.
- Scan du 24/10 (21 h UTC) : **21 marchés rendus exploitables** par la correction, dont les tranches « Clayface » et « Wildwood » du box-office (liquidité 820-3 100 $, écart > 0,05), une tranche de séismes (3 séismes ≥ 6,5, 963 $) et un marché de mentions de Trump (728 $).
  Les 63 marchés de séismes du scan : 28 → 30 exploitables (les autres : écart de 0,63, quasi certains, ou incohérents).

## Cause
Ordre des passes (pages normales d'abord, étiquettes ensuite) et déduplication sur l'identifiant : la première passe qui voit un marché fixe son verdict.

## Correctif
`market_scanner._add_tag_markets` : si le marché est déjà connu, ineligible pour une raison que le seuil d'étiquette peut lever (liquidité, volume, écart, prix extrême : `RELAXABLE`) et exploitable avec les seuils de l'étiquette, il devient éligible ; les exclusions « inactif », « carnet indisponible », « hors horizon », « données incohérentes » ne sont jamais levées.
Test : `tests/test_market_scanner.py::test_a_tag_market_already_read_in_the_normal_pages_gets_the_tag_thresholds` (échoue sans le correctif ; vérifié). Cycle local après correctif : `box_office_favori` voit plus de tranches (« hors de la fenêtre du week-end » ×3), `seismes_marche` voit 2 marchés (et s'abstient pour « doublon possible entre réseaux USGS », la règle du matin).

## Limites
- Les marchés rendus exploitables ne passent dans la liste des 150 surveillés que s'ils sont assez échangés ; les autres ne sont vus que par les stratégies qui les demandent (`candidates`).
- Les pages normales ne contiennent pas tout : un marché trop peu échangé n'y figure pas, l'étiquette le lit directement (déjà le cas).
