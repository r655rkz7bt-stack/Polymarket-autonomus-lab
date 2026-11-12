# Prises de villes en Ukraine : DeepStateMap en avance sur la carte de l'ISW ? (12/11/2026, piste n° 34 : ÉCARTÉE)

Passage du chercheur de 6 h (12/11/2026). Idée neuve (famille jamais regardée au labo) : des dizaines de marchés « Will Russia
capture / enter <lieu> by …? » (jusqu'à 2,3 M$ échangés pour Kostiantynivka) se règlent sur la **carte de l'ISW** (storymap
`36a7f6a6…`). DeepStateMap (DSM, ukrainien, une carte par jour, historique public) est réputé rapide : montre-t-il l'entrée dans
une commune avant que la carte de l'ISW ne la colore et avant que le prix ne bouge ?

## Règles (lues mot à mot)

- « enter <lieu> » / « capture any territory » : une partie de la commune (limites de la couche ISW « Ukrainian Settlements »)
  colorée par « Assessed Russian Infiltration Areas », « Assessed Russian Control », « Advance » ou « Gains in the past 24 hours »,
  et la couleur doit tenir jusqu'à la mise à jour ISW suivante. **Les infiltrations comptent.**
- « capture <ville> » : parfois un REPÈRE précis (Kostiantynivka : la gare de Pravoberezhna vulytsia ; infiltrations exclues).
- « capture all of <lieu> » : toute la commune.
Chaque marché a sa règle : ne jamais déduire d'un titre.

## Données (`prises_ukraine/scripts/`, données dans `donnees/`, ignoré par Git)

- `releve_marches.py` : 89 événements, 411 marchés (Gamma `public-search`, juillet → novembre 2026 ; les plus anciens ne
  sortent pas de la recherche), 312 réglés (46 OUI), 230 avec coordonnées dans la règle, tous réglés sur l'ISW.
- `communes.py` : limites des 49 communes (`services5.arcgis.com/SaBe5HMtmnbqSWlu/arcgis/rest/services/Ukrainian_Settlements_Updated_view/FeatureServer/0/query`,
  sans clé, `outSR=4326`).
- `couverture_dsm.py` : 181 cartes DSM quotidiennes depuis le 01/05/2026 (`deepstatemap.live/api/history/public` puis
  `/api/history/<id>/geojson`, 0,6 Mo chacune, sans clé, pas de `robots.txt`) ; pour chaque commune, part sous « occupé » et
  sous « occupé ou statut inconnu (gris) », et « touche » (un point de grille ou un sommet de zone dans la commune).
- `prix.py` : prix horaires du OUI (CLOB, 319 851 points).
- L'ISW n'a **pas d'historique** lisible : la webmap (`9f04944a2fe84edab9da31750c2b15eb`, 4,3 Mo) ne garde que la carte du jour
  (`pub_date` = date du jour pour tous les polygones).

## Résultat

L'ISW est presque toujours **en avance** sur DSM pour les marchés « enter » (les infiltrations comptent chez l'ISW, DSM les
laisse souvent sans couleur) : Dobropillia réglé OUI le 22/09, DSM touche le 26/10 ; Mykolaïvka OUI le 01/10, DSM jamais ;
Svitle OUI le 23/07, DSM le 29/09 ; Matiasheve OUI le 08/08, DSM le 29/08 ; Hannivka OUI le 03/09, DSM le 18/10 ;
Krasnoiarske, Novyi Donbas : même chose. DSM en avance : Myrne (10/07, marché « by 31/07 » perdu) et Stinky (31/07, réglé OUI
le 13/08).

Pari « acheter le OUI des marchés « enter / capture » encore ouverts 2 h après la carte DSM qui touche la commune »
(`analyse.py 2 touche`) : **8 paris, 2 gagnés pour 3,15 attendus, −36,6 % par mise** ; 4 des 8 sont des artefacts du début du
relevé (commune déjà touchée le 01/05), 107 marchés n'ont aucun signal DSM avant leur fermeture (dont 22 réglés OUI). Un seul
réglage regardé (2 h, « touche ») : inutile d'en essayer d'autres, le signal arrive après le règlement dans presque tous les cas.

**Verdict : écartée.** DeepStateMap n'est pas un témoin rapide de la carte de l'ISW pour ces règles. Le seul témoin utile serait
la carte de l'ISW elle-même, relevée chaque jour (pas d'historique) : on saurait alors si le prix suit l'ISW avec retard. Pas
fait (4,3 Mo par jour) ; à reprendre seulement avec une idée qui le justifie.
