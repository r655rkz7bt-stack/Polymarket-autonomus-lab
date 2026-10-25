# Détroits, marchés à seuil (« returns to normal », « on any day by ») — 25/10/2026

Suite de `experiments/detroits.md` (« Reste à faire », point 1). Données : 59 marchés d'Ormuz réglés (Gamma), prix horaire du OUI
(`prices-history`, tranches de 13 jours), PortWatch (`n_total`, jusqu'au 18/10). Scripts : `experiments/detroits_seuils/scripts/`
(`releve_rtn.py`, `analyse.py`), relevé versionné `experiments/detroits_seuils/releves/seuils.json`.

## Ce qui est réglé
- « returns to normal by … » : la moyenne sur 7 jours de PortWatch ≥ 60. Depuis mars 2026, la plus haute moyenne sur 7 jours est
  77,6 (mars, début), puis 11 (avril), 12 (mai), 32 (juin), 27 (juillet), 6 (août), 5 (septembre), 4 (octobre) : **12 marchés réglés sur 12 : NON**.
- « on any day by … » (seuils de 10 à 50 passages un jour) : 8 événements mensuels, 38 marchés à J-14.

## Résultats (achat du NON au prix horaire, sans frais ni écart : premier regard)
| Famille | J-30 | J-14 | J-7 | J-3 |
|---|---|---|---|---|
| returns to normal | 8 NON, +26,2 % | 10, +9,3 % | 9, +4,9 % | 4, +1,8 % |
| on any day by | 27, +19,6 % (4 OUI gagnés) | 38, +10,9 % (5) | 34, +6,9 % (3) | 39, +5,1 % (4) |

Les 12 « returns to normal » sont **un seul chemin** : le détroit est resté fermé de mars à octobre, tous les événements se chevauchent.
Aucune statistique par événement n'a de sens ici (12 événements = une observation).

## Ce qui compte : la prime d'espoir a disparu
OUI moyen (prix horaire, tous les marchés « returns to normal ») : mars 0,35 ; avril 0,36 ; mai 0,27 ; juin 0,24 ; juillet 0,14 ; **août 0,065 ; septembre 0,01**.
Le marché a payé cher l'espoir d'une réouverture tant que le détroit était récemment fermé, puis a appris. Aujourd'hui : OUI 0,0045 (31/10), 0,055 (30/11),
0,115 (31/12). Sur 7 mois de fermeture, la moyenne sur 7 jours n'a jamais atteint 60 : un taux de réouverture de ~5 % par mois (0,055 à 36 jours, 0,115 à 67 jours) est de
l'ordre de ce que l'historique permet (règle de trois : borne haute ~40 % par mois), donc rien à gagner prouvé aujourd'hui.

## « on any day by » (10 à 50 passages)
Le NON gagne 85-91 % pour un prix de 0,78-0,85 à J-14/J-7 : +7 à +11 %, 8 événements, mais en 2026 seuls juin et juillet (29, 51 passages) ont franchi des seuils ≥ 20.
Un seul régime là aussi. Ouvert aujourd'hui : « au moins 10 le 31/10 » OUI 0,28 (carnet 0,07-0,49, inutilisable), « au moins 20 » 0,085, « au moins 30 » 0,065 ; le maximum d'un jour en septembre-octobre est 8.
Non testé davantage (pas de loi sur le maximum d'une période ; 8 événements).

## Verdict : ÉCARTÉE comme avantage (indice historique disparu)
- Essais : 4 horizons × 2 familles, aucun réglage ajusté ensuite. Aucune preuve : un chemin, des événements corrélés, prime déjà effacée.
- Fantôme gratuit `detroits_non_normal` (quart de Kelly, NON de « traffic returns to normal » entre 0,80 et 0,95, biais 0,03) uniquement pour voir si la prime
  revient avec une nouvelle de négociation : l'arène juge ; pas de priorité au principal.
- Restent : une loi sur le maximum d'une période pour les seuils « on any day », à reprendre quand la fermeture finira (nouveau régime = nouvelles données).
