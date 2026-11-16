# Piste n° 43 : taux du Trésor, barrière sur les clôtures quotidiennes (12/11/2026, passage de 16 h)

**Marchés** (étiquette `treasuries` 102028, `economics_fees` ou `zero_fees`) : « How high / low will <2, 5, 10, 30>-year Treasury
yield go / get in <mois> » (9 à 13 seuils, 400-1 900 $ de liquidité par seuil) et « … before 2027 ». **Règle** : colonne de la durée
dans « Daily Treasury Par Yield Curve Rates » (home.treasury.gov), une valeur par jour ouvré au centième ; « hit » = une clôture
≥ niveau, « dip below » = une clôture strictement sous le niveau, entre deux dates de la description. Les cours en séance ne
comptent pas. Source : CSV de l'année, sans clé (`robots.txt` : tout permis).

**Question** : une marche aléatoire des clôtures restantes (écart-type des 60 jours ouvrés précédents × K) bat-elle le prix ?

## Données (`taux_tresor/scripts/`)
- `releve.py` : 33 événements réglés (`public-search`), 159 marchés ; mensuels de septembre et octobre 2026 seulement (14 événements,
  8 durées × sens), plus 3 annuels de 2025 (sans observation utilisable) ; prix horaires du CLOB.
- Contrôle du règlement : 126 marchés sur 128 retrouvés par les clôtures (les 2 écarts : « dip below » compté ≤ au lieu de < dans
  la première lecture ; le module `taux_tresor.touche` suit la règle).
- `analyse.py` : décision chaque jour ouvré à 02 h UTC, clôtures datées d'avant le jour seulement, simulation de 4 000 trajectoires.

## Résultats (2 000 observations marché × jour)

| K | log-score modèle | log-score prix |
|---|---|---|
| 0,8 | −0,597 | −0,525 |
| 1,0 | −0,512 | −0,525 |
| 1,2 | −0,475 | −0,525 |
| 1,4 | −0,462 | −0,525 |
| 1,7 | −0,464 | −0,525 |

Par mois et sens (K 1,2) : septembre « high » −1,19 contre −1,30 (taux en hausse, tous les seuils touchés), octobre « low »
−0,65 contre −0,75 (taux en baisse) ; « high » d'octobre et « low » de septembre ≈ égaux. **Le K qui gagne est celui qui suit
les deux tendances** : deux mois = deux trajectoires (toutes les durées bougent ensemble).

Achats simulés (`achats.py` : premier jour où la chance dépasse le prix + 0,02 + seuil, achat au prix + 0,02, un pari par marché,
9 réglages) : K 1,0 +27 à +42 % (septembre −24 à −6 %) ; **K 1,2 +54 à +57 % (septembre −9 à +21 %, octobre +79 à +100 %)** ;
K 1,4 +52 à +69 % (septembre +20 à +47 %, octobre +62 à +105 %). Positif les deux mois à K 1,2-1,4 (hausse puis baisse) : le modèle
ne gagne pas seulement en devinant la direction, il paie les seuils éloignés plus cher que le marché.

**Aux vrais échanges** (`echanges.py`, data-api v2, 159 marchés : premier achat PRENEUR du côté voulu à ≤ prix visé après 02 h UTC,
≥ 10 ou ≥ 50 parts) : avec une fenêtre de 24 h, 8 à 31 paris « exécutables » et +74 à +413 % — **faux** : la fenêtre compte des
achats faits après un mouvement des taux en séance, aux vendeurs restés en retard (regard vers le futur). Avec la fenêtre honnête de
3 h (02-05 h UTC, marché américain fermé) : **2 à 4 paris par réglage** (K 1,0-1,4, seuils 0,05-0,15), de −100 % à +279 % : trop peu
pour juger ; 6 h : 4 à 9 paris. La nuit, presque personne n'achète ces marchés : le test de l'exécution reste à faire en direct
(le fantôme achète au vendeur affiché, que les échanges passés ne montrent pas).

**Limites** : deux trajectoires ; prix horaires (milieu ou dernier échange), pas de vrais échanges ni de test de profondeur
(carnets de 400-1 900 $) ; les fériés (Veterans Day, Thanksgiving) comptés à part dans le module, pas dans le test.

