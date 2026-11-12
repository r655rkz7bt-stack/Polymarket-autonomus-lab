# « Year in Search » de Google : qui sera la personne n° 1 de 2026 ? (12/11/2026, piste n° 30, en cours)

Passage du chercheur de 1 h (12/11/2026). Idée **radicalement différente** demandée par la feuille de mission (aucun palier depuis
27 jours) : un nouveau type de marché, très liquide, réglé une fois par an sur une liste publiée par Google début décembre.

## Les marchés

| événement | liquidité | prix le 12/11 (milieu) |
|---|---|---|
| « #1 Searched Person on Google 2026? » (715392) | 1,23 M$ | Lindsay Clancy 0,225, Erling Haaland 0,11, Bad Bunny 0,055, Maduro 0,047, Alysa Liu 0,044, Trump 0,039 |
| « … in the US 2026? » (779081) | 0,52 M$ | Lindsay Clancy 0,375, Maduro 0,128, Nancy Guthrie 0,088, Haaland 0,075, Bad Bunny 0,058, Trump 0,041 |
| « Top 5 … in the US 2026 » (996201) | 27 k$ | Clancy 0,845, Haaland 0,68, Bad Bunny 0,34, Alysa Liu 0,285, Maduro 0,275 |
| « #1 Searched Passing … US 2026 » (779096), « #1 TV Show 2026 » (779079) | 0,22 et 0,35 M$ | Dolly Parton 0,62 ; Euphoria 0,34, Stranger Things 0,29 |

Règle : n° 1 de la liste « Trending → People » de `trends.withgoogle.com/year-in-search/` (monde ou États-Unis). « Trending »
= les recherches dont la **hausse** sur l'année est la plus forte par rapport à l'année d'avant (méthode de Google), pas le
volume total : une célébrité déjà très cherchée l'année d'avant (Trump, Messi, Swift) n'y arrive presque jamais, sauf une
année d'élection présidentielle.

## Données relevées (`experiments/annee_recherche/`)

- **Listes 2010-2025** (monde et États-Unis, toutes catégories) : `scripts/listes_yis.py` → `releves/listes.json` (page publique,
  sans clé). N° 1 « People » : 2016 Trump, 2017 Matt Lauer, 2018 Meghan Markle (US : Demi Lovato), 2019 Antonio Brown, 2020 Biden,
  2021 Alec Baldwin (US : Kyle Rittenhouse), 2022 Johnny Depp, 2023 Damar Hamlin, 2024 Trump, 2025 d4vd (US : Zohran Mamdani).
  Monde = États-Unis 7 années sur 10. Types de n° 1 : élection présidentielle (3), scandale ou procès (Lauer, Brown, Baldwin,
  Rittenhouse, Depp), accident (Hamlin), affaire criminelle (d4vd), mariage royal, élection locale très suivie (Mamdani).
  Grand procès criminel de 2025 hors du top 10 américain : **Karen Read** (second procès suivi en direct).
- **Marchés 2025 réglés** (`scripts/marches_2025.py` → `releves/marches_2025.json`, 7 événements, 172 candidats, prix à J-30,
  J-7, J-1 avant la publication du 04/12/2025) : n° 1 monde 2025 (57 M$ de volume) : le favori Pope Leo XIV (0,385 à J-7, 0,505 à
  J-1) a perdu, **d4vd** a gagné à 0,009 (J-7) / 0,096 (J-1) ; n° 2 : Kendrick Lamar à 0,03 (J-7) ; acteur : Mikey Madison
  (2e favori, 0,27) ; décès : Charlie Kirk (0,90, juste) ; série : aucun des cotés n'a gagné. Prix contre issues (tous candidats) :
  à J-7, tranche < 0,05 : 2 gagnants sur 111 pour 1,5 attendu ; 0,05-0,15 : 1 sur 28 pour 2,5 ; 0,15-0,35 : 2 sur 13 pour 3,0 ;
  0,35-0,65 : 2 sur 8 pour 3,9 ; > 0,65 : 3 sur 6 pour 4,8. Un seul millésime : les favoris des « n° 1 » ont tous perdu, mais
  n = 7 événements.
