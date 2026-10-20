# Vingt nouvelles pistes (20/10/2026)

**Demande d'Etienne** : « Fais une recherche pour 20 stratégies différentes de celles qu'on a déjà
(explore de nouvelles pistes), qui auront elles-mêmes des filles petit à petit. »

## Ce qu'on avait déjà (à ne pas refaire)
Favori (50 variantes), retour à la moyenne, calibrage, seuils crypto (modèle log-normal), échelles
de seuils, déséquilibre du carnet, nouvelles + mouvement, annonce officielle, sentiment social,
météo (prévisions, plancher de température), tenue de marché, suivre / contrer un mouvement, fin de
match, cotes des bookmakers (vainqueur), vague d'opinion, parking politique.
**Déjà testées et écartées sur le passé** (pas reprises) : copier les portefeuilles gagnants
(experiments/smart_money.md : top 1 % → −9,7 % ensuite) ; Kalshi contre Polymarket en sport
(experiments/sport_kalshi.md : prix identiques à 0,4 point près).

## Recherche (web, 20/10/2026)
- Les robots qui gagnent vivent surtout de la **tenue de marché** et des **arbitrages entre issues
  liées** ; les arbitrages simples durent quelques secondes ([Medium, 2026](https://medium.com/illumination/beyond-simple-arbitrage-4-polymarket-strategies-bots-actually-profit-from-in-2026-ddacc92c5b4f) ; [QuickNode](https://www.quicknode.com/ja/builders-guide/best/top-10-polymarket-trading-bots)).
- « **Nothing ever happens** » : 73 % des marchés réglés finissent en NON ; marchés de 90 à 180 jours :
  73,5 % de NON, moins d'une semaine : 52 % ([Decrypt](https://decrypt.co/364381/polymarket-bot-bets-no-has-a-point?amp=1)). Débattu : c'est peut-être déjà dans les prix
  ([Delta Confidence](https://deltaconfidence.substack.com/p/nothing-ever-happens)). → piste « décroissance du temps », qui mesure le prix CONTRE le temps qui passe.
- Marchés « **mentions** » (« dira-t-il tel mot ? ») : la méthode décrite est le taux de base
  historique ([DeFi Rate](https://defirate.com/prediction-markets/mention-markets/)).
- Marchés « **combien de tweets** » : réglés par le compteur XTracker de Polymarket ; méthode
  décrite : projeter le rythme ([fiche d'outil](https://skills.cat/skills/spartanlabsxyz/simmer-sdk/polymarket-elon-tweets)). API XTracker publique (vérifiée le 20/10).
- **Données économiques** : Kalshi prévoit l'inflation un peu mieux que le consensus Bloomberg
  (étude de la Fed, [Fortune](https://www.fortune.com/2026/01/28/kalshi-prediction-market-federal-reserve-betting-forecast-nber-working-paper)) → Kalshi comme référence HORS sport.
- Thèse de Princeton sur Polymarket : prix globalement **trop prudents** (pente de recalibrage
  1,11), sport le moins bien calibré ([Princeton](https://theses-dissertations.princeton.edu/entities/publication/d5708372-5ea3-4252-b669-7f9cee07387c)).
- Sources gratuites vérifiées en direct le 20/10 : Kalshi (200), PredictIt (200), Manifold (200),
  XTracker (200), échanges publics de Polymarket (200). Refusées : Metaculus (compte obligatoire),
  Binance depuis le labo (451), Wikimedia depuis le labo (429).

## Les vingt pistes
| # | Stratégie | Idée | Données | Lot |
|---|---|---|---|---|
| 1 | decroissance_temps | « d'ici le 31 » : le OUI doit fondre avec le temps | Polymarket | A |
| 2 | echelle_dates | « d'ici juin » ≤ « d'ici décembre » (arbitrage) | Polymarket | A |
| 3 | coherence_match | handicap ≤ vainqueur dans un même match (arbitrage) | Polymarket | A |
| 4 | implication_politique | président ≤ candidat du parti (arbitrage) | Polymarket | A |
| 5 | paire_oui_non | OUI + NON < 1 (arbitrage) | Polymarket | A |
| 6 | outsiders_surcotes | somme des OUI > 1 : NON aux outsiders | Polymarket | A |
| 7 | marche_neuf | marché tout neuf trop prudent : renforcer le favori | Polymarket | A |
| 8 | apres_echeance | échéance passée, pas encore réglé : le favori | Polymarket | A |
| 9 | marches_jumeaux | même question, deux prix (arbitrage) | Polymarket | A |
| 10 | choc_sans_nouvelle | gros mouvement sans nouvelle : retour partiel | Polymarket + nos nouvelles | A |
| 11 | compteur_tweets | rythme des tweets → chance de chaque tranche | XTracker | B |
| 12 | kalshi_reference | même question sur Kalshi (hors sport) | Kalshi | B |
| 13 | predictit_reference | même candidat sur PredictIt | PredictIt | B |
| 14 | manifold_reference | même question sur Manifold | Manifold | B |
| 15 | futurs_bookmakers | champion de la saison contre Pinnacle | The Odds API | B |
| 16 | football_trois_issues | victoire / nul / victoire contre les bookmakers | The Odds API | B |
| 17 | cotes_tennis | tennis contre Pinnacle (le morceau qui gagne) | The Odds API | B |
| 18 | fatigue_nhl | équipe qui a joué la veille | API de la NHL | C |
| 19 | mots_nouveaux | « dira-t-il ce mot ? » jamais proposé : le OUI est trop cher | Polymarket | C |
| 20 | mots_prononces | « dira-t-il ce mot ? » : combien de fois il l'a déjà dit | Polymarket | C |

Écartées après test sur le passé (lot C) : haut_ou_bas_crypto (prévue en n° 19), totaux de buts
NHL, séries de victoires ou de défaites NHL. Pour mots_prononces, le taux historique des marchés
passés a remplacé l'idée de départ (fréquence dans Google Actualités, impossible à tester sur le
passé).

## Lot A : essai à blanc en direct (20/10/2026, vers 9 h UTC)
Scan réel (922 marchés dont 100 échus), carnets réels, journal d'essai à 1 000 :
decroissance_temps 31 candidats → 1 proposition ; echelle_dates 2 ; coherence_match 7 ;
outsiders_surcotes 22 ; marche_neuf 30 ; apres_echeance 1 candidat → 1 proposition ;
marches_jumeaux 6 → 4 propositions (« Will there be no Hormuz agreement? » à 0,931 et 0,871 dans
deux événements combinés : règle durcie, même description et même échéance exigées) ;
implication_politique, paire_oui_non, choc_sans_nouvelle : rien à ce moment-là (arbitrages rares).
Après l'échéance, un favori encore à 0,90 a souvent une raison (« Russia target Kyiv on October
17 ? ») : seuil relevé à 0,94 ; les marchés en contestation UMA (températures du Cap) sont écartés.

## Lot B : vérifications en direct et sur le passé (20/10/2026)
**Rattachements** (scan réel du 20/10 vers 11 h UTC) : Kalshi 2 marchés, PredictIt 8, Manifold 0
à ce moment-là, compteur de tweets 26 marchés. Les premiers rattachements PredictIt contenaient des
erreurs (« course la plus serrée » du Texas, vice-président pris pour président, tranches d'écart,
district pris pour chambre) : règles durcies (mots du contrat ET du marché, mêmes nombres, aucun
nombre en trop) ; après correction, les 10 rattachements relus à la main étaient justes.

**Compteur de tweets** : premier essai en direct, le modèle (rythme des 72 dernières heures,
dispersion 4) s'écartait beaucoup du marché (« moins de 40 » : 0,051 au marché, 0,208 au calcul).
Vérifié sur le passé avant d'envoyer :
- XTracker garde chaque message (`/api/users/{compte}/posts`) : le nombre de messages de chaque
  période en cours égale exactement son « Post Counter » (131, 107, 126, 90, 34, 14, 18, 1 le 20/10).
  Le relevé lit désormais 14 jours de messages heure par heure (avant, seulement la période en cours).
- **Calibrage** (7 comptes, toutes les semaines depuis le début de leur historique, une prévision
  toutes les 6 h, 6 058 prévisions) : meilleur réglage = moitié rythme des 7 derniers jours, moitié
  rythme des 14 derniers jours, dispersion 8 à 16 (dispersion 4 : tranches trop larges).
- **Contre le marché** (177 périodes passées, juillet-octobre 2026, prix réels heure par heure,
  frais 0,05·p·(1−p) et demi-écart 0,01 à 0,02 comptés) : avec la dispersion 4, perte (−13 % par
  achat) ; dispersion 12 : log-score du modèle −1,046 contre −1,085 pour le marché. Les billets à
  moins de 0,10 perdent avec tous les réglages (−34 % à −63 %) : `min_price 0,10`. Avec la
  dispersion 12 et ce plancher : +12 % par achat, gagnant chaque mois (juillet +22 %, août +3 %,
  septembre +15 %, octobre +5 %), moyenne par période +8 % (t 1,7). NYC Mayor (très peu de
  messages) perd avec tous les réglages : une fille sans lui pourra le vérifier.

## Lot C : vérifications sur le passé (20/10/2026)
- **haut_ou_bas_crypto, écartée** : 444 marchés quotidiens « Bitcoin / Ethereum / Solana / XRP Up
  or Down » (juillet-octobre 2026), prix réels toutes les 10 minutes, Binance (la source de
  règlement, notre lecture redonne le règlement dans 443 cas sur 444). Modèle log-normal (prix
  actuel contre prix d'ouverture, volatilité horaire de 7 jours) : log-score −0,540 contre −0,521
  pour le marché ; acheter quand le modèle s'écarte de 3 points : **−16 % par achat** (3 880
  achats, t −8), perdant sur les 4 monnaies et à toute heure. Frais 0,07·p·(1−p) en plus. Le
  marché est plus juste que le modèle : pas de stratégie.
- **fatigue_nhl, retenue (faible)** : saisons 2024-25 et 2025-26, calendrier officiel de la NHL et
  1 861 matchs Polymarket (prix une heure avant le match). Équipe qui a joué la veille, à
  l'extérieur, contre un adversaire reposé : 299 matchs, 37,8 % gagnés pour un prix moyen de
  43,2 % (−5,4 points ; −5,7 en 2024-25, −5,1 en 2025-26) ; acheter l'adversaire reposé au prix
  + 0,01, frais 0,05·p·(1−p) : +6,1 % par achat (t +1,2). À domicile : −3,3 points (99 matchs,
  +5,7 %, t +0,5). Matchs sans fatigue : rien (−1 point). Même sens les deux saisons, mais encore
  faible statistiquement : fantôme, l'arène tranchera.
- **mots_prononces, retenue** : 21 824 marchés « mentions » réglés ; prix réels pour 3 000 marchés
  dont le mot avait déjà au moins 3 précédents chez le même orateur. Taux historique du mot,
  rapproché du taux de l'orateur (2 marchés fictifs). En moyenne, le marché est mieux calibré
  (log-score −0,536 contre −0,576). Mais acheter quand le taux s'écarte de 5 points ET que le
  billet coûte au moins 0,30, frais 0,04·p·(1−p) et 0,02 d'écart comptés : +19 % par achat
  (223 achats, t +2,8) au prix de deux heures après l'ouverture, +27 % (t +4,0) à douze heures,
  +21 % à vingt-quatre heures ; moyenne par événement +11 % (t +1,3) à +26 % (t +3,2). Sous 0,30 :
  rien ou perte. Les questions « Will "X" be said » sans orateur sont écartées.
- **mots_nouveaux, retenue (indice court)** : mots jamais proposés chez un orateur qui a au moins
  10 marchés passés ; prix réels seulement pour septembre-octobre 2026 (314 marchés sur 2 500,
  les plus anciens n'ont plus d'historique de prix). OUI à 0,30-0,85 : réalisé nettement en
  dessous (prix 0,44 → 29 % ; 0,55 → 45 %). Acheter le NON, frais et écart comptés : +16 % par
  achat deux heures après l'ouverture (228 achats, t +1,8 ; par événement +24 %, t +2,5), +20 %
  à douze heures, +9 % à vingt-quatre heures. Garde-fou ajouté après l'essai en direct : carnet
  écarté de plus de 0,10 ignoré (les marchés mensuels de Trump affichent souvent 0,16 / 0,85).
- **Totaux de buts NHL, écartés** : 1 440 marchés « plus ou moins de 5,5 / 6,5 buts » : le marché
  est bien calibré (« plus » gagné 51,2 % pour un prix moyen de 49,7 %), écart effacé par les
  frais ; trop peu de matchs avec plusieurs lignes (40) pour tester leur cohérence.
- **Séries NHL, écartées** : après 3 défaites, 4 victoires, une lourde défaite ou une large
  victoire : aucun écart régulier sur les deux saisons (le seul signal, « après une large
  victoire, l'équipe est trop chère », t −1,9 sur 4 essais, n'est pas retenu).

**Essai en direct du lot C (20/10 vers 13 h UTC)** : 44 matchs NHL à venir rattachés au
calendrier, 9 avec une seule équipe fatiguée (ex. Maple Leafs à Columbus le 20/10, après leur match
du 19) ; 240 marchés « mentions » ouverts, 116 rattachés à leur historique (5 achats possibles à ce
moment-là), 68 mots nouveaux dont 36 dans la fourchette 0,30-0,85.

## Ce qu'on regardera
Chaque piste est un fantôme gratuit : l'arène la juge (confiance sur le rendement, retrait des
perdantes) et l'entonnoir 80/20 (reports/pareto.md) propose ses filles dès qu'elle grandit.
