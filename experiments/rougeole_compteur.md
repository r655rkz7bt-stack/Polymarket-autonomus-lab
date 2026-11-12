# Compteur de la rougeole du CDC contre les échelles « Measles cases in U.S. by <date> » (12/11/2026, piste n° 8)

Passage du chercheur de 1 h (12/11/2026). Suite de la piste n° 8 (« compteurs officiels à lecture directe ») : jusqu'ici
bloquée faute d'historique du compteur.

## Ce qui règle

« Will there be at least <N> measles cases in the U.S. by November 30, 2026? » (événement 1283700, frais météo sur les seuils
≥ 5 000) : compteur « Total Cases » 2026 de `www.cdc.gov/measles/data-research/index.html` à l'échéance (23 h 59, heure de
l'Est). Le compteur affiché = la dernière mise à jour publiée. Les dates « As of » de 2026 sont des **jeudis**
(22/10 4 588, 29/10 4 852, 05/11 5 182).

## Données trouvées ce passage

- **Courbe hebdomadaire du CDC** (`/wcms/vizdata/measles/MeaslesCasesWeekly.json`, lue par la page, sans clé) : cas par semaine
  d'éruption depuis le 02/01/2022 ; la somme des semaines 2026 = le compteur exact (5 182 le 05/11). Les dernières semaines
  sont incomplètes (138 puis 93) et révisées d'une mise à jour à l'autre : une copie datée est gardée à chaque passage
  (`rougeole/scripts/cdc_historique.py` → `rougeole/releves/courbe_hebdo/`).
- **Compteur de fin de mois** reconstitué par les échelles mensuelles réglées (Gamma) : janvier 500-600, février 1 100-1 150,
  mars 1 575-1 600, avril 1 775-1 800, mai 1 950-2 000, juin < 2 140, juillet 2 350-2 380, août 2 900-2 950,
  septembre 3 600-3 700, puis 4 588 (22/10), 4 852 (29/10, « 4 800+ » réglé OUI, « 4 900+ » NON fin octobre), 5 182 (05/11).
  Hausse : ≈ 165 par semaine en septembre, ≈ 300 depuis octobre (264 et 330 aux deux dernières mises à jour) ; par date
  d'éruption ≈ 205 par semaine en août-octobre (892, 894, 806).

## Modèle (`src/polymarket_agent/rougeole.py`)

Semaines restantes avant l'échéance (jeudis : 12, 19, 26/11 pour le 30/11) ; hausse par semaine N(mu + choc commun, sd) avec
mu = 270, sd = 60, choc commun 60 (remplacés par le journal `rougeole:histo` dès 3 hausses) ; chaque mise à jour publiée avec la
chance 0,97, 0,9 la semaine d'un jour férié (Thanksgiving le 26/11, Noël, Nouvel An ; d'abord 0,6 par prudence, puis 0,9 après
vérification sur 2025, ci-dessous). Les cas d'une mise à jour sautée
arrivent à la suivante : seule une mise à jour sautée EN FIN de période retire une semaine.

| seuil au 30/11 | modèle (férié 0,6, abandonné) | modèle (aucun saut) | marché 12/11 01 h (milieu ; acheteur/vendeur) |
|---|---|---|---|
| 5 600+ | 0,889 | 0,964 | 0,9645 (0,945/0,984) |
| 5 800+ | 0,609 | 0,814 | 0,785 (0,66/0,91) |
| 6 000+ | 0,300 | 0,466 | 0,36 (0,15/0,57) |
| 6 200+ | 0,098 | 0,149 | — |

**Le marché cote exactement le modèle sans risque de jour férié.** Tout l'écart tenait à une seule question : le CDC publie-t-il
la semaine de Thanksgiving ? **Vérifié le même passage (CIDRAP, Google Actualités)** : en 2025 le CDC a publié le mercredi 26/11
(veille de Thanksgiving, 1 798 cas), la semaine de Noël (2 012) et le 31/12 (2 065). Les jours fériés ne font pas sauter de mise
à jour → `q_ferie` = 0,9. Modèle corrigé : 5 600+ 0,949, 5 800+ 0,775, 6 000+ 0,434, 6 200+ 0,140 : **le marché avait raison**
(écart ≤ 0,07 au milieu, carnets de 0,04 à 0,42 d'écart) ; aucun achat ni conviction.

Année entière (« in 2026 », événement 91942) : 8 mises à jour (12/11 → 31/12, trois autour de jours fériés) ; « 7 000+ » 0,785,
« 7 500+ » 0,315, proches de mon calcul (5 182 + 8 × 200-300). **Écartée de la stratégie** : la règle ne dit pas si un rattrapage
publié en janvier compte pour 2026.

## Verdict et arène

Pas de test sur le passé possible (compteur hebdomadaire non archivé, dates des mises à jour inconnues) : **expérience
audacieuse** → fantôme `rougeole_compteur` (Kelly entier sur la borne basse = chance − 0,10, un seuil par échelle, source
`rougeole` toutes les 2 h, étiquette `measles` 101906 au scanner). Cycle local (deux cycles, 12/11 01 h 52) : 3 marchés rattachés,
0 proposition (« avantage net insuffisant » ×2, « hors plage » ×1). Une perte apprendrait que le rythme bouge plus que le choc
commun de 60 cas. Avec `q_ferie` 0,9 le fantôme n'achètera que si un carnet s'écarte de ≥ 0,15 du modèle (borne − 0,10, seuil 0,05).

## À faire

- Le 25-26/11 : relire la page du CDC (date « As of » de la semaine de Thanksgiving) pour confirmer `q_ferie`.
- Dès 3 hausses au journal `rougeole:histo`, le rythme vient du journal (vérifier sur `published/data.json`).
- Test possible plus tard : la courbe par éruption d'une mise à jour prévoit-elle la hausse du compteur à la suivante ?
  (`releves/courbe_hebdo/`, une copie par semaine).