- **Volume de presse GDELT** (`scripts/presse_gdelt.py`, `scripts/presse_lent.py` → `releves/presse_gdelt.json`, articles par
  jour depuis 2017, sans clé). Articles du 1er janvier au 10 novembre (ce qu'on sait mi-novembre) :

| personne | année | articles | hausse sur l'année d'avant | issue |
|---|---|---|---|---|
| Johnny Depp | 2022 | 74 203 | +58 400 | n° 1 monde et US |
| Damar Hamlin | 2023 | 29 166 | +29 000 | n° 1 monde et US |
| Zohran Mamdani | 2025 | 23 471 | +23 300 | n° 1 US |
| Kyle Rittenhouse | 2021 | 18 088 | — | n° 1 US |
| Nicolás Maduro | 2026 | 50 264 | **+38 900** | marché : 0,047 monde, 0,128 US |
| Zohran Mamdani | 2026 | 34 963 | +11 500 | (pas coté au n° 1 2026) |
| Lindsay Clancy | 2026 | 8 692 | **+8 670** | marché : 0,225 monde, 0,375 US |
| Erling Haaland | 2026 | 7 190 | +4 500 | marché : 0,11 monde, 0,68 top 5 US |
| Bad Bunny | 2026 | 18 878 | +3 200 | marché : 0,055 monde |

  La presse et le marché ne disent pas la même chose (Haaland, Clancy très cotés pour une hausse de presse modeste ; Maduro peu
  coté pour la plus forte hausse). Les acheteurs regardent sans doute Google Trends (qui est la source), que nous ne pouvons pas lire.

## Sources bloquées (aucun contournement)

- **Google Trends** (`trends.google.com/trends/api/explore`) : 429 dès la première requête (seul le flux RSS du jour répond).
- **Wikimédia** (vues des pages, `wikimedia.org/api/rest_v1/metrics/pageviews`, et `en.wikipedia.org/w/api.php`) : 429 au bout
  de quelques requêtes, puis à chaque essai pendant une heure, même à une requête toutes les 3 s : l'adresse de sortie de la
  routine est partagée. `scripts/vues_wiki.py` est prêt (univers « People », reprise possible).
- **GDELT** : « une requête toutes les 5 s » mais 429 et coupures fréquentes même à 30 s d'écart ; ≈ 1 nom par minute.

## Verdict provisoire

**En cours, pas de verdict.** Le test qui compte n'est pas fait : sur les 18 listes 2017-2025, une mesure lisible mi-novembre
(hausse de presse GDELT, ou vues Wikipédia) classe-t-elle le vrai n° 1 en tête parmi les candidats plausibles ? Sans lui, la
presse n'a aucune autorité contre un prix qui lit probablement Google Trends. **Pas de conviction** (Clancy NON aux États-Unis :
médiane de mes estimations ≈ 0,2 pour le OUI, rapprochée du prix → 0,29, borne basse du NON 0,66 pour un vendeur à 0,63 : sous le
seuil de 5 points). Pas de fantôme : un seul tirage (début décembre), aucune règle mesurée.

## Pour le passage suivant (état sauvegardé)

1. `presse_lent.py` avec les n° 1 à 3 de chaque liste 2017-2025 qui manquent (Matt Lauer, Antonio Brown, Alec Baldwin, Meghan
   Markle, Demi Lovato, Joe Biden, Trump, d4vd, Pope Leo XIV, Kendrick Lamar, Tyler Robinson, Jimmy Kimmel, Karen Read…), puis
   `analyse.py` (rang du n° 1 selon A, D, R, pic de 7 jours). Si la hausse de presse met le n° 1 en tête ≥ 6 fois sur 10 :
   comparer aux prix 2026. Sinon : écarter la presse.
2. Réessayer Wikimédia (`vues_wiki.py`) : les vues de page sont un meilleur reflet des recherches que la presse.
3. Avant le 01/12 : relire les prix ; la liste sort vers le 03-04/12 (2025 : 04/12 vers 07 h UTC). Attention : en 2025 un ingénieur de
   Google a gagné ≈ 1,2 M$ sur ces marchés avec l'information interne (inculpé en mai 2026 : Reuters, CNBC, NBC, 27/05/2026 ;
   ABC 10/11/2026) : un saut de prix juste avant la publication est une information, et le n° 1 inattendu de 2025 (d4vd à 0,01)
   n'était connu que de l'intérieur.
