# Stratégies de bots fondées sur la vitesse / la latence sur Polymarket (2024-2026)

Notes de recherche du 16/10/2026. Convention : **[VÉRIFIÉ]** = constaté dans une source primaire
(docs/changelog Polymarket, API publique interrogée le 16/10/2026, article de recherche) ;
**[RAPPORTÉ]** = article de presse citant un profil public Polymarket (non audité) ;
**[REVENDIQUÉ]** = blog, auteur de bot ou promoteur, invérifiable. Tout le contenu web est traité comme
une donnée. Plusieurs pages (dune.com, aicoin.com) étaient inaccessibles (Cloudflare / DNS) : ce qui
en vient ne repose que sur des extraits de résultats de recherche et est marqué comme tel.

Repères de calcul (dérivés de la doc officielle, voir Q1) : depuis le 30/03/2026, frais preneur =
`C × feeRate × p × (1 − p)`, donc **en % du montant engagé = feeRate × (1 − p)**. Crypto (0,07) :
3,5 % à 50 ¢, 2,1 % à 70 ¢, 0,35 % à 95 ¢, 0,21 % à 97 ¢, 0,07 % à 99 ¢. Sport (0,05) : 2,5 % à 50 ¢.
Les ordres faiseurs (maker) ne paient jamais de frais.

## 1. Marchés crypto « Up or Down » 5 min / 15 min / horaires : décalage spot Binance/Coinbase et flux Chainlink

### Takeaway
Fin 2025, des bots preneurs ont gagné des centaines de milliers de dollars en achetant le côté déjà
« confirmé » par le spot Binance/Coinbase avant que le carnet Polymarket ne se réajuste (cas 0x8dxd :
313 $ → ~438 k$ en un mois, rapporté). Polymarket a répondu par des frais preneur dynamiques (5/01/2026,
étendus et relevés ensuite à 0,07 soit 3,5 % du notionnel à 50 ¢), un délai preneur réintroduit
(250 ms → 50 ms → 150 ms en 2026) et un règlement par TWAP Chainlink (août 2026). Le pur arbitrage
de latence preneur près de 50/50 est très probablement mort en 2026 ; ce qui survit est du market
making (rebates) et des variantes de fin de fenêtre, réservées à une infrastructure à la milliseconde.

