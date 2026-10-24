# Barres touchées par l'or, l'argent, le pétrole et le gaz : « What will <matière> hit Week of … » (24/10/2026, après-midi)

Famille nouvelle (découverte en recensant les familles d'événements Gamma réglés depuis janvier 2026, par volume) : ~25 actifs (matières premières, actions, indices) ont chaque semaine
une échelle de barres « Will Gold (XAUUSD) hit (HIGH) $4,300 Week of October 26 2026 ? » et « (LOW) $3,900 », réglée sur les **bougies d'1 minute de Pyth** (« any Pyth 1-minute candle … High or Low equal to or
beyond the listed price », après la création du marché, séances de la semaine). Volumes : 40-50 k$ par semaine et par matière (mensuels : 4-60 M$ pour le pétrole). Pas de piste équivalente jusqu'ici :
`toucher_avant_fin` (22/10) ne testait que Bitcoin/Ethereum/Solana « dans la journée » contre « au-dessus de X à midi ».

## En bref
- **Question.** La chance de toucher une barre avant la fin de la semaine, calculée par une barrière brownienne à partir du prix, de la volatilité et des extrêmes déjà atteints, est-elle mieux étalonnée que le prix du marché ?
- **Données.** 112 échelles hebdomadaires réglées (28 semaines d'avril à octobre 2026 × pétrole WTI, gaz naturel, or, argent ; ≈ 18 barres par échelle) ; prix horaires des contrats à terme (Yahoo Finance, API de graphique, **pour la recherche seulement**) ;
  vrais échanges (`idea_test.fetch_event_trades`). Règlement relu : les barres horaires redonnent l'issue officielle dans **96 %** des cas (WTI 411/426, gaz 430/456, or 419/470, argent 442/494 ; les écarts sont des barres à moins d'une heure de bougie près).
- **Protocole.** Décision chaque jour à 14 h UTC de la création du marché au jeudi ; prix connu = barres horaires FINIES avant la décision (premier essai : une barre en cours → regard d'une heure vers le futur, corrigé) ; barre déjà touchée : pas de pari ;
  achat au premier échange réel dans les 2 h, résultat officiel Gamma ; seuils d'écart (chance − prix) 0,05 / 0,10 / 0,20 ; 4 matières → 12 réglages, plus les variantes de volatilité (10 derniers jours, ou fixe sur l'année) et les découpages : ~25 regards.
- **Résultat (volatilité des 10 derniers jours, fichier `resultats_paris_volatilite_10_jours.txt`).** Les quatre matières ensemble, seuil 0,05 : **328 paris sur 98 événements, +33,5 % par pari, t par événement +2,35, z des prix +1,96 (178 gagnés pour 163 attendus), 5 mois sur 7 gagnants, +19 % sans les 3 meilleurs paris** ;
  seuil 0,10 : 199 paris, +52,8 %, t +2,27, z +2,0. `idea_test.verdict` : « retenue ». Par matière : or +53 % (z +1,4), pétrole +18 %, gaz +29 %, argent +29 % (sans les 3 meilleurs : or +16 %, les trois autres ≈ 0).
  Avec une **volatilité fixe** (médiane quadratique de l'année : or 0,36 %, argent 0,80 %, pétrole 0,74 %, gaz 0,91 % par heure) : or +55 %/+72 %, gaz +62 %/+70 %, pétrole +4 %/+20 %, argent +21 %/+26 % : même sens.
- **Où est le gain.** Seulement les barres cotées **0,10-0,45** : 0,15-0,40 → +61 % (91 paris, t par événement +2,66, z des prix +2,9) ; < 0,15 → +139 % (42 paris, 9 gagnés pour 4,3 attendus) ; **≥ 0,40 : −3 % à 0 %** (195 paris). Le marché sous-cote les touches
  de barres éloignées (OUI) et sur-cote leur NON ; il est bien étalonné près de la barre. Le gain est dans les deux sens (OUI +38 %, NON +30 %).
- **Contre-épreuve sur les échelles MENSUELLES** (« What will Gold / Silver / WTI / Natural Gas hit in <mois> », 22 événements réglés, même code avec `MOIS=1`, `resultats_mensuels.txt`) : **pas de répétition**. Pétrole −60 % (6 paris), gaz −5 % (30 paris), argent −4 % / −13 % (61 / 53),
  or +27 % / +99 % (42 / 37 paris, seule matière positive) ; log-score du modèle 0,368 contre 0,320 pour le marché (nettement pire que sur les semaines). L'effet ne se retrouve que sur les échelles hebdomadaires et surtout sur l'or : raison de plus pour rester en fantôme à quart de Kelly.
- **Ce qui inquiète.** Septembre (−17 %, 62 paris) et octobre (−18 %, 47 paris) perdent : l'effet s'est peut-être résorbé (ou le hasard : z −1,7 et −1,0). Le log-score du modèle est **moins bon** que celui du marché (0,471 contre 0,451 pour le pétrole et le gaz ; 0,617 contre 0,608
  pour l'or et l'argent) : l'avantage ne vient que des endroits où le modèle s'écarte beaucoup du marché. Or et argent : contrat à terme (GC=F, SI=F) au lieu du prix au comptant de Pyth (écart de base ≈ 1 %).
  Le prix payé est celui du premier échange réel après la décision, pas un carnet profond : marchés minces (médiane de quelques dizaines de dollars par échange).
- **Verdict : RETENUE au sens d'`idea_test` (t 2,35, z 1,96, 5/7 mois), mais fragile** (~25 regards, effet qui s'affaiblit, modèle moins bon que le marché en log-score) → fantôme `toucher_metaux` (quart de Kelly), or et argent seulement.

