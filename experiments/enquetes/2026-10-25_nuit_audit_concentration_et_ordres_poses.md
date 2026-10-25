# 2026-10-25 (nuit, passage de 21 h) : audit, concentration des gains, principal contre championne, ordres posés

Famille du jour : 25 mod 6 + 1 = 2 (le gain résiste-t-il sans ses plus gros paris ?). Données : journaux publiés du 25/10 à 20 h 47 UTC.

## Obligations de la feuille de mission
- **Audit (2 anomalies)** : ce sont les deux achats du NON « Will Ethereum dip to $2,300 on October 24? » à 0,001 (`crypto_threshold_non`, `crypto_threshold_prix_bas`, 24/10 15 h 17), déjà expliqués et corrigés le 24/10 (`2026-10-24_touche_deja_touchee_non_a_0_001.md`, `TOUCH_MIN_ASK`). L'état d'audit garde l'anomalie. Vérifié : **aucun achat de ces cinq stratégies crypto à moins de 0,05 depuis 16 h le 24/10**.
- **`nf_court_soir` (3 paris = 97 % du gain)** : 54 paris, 50 gagnés pour 48,6 attendus (z 0,63) ; sans les 3 plus gros : +3 € sur 54 paris. Un rendement de +1,8 % sans avantage mesuré.
- **`nf_sport_patiente` (3 paris = 120 % du gain, 18/10 = 214 %)** : 174 paris, 156,5 gagnés pour 151,1 attendus (z 1,23), +113 € mais **−22 € sans les 3 plus gros** et −185 € sans son meilleur jour. Aucun avantage au-delà du prix. Même conclusion qu'à midi (`2026-10-25_midi_tirage_sans_5050_et_chance.md`).
- **`champion_sans_avantage`** (26 gagnés / 26,3 attendus sur 30) : voir la recherche ci-dessous, c'est là que la cause se trouve.

## Contrôle à la main (famille 2) : script `chance_famille2_25_10.py` rejoué
24 fantômes positifs sur les 25 plus gros ; 14 le restent sans leurs 3 meilleurs paris, 11 sans leur meilleur jour. Seuls z > 2 : `moins_de_cartes` (2,59, suivi depuis midi, indice) et `contrer_crypto_patiente` (2,10, +8 € : rien de net).

## Principal contre championne (copie fidèle ?)
Principal : 212 paris réglés, −239 €. Depuis le 21/10 : 79 paris, −9,1 % (z −1,9), alors que la championne fait +0,8 % sur toute sa vie. Jeton par jeton depuis le 21/10 :
- 32 jetons communs : principal −13,8 % (−88 € / 638 €), championne −13,1 % (−511 € / 3 886 €) : **même résultat, la copie est fidèle** (la taille est celle du capital) ;
- 54 jetons que la championne a pris sans le principal : +7,5 % (51 gagnés sur 54 pour 47 attendus) ; le principal suivait à ce moment une autre championne (l'écart est une affaire de calendrier, pas de copie) ;
- les 47 autres paris du principal viennent d'autres stratégies et font −1 %.
Le trou du principal est donc surtout le 18-19/10 (−206 € avant la correction des mises du 20/10), puis du hasard défavorable : rien à corriger dans la copie.

## Ce qui sort de ce contrôle
Les 32 jetons communs sont presque tous des ordres posés servis en cours de match. D'où la recherche du soir : `experiments/ordres_poses_en_jeu.md` — ordres posés −6,8 % (239 paris, z −2,8), immédiats −0,2 %, effet surtout hors échantillon (22-25/10 : −12,7 %, z −3,5). Pas un défaut de code : sélection adverse du mode patient en jeu. Sœur `nf_sport_patiente_avant_match` ajoutée.

## Aucun défaut de code trouvé
Pas de correctif ni de test de non-régression ce soir (rien à corriger dans le code) ; le contrôle `chance` reste utile. Reste à faire côté contrôle automatique : un contrôle `posees_en_jeu` (rendement des ordres posés en cours de match contre les immédiats) quand il y aura assez de recul (le chiffre ci-dessus tient sur 9 jours).
