# Test sur le passé : Kalshi prévoit-il mieux que Polymarket sur les matchs ? (16/10/2026)

**Question** : pour le même match, le prix de Kalshi prévoit-il mieux le vainqueur que le prix de
Polymarket ? Si oui, acheter sur Polymarket le côté que Kalshi préfère (quand l'écart dépasse frais +
marge) rapporterait de l'argent.

**Réponse courte : non.** Les deux prix sont presque identiques (écart moyen 0,4 point de
probabilité). Ils prévoient aussi bien l'un que l'autre, et les rares écarts sont plus petits que
les frais plus l'écart achat-vente. **Il n'y a pas de stratégie à en tirer.** Ce résultat négatif est
solide : 1 813 matchs appariés, 14 ligues, 4 instants de décision.

## Données (toutes réelles, publiques, sans clé ni abonnement)
- **Kalshi** : marchés « match » réglés (`/trade-api/v2/markets?series_ticker=…&status=settled`),
  du 1er/09 au 15/10/2026, 14 séries : KXMLBGAME, KXNFLGAME, KXNHLGAME, KXNBAGAME (présaison),
  KXWNBAGAME, KXNCAAFGAME, KXEPLGAME, KXUCLGAME, KXUELGAME, KXLALIGAGAME, KXBUNDESLIGAGAME,
  KXSERIEAGAME, KXLIGUE1GAME, KXMLSGAME. Prix : chandeliers d'**une minute**
  (`/series/{série}/markets/{ticker}/candlesticks?period_interval=1`, sans clé : vérifié), avec le
  meilleur acheteur et le meilleur vendeur du « Oui » à la fin de chaque minute.
- **Polymarket** : marchés « vainqueur » clos (`gamma-api /markets?sports_market_types=moneyline&tag_id=…`),
  avec leur heure de coup d'envoi (`gameStartTime`) et leur barème de frais (0,05 la plupart du temps,
  0,03 pour une partie du baseball et la MLS). Prix : historique public du CLOB (`prices-history`, pas
  d'une minute).
- Tags Gamma utilisés : MLB 100381, NFL 450, NHL 899, NBA 745, WNBA 100254, foot US universitaire 100351,
  Premier League 306, Ligue des champions **100977**, Ligue Europa 101787, Liga 780, Bundesliga 1494,
  Serie A **101962**, Ligue 1 102070, MLS 100100 (le « primaryTagId » de `/sports` ne marche pas pour la
  Ligue des champions et la Serie A).

## Appariement des matchs
Même ligue ; coup d'envoi Polymarket à moins de 3 h (baseball, à cause des programmes doubles) ou 8 h
(autres) du coup d'envoi Kalshi estimé (`expected_expiration_time` − 3 h : écart médian mesuré = 0 min) ;
les **deux** équipes reconnues (abréviation identique après une petite table d'équivalences, ou noms
qui se ressemblent : « New York Y » ~ « New York Yankees », « Frankfurt » ~ « Eintracht Frankfurt ») ;
un pour un, sinon écarté. Contrôle : le vainqueur est le même des deux côtés.

| Ligue | matchs Kalshi | matchs Polymarket | appariés |
|---|---|---|---|
| Baseball (MLB) | 404 | 396 | 389 |
| Foot US (NFL) | 79 | 78 | 78 |
| Foot US universitaire | 717 | 742 | 709 |
| Hockey (NHL) | 177 | 175 | 172 |
| Basket NBA (présaison) / WNBA | 55 / 46 | 53 / 46 | 53 / 44 |
| Premier League / Liga / Bundesliga / Serie A / Ligue 1 | 40 / 48 / 36 / 40 / 36 | 40 / 48 / 36 / 40 / 36 | 40 / 42 / 36 / 36 / 36 |
| Ligue des champions / Ligue Europa / MLS | 36 / 36 / 106 | 36 / 36 / 106 | 36 / 36 / 106 |
| **Total** | | | **1 813** |

Aucun match ambigu, **aucun désaccord sur le vainqueur** entre les deux plateformes.
Propositions comparées : en sport à 2 issues, « l'équipe A gagne » (1 par match) ; en football,
3 propositions par match, chacune comparée à la même chez l'autre (« A gagne », « match nul »,
« B gagne », temps réglementaire des deux côtés). Total : 2 549 propositions.