## Production (fantôme `toucher_metaux`)
- **Source des prix** : l'historique de Pyth (arbitre) demande désormais une clé (`benchmarks.pyth.network` : 401, `hermes.pyth.network/v2/updates/price/*` : 401 ; seule la liste des flux répond), Yahoo n'a pas d'API documentée (interdit par `CHANTIERS.md`),
  Stooq ne répond pas. **gold-api.com** (sans clé) donne l'or (XAU) et l'argent (XAG) au comptant : `sources/goldapi.py`, relevé à chaque cycle dans la table `prix_matieres` (`matieres.record_prices`). Pas de pétrole ni de gaz (aucune source libre).
- **Extrêmes** : le maximum et le minimum déjà atteints depuis la création du marché viennent de ce journal (relevés de 5 minutes) ; le fantôme ne joue qu'un marché que le journal couvre depuis sa création (premier relevé ≤ 12 h après) :
  **les barres de la semaine du 26/10 (créées le 23/10 à 22 h) ne sont pas couvertes ; premiers achats attendus pour la semaine du 02/11** (marchés créés vers le 30/10). Barre à moins de 0,1 % d'un extrême relevé : pas de loi (une bougie d'1 minute a pu la toucher).
- **Modèle** : `matieres.hit_probability` (barrière brownienne sans dérive, σ horaire fixe, τ = heures restantes × 23/24, loi en service jusqu'à 18 h avant la fin) ; achat si chance − prix ≥ 0,10, prix demandé 0,08-0,50, au plus 3 barres par semaine, chance plafonnée à 0,05-0,95.
- Tests : `tests/test_matieres.py` (formule, journal, couverture, barre touchée / incertaine, collecteur, stratégie). Scanner : étiquettes `gold` (101589) et `silver` (100733) (60 marchés, dont 28 hebdomadaires, au cycle local).

## À faire au prochain passage
1. Relancer le test avec les semaines d'octobre-novembre réglées (confirmer ou non l'affaiblissement de septembre-octobre) : `experiments/commodites_toucher/scripts/prix_yahoo.py` puis `backtest.py WTI,NG,XAUUSD,XAGUSD` (`PYTHONPATH=src`), `releve_evenements.py` d'abord.
2. Pétrole et gaz : chercher une source libre de prix (contrats ICE WTI / NYMEX NG, ou clé Pyth gratuite : à demander à Etienne) ; mensuels (« in October 2026 », 4,2 M$ pour le pétrole) à tester de la même façon.
3. Actions (NVDA, TSLA, AAPL… : mêmes échelles hebdomadaires, 1 à 3 événements réglés par action) : trop peu d'historique pour l'instant.
4. Lire le journal `prix_matieres` publié (sauvegarde de la base) et le comparer aux bougies Pyth si une clé devient disponible.

## Fichiers
`scripts/releve_evenements.py` (événements Gamma), `prix_yahoo.py` (prix horaires, recherche seulement), `backtest.py` (test : modes `PREMIER=1`, `SIGMA_FIXE=1`), `analyse.py` (découpages), `resultats_paris_volatilite_10_jours.txt`. Données : `donnees/` (ignoré par Git).
