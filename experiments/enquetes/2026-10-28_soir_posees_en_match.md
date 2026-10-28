# 2026-10-28 (soir) : les ordres posés servis en match perdent 10 % par pari, le principal les annule au coup d'envoi

Famille du jour : 28 mod 6 + 1 = 5 (comparaisons faussées) pour le contrôle à la main, et le constat « à regarder » `posees_en_jeu` de l'enquête automatique
(256 ordres posés servis en match, 196,5 gagnés pour 210,4 attendus, z −2,6). Données : journaux publiés du 28/10 à 20 h 48 UTC. Script :
`scripts/posees_en_jeu_28_10.py` (résultat : `scripts/posees_en_jeu_28_10.txt`).

## Constat (chiffré)
Le contrôle comptait un jeton une fois par premier achat vu, mais le premier passage (25/10, `experiments/ordres_poses_en_jeu.md`) et ce contrôle sont restés
au stade « à regarder » : personne n'avait demandé si le principal subit la même chose. Refait ici, **un compte par jeton** (premier fantôme qui l'a acheté),
règlements nets 0 / 1, rendement par pari au prix payé :

| groupe | jetons | événements | gagnés / attendus | z | par pari |
|---|---|---|---|---|---|
| en match, **posés** | 320 | 300 | 251,0 / 267,8 | −2,84 | **−9,8 %** (z par événement −3,0) |
| en match, immédiats | 907 | 766 | 790,5 / 794,8 | −0,45 | −0,3 % |
| avant le match, posés | 52 | 44 | 29,5 / 30,3 | −0,27 | −11,7 % (peu de paris) |
| avant le match, immédiats | 521 | 368 | 378,0 / 376,8 | +0,14 | +0,2 % |
| en match, posés **avant le 25/10** | 209 | 195 | 165,5 / 175,4 | −2,02 | −8,2 % |
| en match, posés **depuis le 25/10** (hors échantillon) | 111 | 105 | 85,5 / 92,4 | −2,08 | −12,7 % |

Les deux moitiés ont le même signe ; la seule chose qui change entre posé et immédiat en match est la manière d'être servi : l'ordre posé n'est servi que quand le
prix descend jusqu'à lui (but, blessure, break), donc quand le favori vient d'avoir de mauvaises nouvelles (sélection adverse, comme la tenue de marché : −800 €).
Pas un défaut du simulateur (la règle prudente ne sert que si le marché traverse le prix).

## Le principal est touché aussi
Journal du principal : 22 achats posés en match (13 de `nf_sport_patiente_prix_850_875`, 8 de `nf_sport_patiente`, 1 de `nf_sport_patiente_6_24h`) : **16 gagnés pour
19,1 attendus, −37,6 € sur 331 €** (−11,4 %). Petit en euros (mises de 4-5 €), mais c'est exactement la partie du champion qui perd. Chez les fantômes :
`nf_sport_patiente` 24 paris posés en match −9,8 % (−220 €) contre −0,3 % pour le reste de ses paris ; `nf_sport_patiente_prix_850_875` (n° 1) −2,9 % en match posé contre
+8,1 % pour le reste (+459 €).

## Correctif
`main._fill_resting` : pour le **principal seulement** et pour un achat, un ordre posé dont le match a commencé (`market.game_start` passé) est annulé (statut `ANNULE`)
au lieu d'être servi. Réglage `principal.annuler_posees_au_coup_d_envoi` (config/settings.yaml, `true`). Les fantômes continuent de subir l'effet : c'est la mesure, et
elle permet de retirer le frein par un rejeu si l'effet disparaît. Les ordres posés AVANT le coup d'envoi et servis avant lui ne changent pas.
Tests (`tests/test_cycle.py`) : `test_principal_cancels_resting_buy_when_the_match_starts_but_the_ghost_keeps_it` (échoue avec le réglage à `false`),
`test_principal_still_gets_its_resting_buy_before_the_match`.

## Contrôle à la main, famille 5 : classement « capital réalisé » et positions ouvertes (`scripts/ouvertes_classement_28_10.py`)
Le classement ne compte que les règlements. Mise en jeu (positions ouvertes, au prix payé) des fantômes en tête : `nf_sport_18_24h` 1 281 € en 25 positions (la plus vieille 3,0 j),
`nf_sport_prix_haut` 1 186 € (31), `nf_sport_v1` 1 066 € (47) ; `market_structure` 5 183 € et `market_maker_serre` 4 790 € (255 et 179 positions ouvertes, éliminées, jamais réglées : leur capital
« réalisé » est donc sous-estimé, pas gonflé). Les stratégies à Kelly entier du haut du classement ont tout leur capital en jeu sur 25-30 positions de moins de 4 jours :
leur rang du jour dit ce qu'elles ont réglé, pas ce qu'elles valent. Pas un défaut de code (contrôle `capital_bloque` existant), à garder en tête en lisant le classement.

## Contrôle automatique
`enquete.posees_en_jeu` existe déjà (z ≤ −2) ; il reste « à regarder » parce que les fantômes continuent d'en faire. Rien à ajouter.