## Méthode (sans regard vers le futur)
Instants de décision : 24 h, 6 h, 2 h et 30 min avant le coup d'envoi. À chaque instant :
- prix Polymarket = dernier point de l'historique **au plus tard** à cet instant (au plus 6 h avant) ;
- prix Kalshi = milieu (acheteur + vendeur) / 2 à la fin de la dernière minute close **au plus tard**
  à cet instant ; en sport à 2 issues, moyenne de « A gagne » et de 1 − « B gagne ».
Modèles jugés contre le prix Polymarket (harnais `idea_test.py`) : (a) Kalshi seul ; (b) moyenne des
deux ; (c) Polymarket déplacé vers Kalshi d'un facteur k réglé sur la première moitié des dates.
**Jugement sur la seconde moitié des dates** (22-23/09 → 15/10). Simulation : 1 part par pari, achat sur
Polymarket du côté jugé sous-coté si l'avantage, après frais réels (taux × p × (1 − p)) et écart
achat-vente simulé, dépasse le seuil.

## Résultats

Qualité des prévisions (plus bas = mieux) :

| Avant le match | cas (test) | Brier tout l'échantillon PM / Kalshi | Brier test PM | (a) Kalshi | (b) moyenne | (c) déplacé | Log loss test PM / Kalshi | écart moyen \|K − PM\| | écarts > 0,02 / > 0,03 (tout) |
|---|---|---|---|---|---|---|---|---|---|
| 24 h | 2 486 (1 091) | 0,1932 / 0,1933 | 0,2010 | 0,2012 | 0,2011 | 0,2010 (k = 0) | 0,5868 / 0,5872 | 0,0046 | 45 / 14 |
| 6 h | 2 490 (1 079) | 0,1921 / 0,1920 | 0,1994 | 0,1992 | 0,1993 | 0,1992 (k = 0,95) | 0,5830 / 0,5826 | 0,0040 | 20 / 5 |
| 2 h | 2 490 (1 086) | 0,1918 / 0,1919 | 0,2000 | 0,1998 | 0,1999 | 0,2000 (k = 0) | 0,5844 / 0,5838 | 0,0036 | 16 / 2 |
| 30 min | 2 488 (1 090) | 0,1915 / 0,1915 | 0,1992 | 0,1992 | 0,1992 | 0,1993 (k = 1,5) | 0,5829 / 0,5829 | 0,0039 | 23 / 3 |

**Lecture** : les deux plateformes sont **aussi bien étalonnées l'une que l'autre** (différences de
Brier au 4e chiffre après la virgule, dans le bruit). Même chose ligue par ligue, sur la seconde
moitié des dates : 14 ligues × 4 instants = 56 comparaisons, Polymarket meilleur dans 29, Kalshi meilleur
ou égal dans 27, plus grand écart de Brier 0,0023 (WNBA, 24 h, 25 cas) (détail dans `resultats.json`, clé `par_ligue`).
Le facteur k « réglé » saute de 0 à 1,5 selon l'instant : signe qu'il n'y a rien à régler.

Simulation, modèle (a) Kalshi seul, seconde moitié des dates — paris / rendement des mises / jours gagnants :

| Avant le match | seuil 0, écart 0 (irréaliste) | seuil 0, écart 0,01 | seuil 0,02, écart 0,01 | seuil 0,03, écart 0,01 | seuil 0,05, écart 0,01 | seuil 0,02, écart 0,02 |
|---|---|---|---|---|---|---|
| 24 h | 346 / −0,2 % / 9 sur 19 | 36 / −6,3 % / 5 sur 7 | 2 / +71,8 % | 1 / +71,8 % | 0 | 1 / +68,9 % |
| 6 h | 318 / +4,0 % / 11 sur 20 | 26 / −5,2 % / 1 sur 4 | 0 | 0 | 0 | 0 |
| 2 h | 304 / +4,5 % / 9 sur 18 | 23 / −11,7 % / 2 sur 6 | 0 | 0 | 0 | 0 |
| 30 min | 308 / +5,6 % / 9 sur 19 | 19 / +12,3 % / 4 sur 5 | 0 | 0 | 0 | 0 |

- Avec un écart achat-vente réaliste (0,01-0,02) et un seuil de 0,02 à 0,05 : **0 à 2 paris en
  3 semaines et demie** sur ~1 080 propositions. Les « +70 % » portent sur 1 ou 2 paris : pur hasard.
