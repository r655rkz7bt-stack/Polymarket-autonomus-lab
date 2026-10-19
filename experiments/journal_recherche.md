# Journal de recherche

Une entrée datée par session de recherche (routine « chercheur » ou session manuelle) :
ce qui a été lu, fait, testé, et ce qui reste ouvert. Les plus récentes en haut.

## 2026-10-20 (passage chercheur, ~01 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (23:49 UTC) : capital réalisé 794,02 (palier 1500, 4,5 jours
  sans palier), champion nf_sport_patiente (+157, 71 opérations, P(hasard) 0,06). Aucune obligation.
- **Fait** : variante `nf_sport_patiente_soir` (sans nouveau code : champion sport + ordre posé, seulement 18-24 h UTC),
  pour voir si le gain vient des matchs américains du soir. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordres posés, markout à surveiller. Rien vérifié en réel.

## 2026-10-19 (passage chercheur, ~20 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (19:49 UTC) : capital réalisé 784,69 (palier 1500, 4,3 jours
  sans palier), champion nf_sport_patiente (+139, 67 opérations, P(hasard) 0,082). Aucune obligation.
- **Fait** : variante `nf_sport_patiente_non` (sans nouveau code : champion sport + ordre posé, favori NON seulement),
  moitié complémentaire de `nf_sport_patiente_oui`, pour localiser le camp qui porte le gain.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordres posés, markout à surveiller. Rien vérifié en réel.

## 2026-10-19 (passage chercheur, ~15 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (14:52 UTC) : capital réalisé 821,86 (palier 1500, 4,1 jours
  sans palier), champion nf_sport_patiente (+247, 62 opérations, « prometteuse », P(hasard) 0,018). Obligation : remplacer
  market_structure, meteo_prevision, news_momentum, news_momentum_patiente (éliminées).
- **Fait** : ces 4 stratégies retirées de `strategies.yaml` (leurs classes de code restent : les filles `nm_*`,
  `meteo_prevision_patiente` s'en servent). Remplacées par 3 fantômes sans nouveau code, tous dérivés du champion :
  `nf_sport_patiente_6_24h` (fenêtre 6-24 h), `nf_sport_patiente_demi_mise` (demi-Kelly), `nf_sport_patiente_large` (prix dès 0,65).
  Test de configuration mis à jour, 399 tests verts.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordres posés, donc markout à surveiller. Rien vérifié en réel.

## 2026-10-19 (passage chercheur, ~10 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (09:54 UTC) : capital réalisé 786,73 (palier 1500, 3,9 jours
  sans palier), champion nf_sport_patiente (+131, 54 opérations, « prometteuse », P(hasard) 0,039). Obligation : remplacer
  temperature_floor (éliminée).
- **Fait** : temperature_floor retirée de `strategies.yaml` ; remplacée par deux fantômes sans nouveau code :
  `nf_sport_patiente_oui` (champion, favori OUI seulement) et `nf_sport_patiente_2crans` (champion, ordre posé à 2 crans). Test de configuration mis à jour, 395 tests verts.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordres posés, donc markout à surveiller. Rien vérifié en réel.

## 2026-10-19 (passage chercheur, ~05 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (04:49 UTC) : capital réalisé 843,49 (palier 1500, 3,7 jours
  sans palier), champion nf_sport_patiente (+160, 48 opérations, « prometteuse », P(hasard) 0,015). Aucune obligation.
  nf_sport_patiente_prix_haut : 1 opération, −180 (perte unique, échantillon trop petit pour conclure).
- **Fait** : petite-fille `nf_sport_patiente_prix_moyen` (sans nouveau code : champion sport + ordre posé, favori à 0,80-0,875),
  complément de `nf_sport_patiente_prix_haut` pour localiser le gain par tranche de prix. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordre posé donc à surveiller au markout. Rien vérifié en réel.

## 2026-10-19 (passage chercheur, ~00 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (23:54 UTC) : capital réalisé 864,57 (en baisse depuis 963 :
  le principal a perdu, nf_court −161 sur 11 opérations), palier 1500. Champion nf_sport_patiente (+197, 45 opérations,
  « prometteuse », P(hasard) 0,001). Aucune obligation.
- **Fait** : petite-fille `nf_sport_patiente_prix_haut` (sans nouveau code : champion sport + ordre posé, limitée à 0,875-0,95,
  meilleur morceau de prix de nf_sport_prix_haut). Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordre posé donc à surveiller au markout (sélection adverse). Rien vérifié en réel.