## Verdict : **indice faible** → fantôme `taux_tresor_barriere` (expérience)
K = 1,3, chance donnée de 00 h à 12 h UTC seulement (le marché voit la séance du jour, pas nous), Kelly entier plafonné à 4 % par
pari, deux seuils par événement au plus. Le 12/11 à 16 h, avec la clôture du 10/11 (4,98) : « hit 5,06 » 0,62 contre 0,82 au marché,
« 5,38 » 0,06 contre 0,047, « dip below 4,82 » 0,37 contre 0,12 : le marché a déjà la séance du jour (le 10 ans a monté le 10/11).

## Reste ouvert
- Exécution : regarder les achats du fantôme (vendeurs de nuit) ; refaire le test fin novembre (3e mois), aux prix horaires et aux échanges.
- Les annuels « before 2027 » (fenêtre septembre-décembre) : même module, horizon long (la marche aléatoire y est plus fragile).

## Rejeu du 13/11/2026 (passage de 1 h) : trajectoires réelles contre marche aléatoire (`scripts/trajectoires.py`)
Leçon de Freddie Mac (`taux_immobilier.md` : la marche aléatoire sous-estime les tendances des taux immobiliers) rejouée ici. Mêmes
observations (marché × jour ouvré, décision à 02 h UTC, 1 941 observations sur 169 marchés relevés de nouveau), clôtures du Trésor
1990 → 31/07/2026 (aucune fenêtre d'après la coupure) ; marche aléatoire en formule fermée (barrière discrète, correction de
Broadie-Glasserman) au lieu de la simulation.

| modèle | log-score |
|---|---|
| prix du marché | −0,530 |
| marche aléatoire × 1,0 | −0,526 |
| **marche aléatoire × 1,3 (en production)** | **−0,468** |
| trajectoires réelles, en points | −0,488 |
| trajectoires réelles mises à l'échelle de l'écart-type des 60 jours | −0,523 |

Par mois et sens, × 1,3 gagne en septembre « high » (−1,11 contre −1,15 et −1,36 au prix) et en octobre « low » (−0,63 contre −0,73 et
−0,75) ; les trajectoires en points gagnent octobre « high » (−0,214 contre −0,292). Par durée, × 1,3 est devant pour les 2, 5, 10 et
30 ans. **Le modèle en production reste** : sur les taux quotidiens, les trajectoires réelles n'apportent rien de plus que l'écart-type
gonflé de 30 %. (Les 75 observations de « November high » ne portent que sur des seuils déjà réglés, donc touchés : biaisées, non comptées.)

## Étalonnage sur 36 ans (16/11/2026, passage de 21 h) : K = 1,3 surestimait les barrières

Déclencheur : le 16/11, le modèle K 1,3 voyait 0,22 à 0,30 d'avantage sur des seuils hauts déjà achetés (17 OUI sur 17).
`scripts/etalonnage_historique.py` : CSV du Trésor 1990-2026 (37 années, `donnees/`), chaque 5e jour ouvré, 2/5/10/30 ans, horizons
5/10/20/30 jours, barrières à z × σ60 × √n (z 0,5-2,5), haut et bas, 284 360 barrières ; chance en formule fermée (barrière discrète).

| période | K 0,8 | K 1,0 | K 1,15 | K 1,3 | K 1,5 |
|---|---|---|---|---|---|
| 1990-2007 | −0,4279 | −0,3954 | **−0,3922** | −0,4011 | −0,4237 |
| 2008-2019 | −0,3727 | **−0,3554** | −0,3607 | −0,3760 | −0,4050 |
| 2020-2026 | −0,4005 | **−0,3769** | −0,3786 | −0,3912 | −0,4176 |
| tout | −0,4041 | **−0,3784** | −0,3790 | −0,3908 | −0,4162 |

Fréquences (tout, n = 10) : z 1,0 observé 0,242, K 1,0 0,237, K 1,3 0,341 ; z 2,0 : 0,040 / 0,029 / 0,085. Le cœur suit K 1,0, les
queues sont plus épaisses qu'une gaussienne. **K 1,3 venait des deux tendances de septembre-octobre** (ce que l'hypothèse disait
qu'une perte apprendrait).

