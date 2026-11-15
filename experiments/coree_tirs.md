# Piste n° 64 : nombre de jours de tirs de missiles nord-coréens dans le mois (15/11/2026, passage de 16 h)

Idée neuve (« lire les règles mieux que la foule ») : « Number of North Korea Missile Tests in <mois> 2026? » compte les JOURS de
tir (heure de Pyongyang) de missiles balistiques, de croisière ou antinavires ; les missiles sol-air, lance-roquettes multiples et
torpilles ne comptent pas. Règlement sur « sources fiables » (pas de source unique). Question : à mi-mois, le prix se trompe-t-il
sur ce qui compte (un tir annoncé « défense aérienne » par la KCNA mais « plusieurs missiles » par l'état-major sud-coréen) ?

## Données (`coree_tirs/scripts/releve.py`, `coree_tirs/releve.json`)
Gamma `public-search` : 7 événements mensuels réglés (mai → octobre 2026, deux pour août) et novembre ouvert ; prix de chaque tranche
au 8, au 15 et au 22 du mois (prices-history du CLOB, dernière barre horaire finie). Avant mai : marchés « missile test by <date> »
(19 événements 2023-2026), autre question (au moins un tir).

| Mois | Tranche réglée | Prix de la gagnante au 8 | au 15 | au 22 |
|---|---|---|---|---|
| mai | < 2 | 0,49 | 0,68 | 0,72 |
| juin | 1-2 | 0,35 | 0,165 | 0,14 |
| juillet | 1 | 0,385 | 0,215 | 0,28 |
| août | 3+ | 0,315 | 0,65 | 0,9995 |
| septembre | 2 | 0,205 | 0,34 | 0,325 |
| octobre | 4+ | 0,135 | 0,59 | 0,70 |

Au 15 du mois, le prix de la tranche gagnante vaut 0,44 en moyenne (log-score −0,96 ; une loi uniforme sur 3-5 tranches ≈ −1,4).
Les erreurs du prix viennent des tirs de FIN de mois (juin : « < 1 » à 0,74 le 15, un tir ensuite ; juillet : « 3+ » à 0,41, un seul
jour de tir), pas d'une mauvaise lecture des tirs déjà faits.

## Novembre (ouvert)
Le 08/11 le marché donnait « 4+ » 0,48 et « 3 » 0,33 ; le 15/11 « 2 » 0,30, « 3 » 0,27, « 4+ » 0,225 : il a retiré un ou deux jours
déjà comptés (tir du 04/11 annoncé « nouveau système de défense aérienne » par la KCNA, « plusieurs missiles, peut-être de types
différents » par l'état-major de Séoul ; essai de « tactique à sous-munitions » vers le 01/11 non annoncé par Séoul le jour même).
La foule lit déjà cette ambiguïté ; je n'ai pas de source qui tranche (règlement par « sources fiables », pas de base de données
nommée). Rythme 2026 : « quatrième tir en un mois » au 04/11 (Séoul).

## Verdict : **écartée en l'état**
6 mois réglés seulement, aucun modèle de rythme sans base de dates de tirs (la base du CNS / NTI serait la source ; pas lue
aujourd'hui), et la règle laisse le décompte à l'interprétation. Rien dans l'arène. À reprendre si une base de dates ouverte et
permise (robots lus) permet un modèle de Poisson par mois sur 2017-2026 et s'il y a 12 mois réglés ou plus.