## 2026-10-18 (passage chercheur, ~20 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (19:49 UTC) : capital réalisé 963,07 (palier 1500), champion nf_court
  (+154, 62 opérations), nf_sport +169 (24), nf_sport_patiente +144 (41, « prometteuse », P(hasard) 0,009). Aucune obligation.
- **Fait** : petite-fille `nf_sport_6_24h` (sans nouveau code : sport entre 6 et 24 h avant la fin, ordres pris) pour compléter
  `nf_sport_tres_court` et localiser le gain du sport à court délai. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; recouvrement avec nf_sport_court. Rien vérifié en réel.

## 2026-10-18 (passage chercheur, ~15 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (14:42 UTC) : capital réalisé 1023,07, champion nf_court
  (+146, 42 opérations), nf_sport +146 (19). Obligation : remplacer les stratégies éliminées social_sentiment et information_advantage.
- **Fait** : ces deux stratégies retirées de `strategies.yaml` et remplacées par deux fantômes sans nouveau code :
  `nf_sport_tres_court` (sport, moins de 6 h) et `nf_court_prix_haut` (moins de 24 h, favori à 0,90 ou plus, ordres pris).
  Test de configuration mis à jour ; 387 tests verts.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; recouvrement avec nf_sport_court / nf_court. Rien vérifié en réel.

## 2026-10-18 (passage chercheur, ~12 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (09:42 UTC) : capital réalisé 1022,64,
  champion nf_court (+152, 36 opérations), aucune obligation. nf_sport +143 (18), nf_sport_court +80 (7).
- **Fait** : fille `nf_court_hors_sport` (sans nouveau code : le champion nf_court sans le sport, ordres pris)
  pour savoir si le court délai gagne ailleurs que dans le sport. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; rien vérifié en réel.

## 2026-10-18 (passage chercheur)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (04:49 UTC) : capital réalisé 1009,30,
  aucun champion, aucune obligation. nf_sport +123 (14 opérations), nf_court +93 (27), naive_favorite +91 (14).
- **Fait** : petite-fille `nf_sport_non` (sans nouveau code : sport croisé avec favori NON, ordres pris, pas posés)
  dans l'arène, pour compléter `nf_sport_oui`. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon minuscule ; rien vérifié en réel.

## 2026-10-17 (passage chercheur, ~00 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (23:54 UTC) : capital réalisé 994,24,
  aucun champion, aucune obligation. naive_favorite +86 (12 opérations), nf_court +46 (20), market_structure -491 (452).
- **Fait** : fille `nf_tres_court` (sans nouveau code : naive_favorite à moins de 6 h de la fin, ordres pris) dans l'arène.
  Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon minuscule ; recouvre en partie nf_court. Rien vérifié en réel.

## 2026-10-17 (passage chercheur, ~20 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (19:49 UTC) : capital réalisé 994,06,
  aucun champion, aucune obligation. nf_sport_patiente +118 (14 opérations), naive_favorite +93 (11), market_structure -491 (452).
- **Fait** : petite-fille `nf_sport_court` (sans nouveau code : sport croisé avec moins de 24 h, ordres pris, pas posés)
  dans l'arène. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon minuscule ; sport et court délai se recouvrent sans doute beaucoup. Rien vérifié en réel.

## 2026-10-17 (passage chercheur, ~16 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (14:53 UTC) : capital réalisé 994,06,
  champion meteo_prevision, aucune obligation. nf_sport_patiente +104 (7 opérations), naive_favorite +89 (10),
  market_structure -491 (452).
- **Fait** : petite-fille `nf_sport_oui` (sans nouveau code : sport croisé avec favori OUI, ordres pris, pas posés,
  car la méthode déconseille les variantes « patientes » directionnelles sans markout) dans l'arène.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon minuscule ; sport et OUI peuvent se recouper beaucoup. Rien vérifié en réel.

## 2026-10-17 (passage chercheur, ~10 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (09:48 UTC) : capital réalisé 994,06,
  aucune obligation. naive_favorite +89 (10 opérations), nf_sport +32 (3), market_structure -491 (452).
- **Fait** : petite-fille `nf_sport_patiente` (sans nouveau code : morceau gagnant « sport » + ordres posés
  1 cran au-dessus du meilleur acheteur) dans l'arène. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : 3 opérations seulement pour la fille sport ; un ordre posé peut ne jamais être exécuté. Rien vérifié en réel.

## 2026-10-17 (passage chercheur, ~5 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, ARCHITECTURE.md, CHANTIERS.md, feuille de mission (04:44 UTC) : capital réalisé
  994,06, aucun champion, aucune obligation. naive_favorite en tête (+84, 9 opérations) ; market_structure -491 (450).
