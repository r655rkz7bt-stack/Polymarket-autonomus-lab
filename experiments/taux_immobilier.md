# Piste n° 46 : taux immobilier de Freddie Mac, barrière sur les relevés hebdomadaires (13/11/2026, passage de 1 h)

**Marché** (événement 197683, étiquette `freddie-mac` 102609, frais `finance_prices_fees` 4 % × p(1−p), 127 k$ de volume depuis février) :
« Will the U.S. 30-year Fixed-Rate Mortgage hit <x>% (HIGH / LOW) by December 31, 2026? ». **Règle lue mot à mot** : OUI si, pour une
semaine **finie après la création du marché** et au plus tard le 31/12/2026, le taux à 30 ans de l'enquête hebdomadaire de Freddie Mac
(PMMS, publiée le jeudi, au centième) est ≥ (HIGH) ou ≤ (LOW) au niveau ; révisions ignorées. Piège de lecture : « 6,25 % LOW » (créé le
03/08) est ouvert alors que le taux était à 5,98 % en février : la fenêtre commence à la création de CHAQUE seuil, pas au 1er janvier.

**Sources** : `www.freddiemac.com/pmms/docs/PMMS_history.csv` (`robots.txt` : `/pmms/docs/` permis ; 1971-2026, sans clé) ; clôtures du
10 ans (CSV du Trésor, déjà lu par `taux_tresor`). Relevé : `taux_immobilier/scripts/releve.py` (marchés, prix horaires du CLOB).

## État au 13/11 à 01 h UTC
Freddie Mac : 7,40 % les 08 et 15/10 (sommet), puis 7,32, 7,24, 7,18, **7,11 le 12/11**. Le 10 ans : moyenne lundi-mercredi de la semaine
du 12/11 = 4,93 (9 et 10/11 ; le 11/11 férié), clôture du 12/11 = 5,10 (+0,17). Bêta du relevé hebdomadaire sur le 10 ans : 0,74 (2019-2026),
0,61 (2023-), 0,77 (2026) ; résidu 0,05-0,07 → le relevé du 19/11 est attendu vers 7,23. Restent **7 relevés** (19/11 → 31/12).

## Modèle
1. Marche aléatoire (gaussienne puis Student à 3 degrés) : elle **sous-estime** les grandes hausses : +0,89 en 7 relevés arrive dans 1,3 %
   (1990-2026) à 3 % (2019-2026) des vraies fenêtres, contre 0,1-0,6 % pour la marche aléatoire calée sur l'écart-type : les taux
   immobiliers ont des tendances (septembre 2022 : +1,57 en 7 semaines).
2. **Retenu : trajectoires réelles** (`taux_immobilier.chance`) : part des fenêtres de n relevés consécutifs (depuis 1990 et depuis 2019,
   moyenne des deux) dont le relevé, décalé au niveau d'aujourd'hui + avance du 10 ans, touche le niveau.

| seuil | marché (acheteur / vendeur du OUI) | sans avance du 10 ans | avec avance (+0,12) |
|---|---|---|---|
| 7,50 % HIGH | 0,25 / 0,67 | 0,10-0,19 | 0,16-0,29 |
| 7,75 % HIGH | 0,09 / 0,13 | 0,03-0,08 | 0,06-0,12 |
| **8,00 % HIGH** | **0,10 / 0,11** | 0,009-0,030 | **0,016-0,042** |
| 7,00 % LOW | 0,20 / 0,80 | 0,43-0,54 | 0,16-0,28 |
| 6,75 % LOW | 0,012 / 0,209 | 0,05-0,11 | 0,02-0,05 |
| 6,50 % LOW | 0,025 / 0,085 | 0,013-0,035 | 0,008-0,02 |
| **6,25 % LOW** | **0,045 / 0,076** | 0,000-0,005 | 0,000-0,003 |

(fourchettes : 6 ou 7 relevés × 1990 / 2010 / 2019 comme début de l'historique)

## Test sur le passé : impossible aux prix
L'échelle n'existe que depuis février 2026 : 6 seuils réglés, tous touchés (6,00 LOW ; 6,20 à 7,25 HIGH) ; les seuils lointains sont restés
des mois à des **prix de façade** (5,50 % LOW coté 0,45-0,55 de février à juillet quand le taux était à 6,0-6,6 ; 7,00 % HIGH ≈ 0,45 de
février à août) : milieux de carnets vides, sans échanges (`scripts/veille.py`). Aucun log-score honnête possible (un seul tirage, prix non
exécutables). Ce qui est vérifié : la règle, la source (relevé du 12/11 = 7,11 lu au CSV), le calcul (tests sur le vrai CSV).

## Conviction ?
« 8,00 % HIGH » NON : médiane de cinq angles (trajectoires 1990 : 0,016-0,017 ; 2019 : 0,03-0,04 ; marche aléatoire : 0,001-0,005 ; pire
régime connu, 2022 : +1,57 en 7 semaines, soit une fois en 36 ans ; régime de 2026 agité, 10 ans +0,22 en trois séances : 0,05) ≈ 0,03
→ NON 0,97 ; rapprochée de moitié du milieu (NON 0,895) → 0,93, borne basse 0,91 pour un vendeur du NON à 0,90 : **sous le seuil de
5 points, pas de conviction**.

## Verdict : **expérience** (pas de test aux prix possible) → fantôme `taux_immobilier_barriere`
Kelly entier sur la borne basse (incertitude 0,02), au plus 5 % du fantôme par pari, deux seuils par échelle (compteur des positions déjà
tenues, correctif du même passage), chance donnée la nuit seulement (00-12 h UTC : en séance, le marché voit le 10 ans du jour, pas nous).
Une perte apprendrait que 2026 est un régime plus violent que 36 ans d'historique, ou que les prix de façade cachent une information.

## À reprendre
- Relevé du 19/11 (le modèle l'attend vers 7,23 ± 0,07) : si l'avance du 10 ans se trompe de plus de 0,15, revoir le bêta.
- Règlement au plus tard le 15/01/2027 : gagnés contre attendus de chaque seuil acheté.
- Même mécanique ailleurs : toute échelle « hit __ by <date> » réglée sur une série HEBDOMADAIRE ou mensuelle publiée (stocks de pétrole
  de l'EIA le mercredi, demandes d'allocations le jeudi) : trajectoires réelles plutôt que marche aléatoire.
- Lac Mead (« How low will Lake Mead drop? », 23 k$) : à lire dans la prévision à 24 mois de l'USBR ; **bloqué** : `data.usbr.gov` et
  `www.usbr.gov` refusés par le proxy de la routine, `lakemead.water-data.com` interdit les robots ; l'USGS ne publie que le lac Powell
  (09379900 : 3 539,1 ft le 11/11, minimum 3 516,4 le 16/09 depuis la création ; baisse d'hiver 9 à 24 ft sur 7 hivers, il en faudrait 29
  pour 3 510 : ≈ 0,98-0,99 contre un vendeur à 0,966, juste).
