# Contre-mouvement crypto à 0,10-0,45 : test sur le passé (27/10/2026, piste 0c)

**Verdict : ÉCARTÉE.** Le « +8 % » du premier tirage (2 880 marchés) disparaît sur l'échantillon complet : 1 492 paris, −4,2 %, gagnés 402 pour 405,1 attendus (z −0,18).
Les 58 gagnés pour 39,3 attendus des fantômes `contrer_crypto*` ne se confirment pas sur le passé (174 paris en direct, tranche choisie après coup : probablement un tirage). Les fantômes « audace » restent en jeu (ils ne coûtent rien au principal).

## Données et méthode (`experiments/contrer_crypto_passe/scripts/`)
- `releve_marches.py` : Gamma `/events/keyset` (étiquette `crypto`, jamais `offset`), événements réglés dont la fin est depuis le 01/06/2026 : 145 605 marchés Oui/Non ;
  gardés : volume ≥ 5 000 $, pas « up or down », réglés net 0/1 → 8 996 marchés (échelles « au-dessus de X à telle heure », « reach / dip to »), plus quelques marchés plus anciens à fin lointaine.
- `releve_echanges.py` : vrais échanges des preneurs (data-api `trades?market=`), 8 974 marchés.
- `analyse.py` : la règle en direct rejouée toutes les 30 minutes, avec seulement les échanges d'avant l'instant T : mouvement = dernier échange du OUI avant T moins dernier échange avant T − 6 h ;
  on achète l'autre côté si son prix est dans la plage et s'il reste ≥ 2 h ; prix payé = premier échange réel qui achète ce côté dans l'heure suivante ; frais crypto 0,07·p(1−p) ; un pari par marché ;
  jugement `idea_test.verdict` (paris liés par événement). Contrôle du règlement : prix de règlement Gamma 0/1 net seulement (non relu sur Binance : la source de règlement n'est pas rejouée).

## Résultats (`resultats_analyse.txt`, 8 réglages de plage × mouvement essayés)
| réglage | paris | rendement | gagnés / attendus |
|---|---|---|---|
| contrer 0,10-0,45, mouvement 0,05 (règle des « audace ») | 1 492 | −4,2 % | 402 / 405,1 |
| mouvement 0,03 / 0,10 | 1 491 / 1 537 | −2,2 % / −4,6 % | 394 / 395,8 ; 424 / 431,0 |
| contrer 0,05-0,60 (règle des mères) | 1 828 | −7,7 % | 466 / 495,1 |
| sous 0,10 | 1 898 | −11,4 % | 159 / 165,9 |
| contrer 0,45-0,90 | 1 803 | −5,2 % | 1 300 / 1 353,5 (z −3,1) |
Par mois : 2026-06 +4,5 %, 07 −20,1 %, 08 −10,5 %, 09 −5,5 %, 10 +3,2 % (aucun mois solide). Par genre : « au-dessus de » −2,2 %, « touche » −6,5 %.

## Ce que les références sans signal ont montré (`resultats_baseline_non.txt`)
- **Suivre** le mouvement (l'inverse) à 0,10-0,45 : +14,4 % (z +2,98) : le même effet que le NON bon marché ci-dessous, pas un signal de mouvement.
- **NON à 0,10-0,45 sans aucun signal : +14,4 %** (1 111 paris, 398 gagnés pour 357,8, z +2,66, t par événement +1,70) mais **fragile** : sans ses 5 meilleurs jours −0,7 % ; juin +44 %, août −31 % ;
  tranche 0,20-0,30 −18,5 %. Le NON 0,05-0,10 fait +35 % (z +3,1) : billets, jamais joués.
- **Dans les marchés « touche » (reach / dip to / hit), NON à 0,10-0,45 : 386 paris, 200 événements, +22,6 %, 163 gagnés pour 131,7 (z +3,44), t par événement +2,95, 6 mois sur 6.**
  Dans les échelles « au-dessus de » : +10,0 % (t par événement +0,15). Bitcoin +8,4 %, Ethereum +19,0 %. Environ 30 découpages regardés.
  **Verdict : indice** (6 mois seulement, découpage choisi après coup) → fantôme `toucher_non_crypto` (Kelly entier, biais supposé 0,05), pas de capital principal avant 30 nouveaux paris.

## Suite
- Vers le 03/11 : juger `toucher_non_crypto` et les deux « audace » sur leurs nouveaux paris (gagnés contre attendus ; par événement).
- Avant toute promotion : refaire le « touche NON » sur le premier semestre 2026 (le relevé démarre en juin ; `releve_marches.py 2026-01-01` et `releve_echanges.py`, environ 1 h) et sur Ethereum seul.
- Cette piste tient une leçon : un « avantage » trouvé dans 174 paris d'un fantôme et confirmé par un premier sous-échantillon (2 880 marchés, +8 %) a disparu à 8 974 marchés. Toujours refaire sur plus de données avant d'écrire « confirmé ».