- **Fait** : variante `naive_favorite_large` (sans nouveau code : fourchette 0,65-0,97 au lieu de 0,80-0,95) dans
  l'arène. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire ».
- **Limites** : échantillon minuscule ; élargir vers le bas peut annuler le biais favori (étude favori.md : piège
  hors politique). Rien vérifié en réel : l'arène tranchera.

## 2026-10-16 (passage chercheur, ~22 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (19:47 UTC) : capital réalisé 994,06,
  aucun champion, aucune obligation. naive_favorite en tête (+79, 7 opérations), market_structure -486 (439).
- **Fait** : variante `naive_favorite_patiente` (sans nouveau code : achat du favori posé 1 cran au-dessus
  du meilleur acheteur, seuil d'avantage 0,01, Kelly 0,5) dans l'arène. Test de configuration mis à jour.
  Vérifié : `api.manifold.markets` est accessible depuis la session (chantier n°2 débloqué, code à écrire).
- **Pas fait** : chantiers sport (étape 3 du n°0), Kalshi/Manifold : restent « à faire ».
- **Limites** : 7 opérations seulement ; un ordre posé peut ne jamais être exécuté. Rien vérifié en réel.

## 2026-10-16 (passage chercheur, ~17 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (14:47 UTC) : capital réalisé 994,06,
  aucun champion, aucune obligation. crypto_threshold -150 (4 opérations), market_structure -464 (387).
- **Fait** : variante `crypto_threshold_patiente` (sans nouveau code : ordres posés 1 cran au-dessus
  du meilleur acheteur, seuil d'avantage 0,02, Kelly 0,5) dans l'arène. Test de configuration mis à jour.
- **Pas fait** : chantiers sport (étape 3 du n°0), Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon minuscule ; un ordre posé peut ne jamais être exécuté. Rien vérifié en réel.

## 2026-10-16 (passage chercheur, ~10 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (09:47 UTC) : capital réalisé 994,06,
  aucun champion, aucune obligation. market_structure : 285 opérations, -448, verdict « ne fonctionne pas ».
- **Fait** : deux variantes « patientes » (sans nouveau code, ordres posés 1 cran au-dessus du meilleur
  acheteur) dans l'arène : `meteo_prevision_patiente` (seule idée avec un avantage mesuré hors échantillon,
  on économise écart + frais taker) et `news_momentum_patiente` (la seule stratégie positive du classement).
  Test de configuration mis à jour ; suite verte.
- **Pas fait** : chantier n°0 sport (match terminé, cotes) et chantiers Kalshi/Manifold, faute de temps
  dans ce passage ; restent « à faire ». Rien vérifié en réel (jugement par l'arène).
- **Limites** : échantillon minuscule (3 opérations pour news_momentum) ; un ordre posé peut ne jamais
  être exécuté, d'où l'intérêt de comparer au fantôme « impatient ».

## 2026-10-16 (session avec Etienne, ~6 h UTC) — météo

- **Constat** : aucune championne ; la plupart des stratégies détiennent des positions sur des
  marchés à échéance lointaine, donc rien n'est prouvé vite et le capital principal attend.
- **Idée écartée, mesurée** : relevé du jour au-delà d'une tranche → tranche perdue. Le marché la
  cote déjà 0,001 (33 cas sur 33) : aucun avantage.
- **Test** : prévisions GFS + ECMWF (Open-Meteo « previous runs », sans regard vers le futur)
  contre les prix, 14 553 marchés de température résolus du 1er au 15/10, réglage sur le
  1er-7/10, jugement sur le 8-15/10. Brier 0,097 (modèle) contre 0,113 (marché) ; NON sur la
  tranche favorite cotée 0,2-0,8 : +23 à +27 % des mises, 8 jours gagnants sur 8 ; OUI bon
  marché : −55 %. Détail : `experiments/meteo_backtest.md`.
- **Fait** : stratégie `meteo_prevision` (NON seulement), sources `meteo_prevision` (Open-Meteo)
  et coordonnées des stations ; essai réel complet (cycle local) : 6 paris de ≈ 15 € par cycle.
- **Reste ouvert** : confirmer en réel (carnets réels, l'arène) ; essayer d'autres modèles
  (ICON, ensembles) et un σ selon l'échéance ; regarder les marchés de pluie / neige.

## 2026-10-16 (passage chercheur, ~5 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (04:46 UTC), classement.
- **Constat** : capital réalisé 994,06 (palier 1500), aucun champion, aucune obligation. market_structure :
  192 opérations, -400,70, verdict « ne fonctionne pas » (frais). crypto_threshold -150 (4 opérations).
  news_momentum +4,03 (2 opérations). Les autres : 0 à 3 opérations.
- **Fait** : chantier n°0 étape 3 (température). Nouvelle stratégie `temperature_floor`
  (`strategies_v2.py`, `weather_model.py`, entrée `strategies.yaml`) : le maximum METAR du jour ne peut que
  monter, donc une tranche dépassée d'1 °C (2 °F) est perdue d'avance (achat de « Non »), et « X ou plus »
  déjà atteint est gagné (achat de « Oui »). Observation météo rattachée aux marchés (`MarketInfo.weather`,
  `intel_pipeline.py`). Formats de questions vérifiés sur Gamma (°C, °F, « or below », « or higher »).
  Tests : 3 nouveaux, suite verte.
- **Reste ouvert** : sport (match terminé non réglé, cotes `odds_api`) ; vérifier au premier cycle de
  production que `market.weather` est bien rempli (les observations ne sont reliées qu'aux stations
  citées) ; jugement de l'arène. market_structure reste très négative : à éliminer si rien ne change.
- **Limites** : jour local estimé par la longitude ; rien vérifié en réel (pas d'accès au cycle de
  production) ; prix des tranches météo non observés ici (le marché est peut-être déjà à jour).

## 2026-10-15 (passage chercheur, ~20 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (19:46 UTC), classement.
- **Constat** : capital réalisé 997,99 (palier 1500), aucun champion, aucune obligation. market_structure :
  53 opérations, -145,27, verdict « ne fonctionne pas » (frais > moitié du résultat sur 16). crypto_threshold -128
  (3 opérations, surconfiance). 5 stratégies : toujours 0 opération.
- **Fait** : (1) nouvelle variante `market_structure_patiente` (ordres posés 1 cran au-dessus du meilleur
  acheteur, déséquilibre ≥ 0,7, objectif 0,04) : hypothèse = les frais taker ruinent la version actuelle.
  (2) Chantier n°0, étape 1 : inventaire des sources de résolution de 100 marchés réels
  (`experiments/sources_resolution.md`) ; uefa.com domine (35 %), 22 % sans source déclarée.
  Tests : 313 verts.
- **Reste ouvert** : archivage automatique de `resolutionSource`, lecteurs dédiés, stratégie de comparaison
  au seuil ; comprendre pourquoi 5 stratégies n'ont rien tradé.
- **Limites** : inventaire sur un seul instantané ; variante non encore jugée (aucune donnée).

## 2026-10-15 (passage chercheur, ~14 h 30 UTC)

- **Lu** : CLAUDE.md, METHODE.md, feuille de mission publiée (14:26 UTC), classement, verdicts.
- **Constat** : capital réalisé 1000 (palier 1500), aucun champion, aucune obligation. market_structure :
  20 opérations, -30,24, verdict « ne fonctionne pas » (P(hasard) 0,965, frais > moitié du résultat
  sur 4). reversion : 1 opération à -231,05 (Kelly complet, 23 % du capital sur un seul pari).
  naive_favorite : 1 opération (+8,81). 6 stratégies : 0 opération.
- **Fait** : tests lancés (273 verts). Aucune modification de code : trop peu de données.
- **Reste ouvert** : market_structure à surveiller (take_profit plus large si encore négative vers
  50 opérations) ; reversion : relire la taille des mises (kelly_fraction 1,0) si 3 pertes de plus ;
  comprendre pourquoi 6 stratégies n'ont encore rien tradé.
- **Limites** : échantillon minuscule, rien testé en arène.

## 2026-10-15 (passage chercheur, ~14 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, feuille de mission publiée (13:56 UTC), classement de l'arène.
- **Constat** : système en service depuis ~2 h (0,07 jour). Capital réalisé 1000 (palier suivant 1500),
  aucun champion, aucune obligation. naive_favorite : 1 opération (+8,81). market_structure : 14
  opérations, -54,66, dont 3 où les frais dépassent la moitié du résultat. Les 7 autres : 0 opération.
- **Fait** : tests lancés (268 verts). Aucune modification de stratégie : 14 opérations / 1 opération
  ne permettent aucune conclusion (verdicts « données insuffisantes »), ajuster maintenant
  serait du surapprentissage.
- **Reste ouvert** : si market_structure reste négative après ~50 opérations, essayer un
  take_profit plus large (0,02 est proche du coût des frais + spread) ; surveiller pourquoi 7
  stratégies n'ont encore rien tradé (filtres trop stricts ou peu de signaux ?).
- **Limites** : analyse sur un échantillon minuscule ; rien n'a été testé en arène.
