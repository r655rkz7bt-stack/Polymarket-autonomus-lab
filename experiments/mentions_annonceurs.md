# Mentions : « the announcers » et « anyone » (passage du 21/10/2026)

Piste n° 1 de `PISTES.md`. Question : sur les marchés « dira-t-on ce mot pendant ce match / cet épisode ? »
dont l'orateur est « the announcers » (commentateurs) ou « anyone » (n'importe qui), le taux de OUI passé du
même mot bat-il le prix ? (Le 20/10, ces deux orateurs étaient les meilleurs morceaux de `mots_prononces`
sur le passé : +29 % à +45 %.) Scripts : `experiments/mentions_annonceurs/` (données dans `donnees/mn/`,
ignorées par Git).

## Données
- 3 555 marchés réglés (Gamma, tag `mention-markets`) : 1 982 « the announcers » (95 événements, 61 Coupe du
  monde 2026, 34 NFL / UFC / football universitaire), 1 574 « anyone » (103 événements : Big Brother, Love
  Island, Rick and Morty, House of the Dragon, South Park, résultats d'entreprises, débats).
- Prix horaires (`prices-history` avec fenêtre explicite `startTs/endTs` : `interval=max` ne rend presque
  rien pour les marchés clos depuis longtemps, 269 marchés sur 3 555) et vrais échanges (`data-api`
  `trades?eventId=`, médiane 253 échanges par événement, soit une douzaine par marché).
- **Contrôle du règlement** : 9 familles de seuils (« Goal 20+ / 40+ / 60+ times ») dans un même événement,
  607 marchés : 0 incohérence (un seuil haut OUI avec un seuil bas NON).
- Jamais de regard vers le futur : le taux d'un mot est calculé avec les seuls marchés de la même série
  RÉGLÉS avant l'instant de décision.

## Résultat 1 : l'illusion du prix « historique » (+31 % → −7 %)
Avec le prix horaire du CLOB deux heures après l'ouverture (méthode du 20/10) : 1 192 achats, **+31 % par
achat, t +6,8**, log-score du taux historique −0,556 contre −0,605 pour le marché. Mais 467 marchés
« anyone » et 248 marchés « annonceurs » sont à **exactement 0,50** : carnet vide, milieu sans valeur
(Big Brother : 0,505 pendant 18 heures de suite). Ces « prix » ne sont pas exécutables : c'est le défaut
du 16/10 (météo : +28 % au test, −6 % aux prix des vrais échanges) qui revient.

Aux prix des **vrais échanges** (premier échange de preneur sur le jeton après l'instant de décision, +0,01
d'écart, frais 0,04·p·(1−p) du barème `mentions_fees` relu sur Gamma, aucun échange dans la fenêtre = pas de
pari) : 220 achats, **−6,7 %** (t −0,6) ; sur 7 réglages (délai 2 à 24 h après l'ouverture, fenêtre 2 à 24 h,
marge 3 à 8 points, 3 à 5 précédents) le rendement va de −27 % à +16 % sans régularité. Log-score aux prix
payés : marché −0,55, taux historique −0,63 : **le taux d'un mot ne bat pas le prix**.
- **« anyone » : écartée**. Presque aucun échange (4 achats possibles en tout) : séries sans liquidité, les
  +60 % du test historique n'existent pas.
- **Coupe du monde (annonceurs) : écartée**. 7 réglages sur 7 négatifs, −4 % à −34 % par achat (200 à 500
  achats, 43 à 56 événements).

## Résultat 2 : un indice, les matchs de NFL
Reste « the announcers » hors Coupe du monde. En séparant les matchs de NFL / football américain (titre
« … game ») de l'UFC et en ne calculant le taux que sur les matchs de NFL :

| délai (h) | marge | K | précédents | fenêtre (h) | achats | événements | rendement | t par événement |
|---|---|---|---|---|---|---|---|---|
| 2 | 0,05 | 2 | 3 | 24 | 72 | 14 | +68 % | +4,8 |
| 12 | 0,05 | 2 | 3 | 12 | 38 | 12 | +91 % | +2,4 |
| 2 | 0,05 | 2 | 3 | 6 | 20 | 4 | +44 % | +2,8 |
| 6 | 0,05 | 2 | 3 | 12 | 38 | 11 | +61 % | +2,3 |
| 2 | 0,08 | 2 | 3 | 12 | 34 | 10 | +75 % | +3,3 |
| 2 | 0,03 | 5 | 5 | 24 | 92 | 13 | +21 % | +0,8 |

6 réglages sur 6 positifs ; deux moitiés dans le temps toutes deux positives (+89 % avant le 20/09, +58 % après, taux NFL + UFC mêlés) ;
septembre et octobre gagnants. Par prix payé : 0,30-0,70 → +40 % (45 achats), 0,10-0,30 →
+174 % (19 achats, fragile), ≥ 0,70 → +6 %, < 0,10 → perte.

**Verdict : indice, pas retenue.** Raisons : 14 matchs seulement et deux mois (début de saison NFL) ;
une quinzaine de découpages regardés au total (séries, sport, moitiés, réglages) ; marchés minces
(une douzaine d'échanges par marché : les mises de l'arène pourraient ne pas être servies) ; le test
« Coupe du monde » sert de contre-épreuve négative, mais la valeur du mot « NFL » a été choisie après coup.
→ fantôme `mots_prononces_nfl` (filtres `question_contient: ["game?"]`, `question_exclut: ["world cup",
"ufc"]`), à confirmer sur de nouveaux matchs (NFL : un par semaine, jeudi / dimanche / lundi).

## Changements dans le code
- `references.mention_key` : trois historiques séparés pour « the announcers » (Coupe du monde, matchs
  « … game », autres) ; avant, 1 408 marchés de football et 573 de NFL / UFC faisaient un seul taux.
- `Filtered` : filtres `question_contient` / `question_exclut`.

## Reste ouvert
- `mots_prononces` (mère, Trump surtout) reste sans filtre : elle peut encore jouer des « annonceurs » Coupe
  du monde (perdants) maintenant qu'ils ont leur historique à part ; suivre son journal.
- Vérifier sur les prochains matchs NFL (6 par semaine environ) que le carnet réel sert les mises.
