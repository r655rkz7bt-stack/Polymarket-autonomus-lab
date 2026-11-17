# Piste n° 70 : pannes critiques de GitHub (17/11/2026, passage de 16 h)

Idée neuve (famille jamais regardée) : « Longest GitHub critical incident in <mois>? » (5 tranches : < 1 h, 1-3 h, 3-6 h, 6-12 h,
12 h+), « GitHub.com critical incident by…? », « GitHub Git Operations critical incident by…? ». Réglés sur githubstatus.com :
impact « critical » seulement, durée = début officiel → « Resolved », mois du début en heure de l'Est, incidents « Copilot seul » exclus.

## Source
- `www.githubstatus.com/api/...` est **INTERDIT par robots.txt** (`scripts/robots_ok.py`) : jamais lu.
- `www.githubstatus.com/history?page=N` est permis : chaque page embarque 3 mois d'incidents en JSON (`data-react-props` → `months`
  → `incidents` : code, nom, impact, « Nov 16, 11:59 - 16:26 UTC »). Relevé : `github_pannes/releve.py` (16 pages, 2 s entre deux),
  785 incidents de décembre 2022 à novembre 2026 (`github_pannes/releves/incidents_20261117.jsonl.gz`) ; analyse :
  `github_pannes/analyse.py`.
- Limite : la page ne liste pas les composants ; « Copilot seul » est reconnu au nom (5 incidents critiques exclus).

## Contrôle du règlement
Les 3 mois réglés redonnent le résultat officiel : août « 6-12 h » (10,7 h relevés), septembre « 1-3 h » (1,5 h), octobre « 3-6 h »
(4,5 h) ; les marchés « by … » de novembre (premier incident critique le 09/11) aussi.

## Ce que disent les données
- **Avant avril 2026, presque aucun incident n'est classé « critical »** (1 en 40 mois) ; depuis le 01/04 : **34 en 230 jours**
  (≈ 4,4 par mois), dont 13 de 3 h ou plus, 5 de 6 h ou plus, aucun de 12 h. Une seule ère comparable (7,5 mois) : la fréquence de
  base est incertaine (septembre : 1 incident ; mai : 8).
- Novembre au 17/11 16 h UTC : 3 critiques (0,8 h, 1,8 h, 0,6 h) : la tranche courante est « 1-3 h ».
- Poisson sur les 13,5 jours restants (taux d'avril-novembre) : 1-3 h **0,47**, 3-6 h **0,28**, 6-12 h **0,23**, 12 h+ **0,03**.

## Contre le marché (carnets du 17/11, 16 h UTC)
| tranche | modèle | acheteur / vendeur du OUI |
|---|---|---|
| 1-3 h | 0,47 | 0,52 / 0,76 (NON vendu 0,48 pour 0,53) |
| 3-6 h | 0,28 | 0,11 / 0,35 |
| 6-12 h | 0,23 | 0,11 / 0,25 |
| 12 h+ | 0,03 | 0,013 / 0,088 |

Aucun écart de 5 points après frais ; le milieu des carnets est proche de la fréquence de base. Pas de test aux vrais échanges possible
de façon utile : 3 mois réglés seulement dans l'ère « critical » (un tirage par mois).

## Verdict : **écartée en l'état** (marché aligné sur la fréquence de base, 3 mois réglés)
Ce qui pourrait la rouvrir : (1) une lecture EN DIRECT d'un incident critique en cours (la tranche monte avec la durée ; mesurer le
retard du marché sur la page de statut, comme pour ChatGPT le 27/10 où le marché suivait déjà) ; (2) plus de mois réglés (relever
le prix au 15 de chaque mois, puis comparer en mars 2027).