- Même dans le cas irréaliste (aucun écart achat-vente, seuil nul, ~300 paris) : +4 à +6 % avec
  environ un jour gagnant sur deux, alors que l'erreur type d'un rendement sur 300 paris à ~0,5 est
  d'environ ±6 % : rien de distinguable de zéro.
- Modèles (b) et (c) : pas mieux (par ex. (c) à 30 min, seuil 0, écart 0,01 : 105 paris, +1,0 %,
  3 jours gagnants sur 12).
- Restreint aux cas où le carnet Kalshi est serré (écart acheteur-vendeur ≤ 0,02, ~1 000 cas du
  test) : mêmes Brier, 18 à 25 paris au seuil 0, rendements de −12 % à +16 % selon l'instant : du bruit.

**Qui suit qui ?** Quand Kalshi et Polymarket diffèrent de plus de 0,02, le prix Polymarket se
rapproche un peu de Kalshi dans les 15 minutes qui suivent (pente 0,12 à 0,29 ; mouvement moyen
dans le sens de Kalshi : +0,3 à +1,5 point). Mais ces écarts sont **rares** (16 à 45 cas sur ~2 490 par
instant, sur tout l'échantillon) et le rattrapage moyen (≤ 1,5 point) est plus petit que l'écart
achat-vente plus les frais (≈ 2,25 points à p = 0,5). Pas exploitable non plus avec des ordres preneurs.

## Conclusion
Sur les matchs, Polymarket et Kalshi donnent **le même prix** (à 0,4 point près en moyenne) et le
même niveau de prévision, de 24 h à 30 min avant le coup d'envoi, dans toutes les ligues testées. Des
teneurs de marché (et des robots d'arbitrage) relient visiblement les deux carnets. **Copier Kalshi
sur Polymarket ne rapporte rien après frais** ; aucune proposition de stratégie de production.
Ce qu'on en retient pour le labo :
- le prix Polymarket d'un match est déjà une prévision « consensus » de bonne qualité : pour battre
  ce marché, il faudrait une information que Kalshi n'a pas non plus (pas un autre marché de paris) ;
- Kalshi reste utile comme **contrôle de cohérence gratuit** (un prix Polymarket très loin de Kalshi
  signale un carnet vide ou une erreur de lecture), pas comme source d'avantage.

## Limites (honnêtes)
- Les prix historiques ne sont pas des prix exécutables : Polymarket = point de l'historique CLOB
  (dernier échange / milieu), Kalshi = milieu acheteur-vendeur à la fin d'une minute. L'écart
  achat-vente de Polymarket est simulé. Comme on ne trouve rien même sans écart, cela ne change pas
  la conclusion.
- Sémantique Kalshi : un chandelier d'une minute n'existe que si quelque chose a bougé ; on prend le
  dernier dont la fin est ≤ l'instant de décision (jusqu'à 6 h avant). Heure de coup d'envoi = celle de
  Polymarket ; Kalshi aligné via `expected_expiration_time − 3 h` (contrôlé : écart médian 0).
- Taille : 3 semaines et demie de test (~1 080 propositions par instant), une seule saison (septembre-
  octobre : baseball en fin de saison et séries éliminatoires, débuts NFL/NHL, NBA en présaison).
  En football, les 3 propositions d'un même match sont liées (pas indépendantes).
- ~60 propositions par instant écartées faute de prix des deux côtés ; quelques matchs non appariés
  (noms trop différents, surtout Liga et foot US universitaire) : sans effet visible sur la conclusion.
- On a testé des ordres preneurs (frais payés). Un ordre posé (sans frais, avec ristourne) qui
  attendrait l'écart ne se jugera qu'en direct, et les écarts > 0,02 sont trop rares pour que ça vaille
  la peine.

## Refaire le test
```
python3 -I experiments/sport_kalshi/collect.py <dossier_de_travail> src 2026-09-01 2026-10-15   # ≈ 2 min
python3 -I experiments/sport_kalshi/match.py <dossier_de_travail> src                          # quelques secondes
python3 -I experiments/sport_kalshi/prices.py <dossier_de_travail> src                         # ≈ 45 min (Kalshi limite la fréquence)
python3 -I experiments/sport_kalshi/evaluate.py <dossier_de_travail> src                       # écrit resultats.json
```
Tout est gardé en cache dans `<dossier_de_travail>` (relancer ne retélécharge rien). Code commun
(ligues, tags, noms d'équipes) : `experiments/sport_kalshi/common.py`.
