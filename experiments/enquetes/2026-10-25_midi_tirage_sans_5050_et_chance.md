# 2026-10-25 (passage de midi) : le test de `moins_de_cartes` écartait les matchs réglés à 50-50 dès le tirage

Famille du jour : n° 2 (25 mod 6 + 1) « la mesure récompense la chance ». Scripts : `scripts/chance_famille2_25_10.py`, `scripts/regl_moins_de_cartes_25_10.py`,
`experiments/bo3_coherence/sous_2_5_50_50.py`, `sous_2_5_neufs.py`.

## Contrôle à la main (famille 2), 159 journaux signés
Pour chaque fantôme de 25 paris réglés ou plus : gain, gain sans ses 3 meilleurs paris, sans son meilleur jour, gagnés contre attendus (payé réel, 50-50 = 0,5).
- Sur 23 fantômes gagnants, **13 gagnent encore sans leurs 3 meilleurs paris et 11 sans leur meilleur jour**. La championne `nf_sport_patiente` : +113 €, **−22 € sans ses 3 meilleurs paris, −185 € sans son meilleur jour**, 156,5 gagnés pour 151,1 attendus (z +1,2). Même mécanisme qu'aux passages précédents (mise ∝ 1/(1 − prix)) : pas de défaut de code, les trois obligations « chance / champion sans avantage » restent des constats de hasard.
- Aucun z > 2 parmi ces 25 fantômes, sauf `contrer_crypto` et `contrer_crypto_patiente` (z +1,9 et +2,0 : ils gagnent plus souvent que leur prix mais le gain en euros est nul, −10 € et +2 € : les gains sont petits, les pertes grandes ; à regarder si la stratégie réapparaît dans la feuille de mission).
- **Piège de mon propre script** (corrigé) : `charge_fantome.charger` marquait « gagné » tout règlement > 0, donc un règlement à 0,5 comptait pour 1. Il garde maintenant `pay` ; sans cette correction `moins_de_cartes` aurait affiché z +2,5 au lieu de +1,9.

## Défaut trouvé : les règlements 50-50 absents du test sur le passé
`moins_de_cartes` (fantôme depuis le 23/10, 42 paris réglés) : 28 gagnés, 10 perdus, **4 réglés à 0,5/0,5** (Gamma relu : 42 marchés sur 42 conformes au journal). Soit 9,5 % de 50-50, alors que le test sur le passé (`experiments/pistes_sport_coherence.md`, 457 paris) n'en avait presque aucun.
- **Cause** : `series.regle` rend `None` pour un marché réglé 0,5/0,5 ; `match_cas` écarte ces marchés, et un match dont TOUS les totaux sont à 50-50 n'a plus de marché lié : il disparaît, et il ne peut pas non plus être tiré par `releve_echanges` (même fonction). Le tirage excluait donc ~4 % des matchs utilisables (15 484 sur 16 156), presque tous CS2 (738 totaux à 50-50 sur ~6 500) et Dota 2 (83 sur ~1 600). Même défaut que le 24/10 (`reglements_50_50`, `idea_test.parse_event_market`), mais cette fois **dans le tirage** : on ne pouvait pas le corriger après coup.
- **Correctif** : `series.INCLURE_50_50` (variable d'environnement, `regle` rend −1, payé 0,5), `sous_2_5_50_50.py` ; échantillon retiré à 60 matchs par mois et par jeu (2 755 matchs, 3 012 totaux dont 70 à 50-50 = 2,3 %).
- **Chiffre** : « Under » à 3 h du coup d'envoi (fenêtre 6 h) : +8,1 % sans les 50-50, **+7,7 % avec** (865 paris, t par match +2,0, z des prix +1,5, « indice » au lieu de « retenue »). Les 50-50 coûtent 0,4 point et 0,6 point de z.
- **Échantillon neuf** (1 804 matchs du nouveau tirage absents du tirage du 23/10, donc jamais vus par la découverte) : +8,3 % (522 paris, t +1,84, z +0,9), **LoL +15,1 % (255 paris, t +2,2, z +2,0)**, BO5 +23,1 % (t +1,9), CS2 +8,2 %, Dota 2 −5,4 %, Valorant +1,7 %. L'effet se retrouve, mais il est surtout LoL et BO5 ; les autres jeux sont à zéro dans les deux tirages.
- Pas de contrôle automatique ajouté à `enquete.py` : le défaut est dans un script de recherche, pas dans l'arène ; la leçon est écrite dans les astuces de la routine (« un tirage qui exige un marché réglé net exclut les 50-50 »).

- **Sept autres jeux** (HoK, MLBB, CoD, R6, RL, SC2, OW ; 2 220 matchs, aucun 50-50) : « Under » +2,1 % (t 0,69) : `moins_de_cartes` n'est pas un effet général d'e-sport, d'où une fille LoL et pas une extension.

## Suite
Fille `moins_de_cartes_lol` (fantôme, filtre `titre_contient`, test), cycle local : 0 proposition (les deux matchs LoL du jour sont à 7,5 h et 10,5 h, hors de la fenêtre 1-6 h : elle n'est pas sourde). À juger contre sa mère sur les mêmes marchés.

## Famille 5 en plus : les filles battent-elles le RESTE de leur mère ? (`scripts/filles_contre_mere_25_10.py`)
30 filles de ≥ 10 paris réglés, comparées aux paris de leur mère achetés depuis le premier achat de la fille sur des jetons que la fille n'a pas joués (le « reste »).
- Écart moyen **+7,1 points** en faveur des filles (t 2,05, 20 filles sur 30 meilleures que le reste de leur mère). Presque toutes sont des filles de `nf_sport_patiente`, dont le reste rend −17 à −40 % : **filles corrélées (mêmes matchs), pas 30 preuves**.
- Pourquoi le reste est mauvais, pour la championne elle-même (174 paris réglés) : 0,70-0,80 : −0,2 % (7 paris) ; 0,80-0,85 : **+6,8 %** (60) ; 0,85-0,90 : **+8,9 %** (46) ; **0,90 et plus : −7,3 % sur 6 653 € misés (61 paris, 55 gagnés pour 56,4 attendus)**. Les mises de la tranche haute sont les plus grosses (∝ 1/(1 − prix)) et font le résultat de la mère, donc du principal qui la copie. Ce n'est pas un nouveau défaut (le 21/10, `prix_final` a coupé les ordres posés sous 0,80) mais cela confirme le mécanisme des filles « prix 0,85-0,875 » en tête de l'arène : elles retirent la tranche ≥ 0,90. 61 paris avec z −0,4 : pas démontré non plus.
