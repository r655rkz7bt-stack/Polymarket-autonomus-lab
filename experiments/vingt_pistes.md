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
| 19 | haut_ou_bas_crypto | « monte ou baisse aujourd'hui » : modèle du prix | prix crypto | C |
| 20 | mots_prononces | « dira-t-il ce mot ? » : fréquence dans l'actualité | Google Actualités | C |

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

## Ce qu'on regardera
Chaque piste est un fantôme gratuit : l'arène la juge (confiance sur le rendement, retrait des
perdantes) et l'entonnoir 80/20 (reports/pareto.md) propose ses filles dès qu'elle grandit.
