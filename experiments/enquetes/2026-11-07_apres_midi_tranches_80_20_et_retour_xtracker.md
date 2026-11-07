# 07/11/2026, passage de 16 h : trois filles 80/20 relues, XTracker de retour

Famille 2 (gain concentré / tranche choisie après coup). Aucun défaut de code trouvé.

## Constat 1 : les trois « filles » de la feuille de mission sont des tranches choisies après coup

Script : `experiments/enquetes/scripts/tranches_filles_80_20.py` (journaux signés des mères, un pari par jeton).

| Mère | Tranche proposée | Tranche | Reste de la mère |
|---|---|---|---|
| `crypto_non_10_20` (86 paris, 44 événements, +35 €, z +1,37) | délai 24-72 h | 28 paris, 17 événements, +173 €, 9 gagnés pour 4,0 attendus, z +2,74, **−48 € sans les 3 plus gros**, +29 € sans le meilleur jour (9 jours) | 58 paris, −138 €, z −0,22 |
| `contrer_crypto_audace` (47 paris, −38 €) | délai 72-168 h | 9 paris, **5 événements, 2 jours**, +154 €, z +2,02, +11 € sans les 3 plus gros | 38 paris, −192 € |
| `compteur_tweets` (107 paris, 29 événements, +166 €, z +2,45) | prix payé 0,45-0,60 | 12 paris, 10 événements, +71 €, z +2,12, **−1 € sans les 3 plus gros** | 95 paris, +95 € |

Lecture : dans chaque cas le « 80 % du gain » tient à trois paris ; la tranche a été choisie parmi une dizaine de découpages
(délais, prix) sur le même échantillon. Un z de 2 à 2,7 y est attendu sans aucun avantage. Refusées, comme aux passages précédents.

Pourquoi pas un fantôme « pour voir » : une fille filtrée n'achète que des paris que sa mère achète aussi. Le test hors
échantillon se fait donc déjà, gratuitement, **sur le journal de la mère** : relancer le script avec une date de coupure,
par exemple `.venv/bin/python experiments/enquetes/scripts/tranches_filles_80_20.py 2026-11-08` (paris réglés à partir du
08/11). Une fille ne se justifie que si la tranche tient sur ces paris-là (au moins 30 paris, 15 événements).

## Constat 2 : « copie absente » de `naive_favorite_sans_fin` (3 jetons copiés sur 19)

Refus du principal sur 48 h (`data.json` → `refus_principal`) : « budget de la part épuisé » (6) et « budget de la part trop
juste pour le minimum du marché » (6). C'est la part de capital donnée à cette stratégie qui limite la copie, pas un défaut
de copie (même mécanisme que la fiche du 26/10 soir, mais ici le plancher de copie ne sert pas : la part est vide). Rien à corriger.

## Constat 3 : XTracker de retour, la source de secours CNN n'a pas servi à tort

XTracker répond 200 depuis ce passage (appel à la main, User-Agent `curl/8`), l'archive CNN aussi (200). Dans le battement
de 15 h 41 UTC : `xtracker ok (28 prix relevés)`, références « tweets 33 » ; `compteur_tweets` n'est plus en abstention
« compteur pas à jour » : ses refus sont « avantage net insuffisant » (21) et « billet trop bon marché » (11). La reprise
du 07/11 (secours CNN, puis XTracker) est donc vérifiée en production. `compteur_truth` (et ses filles) écartent
30 marchés : ce sont les comptes autres que Trump, toujours sans compteur (voulu).

## Contrôle « estimation_perimee » (compteur_tweets_72_168h, 17 € à 0,279 estimés 0,966)

Déjà jugé le 06/11 soir (`2026-11-06_soir_silence_apres_rafale_trump.md`) : moyenne de 14 jours portée par la rafale.
Rien de neuf, le billet se règle le 13/11.