**Modèle empirique** (`etalonnage_hors_echantillon.py`) : part des excursions passées (divisées par σ60) d'au moins z en n jours,
apprise sur 1990-2015, jugée sur 2016-2026 : **−0,3761** contre −0,3788 (K 1,0), −0,3798 (K 1,15), −0,3918 (K 1,3). 4 modèles essayés.
En production depuis ce passage (`taux_tresor_excursions.json`, 1990 → 07/2026, `table_excursions.py`).

**Ce que le modèle étalonné voit le 16/11 au soir** (décision simulée à 02 h UTC le 17/11, clôture du 16/11) :

| marché | K 1,3 | empirique | acheteur / vendeur |
|---|---|---|---|
| 5 ans « 5,25 % avant 2027 » | 0,411 | 0,291 | 0,15 / 0,19 |
| 30 ans « 5,70 % avant 2027 » | 0,414 | 0,298 | 0,19 / 0,24 |
| 10 ans « 5,5 % avant 2027 » | 0,294 | 0,185 | 0,092 / 0,101 |
| 30 ans « 5,80 % avant 2027 » | 0,274 | 0,166 | 0,10 / 0,109 |
| 10 ans « 5,33 % en novembre » | 0,257 | 0,148 | 0,048 / 0,098 |
| 5 ans « 5,03 % en novembre » | 0,556 | 0,468 | 0,38 / 0,40 |

L'avantage fond d'environ 0,11 par seuil mais ne disparaît pas sur les seuils hauts : après +60 points en 60 jours, le marché parie
sur un retour en arrière que l'histoire moyenne (à agitation égale) ne montre pas. Les seuils bas (« dip below ») sont justes.

**Verdict** : le module K 1,3 est **corrigé** (défaut d'étalonnage) ; `taux_tresor_barriere` n'achète plus et garde ses 17 positions
jusqu'au règlement (elles jugent l'ancienne hypothèse) ; **expérience `taux_tresor_empirique`** (seuil 0,06, Kelly entier, 4 % par
pari) : hypothèse = le marché sous-paie les queues après une tendance forte.

**Retour ou élan après une tendance ?** (`scripts/tendance_retour_ou_elan.py`, même passage ; tendance = variation des 60 jours /
(σ60 × √60), 35 304 observations, chaque 3e jour 1990-2026, barrières à z σ60) : **élan**, pas retour. Exemple n = 20 jours :

| |tendance| | z 2 dans le sens | z 2 contre | z 3 dans le sens | z 3 contre |
|---|---|---|---|---|
| 0-0,5 | 0,542 | 0,523 | 0,396 | 0,371 |
| 0,5-1,0 | 0,588 | 0,500 | 0,456 | 0,360 |
| 1,0-1,5 | 0,613 | 0,512 | 0,463 | 0,379 |
| ≥ 1,5 | 0,619 | 0,534 | 0,501 | 0,392 |
| sans condition | 0,549 | | 0,408 | |

Même sens à n = 10 et 30 et sur 2010-2026 seul. Le 16/11, tendances : 2 ans +1,3, 5 ans +1,1, 10 ans +1,0, 30 ans +0,6 (hausse).
Le pari du marché sur un retour en arrière va donc CONTRE 36 ans d'histoire ; la loi sans condition en production est prudente
(elle ne compte pas l'élan, qui ajouterait ≈ 0,05-0,07 aux seuils hauts). Pas de modèle conditionnel en production : une seule
découpe regardée (4 tranches × 4 z × 3 n), à refaire hors échantillon avant de s'en servir.

**Hors échantillon** (`scripts/tendance_hors_echantillon.py`, tranches fixées avant le test, appris 1990-2015, jugé 2016-2026,
344 064 barrières, z 0,5-4, n 5-30) : log-score conditionnel à la tendance **−0,5776** contre −0,5814 sans condition ; tendances
≥ 1 : −0,5844 contre −0,5890 ; ≥ 1,5 : −0,5929 contre −0,5973. L'élan tient hors échantillon, gain modeste (≈ 0,004).

Reste ouvert : (1) mettre la loi conditionnelle en production (table 4 tranches × 2 sens × 90 jours, ≈ 0,5 Mo) si
`taux_tresor_empirique` achète et que l'exécution de nuit tient ; (2) vrais échanges de nuit (peu
nombreux) ; (3) fin novembre, juger les 17 positions de la version K 1,3 contre leurs prix.
