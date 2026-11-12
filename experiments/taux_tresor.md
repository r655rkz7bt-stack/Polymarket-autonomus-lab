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

**Limites** : deux trajectoires ; prix horaires (milieu ou dernier échange), pas de vrais échanges ni de test de profondeur
(carnets de 400-1 900 $) ; les fériés (Veterans Day, Thanksgiving) comptés à part dans le module, pas dans le test.

## Verdict : **indice faible** → fantôme `taux_tresor_barriere` (expérience)
K = 1,3, chance donnée de 00 h à 12 h UTC seulement (le marché voit la séance du jour, pas nous), Kelly entier plafonné à 4 % par
pari, deux seuils par événement au plus. Le 12/11 à 16 h, avec la clôture du 10/11 (4,98) : « hit 5,06 » 0,62 contre 0,82 au marché,
« 5,38 » 0,06 contre 0,047, « dip below 4,82 » 0,37 contre 0,12 : le marché a déjà la séance du jour (le 10 ans a monté le 10/11).

## Reste ouvert
- Vrais échanges des marchés réglés (data-api v2) et profondeur au prix avant d'y croire ; refaire le test fin novembre (3e mois).
- Les annuels « before 2027 » (fenêtre septembre-décembre) : même module, horizon long (la marche aléatoire y est plus fragile).