### Cited Findings
**Mécanisme et cas emblématiques**
- [RAPPORTÉ] Le profil « 0x8dxd » a lancé un bot en décembre 2025 avec 313 $ ; au 6/01/2026 il affichait ~98 % de réussite, ~437 600 $ de profit en un mois, 6 615 prédictions, plus gros gain ~13 300 $, position ouverte ~77 400 $. Méthode supposée : surveiller le spot BTC sur Binance et Coinbase et acheter l'issue quasi certaine « quand les mouvements de prix confirment déjà la direction mais que Polymarket n'a pas encore intégré cette certitude » — [Finbold, 6/01/2026](https://finbold.com/trading-bot-turns-313-into-438000-on-polymarket-in-a-month/)
- [RAPPORTÉ] Au 9/01/2026, ~700 prédictions de plus, profit mensuel ~512 000 $, profit total > 550 000 $, élargi à ETH, SOL, XRP — [Finbold](https://finbold.com/polymarket-trading-bot-that-turned-300-into-400000-is-now-up-this-much/) ; un autre article note que l'explication « décalage Binance » reste une hypothèse — [MEXC news (reprise)](https://www.mexc.com/news/441034)
- [RAPPORTÉ] Le chiffre « 313 $ → 414 k$ » vient d'un post X de @DextersSolab du 5/01/2026 cité par Finance Magnates ; la presse donne ensuite ~438 k$ (même compte, date différente) — [Finance Magnates, 7/01/2026](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/)
- [RAPPORTÉ] Finance Magnates décrit l'arbitrage : bots surveillant de petits décalages entre le prix interne Polymarket et le spot des grandes plateformes, entrant quand la cote est proche de 50/50 et sortant « quelques instants plus tard » quand les prix convergent ; au moins un portefeuille a fait « des milliers » de tels trades en un mois — [Finance Magnates](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/)
- [RAPPORTÉ] Autres comptes cités par Finbold : 63 $ → ~131 000 $ en un mois, et ~82 $ → ~67 000 $ en ~3 semaines, profits liés à la forte volatilité du BTC — [Elite Trader (reprise Finbold)](https://elitetrader.com/et/threads/trading-bot-that-works.388228/latest)
- [RAPPORTÉ, extrait seulement — page Dune bloquée] Les marchés crypto rapides (15 min et horaires lancés vers septembre 2025) sont passés d'~40 % du volume crypto en septembre 2025 à plus de 80 % en mars 2026 — [Dune blog (extrait de recherche)](https://dune.com/blog/polymarket-fast-markets)

**Contre-mesures de Polymarket (chronologie)**
- [VÉRIFIÉ] 5/01/2026 : frais preneur activés sur les marchés crypto 15 min, « pic à 1,56 % à 50 % de probabilité », reversés en rebates USDC quotidiens aux faiseurs — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md)
- [RAPPORTÉ] Finance Magnates parle d'environ 3,15 % sur un contrat à 50 ¢ ; d'autres sources donnent ~1,56 % ou « jusqu'à 3 % » — conflit de chiffres, probablement % du notionnel vs autre base — [Finance Magnates](https://www.financemagnates.com/cryptocurrency/polymarket-introduces-dynamic-fees-to-curb-latency-arbitrage-in-short-term-crypto-markets/) ; contredit par [Changelog Polymarket (1,56 %)](https://docs.polymarket.com/changelog/predictions.md)
- [VÉRIFIÉ] 12/02/2026 : lancement des marchés crypto 5 min, directement avec frais preneur (même courbe, pic 1,56 %) — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md)
- [VÉRIFIÉ] 6/03/2026 : frais étendus à tous les marchés crypto (1H, 4H, journaliers, hebdomadaires) créés après cette date — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md)
- [VÉRIFIÉ] 30/03/2026 : « Fee Structure V2 », frais sur presque toutes les catégories ; barème actuel : crypto feeRate 0,07 (rebate faiseur 20 %), sport 0,05 (15 %), finance/politique/mentions/tech 0,04, géopolitique 0 ; formule `fee = C × feeRate × p × (1 − p)` ; exemple officiel : 100 parts à 0,50 $ en crypto = 1,75 $ de frais (3,5 % de 50 $) — [Docs Polymarket, Fees](https://docs.polymarket.com/trading/fees.md) ; [Changelog](https://docs.polymarket.com/changelog/predictions.md)
- [RAPPORTÉ] Février 2026 : suppression discrète du délai preneur de 500 ms sur les marchés crypto (sans changelog) ; selon Protos, ce délai était un « super-pouvoir » des faiseurs sophistiqués qui pouvaient retirer leurs cotations avant l'exécution des preneurs — [Protos, 20/02/2026](https://protos.com/polymarket-ends-trading-loophole-for-bitcoin-quants/)
- [REVENDIQUÉ] Un auteur de bot date cette suppression au 18/02/2026 et affirme qu'elle a « fermé » la fenêtre d'arbitrage de latence ; ses propres chiffres (bot faiseur, 78 trades/jour) : EV ~0,031 $/trade avant et après — [DEV Community (1kto1m), 25/06/2026](https://dev.to/lkto1m/february-2026-changed-polymarket-forever-heres-what-happened-to-my-bots-numbers-2fi5). **Contradiction** : Protos explique au contraire que le délai protégeait les faiseurs contre les preneurs rapides ; logiquement, retirer un délai preneur avantage plutôt les preneurs rapides.
- [VÉRIFIÉ] La doc actuelle « Order Lifecycle » décrit un délai preneur de 250 ms sur certains marchés crypto et finance up/down (drapeau `itode: true` sur `GET https://clob.polymarket.com/clob-markets/{condition_id}`) ; pendant le délai l'ordre ne peut pas être annulé — [Docs, Order Lifecycle](https://docs.polymarket.com/concepts/order-lifecycle.md)
- [VÉRIFIÉ] 17/08/2026 : délai preneur crypto ramené de 250 ms à 50 ms ; 4/09/2026 : relevé de 50 ms à 150 ms — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md). (La page Order Lifecycle mentionnant 250 ms n'est donc pas à jour.)
- [VÉRIFIÉ] 7/08/2026 : marchés crypto up/down réglés par TWAP Chainlink (prix d'ouverture et de règlement) au lieu d'un instantané ; 5 min = 30 s, 15 min et 4 h = 60 s ; 14/08/2026 : les 5 min passent à une TWAP 60 s — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md) ; [Docs, Resolution](https://docs.polymarket.com/concepts/resolution.md)
- [RAPPORTÉ] Raison du TWAP : étude Stanford / Singapore Management University sur ~2 mois de contrats BTC 5 min : 821 comptes, ~8,2 M$ capturés en fenêtres manipulées (grosse position Polymarket puis ordres Binance surdimensionnés dans les dernières secondes pour faire franchir le seuil) ; hors faiseurs, 93 % des pertes sur les particuliers ; un pari « quasi certain » a été renversé une fois sur trois dans ces fenêtres — [crypto.news, 10/08/2026](https://crypto.news/polymarket-five-second-exploit-manipulation-twap-fix/) ; [CryptoDaily](https://cryptodaily.co.uk/2026/08/polymarket-replaces-snapshot-with-chainlink-twap)
- [VÉRIFIÉ] 2/10/2026 : le canal de prix `price.crypto` (PolyBolt) sert Chainlink par défaut ; flux TWAP Chainlink 60 s publié en temps réel — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md)

**Infrastructure requise**
- [REVENDIQUÉ] Les bots avancés passent par WebSocket et nœuds RPC dédiés pour une latence d'exécution < 100 ms ; fenêtres d'arbitrage disparaissant en < 3 s — [QuickNode builders guide](https://www.quicknode.com/builders-guide/best/top-10-polymarket-trading-bots)
- [REVENDIQUÉ] Bot rentable en 2026 = bot faiseur (zéro frais + rebates), WebSocket, boucle annuler/remplacer < 100 ms contre la sélection adverse — [HTX news (reprise « New rules »)](https://www.htx.com/news/polymarket-new-rules-released-how-to-build-a-new-trading-bot-mkPMdTD8/)
- [VÉRIFIÉ] Limites CLOB relevées le 1/06/2026 : POST /order 200/s soutenu ; 24/07/2026 : pipeline de commit asynchrone pour réduire la latence de matching — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md)
- [RAPPORTÉ] Le volume des marchés courts n'a pas visiblement ralenti après les frais — [DeFi Rate](https://defirate.com/news/polymarket-users-approve-new-crypto-market-fees/) ; [Pine Analytics](https://pineanalytics.substack.com/p/polymarket-fee-rollout) (données encore partielles à sa date)

### Inferences
- Avec 3,5 % de frais à 50 ¢ et 2,1 % à 70 ¢ (crypto, depuis le 30/03/2026), un preneur qui achète « en retard d'une seconde » sur Binance doit capter un écart supérieur à frais + spread ; c'est plus du double du niveau de janvier (1,56 %). Les chiffres de 0x8dxd (déc. 2025, zéro frais, sans délai TWAP) ne sont pas reproductibles tels quels en 2026.
- Le délai preneur de 150 ms (sept. 2026) et la TWAP 60 s rendent la stratégie « dernier tick » et la manipulation de fin de fenêtre beaucoup plus coûteuses ; il reste un avantage d'information sur la TWAP en cours (on peut calculer la TWAP partielle à partir du flux Chainlink public), mais il est arbitré par des acteurs à la milliseconde.
- L'edge existe probablement encore sous forme de market making avec rebates (20 % des frais crypto reversés aux faiseurs), pas sous forme de prise de liquidité.

### Gaps
- Aucune donnée P&L agrégée et vérifiée des bots de latence après les frais V2 (mars 2026) ; Dune inaccessible.
- Date et nature exactes de la suppression du délai 500 ms (aucun changelog) et date de réintroduction du délai 250 ms (seul un agrégateur disparu évoquait un « 5 juin ») non confirmées.
- Pas trouvé le dépôt GitHub d'un bot 15 min ayant publié des résultats réels vérifiables.

## 2. Stratégie « both sides » / « gabagool » : acheter YES et NO quand leur somme < 1 $

### Takeaway
Le principe (acheter les deux côtés pour < 1 $ et toucher 1 $ à la résolution) est un arbitrage de
« rééquilibrage » documenté académiquement (~40 M$ extraits sur Polymarket, toutes formes confondues,
avr. 2024-avr. 2025). Pour les marchés crypto courts, il n'existe que des dépôts GitHub et des
analyses de blog, sans P&L vérifié ; les frais preneur 2026 (jusqu'à 3,5 % par jambe) le rendent
quasi impossible en preneur, il ne reste viable qu'en ordres posés (faiseur), avec risque de jambe
non remplie.

### Cited Findings
- [VÉRIFIÉ, article de recherche] « Unravelling the Probabilistic Forest » (Saguillo et al., arXiv 2508.03474, août 2025 ; version AFT 2025) : ~40 M$ de profit réalisé estimé via deux types d'arbitrage : rééquilibrage intra-marché (somme des issues ≠ 1) et arbitrage combinatoire inter-marchés — [arXiv](https://arxiv.org/abs/2508.03474v1) ; [AFT 2025 / Dagstuhl](https://drops.dagstuhl.de/storage/00lipics/lipics-vol354-aft2025/html/LIPIcs.AFT.2025.27/LIPIcs.AFT.2025.27.html)
- [RAPPORTÉ] Selon DL News, 86 M de paris analysés ; les 3 portefeuilles en tête ont placé > 10 200 paris en un an pour 4,2 M$ de profit — [DL News](https://www.dlnews.com/articles/markets/polymarket-users-lost-millions-of-dollars-to-bot-like-bettors-over-the-past-year/)
- [REVENDIQUÉ] Dépôt « gabagool » (strongca22-cpu) : bot Python sur les 15 min BTC/ETH/SOL, achète YES et NO quand chacun est temporairement bon marché ; exemple YES 0,48 + NO 0,45 = 0,93 → 1,00 $ ; ~197 étoiles / 93 forks en janvier 2026 ; aucun P&L publié — [BrightCoding (résumé du dépôt)](https://converter.brightcoding.dev/blog/strongca22-cpugabagool-a-polymarket-arbitrage-bot-for-risk-profit-trading) ; [miroir Gitee](https://gitee.com/xpp/gabagool)
- [REVENDIQUÉ] Analyse du compte @gabigol (portefeuille 0x8852…c569) : ~308 k$ de P&L cumulé, ~20,6 M$ de volume, ~100 000 marchés ; achats uniquement (3 499 achats pour 1 vente sur 3 500 trades), médiane ~1,92 $ par trade, jusqu'à 7 achats/s ; jambe « convergence » (~48 % des achats : balayer les asks 94-99 ¢ du favori dans les 1-2 dernières minutes) + jambe « loterie » (~21 % : outsider à 3-30 ¢) ; les deux côtés du même marché sont fréquents ; taux de réussite par marché ~60 %, profit factor ~2,4 — [DEV Community (abrownfox001), juil. 2026](https://dev.to/fatherson/reverse-engineering-gabigol-high-frequency-crypto-updown-farmer-on-polymarket-d0a)

### Inferences
- Sur un marché 15 min avec frais crypto V2, acheter YES à 0,48 et NO à 0,45 en preneur coûte ~0,0175 + ~0,0173 $ de frais par paire (≈ 3,5 ¢) : la marge brute de 7 ¢ de l'exemple tombe à ~3,5 ¢, et une marge typique de 1-2 ¢ devient négative. La stratégie ne tient qu'avec des ordres posés (zéro frais) — d'où le risque d'une seule jambe remplie (exposition directionnelle complète).
- « gabagool » et « gabigol » semblent être deux choses distinctes (un dépôt open-source vs un compte réel dont le profil ressemble plus à « convergence + loterie » qu'à un pur arbitrage both-sides).

### Gaps
- Pas de source primaire sur le trader « gabagool » original (post X) ni sur ses gains réels.
- Pas de mesure de la fréquence actuelle des situations YES+NO < 1 $ (asks) dans les 5/15 min en 2026.

## 3. Sniping de fin de marché / « haute probabilité » (acheter à 0,95-0,99 juste avant la résolution)

### Takeaway
Acheter les favoris ≥ 90 ¢ a un rendement moyen positif mais minuscule sur Polymarket (+0,28 % à
+0,83 % par dollar selon la pondération, étude sept. 2026), négatif en sport ; le gain par trade est
de 1 à 5 % et une seule perte efface 20 à 100 trades. Les risques de queue sont réels : manipulation
de fin de fenêtre (pari « quasi certain » renversé 1 fois sur 3 dans les fenêtres manipulées des
5 min BTC), litiges UMA, résolutions contestées. En crypto court, c'est une stratégie de bot à la
seconde (balayage des asks 94-99 ¢ dans les 120 dernières secondes).

### Cited Findings
- [VÉRIFIÉ, article de recherche] Cardozo & Rivero-Wildemauwe, « The Favorite–Longshot Bias in Prediction Markets: Evidence from Polymarket », arXiv 2609.12878 (11/09/2026) : 560,9 M d'achats, 22,49 G$ ; favoris (p ≥ 0,90) = 10,5 % des achats mais 43 % des montants (9,66 G$). Rendement terminal des favoris : +0,277 % (moyenne par marché), +0,83 % (achats poolés), +0,392 % (moyenne par événement) ; longshots < 0,10 : −6,30 % (par marché), −19,35 % (poolé). Les gains culminent vers 60 ¢ puis décroissent vers 0 quand le prix approche 1 $. Par catégorie (favoris) : crypto +0,643 %, politique +1,044 %, sport −0,230 %, finance +0,085 % — [arXiv 2609.12878](https://arxiv.org/html/2609.12878v1)
- [VÉRIFIÉ, même article] Les rendements ne sont pas annualisés et ne tiennent pas compte de la durée jusqu'à la résolution — [arXiv 2609.12878](https://arxiv.org/html/2609.12878v1)
- [REVENDIQUÉ] Étude de calibration sur 28 407 marchés résolus : les paris à 95 ¢ se résolvent YES légèrement moins de 95 % du temps ; motifs aux extrêmes « suggestifs, pas statistiquement concluants » — [Poly Syncer](https://www.polysyncer.com/blog/polymarket-prediction-accuracy)
- [REVENDIQUÉ] Le bot @gabigol balaye les asks 94-99 ¢ du côté gagnant dans les 1-2 dernières minutes des 5/15 min, clips de ~2 $, « 1-6 % par part moins les frais » — [DEV Community](https://dev.to/fatherson/reverse-engineering-gabigol-high-frequency-crypto-updown-farmer-on-polymarket-d0a)
- [RAPPORTÉ] Manipulation des 5 min BTC avant TWAP : dans les fenêtres manipulées, un pari traité comme quasi certain a été renversé une fois sur trois ; 93 % des pertes (hors faiseurs) sur les particuliers — [crypto.news](https://crypto.news/polymarket-five-second-exploit-manipulation-twap-fix/)
- [VÉRIFIÉ] Résolution UMA : proposition, fenêtre de contestation de 2 h ; si contestée deux fois, vote des détenteurs de jetons UMA (DVM) — [Docs, Resolution](https://docs.polymarket.com/concepts/resolution.md)
- [REVENDIQUÉ] 99,78 % des marchés se résolvent sans litige ; parmi les litiges tranchés, 2 072 (54 %) l'ont été pour « proposition trop tôt » — [Polyflux](https://polyflux.io/blog/polymarket-uma-resolution-disputes/)
- [RAPPORTÉ] Cas de renversement / contestation : en 2024 (marché Barron Trump), Polymarket a outrepassé le résultat UMA et remboursé ; en mars 2025 (accord minerais Ukraine), refus de rembourser ; un détenteur de ~5 M UMA a pesé ~25 % du vote sur un marché de 7 M$ — [Polyflux](https://polyflux.io/blog/polymarket-uma-resolution-disputes/) ; [OddsShopper](https://www.oddsshopper.com/articles/prediction-markets/uma-oracle-polymarket-disputes)

### Inferences
- Achat à 0,97 en crypto (frais V2) : gain si victoire 0,03 $ − 0,002 $ de frais ≈ +2,9 % ; seuil de rentabilité ≈ 97,2 % de victoires. L'étude FLB montre que le surplus moyen réel au-dessus du prix n'est que de quelques dixièmes de point : l'edge vient du timing (acheter quand l'issue est déjà mécaniquement acquise), pas du simple niveau de prix.
- Depuis la TWAP 60 s (août 2026), les 60 dernières secondes d'un 5 min sont partiellement « verrouillées » : un acteur qui calcule la TWAP partielle sait avant la clôture si le seuil peut encore être franchi. C'est l'edge de fin de fenêtre qui reste, mais il exige le flux Chainlink en continu et une exécution en < 1 s.
- Pour les marchés UMA longs, le sniping 95-99 ¢ est un « carry » à faible rendement annualisé avec risque de litige ; la sous-performance des favoris en sport (−0,23 %) suggère d'éviter ce segment.

### Gaps
- Pas de P&L publié d'un bot « sniper 99 ¢ » après la TWAP ; la page Indie Hackers qui le revendiquait était inaccessible.
- Pas de liste chiffrée des pertes subies par des snipers lors de renversements UMA précis.

## 4. Latence en sport : flux de données live plus rapides, délais de Polymarket, légalité

### Takeaway
Des bots exploitent le décalage de quelques secondes entre l'événement (flux officiels, parsing du
stream) et le carnet Polymarket, surtout en e-sport (cas TeemuTeemuTeemu : ~900 $ → ~208 k$ en
3 mois, rapporté). Polymarket impose un délai de matching sur les ordres preneurs des marchés sportifs
(historiquement ~3 s selon des sources secondaires ; **1 s sur la plupart des marchés sportifs
interrogés le 16/10/2026**, 0 s sur d'autres), annule les ordres posés au coup d'envoi et facture
0,05 de frais preneur depuis le 10/07/2026. Aucune source trouvée sur l'illégalité du « courtsiding »
sur Polymarket.

### Cited Findings
- [RAPPORTÉ] TeemuTeemuTeemu : ~208 521 $ de profit en un trimestre (fin 2025), quasi exclusivement LoL et Dota 2 en direct ; surveille les données officielles et le stream, achète quand un kill/objectif/teamfight n'est pas encore intégré (retard « de quelques secondes ») ; plus gros gain ~90 000 $ (Dplus KIA vs Hanwha Life) ; nombreux imitateurs — [Esports.net, 30/12/2025](https://www.esports.net/news/polymarket-bot-makes-over-200k-in-3-months-with-lol-dota-2-esports/)
- [VÉRIFIÉ] Doc officielle : « Sports/game delay » activé sur les marchés sportifs configurés autour des conditions de jeu en direct ; l'ordre marketable attend la fenêtre configurée avant matching, ne peut pas être annulé pendant ce temps, et est rejeté si les contrôles échouent à l'expiration ; statut `delayed` ; champ `market.trading.secondsDelay` — [Docs, Order Lifecycle](https://docs.polymarket.com/concepts/order-lifecycle.md) ; [Docs, Market Details](https://docs.polymarket.com/market-data/market-details.md) ; [Docs, Place Orders](https://docs.polymarket.com/trading/place-orders.md)
- [VÉRIFIÉ, API publique interrogée le 16/10/2026] Sur ~800 marchés actifs (Gamma API, triés par volume 24 h) : 248 marchés sportifs avec `secondsDelay = 1` (ex. `cs2-ast10-mibr-2026-10-16`), 54 avec `0` (ex. `mlb-tb-cle-2026-10-16`), marchés crypto up/down sans valeur — requête `https://gamma-api.polymarket.com/markets?active=true&closed=false&order=volume24hr`
- [REVENDIQUÉ] Article d'aide Polymarket (cité par résultats de recherche, ~6 mois) : délai de 3 s sur les ordres marketables sportifs, test d'un délai de 1 s sur NBA et MLB ; un développeur rapporte football = 1 s, NBA = 0 — [DEV Community (ekocam), oct. 2026](https://dev.to/ekocam/6-things-that-broke-our-polymarket-trading-bot-before-it-made-a-dollar-4efi) ; [MetaMask (délai de 3 s pour protéger les faiseurs)](https://metamask.io/news/5-cent-spread-prediction-markets)
- [REVENDIQUÉ] Les ordres limites sportifs sont annulés automatiquement au coup d'envoi officiel — [DEV Community (ekocam)](https://dev.to/ekocam/6-things-that-broke-our-polymarket-trading-bot-before-it-made-a-dollar-4efi)
- [VÉRIFIÉ] Frais sport : feeRate 0,03 → 0,05 au 10/07/2026, rebate faiseur 25 % → 15 % ; frais activés sur NCAAB et Serie A au 18/02/2026 — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md)
- [REVENDIQUÉ] Polymarket verserait > 5 M$/mois aux faiseurs sur les marchés sportifs — [PyPI sfmm](https://pypi.org/project/sfmm/)
- [REVENDIQUÉ, prudence] Les meilleures firmes de paris en direct atteignent 3-5 s de bout en bout avec flux premium ; les bots particuliers avec flux ESPN gratuits sont plus lents — [polymarkets.co.il (tutoriel)](https://polymarkets.co.il/hi/bots/polymarket-sports-microstructure-bot/)
- [RAPPORTÉ] GRID (données e-sport officielles) s'est associé à Sportstensor pour alimenter des marchés e-sport Polymarket — [Esports.net](https://www.esports.net/news/polymarket-bot-makes-over-200k-in-3-months-with-lol-dota-2-esports/)

### Inferences
- Le délai de 1 s non annulable joue contre le preneur rapide : si le faiseur retire sa cotation pendant la seconde, l'ordre est rejeté. Combiné aux frais 0,05 (2,5 % à 50 ¢), seul un écart de prix important (événement décisif) reste exploitable.
- L'edge e-sport décrit fin 2025 repose sur un flux plus rapide que le carnet ; avec la concurrence et les délais, il s'est probablement réduit, mais aucune donnée 2026 ne le mesure.

### Gaps
- Date exacte du passage de 3 s à 1 s : non trouvée dans le changelog.
- Légalité : aucune source fiable sur le statut juridique du courtsiding / flux plus rapides sur Polymarket (pour la France, de toute façon : aucun ordre réel).

## 5. Bots sur l'actualité, marchés « mentions » (« Will X say Y ») et soirées électorales

### Takeaway
Les marchés « mentions » existent en nombre (~106 actifs) et rapportent à certains traders, mais
**aucune source fiable** ne documente de bot à transcription en direct ; pour les soirées électorales,
les gains connus (baleine « Théo », ~47-85 M$ en 2024) sont directionnels, pas des bots de vitesse.
Les analyses générales montrent toutefois que le top 1 % des comptes (surtout des bots) capte > 80 %
des profits, en partie en entrant dans les secondes suivant l'ouverture d'un marché.

### Cited Findings
- [VÉRIFIÉ, page Polymarket] Polymarket héberge ~106 marchés « Mentions » actifs ; résolution YES si la personne prononce le terme dans la fenêtre (formes plurielles/possessives selon les règles) — [Polymarket, Mention markets](https://polymarket.com/predictions/mention-markets)
- [VÉRIFIÉ] Frais « Mentions » : feeRate 0,04 depuis le 30/03/2026 — [Docs, Fees](https://docs.polymarket.com/trading/fees.md)
- [RAPPORTÉ] Discours de Trump sur l'Iran : > 100 000 $ misés sur « Ceasefire/Peace Deal » ; le trader Dragontree a acheté 9 741 parts NO à 35 % pour ~6 300 $ de profit — [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/trumps-speech-skipped-ceasefire-peace-213121542.html)
- [RAPPORTÉ] Présidentielle 2024 : la baleine « Trump Whale » a gagné ~47 M$ (Polymarket Analytics) ; Fortune donne ~40 M$ ; une reprise crypto parle de ~85 M$ — [Fortune, 6/11/2024](https://fortune.com/2024/11/06/polymarket-whale-won-40-million-betting-on-trump) ; [The Defiant](https://thedefiant.io/news/defi/polymarket-whales-cash-out-millions-on-trump-win)
- [RAPPORTÉ, source secondaire] Polymarket était à 95 % pour Trump à 23 h 43 ET, près de 6 h avant l'appel AP (5 h 34) — [Wedbush / PredictStreet](https://investor.wedbush.com/wedbush/article/predictstreet-2026-1-16-the-death-of-the-toss-up-how-polymarkets-19b-election-bet-vindicated-prediction-markets)
- [RAPPORTÉ, via résultat de recherche — Bloomberg non consulté directement] Analyse Bloomberg de ~2 M d'adresses actives depuis janvier 2025 : le top 1 %, surtout des bots, capte > 80 % des profits, notamment en entrant « dans les secondes » suivant l'ouverture d'un marché — [MEXC news (reprise)](https://www.mexc.com/news/1061296)

### Inferences
- Un bot « mentions » en direct (speech-to-text) est techniquement plausible mais non documenté ; la fenêtre utile est de quelques secondes après la prononciation du mot, irréaliste pour un cycle de 5 minutes.
- Le marché électoral 2024 a anticipé l'appel AP de plusieurs heures : l'edge « vitesse » le soir d'élection se joue sur les dépouillements comté par comté, pas sur l'annonce officielle.

### Gaps
- Aucune source sur des bots de transcription live pour les marchés mentions.
- Aucune source sur des bots de vitesse documentés le soir de l'élection 2024 ni pour les élections 2026.

## 6. Sniping de nouveaux marchés (premiers ordres sur carnets vides)

### Takeaway
Seuls des outils d'alerte commerciaux (PolySpy) et une affirmation reprise de Bloomberg (les bots
entrent « dans les secondes » après l'ouverture) existent ; aucun bot de sniping de nouveaux
marchés avec résultats vérifiés n'a été trouvé.

### Cited Findings
- [REVENDIQUÉ] PolySpy (bot Telegram, code fermé) surveille le flux de création de marchés et notifie dès l'ouverture, au motif que les cotes initiales sont souvent mal fixées pendant les premières heures à faible liquidité ; historique public limité — [pm.wiki, PolySpy](https://pm.wiki/uk/projects/polyspy)
- [RAPPORTÉ, via résultat de recherche] Analyse Bloomberg : les bots entrent souvent dans les secondes suivant l'ouverture d'un marché pour obtenir les prix les plus bas — [MEXC news (reprise)](https://www.mexc.com/news/1061296)
- [REVENDIQUÉ] Bot open-source de market making « poly-maker » (warproxxx) cité comme base pour coter tôt — [gittrend, poly-maker](https://gittrend.io/repo/warproxxx/poly-maker)

### Inferences
- Le sniping de nouveaux marchés n'exige pas la milliseconde quand la mauvaise cotation dure « des heures » (thèse PolySpy) : c'est l'un des rares cas partiellement accessible à un cycle de 5 minutes, à condition de lister les marchés récemment créés (Gamma API, tri par date de création) et de vérifier la profondeur réelle du carnet.

### Gaps
- Aucune mesure publique de la rentabilité des premiers ordres sur nouveaux marchés, ni de la durée typique de la mauvaise cotation.

## 7. Quelles stratégies sont reproductibles dans une simulation tournant toutes les 5 minutes ?

### Takeaway
Presque aucune stratégie de vitesse ne l'est : arbitrage de latence crypto, both-sides en preneur,
sniping des 120 dernières secondes, latence sportive et mentions live exigent des réactions de
50 ms à quelques secondes. Sont reproductibles, de façon dégradée : les favoris 90-99 ¢ sur marchés
longs (carry), le sniping de nouveaux marchés à l'échelle de l'heure, et — seulement si on ajoute un
déclenchement plus rapide — des entrées de fin de fenêtre sur les 1H/4H/journaliers.

### Cited Findings
- [VÉRIFIÉ] Délai preneur crypto actuel 150 ms, TWAP 60 s sur 5/15 min/4 h, délai sportif 1 s : les fenêtres exploitables sont infra-minute — [Changelog Polymarket](https://docs.polymarket.com/changelog/predictions.md) ; Gamma API (16/10/2026)
- [VÉRIFIÉ] Barème des frais à intégrer à la simulation : `C × feeRate × p × (1 − p)`, crypto 0,07, sport 0,05, mentions/politique/finance/tech 0,04, géopolitique 0, faiseurs 0 — [Docs, Fees](https://docs.polymarket.com/trading/fees.md)
- [VÉRIFIÉ] Rendement moyen des favoris ≥ 90 ¢ : +0,28 % à +0,83 % (positif en crypto et politique, négatif en sport) — [arXiv 2609.12878](https://arxiv.org/html/2609.12878v1)

### Inferences
Tableau (cycle de 5 min, ordres simulés sur vrais carnets avec frais) :

| Stratégie | Fenêtre utile | Reproductible à 5 min ? |
|---|---|---|
| Latence spot → 5/15 min crypto | 50 ms – quelques s | **Non** |
| Both sides YES+NO < 1 $ (preneur) | < 1 s, et tué par les frais | **Non** (en preneur) ; en ordres posés seulement si le simulateur gère les ordres reposant et le risque de jambe unique |
| Sniping fin de fenêtre 5/15 min | 60-120 dernières s | **Non** (un cycle de 5 min tombe au hasard dans la fenêtre) |
| Fin de fenêtre 1H / 4H / journalier | dernières minutes | **Partiellement** : possible si le cycle est aligné sur l'échéance, avec calcul de la TWAP partielle Chainlink/Binance ; edge non mesuré |
| Favoris 90-99 ¢ sur marchés UMA longs | heures – jours | **Oui**, mais rendement moyen ~0,3-0,8 % par trade avant capital immobilisé ; éviter le sport |
| Latence sport / e-sport | 1-5 s | **Non** |
| Mentions live / soirée électorale | secondes | **Non** |
| Sniping de nouveaux marchés | minutes – heures (revendiqué) | **Partiellement / oui** : détecter les créations récentes et comparer à une référence (autre plateforme, modèle) |
| Market making avec rebates | continu, annulation < 100 ms | **Non** de façon réaliste (sélection adverse non simulable à 5 min) |

- Recommandation de prudence pour le labo : ne pas « backtester » une stratégie de latence avec des prix échantillonnés toutes les 5 minutes — le simulateur verrait des prix gagnables qui, en réalité, auraient été pris par des bots en 50 ms (biais d'exécution optimiste).

### Gaps
- Aucune mesure publique de la persistance (en minutes) des mauvaises cotations sur les marchés 1H/4H/journaliers, qui déciderait si une version lente de la stratégie de fin de fenêtre a un edge.
