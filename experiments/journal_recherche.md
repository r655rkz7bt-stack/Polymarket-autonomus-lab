# Journal de recherche

Une entrée datée par session de recherche (routine « chercheur » ou session manuelle) :
ce qui a été lu, fait, testé, et ce qui reste ouvert. Les plus récentes en haut.

## 2026-10-23 (passage chercheur, matin : 09 h 55 → 10 h 45 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-23_apres_echeance_match_en_cours.md` ; famille du jour 6 « ce qui ne tourne plus », puis famille 5/2).
  - **Défaut trouvé** : `apres_echeance` (copiée par le principal) achetait les favoris à 0,95-0,97 **1 à 2 h après le coup d'envoi** : pour un match, l'« échéance » Gamma est le début du
    match. 140 achats sur 173 à ce retard : 130 gagnés pour 134,4 attendus, −381 € (−7,8 %) ; le 23/10, huit jambes d'un même Cavaliers-76ers (vainqueur, 5 écarts, total) perdues ensemble :
    **−475 € sur le fantôme, ≈ −16 € pour le principal**. Correctif dans le code (3 h minimum après le coup d'envoi, un pari par événement, tests), contrôle `jambes_meme_evenement`
    (6 fantômes signalés, rien d'anormal chez la championne : +64 € sur ses 4 événements à plusieurs jambes), puis la stratégie est écartée sur le passé (voir Recherche) et éteinte.
  - Obligation `copie_fidele` (1 achat du principal sans jumeau) : ordre posé de `contrer_crypto_patiente` servi au principal une minute avant le fantôme (0,36 €), pas un défaut de copie ; le
    contrôle le classe désormais « à regarder » si le fantôme achète le même jeton dans les 48 h, « grave » sinon (test).
  - Obligations `champion_sans_avantage` (apres_echeance, nf_sport_patiente_prix_850_875) et `chance` (championne : 3 paris = 126 %, 18/10 = 225 %) : causes déjà écrites le 22/10, rien de neuf.
  - Famille 6 à la main (cycle local, lignes « abstentions ») : 14 fantômes sans aucun achat, tous expliqués (calendrier : CPI du 11/11, emploi du 6/11, classements d'IA ≥ 12 jours ; aucun écart :
    Kalshi ≤ 1,6 point, Manifold ≤ 3,6 points, cohérences ; PredictIt écarts > 0,20 refusés exprès ; clé ODDS_API_KEY absente en local).
  - 10 achats tirés au hasard relus sur Gamma : bons jetons, bons marchés (déjà connu : estimations 0,99 pour des prix de 0,92-0,95).
- **Recherche** :
  - **Après la fin du match** (`experiments/apres_fin_match.md`, 10 234 événements de 37 ligues depuis le 30/09, vrais échanges, 36 réglages) : favori à 0,94-0,985 acheté +1…+4 h après le coup d'envoi =
    −0,9 / +1,0 / 0,0 / +0,7 % (t −1,7 à +1,8), idem dans les deux tranches voisines : **écartée**. Le +2,8 % du début du fantôme était de la chance.
  - **n° 6 UFC** (`experiments/ufc_coherence.md`, 687 combats, 548/549 règlements relus) : KO + soumission + décision = 1, mais les trois jambes ne s'échangent jamais ensemble (≤ 63 paniers
    OUI et 20 NON réalisables en 15 min sur 611 combats), les OUI coûtent 1,11-1,20 : **écartée**.
  - **Tennis en jeu relu** sur le relevé de 3 semaines : +30 min −1,9 % (520 paris, 30/09-20/10) puis −4,5 % (63 paris, après) ; 499 gagnés pour 506 attendus : l'« indice » de +3,1 % ne se retrouve pas.
- **Arène** : `apres_echeance` éteinte (écartée sur le passé) ; fille `compteur_tweets_non_hors_elon_trump` (la mère « NON sans NYC Mayor » est retenue sur le passé, Elon −1 % et Trump −2 % : découpage
  a posteriori, ~60 découpages, indice de sélection) ; contrôles `jambes_meme_evenement` et `copie_fidele` affiné.
- **Reste ouvert** : l'identité par combattant des UFC à 19 marchés (volumes de quelques dollars) ; refaire le tennis en jeu avec ≥ 500 matchs ATP/WTA de plus ; vérifier que les marchés « best AI model »
  entrent dans la fenêtre de `statu_quo_ia` vers le 27/10 ; `nf_court_soir` et `nf_court_prix_haut` jouent 3 marchés d'un même match (188-277 €) : à surveiller avec `jambes_meme_evenement`.

## 2026-10-23 (session avec Etienne : verdict de la vague de volume)

- **Recherche** : `experiments/vague_volume_backtest.md` (13 714 marchés, prix payés, 72 réglages) : « contrer » écartée (36/36 perdants),
  « suivre » indice (+1,4 à +2,2 %, presque nul depuis juillet 2026 ; même règle sans vague +1,3 %).
- **Arène** : `vague_volume_contrer` éteinte ; fille `vague_volume_suivre_x5` (meilleur réglage sur 72 : sélection, l'arène confirme).
- **Reste ouvert** : `idea_test.fetch_event_trades` pourrait utiliser le paramètre `end` de data-api (échanges au-delà de 10 000, vérifié sur 5 030 échanges).

## 2026-10-23 (session avec Etienne : intégration des pistes revues)

- **Enquête** : sans objet (voir la session « anomalies » du même jour).
- **Recherche** : rapports des trois analyses à part fusionnés (`pistes_sport_coherence.md`, `pistes_crypto_elections_drames.md`, `bresil_second_tour.md`).
  Pistes 15 et 16 (Brésil) écartées ; 1, 2, 3, 5 écartées ; n° 4 : indice annexe « moins de cartes » en e-sport ; n° 11 : indice sur les seuls drames
  (le chercheur l'avait écartée sur tous les marchés longs : les deux résultats se recoupent, témoin non-drames +0,9 %).
- **Arène** : fantômes `moins_de_cartes` (scanner : `series_pages`, 91 marchés « Games Total » vus le 23/10) et `non_aux_drames` ; cycle local : 1 et 2 achats relus à la main.
- **Reste ouvert** : `non_aux_drames` immobilise l'argent 1 à 4 mois : juger après 30 paris réglés, arrêter si deux drames arrivent le même mois ;
  `moins_de_cartes` : fille LoL seule si l'arène confirme ; ajouter les filtres `start`/`end` de data-api à `idea_test.fetch_event_trades` (échanges anciens).

## 2026-10-23 (passage chercheur, nuit : 23 h 55 UTC (22/10) → 00 h 40 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-23_marches_de_saison_dans_le_sport.md` ; famille du jour 5, puis famille 3).
  - Les 4 obligations de la feuille de mission sont les mêmes que ce soir (championne, `nf_tennis_prix_bas`, concentration de `nf_sport_patiente_prix_850_875` et de la journée du 18/10) : causes déjà écrites dans les fiches du 22/10.
  - Contrôle à la main de la copie du principal (jeton par jeton depuis le 19/10) : 53 jetons de la championne copiés, mise médiane 0,333 de celle du fantôme, gain du principal −22,6 € contre −121 € chez le fantôme sur les mêmes jetons ; ses autres achats viennent de `apres_echeance`, `nf_court_prix_haut`, `contrer_crypto_patiente`, `nf_sport_patiente_prix_850_875`. Pas de défaut.
  - **Défaut trouvé** : la famille « sports » laisse passer les marchés de saison (Ballon d'Or, Série mondiale, coupes) : 15 achats de la championne, 857 €, dont **359 € (30 % du capital) sur « Mbappé gagne le Ballon d'Or, NON » à 0,94**, estimé 0,99 ; aucun test sur le passé ne couvre ce type. Le principal en a copié 18 €. Correctif : filtre `un_match` (+ test), contrôle `sport_hors_match` (+ test), sœur `nf_sport_patiente_matchs` à comparer à la championne.
- **Recherche** (vrais prix, règlement relu) :
  - **Gagnant de saison** (`experiments/saison_sport.md`, 120 événements de sport / 3 927 candidats ; 120 événements hors sport en réplication) : NON d'un candidat à 10-30 % : à 14 jours +8,2 % (91 gagnés / 84,2, t par événement +3,0), +9,9 % aux prix de vrais échanges (196 marchés) ; à 7 jours tout vient d'un seul événement (« Uniswap Cup »), à 30 jours 0 %, **hors sport non répliqué** (14 jours +5,6 %, t +0,2). ≈ 120 réglages : **indice faible**, fantôme `saison_non`.
  - **Tennis en jeu, hors échantillon** (629 matchs depuis le 20/10) : +30 min −4,5 % (43/44,7, n = 51) : ni confirmé ni infirmé (trop peu de matchs).
  - **Après l'échéance au tennis** (4 663 matchs, `experiments/tennis_apres/`) : +6 % sur prix horaires à +4…+6 h mais 85-97 % sans échange : aux prix payés +1,0 % (82 servis, t +0,35) : **écartée**.
  - **n° 12 `chiffres_ronds`** (5 187 ordres posés terminés) : servis 35,1 % (prix ronds) contre 35,3 % : **écartée**, et la mesure ne dépasse pas le simulateur.
- **Arène** : sœur `nf_sport_patiente_matchs` (championne limitée aux matchs) ; fantôme `saison_non` (NON des candidats de saison à 10-30 %, 10 à 18 jours de la fin, quart de Kelly, biais 0,04 ; 5 candidats NASCAR passent aujourd'hui les filtres). Aucune stratégie retirée.
- **Reste ouvert** : résultat du Ballon d'Or (marché fermé le 27/10) pour les 5 paris ouverts de la championne ; `bias` de la championne (décision d'Etienne) ; refaire le tennis hors échantillon avec ≥ 500 nouveaux matchs ATP/WTA ; événements à plusieurs candidats hors « sports » (cinéma, e-sport) pour la piste de saison ; comparaison à Pinnacle (piste n° 1). Une autre session a étudié les pistes 15 et 16 (`bresil_second_tour.md`) : j'ai retiré mon écoute du dépouillement, inutile.

## 2026-10-22 (session dédiée : 2e tour au Brésil, pistes 15 et 16)

- **Lu** : CLAUDE.md, METHODE.md, enquêtes, `fin_de_match.md`, `vingt_cinq_pistes.md`.
- **Fait** : accès aux résultats officiels du TSE (codes 6257/6258, chemins vérifiés) ; vitesse de
  Polymarket au 1er tour sur 31 marchés (échanges réels) ; taux de base officiels 2006-2022 (140 cas) ;
  carnets actuels des 28 marchés « 1re place » du 2e tour. Rapport : `experiments/bresil_second_tour.md`.
- **Verdicts** : piste 15 écartée (35,88 $ achetables à ≤ 0,97 après « décidé + 10 min », le vainqueur
  national à 0,99 à +140 min pour une certitude vers +300 min) ; piste 16 écartée (22/28 États déjà au
  prix de l'histoire, États serrés : références contradictoires). Aucune stratégie ajoutée.
- **Reste ouvert** : prévision à partir des résultats partiels (modèle par région) ; tester l'accès au
  TSE depuis GitHub Actions (workflow `labo-*`) avant la prochaine élection.
## 2026-10-22 (session manuelle, pistes 2, 3 et 11 aux prix payés)

- **Fait** (`experiments/pistes_crypto_elections_drames.md`, scripts dans `toucher_avant_fin/`, `marge_coherente/`, `non_aux_drames/`) :
  - n° 2 `toucher_avant_fin` : **écartée**. 8 693 paires barrière × échelle (17/08-15/10) : la cohérence « toucher ≥ au-dessus » tient aux prix payés
    (13 demi-heures sur 6 488 sous 1, 3 paniers exécutés à 1,000) ; le marché paie le toucher 4,6 fois le au-dessus et c'est ce qui arrive ; règle « 2 fois » −11 % ;
    modèle de barrière (DVOL) : 17 réglages sur 24 perdent sur la 1re moitié, le choisi fait +13,5 % sur la 2e (hausse du Bitcoin) mais t par événement 0,49.
  - n° 3 `marge_coherente` : **écartée** (indice minuscule). 13 élections (2024-2026), écart médian 1,9 point, 49 paniers sans risque vus, 18 exécutables, +0,64 % par panier.
  - n° 11 `non_aux_drames` : **retenue** (petit échantillon). 149 paris sur 106 événements de 2024 à 2026 : +4,6 % par pari, ≈ +23 %/an, 2 drames arrivés pour 9,3 attendus,
    t par événement 2,81, 26 mois sur 28 ; témoin non-drames : +0,9 % par pari (784 paris). Règle du fantôme écrite dans la fiche (mise ≤ 2 % par événement).
  - Découverte : `data-api /trades` accepte `start` et `end` : la limite de 10 000 échanges ne gêne plus (fenêtre autour de T0).
- **Reste ouvert** : créer le fantôme `non_aux_drames` (et peut-être `non_aux_outsiders_longs`, témoin 0,05-0,10) ; ajouter `start`/`end` à `idea_test.fetch_event_trades` ;
  élargir la piste 2 à avril-octobre si on veut revoir les barrières hors d'une période de hausse.
- **Limites** : piste 11 jugée sur 2 pertes seulement ; piste 2 sur 60 jours ; piste 3 sans la quantité disponible.
## 2026-10-22/23 (session à part : pistes n° 1, 4, 5 de `vingt_cinq_pistes.md`, cohérence des marchés de sport)

- **Fait** (`experiments/pistes_sport_coherence.md`, scripts `experiments/score_exact_poisson/`, `bo3_coherence/`, `tennis_sets_coherence/`) :
  inventaire Gamma par `sportsMarketType` (pagination keyset) puis test aux prix réellement payés (« avant » / « après » T0, frais, 72 réglages par piste,
  réglage sur la 1re moitié, jugement sur la 2e). Échantillons tirés par mois : 1 030 matchs de tennis, 1 417 d'e-sport, 505 de football.
- **Tennis, sets** (n° 5) : **écartée (trompeuse)** : « après » −8,9 % à +1,4 % ; le gain « avant » (+9,8 %, +74 % sur 31 paris) vient d'échanges vieux de 2 à 6 h
  (< 30 min : −6,4 %, 2-6 h : +21 %) ; le binomial est moins bon que le prix du marché lié.
- **E-sport, cartes** (n° 4) : cohérence binomiale **écartée** (mêmes prix périmés) ; découverte annexe : acheter le « Under » des totaux de cartes
  (la série finit 2-0), prix « après » : **+13,5 %, 457 paris, t par match +2,75, 10 mois sur 12, z +2,9**, deux moitiés positives, « Over » −15,5 % ;
  trouvée parmi ~90 essais : **indice fort, fantôme `esport_moins_de_cartes` proposé** (règle exacte dans le rapport ; non créé : étude seule).
- **Football, score exact** (n° 1) : **écartée (marchés trop peu négociés)** : 13 061 matchs existent mais 15 à 52 paris par réglage ; 2 paris en test.
- **Défaut à retenir** : prix « avant » d'un marché mince = prix périmé ; ranger les paris par âge du prix avant de conclure.
- **Reste ouvert** : créer le fantôme (et vérifier que le scanner voit les totaux d'e-sport, < 1 000 $/jour) ; fille LoL ; variante en jeu (état du set / de la carte).
## 2026-10-22 (session avec Etienne : skills)

- **Enquête** : sans objet (session d'outillage).
- **Recherche** : skills Polymarket publics lus en entier (`experiments/skills_polymarket.md`) ; aucun fichier installé (ordres réels avec clé privée, pas de licence) ;
  leurs stratégies existent déjà chez nous ou ont été écartées (billets météo : 0 cas sur nos 245 paris météo clôturés ; 46 billets sous 0,10 : 1 gagné pour 1,21 attendu).
  Une idée nouvelle, la vague de volume, réécrite (`VagueVolume`) ; son test sur le passé aux prix payés est lancé (`experiments/vague_volume_backtest.md`, à venir).
- **Arène** : fantômes `vague_volume_suivre` et `vague_volume_contrer` (quart de Kelly), à régler ou retirer selon le test.
- **Outils** : skills dans `.claude/skills/` (README) : nos méthodes `enqueter`, `tester-une-piste`, `nouvelle-strategie`, `verifier-tableau-de-bord`, `evaluer-source-externe` ;
  repris (MIT) `systematic-debugging`, `verification-before-completion`, `test-driven-development`, `statsmodels`, `pymc` ; bibliothèques dans `requirements-recherche.txt` (vérifiées sous Python 3.13).
- **Reste ouvert** : verdict du test de la vague de volume ; biais de la championne (0,02 ou 0,05) à décider par Etienne.
## 2026-10-23 (session avec Etienne : anomalies de l'enquête automatique)

- **Enquête** (fiche : `experiments/enquetes/2026-10-23_deux_camps_et_mises_geantes.md`) : deux camps d'un même match encore achetés le 22/10 (11 fantômes, 1 322 €) → `main._opposite_side` ;
  12 mises de fantômes au-dessus de 25 % du capital (jusqu'à 53 %) → `main._cap_ghost` ; achats hors plage : tous du 20/10, déjà corrigés le 21/10.
- **Recherche** : sans objet.
- **Arène** : biais de la championne laissé à 0,05 (à 0,02 elle deviendrait muette ; les sœurs à 0,03 et 0,02 comparent sur la même période).
- **Reste ouvert** : vérifier que les contrôles `deux_camps` et `mises` tombent à zéro après le 23/10.

## 2026-10-22 (passage chercheur, soir : 19 h 55 → 20 h 42 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-22_soir_mises_geantes_et_types.md` ; famille du jour 5, puis constat « 11 mises de fantômes au-dessus de 25 % du capital »).
  - Les 3 obligations de la feuille de mission sont les mêmes que ce matin (championne, `nf_tennis_prix_bas`, concentration de `nf_sport_patiente_prix_850_875`) : causes déjà écrites dans les fiches du jour.
  - **Mises géantes** : `nf_court_prix_haut` (fantôme) a misé 489 € (53 % de son capital) et 498 € (48 %) sur un seul pari ; cause : `bias` 0,05 fixe (estimation = prix + 0,045, mise ∝ 1/(1 − prix)), comme la championne.
  - **Types de marchés** (4 610 couples stratégie-jeton, 1 383 jetons réglés distincts, 1 896 marchés relus sur Gamma) : aucun type (moneyline, spread, totaux, score exact, crypto, « X gagne ») ne bat son prix ;
    2 300 gagnés pour 2 347,5 attendus par les prix et 2 542 annoncés, dans toutes les tranches de mise. Pas de défaut de code nouveau.
  - **Défaut de méthode trouvé en recherche** : un relevé par fenêtres sur la date de fin de l'événement oublie les événements réglés avant leur date de fin (111 échelles de dates sur 1 173, 9 %, justement celles où le OUI a gagné) : voir « Recherche ».
- **Recherche** (2 pistes de `vingt_cinq_pistes.md`, vrais échanges, règlement relu) :
  - n° 13 `contrer_football_en_jeu` (**1 110 matchs**, saut de prix en match, règlement 2 206/2 207) : **écartée**. 28 réglages ; contrarien −0,4 à −4,8 % (J 0,08-0,18), +2,4 à +6,7 % (J 0,25, z +1,0 à +1,9), **−8,8 à −10,6 % (J 0,35)** ; suiveur −0,6 à −6 % → `experiments/contrer_football.md`.
  - n° 8 `courbe_de_risque` (**1 173 échelles de dates** « by <date> », ≈ 50 réglages) : **écartée**. Première analyse (1 062 échelles) : NON à 30 jours +11,8 % (t événement +1,18) = « indice », fantôme `echelle_non` écrit et testé ; puis le relevé complété
    (111 échelles réglées avant leur date de fin) donne +8,1 % (t +0,28) et **12 réglages sur 12 « écartée »** : le fantôme est retiré. Le OUI reste perdant (−10 à −12 % à 7-30 jours), mais pas payant pour le NON (écart + frais) → `experiments/courbe_de_risque.md`.
  - n° 3 `marge_coherente` (relevé en direct, 19 h 59 UTC) : écart « vendre les tranches − acheter le vainqueur » Flávio +0,015, Lula −0,033 (4 jambes) : toujours non exploitable. Brésil, États : relevé refait (`bresil_etats/releve_20261022_2000.json`), 22 États sûrs toujours à 0,98-0,997.
- **Arène** : nouvelle sœur `nf_court_prix_haut_biais_faible` (biais 0,02 au lieu de 0,05, mêmes filtres : moins de 24 h, prix ≥ 0,90) à comparer sur la même période. Aucune stratégie issue des pistes (rien de retenu).
- **Reste ouvert** : `bias` de la championne (décision d'Etienne) ; **vérifier si les pistes à tranches du 22/10** (`queues_tranches`, `lissage_tranches`) **ont le même biais de relevé** : 133 événements à tranches (neg-risk, hors sport, volume ≥ 5 000 $) sont clos avec une
  date de fin dans le futur (Fed Chair, Nobel…) et manquent, mais leur date de décision n'est pas « fin − H » (à traiter avec la date de clôture réelle) ; piste n° 8 : la courbe de risque elle-même et les lancements de jetons ;
  pistes 15 (nuit du 25/10), 7, 12, 6 de `vingt_cinq_pistes.md` ; proposition d'audit (`proposals/2026-10-22_audit_reglements_trop_tot.md`) toujours en attente d'Etienne.

## 2026-10-22 (passage chercheur, après-midi : 14 h 55 → 15 h 38 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-22_apres_midi_copie_et_positions.md` ; famille du jour 5, puis 1 et 6).
  - Les 6 obligations de la feuille de mission sont les mêmes que ce matin (championne `nf_sport_patiente` / `nf_tennis_prix_bas` : déjà traitées dans les deux fiches du jour). Constat « à regarder » : un fantôme a misé 475 € (45 % de son capital) sur un seul pari (Michelsen, 0,924).
  - **Copie du principal vérifiée jeton par jeton** : 67 jetons copiés sur 88 achats du fantôme depuis le 19/10 (21 non copiés dont 13 datent d'aujourd'hui), taille médiane **0,338** de la mise du fantôme à tous les prix ; le principal n'a pas pris les 475 € (10,6 €). Ticket minimal ~10 € : les petites convictions sont copiées à 94-111 %. Pas de défaut.
  - **Positions non réglées** : 121 marchés clos sur Gamma ont encore une position ouverte dans les journaux, 105 chez des fantômes éteints (plus de cycle), 16 chez des actifs (UMA : les marchés de température ne passent « resolved » que 2 jours après). Aucun défaut de code.
- **Recherche** (6 pistes de `vingt_cinq_pistes.md`, toutes avec vrais prix ou carnets) :
  - n° 11 `non_aux_drames` (686 marchés hors sport) : **écartée** (~40 réglages, +2,8 % à T-60 j avec écart 0,01 puis +1,7 % avec 0,02, négatif aux autres horizons) → `experiments/non_aux_drames.md`.
  - n° 2 `toucher_avant_fin` (433 couples « touche/au-dessus » BTC-ETH-SOL, 27 561 points) : **écartée** (un seul couple à plus de 2 cents d'arbitrage ; NON du « touche » t < 1) → `experiments/toucher_avant_fin.md`.
  - n° 4 `bo3_coherence` (**2 317 matchs** LoL/CS2/Dota 2/Valorant avec leurs vrais échanges, règlement 2 290/2 291) : **écartée** (le prix du match bat le calcul tiré de la carte 1 à tous les retards, log-score 0,536-0,556 contre 0,545-0,579 ; 12 réglages ≤ +5 %) → `experiments/bo3_coherence.md`.
  - n° 5 `tennis_sets_coherence` : **écartée par manque d'échanges** (19 échanges « Total Sets » sur 25 matchs ATP).
  - n° 17 `battre_resultats` (**1 391 marchés** « beat quarterly earnings », taux de OUI 74,4 %) : **écartée** (marché calibré, 30 réglages, meilleur indice +2,9 % qui tombe à l'écart de 0,02) → `experiments/battre_resultats.md`.
  - n° 3 `marge_coherente` (Brésil, relevé en direct) : **indice, non exploitable** : tranches de Flávio 0,803 contre « vainqueur » 0,777 (+0,026, ≥ 709 parts), gain sans risque ≈ 0,65 % sur 4 jambes ; sur le 1er tour le sens change d'un mois à l'autre → `experiments/marge_coherente.md`.
  - Astuce technique : `prices-history` du CLOB refuse les fenêtres longues (400) et ne rend rien pour un marché clos avec `interval=max` : passer `startTs`/`endTs` par tranches de 15 jours.
- **Arène** : nouvelle sœur de la championne `nf_sport_patiente_biais_faible` (biais 0,03 au lieu de 0,05, même filtre ; la mère a déjà 10 filles) : les mises ne grossissent plus comme 1/(1 − prix) ; à comparer sur la même période. Aucune stratégie issue des pistes (rien de retenu). « À la une » du tableau de bord remis à jour (il datait du 17/10).
- **Reste ouvert** : `bias` de la championne (0,02 ou 0,05, décision d'Etienne) et verdict de la sœur à 0,03 dans 3-5 jours ; `experiments/marge_coherente/releve.py` à relancer avant le 25/10 (si l'écart de +0,026 persiste, stratégie à jambes multiples) ; pistes 15 (nuit du 25/10) et 7, 8, 12, 13 de `vingt_cinq_pistes.md` ; proposition d'audit (`proposals/2026-10-22_audit_reglements_trop_tot.md`) toujours en attente d'Etienne.

## 2026-10-22 (passage chercheur, midi : 09 h 55 → 10 h 39 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-22_midi_tennis_prix_bas_et_deux_camps.md`, familles 5, 3 et 6).
  - **Audit : 62 « anomalies » toutes fausses** (`audit/etat.json`) : « réglé alors que le marché n'est pas clos », apparues le 21/10 à 16 h 15 ; relues une à une sur Gamma, le règlement tombe 17 à 225 s après la fermeture
    officielle (`closedTime`) avec le bon paiement 62 fois sur 62. L'audit (`scripts/audit_fills.py`, protégé) lit `closed` trop tôt ; chaque alerte fait échouer son job (e-mail à Etienne).
    Proposition `proposals/2026-10-22_audit_reglements_trop_tot.md` (réessayer 30 minutes) ; contrôle libre `audit_anomalies` (+ test) : fausses alertes « à regarder », autres anomalies « graves ».
  - Obligations `nf_tennis_prix_bas` / `nf_sport_patiente` : 73 gagnés pour 70,8 attendus (sans les 3 meilleurs paris −15 €) ; championne par type de pari : **89 « moneyline » = +8 € (+0,1 %)**, 18 paris annexes = +136 €
    (le gain de +145 € ne vient pas du vainqueur du match). Règlements relus : 16 sur 16 conformes. Deux camps : 6 matchs, premier camp gagné 1 fois sur 6 (renversement en cours de match), pas de correctif.
- **Recherche** (`experiments/score_exact.md`, piste n° 1 ; `experiments/bresil_etats.md`, piste n° 16).
  - n° 1 `score_exact_poisson` : 9 654 matchs de football relevés, 3 471 téléchargés avec leurs échanges réels (10 400 fichiers), 2 111 utilisables, 36 501 paris aux prix des vrais échanges. Règlement relu 1 870 / 1 870.
    Modèle de Poisson (1X2 + O/U 2,5) contre prix : log-score −0,2301 contre −0,2307 ; OUI des scores à 0,03-0,30 : −8 à −20 % ; NON à 0,70-0,97 : −0,6 % ; 4 réglages × 4 seuils ; totaux O/U et BTTS (15 921 paris) : −1 à −7 % par ligne.
    **Écartée** (un seul découpage « retenue » sur 30 paris, perdu aux 3 autres réglages).
  - n° 16 `etats_comme_avant` : 27 États, votes du 1er tour TSE (données ouvertes accessibles). Le favori du 2e tour est le vainqueur du 1er tour dans 26 États sur 27 ; les 4 États incertains sont retrouvés à ±0,03 par un modèle
    de marge : **marché déjà « comme avant »**. 22 États sûrs à 0,98-0,997. **Écartée** comme écart de prix ; indice pour le quasi-certain (à confirmer le 26/10).
- **Arène** : filles `nf_sport_18_24h_vainqueur` (de `nf_sport`), `nf_sport_prix_haut_3_6h` (de `nf_sport_prix_haut`) ; `favori_politique_quasi_certain_connu` (paramètre optionnel `q_max` de `naive_favorite`, 0,99 par défaut ; la mère
  restait muette parce que son estimation plafonnée à 0,99 ne montre aucun avantage au-dessus de 0,985) ; `meteo_prevision_patiente` et `nf_sport_patiente_jour` (éliminées) mises à `enabled: false` ; la fille « nf_tennis 0,800-0,850 »
  de la feuille de mission existe déjà (`nf_tennis_prix_bas_800_850`).
- **Reste ouvert** : décision d'Etienne sur le noyau (`proposals/2026-10-22_audit_reglements_trop_tot.md`) ; `bias` de la championne (0,02 ou 0,05) toujours à trancher ; résultat des 22 États sûrs le 25/10 (relancer
  `experiments/bresil_etats/releve.py` avant le 25/10 puis après) ; piste n° 15 (dépouillement en direct) : seulement la nuit du 25/10 ; totaux et handicaps de football des matchs de moins de 3 000 $ de volume non téléchargés ;
  piste n° 2 (`toucher_avant_fin`) : non commencée (les relevés Gamma ne montrent que peu d'événements « touche » réglés ; à vérifier) ; principal : 88 % en caisse (713 € de 795 €) par la mise sur l'avantage mesuré, pertes venues de `nf_court` (−145 €) et `meteo_prevision` (−58 €) d'avant la copie fidèle.

## 2026-10-22 (passage chercheur, nuit : 04 h 55 → 05 h 51 UTC)

- **Enquête** (fiches : `experiments/enquetes/2026-10-22_championne_biais_et_mises.md`, `..._muettes_budget_cotes.md`, et la 3e ligne du README ; familles 5 puis 2, 6 et 3).
  - Obligations sur `nf_sport_patiente` : **sans ses 3 meilleurs paris +2 € (sur +126 €)**, sans les 5 meilleurs −48 € ; 95 gagnés pour 90,8 attendus ; depuis que le principal la copie (18/10, 21 h 30) elle fait −30 € sur 58 paris,
    le principal −19 € sur 48. Cause : `bias 0,05` fixe, donc `mise ∝ 1/(1 − prix)` (111 € à 0,95, 74 € à 0,82) ; 25 paris à 0,925-0,95 = −522 €. Sur **530 favoris de sport de toute l'arène (un jeton = un pari)** :
    459 gagnés pour 460,9 attendus par les prix : le biais n'existe à aucun prix. Contrôle `estimation_gonflee` (+ test) : arène 827 gagnés pour 938,8 annoncés (z −9,7). Championne **non modifiée** (décision à Etienne : `bias` 0,02 sur les sports).
  - Stratégies muettes : la mère `naive_favorite` n'est pas sourde (279/429 hors plage, 28 « avantage net insuffisant » : `min_net_edge 0,02`) ; 12 stratégies à zéro achat dont 9 expliquées (cohérence / références) ;
    **budget des cotes (The Odds API) épuisé à 12 h 57 UTC le 21/10** : `OddsApiSource.allowed_today` étale les 12 crédits sur la journée (+ test).
  - Pistes sur événements à tranches : le même défaut revient 3 fois (prix `prices-history` d'un carnet vide ou écarté) ; règle ajoutée au README des enquêtes.
- **Recherche** (`experiments/queues_tranches.md`, `experiments/proposition_uma.md` ; pistes n° 14, 10, 9 de `vingt_cinq_pistes.md`). 990 événements à tranches (17 796 marchés, août-octobre) puis 43 207 marchés d'avril à octobre.
  - n° 14 `proposition_uma` : **écartée** (33 des 36 marchés « proposed » à 0,9995).
  - n° 10 `queues_tranches` : **écartée** (NON des OUI à 3-25 % : −1,3 % à +0,9 %, 18 réglages) ; tranches moyennes 0,25-0,60 : +8,8 % au prix du CLOB mais −0,6 % aux prix payés (520 paris) : **trompeuse**.
  - n° 9 `lissage_tranches` : pic isolé +20 % (t +6) au prix du CLOB, **+2,0 % (t +0,4) aux prix payés** (13 pics sur 58 ont un échange réel) : **trompeuse** ; creux : rien.
- **Arène** : filles `nf_sport_18_24h` et `nf_sport_925_950` (de `nf_sport`, pistes 80/20, la seconde avec la réserve écrite dans le YAML) ; pas de fille `nf_tennis` 0,80-0,85 (existe déjà : `nf_tennis_prix_bas_800_850`, −9,8 € sur 12 paris) ;
  `nf_sport_patiente_soir`, `_non`, `_vainqueur` mises à `enabled: false` (éliminées). Aucune stratégie issue de la recherche (rien de retenu).
- **Reste ouvert** : décider du biais de la championne (0,02 ou 0,05) ; `football_trois_issues` et `cotes_tennis` à revoir dans 2 jours (cotes du soir étalées) ; `prix_payes.py` et le contrôle de l'échange réel à T0 comme étape
  obligatoire des tests de tranches ; piste n° 1 (`score_exact_poisson`) et 2 (`toucher_avant_fin`) ; 31 000 marchés d'avril-juillet restent à télécharger (`releve_prix.py`, reprise possible) mais le verdict ne changerait pas
  sans prix d'échange ; 2e tour au Brésil le 25/10 (pistes 15 et 16).

## 2026-10-21 (passage chercheur, soir : 19 h 54 → 20 h 41 UTC)

- **Enquête** (fiches : `experiments/enquetes/2026-10-21_soir_capital_bloque_et_carnet_vieilli.md`, `..._posees_sous_la_plage_suite.md` ; famille 4 du jour, puis 6 et 5).
  - Aucune enquête obligatoire. Suite « ordres posés sous 0,80 » : −12,0 % mais **concentré sur le 20/10** (+82 € le 18, −211 € le 20, t par événement −0,9) ; les 6 achats du
    champion sous 0,80 ont tous gagné ; déjà corrigé le 21/10 (`prix_min 0.80` sur l'ordre posé) : aucun changement.
  - **Mères sans argent** : `naive_favorite`, `favori_politique` (+3 variantes), `naive_favorite_large/_sans_fin` à moins de 1 % d'argent disponible des jours durant (Kelly complet) pendant que leurs
    filles achetaient (118 jetons sur 122 absents de la mère) : une fille « bat sa mère » sans règle meilleure. Contrôle `capital_bloque` ajouté (+ test). La mère `naive_favorite` n'a plus acheté
    depuis le 18/10 alors qu'elle avait 87 → 257 € : **cause non établie** (un cycle local avec argent neuf : elle propose et exécute).
  - **Carnet du début de cycle rejeté « périmé » avant relecture** (`main._execute`) : 12 rejets sur 158 propositions dans un cycle local de 2 min ; corrigé (le contrôle après relecture garde le plafond d'âge) + test.
  - **Stratégies sourdes** : `cpi_tranches` et le nouveau `jobs_favori_non` ne voyaient aucun marché (emplois et CPI : 400-2 000 $ de liquidité, ~0-700 $ de volume par jour, écartés par `min_volume_24h 1000`).
    Corrigé : `scanner.tag_pages` pour les étiquettes nfp (102964) et cpi (101701) + test (le CPI du 21/10 matin, 0 achat, était sourd depuis sa naissance).
- **Recherche** (`experiments/emploi_nfp.md`, piste n° 3 : emploi américain). 28 événements « jobs added » + 26 de chômage, 81 794 échanges réels, règlement relu 27/28 contre les chiffres officiels
  (septembre 2025 : Polymarket « 0-25 k », officiel +119 k). Chômage bien calibré (**écartée**). Emploi : la tranche favorite gagne 5 fois pour 11,1 attendues à T-24 h (z −2,4) ; chez Kalshi (non biaisé par le
  choix du favori) z ≈ −1,3 ; NON aux prix payés +20 à +50 % (9-15 paris). ~200 cellules regardées. **Verdict : indice**. Comparaison Kalshi : les deux marchés s'accordent (Brier 0,1644 / 0,1640).
- **Arène** : `jobs_favori_non` (classe `JobsFavoriNon`, test) ; filles de la feuille de mission `nf_tennis_vainqueur` et `nf_tennis_12_18h_vainqueur` (le morceau « prix 0,80-0,85 » existait déjà :
  `nf_tennis_prix_bas_800_850`) ; 8 éliminées mises à `enabled: false` (cotes_bookmakers, nf_court_hors_sport, nf_long, nf_sport_patiente_demi_mise / 2crans / large / prix_moyen, nf_sport_tres_court).
- **Piste n° 7 (autres séries économiques)** : demandes d'allocations (23 événements de 2021-22) et PIB / ISM (14 événements) : **écartées** ; la tranche favorite des PIB / ISM ne perd pas plus que son prix (z −1,0 à +1,4) : l'effet des emplois ne généralise pas (argument de plus pour « indice »).
- **Piste n° 4 (essence AAA)** : relevé commencé (`experiments/essence/releve.py`) ; pas testable (6 jours de marchés quotidiens, AAA inaccessible en 403).
- **Reste ouvert** : résultat du NFP du 6/11 pour `jobs_favori_non` ; pourquoi `naive_favorite` (mère) n'achète plus malgré son argent (publier propositions et rejets par cycle : `cycle.yml` est protégé, proposition
  à écrire) ; relancer `essence/releve.py` ; autres stratégies à zéro achat à vérifier avec les abstentions de production (`statu_quo_ia`, références Kalshi/PredictIt/Manifold, `mots_prononces_nfl`).

## 2026-10-21 (session avec Etienne, après-midi : AMELIORATION, réponse « Tout »)

- **Règlements par lots** : 723 marchés détenus lus en 3,7 s au lieu d'environ 79 s (même règlement sur 25 vérifiés un par un) ;
  détection de panne de Gamma (panne réelle vers 15 h 25 UTC : scanner vide, 79 s de relectures en 404).
- **Historique des références** : table `historique_references`, une photo par heure, pour tester plus tard Polymarket contre Kalshi / Pinnacle.
- **Championne et filles** : plus d'ordre posé servi sous 0,80 (`prix_final`), suite de l'enquête « posées sous la plage ».
- **Ménage** : retrait sous 750 € après 20 opérations (à blanc : `cotes_bookmakers`, `nf_sport_tres_court`).
- **Budget du chercheur** (PR #106, #108) : passages pilotés par `scripts/budget_chercheur.py` à partir du samedi 24/10, 60 h par semaine au départ.
- **Enquête du 18/10** (`experiments/enquetes/2026-10-21_journee_du_18.md`, arrive avec la PR #103) : chance puis sélection sur la chance (sans le 18/10, confiance 0,43).
  Etienne garde la règle actuelle (pas de règle « sans sa meilleure journée »).

## 2026-10-21 (passage chercheur, ~15 h UTC)

- **Enquête** (détail : `experiments/enquetes/2026-10-21_soir_copie_ordres_poses_et_deux_camps.md`, famille 4 du jour + 1 et 2).
  - Aucune enquête obligatoire. `copie_fidele` (4 copies « à 100 % ») : **faux positif** : ordres posés remplis en 3 à 5 fois, le principal prend 31-32 % du total du fantôme
    (part prévue un tiers). Contrôle réécrit (comparaison par ordre posé) + test du cas réel.
  - `deux_camps` re-mesuré : 9 paires mais 3 matchs seulement (premier camp 0/9 gagné, −630 € ; deuxième 9/9, +66 €) : pas assez pour bloquer le camp opposé.
  - **`idea_test.verdict` trompeur** : 12 victoires sur 12 aux prix 0,78-0,95 = « retenue » (t +6) alors que les prix seuls le font arriver 23 % du temps. Ajout de `z_prix`
    (« retenue » seulement avec `z_prix ≥ 1,5`), test ajouté.
- **Recherche** (`experiments/classements_status_quo.md`, piste n° 2). 211 événements réglés (règlement relu 209/211). IA : le leader à J-14 / J-30 gagne un peu plus que son prix
  (12/12 pour 10,6 attendus aux prix payés, +13 %), mais P(hasard) = 23 % et ~45 découpages : **indice**. Plus grande entreprise (J-3 −13 %, J-1 −18 %) et applis n° 1
  (−9/−10 %) : **écartées** (le leader perd plus que son prix). Spotify : 6 mois, rien.
- **Arène** : fantôme `statu_quo_ia` ; filles de la feuille de mission `nf_tennis_prix_bas_vainqueur` et `nf_tennis_prix_bas_800_850` (la troisième, `nf_sport_patiente_tennis_875_900`,
  existait déjà) ; `nf_sport_patiente_oui` et `nf_tennis` (éliminées) mises à `enabled: false`.
- **Reste ouvert** : confirmer `statu_quo_ia` sur les mois de novembre et décembre (leader Google à 0,58 pour fin novembre) ; relire les anciens « retenue » avec `z_prix` ;
  NFP contre Kalshi ; LMArena (scores publics) comme référence du leader d'IA ; `deux_camps` à refaire avec plus de matchs.

## 2026-10-21 (passage chercheur, ~10 h UTC)

- **Enquête** (détail : `experiments/enquetes/2026-10-21_posees_sous_la_plage.md`, famille 4 « le filtre ne filtre pas »).
  - Aucune enquête obligatoire dans la feuille de mission. Contrôle à la main sur le constat `filtre_prix` (11 achats hors plage) : les ordres posés servis
    **sous 0,80** (famille nf_sport_patiente/nf_tennis, 44 paris distincts, 1 601 € misés) font **−11,9 %** contre +6,7 % dans 0,80-0,875 (t −1,2 : indice de
    sélection adverse, pas de preuve). Pas de défaut de code ; à confirmer sur de nouveaux paris avant de passer les mères en `prix_final`.
  - `positions_oubliees` : marché 5167158 (« Russia target Kyiv ? ») en litige UMA (`disputed`), 5 portefeuilles bloqués 78 h : légitime, rien à corriger.
  - `copie_fidele` (4 copies partielles à 100 %) et `estimation_perimee` (modèles, pas des carnets périmés) : revus, pas de nouveau défaut.
- **Recherche** (`experiments/cpi_nowcast.md`, piste n° 3 : CPI américain). 48 événements réglés (règlement relu 48/48), 337 tranches, 205 703 échanges réels.
  Les cases à 3-25 % gagnent ~moitié moins que leur prix ; NON : +3 à +6 % par achat aux prix réels (12 réglages essayés, 10 positifs ; core négatif).
  **Verdict : indice** (47 événements, tranches liées, beaucoup de tranches sans échange avant la décision). Nowcast de Cleveland non testé (pas d'historique par versions).
- **Arène** : nouvelle stratégie `cpi_tranches` (classe `CpiTranches`, test) ; filles de la feuille de mission `nf_sport_vainqueur` et `nf_sport_patiente_tennis_850_875`
  (`nf_sport_patiente_tennis_875_900` existait déjà) ; 12 stratégies éliminées mises à `enabled: false`.
- **Reste ouvert** : confirmer `cpi_tranches` sur le CPI du 11/11 ; `prix_final` sur les mères si les achats < 0,80 restent négatifs ; piste suivante : emploi (NFP) contre Kalshi,
  champions de saison (besoin d'une clé The Odds API, absente de la routine) ; `cotes_bookmakers` toujours muette/perdante.

## 2026-10-21 (session avec Etienne, matin : AMELIORATION, lot 1)

- **Cause des stratégies muettes trouvée** : références rattachées aux seuls 150 marchés surveillés et pas de `candidates()`
  pour les stratégies à référence ; marchés « mentions » tous écartés par le scanner (liquidité médiane 170 $ pour un seuil de 1 000 $).
  Corrigé (ARCHITECTURE § 48). Cycle local réel : `mots_prononces` 2 achats, `mots_nouveaux` 2 propositions, mentions 51 rattachées,
  `fatigue_nhl`, `compteur_tweets` et `outsider_itf` proposent ; Kalshi et PredictIt évaluent (« avantage net insuffisant »).
- **Raisons d'abstention** maintenant publiées à chaque cycle (demandé au passage de ~0 h) : `cotes_bookmakers` pourra être tranchée.
- **Cycle** : 115 s → 55 s en local (index de rapprochement, règlements dédoublonnés, battements des fantômes espacés).

## 2026-10-21 (passage chercheur, ~5 h UTC)

- **Enquête** (détail : `experiments/enquetes/2026-10-21_filtres_et_prix_executable.md`, famille 4 « le filtre ne filtre pas »).
  - Aucune enquête obligatoire dans la feuille de mission. Le contrôle `filtre_prix` ne lisait pas la plage de prix des filles (`filtres.prix_min/prix_max`) :
    sur 1 279 opérations clôturées, **13 achats hors plage** (9 gagnés, +20,7 €). Cause : `Filtered` filtre le prix du vendeur, puis `PatientOrders`
    pose l'ordre jusqu'à 10 centimes plus bas. Correctif : filtre `prix_final` (le mode patient passe dans la fille) pour les nouvelles filles ; contrôles
    `filtre_prix` (filles) et `filtre_delai` ajoutés, 2 tests. Fenêtres de délai (`echeance_*`, `heures_*`, `heure_utc`) vérifiées : respectées.
  - Constats « à regarder » : `estimation_perimee` (mises prises sur un modèle, pas sur un carnet périmé ; 3 achats du principal datent d'avant le
    correctif de la veille) et `copie_fidele` (2 exécutions partielles copiées à 100 % : non creusé).
- **Recherche** (`experiments/mentions_annonceurs.md`) : piste n° 1, mentions « the announcers » et « anyone », 3 555 marchés, vrais échanges de 198 événements,
  règlement relu (607 marchés à seuils, 0 incohérence). **+31 % au prix horaire (t +6,8) devient −7 % aux prix payés** : 715 prix à exactement 0,50 (carnets vides),
  le même défaut que la météo du 16/10. « anyone » : écartée (presque aucun échange) ; Coupe du monde : écartée (−4 % à −34 %, 7 réglages sur 7) ;
  **NFL : indice** (+21 % à +91 %, 14 matchs, 6 réglages sur 6 positifs, deux mois). ~15 découpages regardés.
- **Arène** : `mots_prononces_nfl` (fantôme, nouveau filtre `question_contient/exclut`, historiques séparés pour les annonceurs) ; les trois filles de la feuille de
  mission : `nf_sport_patiente_tennis_875_900`, `nf_sport_patiente_72_168h_850_875` (avec `prix_final`) et `nf_sport_football`.
- **Reste ouvert** : confirmer `mots_prononces_nfl` sur les prochains matchs de NFL ; `mots_prononces` (mère) joue peut-être encore des annonceurs Coupe du monde ;
  copies partielles du principal (Mannarino, Lynn Vision) ; `cotes_bookmakers` toujours muette ; piste suivante : champions de saison contre Pinnacle.

## 2026-10-21 (passage chercheur, ~0 h UTC)

- **Enquête** (détail : `experiments/enquetes/2026-10-21_type_de_pari_et_reglement.md`, famille 3) : aucun défaut de code nouveau.
  - Règlement relu sur Gamma : 30 paris tirés au hasard sur 1 944 réglés, 30 / 30 conformes (jeton, camp, résultat).
  - Estimation périmée : écart estimation − prix p99 0,366 avant le correctif de 14 h 27, **0,075 après** (416 achats) ; les écarts restants
    sont des modèles (tweets, décroissance du temps), pas des carnets périmés. Les 3 achats du principal signalés datent d'avant le correctif.
  - Type de pari des variantes « favori » : vainqueur **+0,0 %** (28 837 € misés, 414,5 gagnés pour 411,7 attendus) ; handicap −10,5 %
    (principal −14,9 %, 13 paris) ; « autre » du principal −20,6 % (47 paris, météo). Pas d'avantage « favori » sur le vainqueur, en cohérence
    avec `selection_multiple` (la championne est le meilleur de 42).
  - `cotes_bookmakers` toujours muette (≈ 44 h) : cause non tranchée, la sauvegarde n'a pas les observations ni le budget de crédits.
- **Recherche** (`experiments/tweets_filles.md`) : piste n° 1, compteur de tweets, 182 périodes / 7 comptes (règlement relu 178 / 182),
  référence retrouvée (+12,2 %). **NON seulement, sans NYC Mayor : retenue** (+16,3 % par achat, +12,8 % par période, t +3,9 ; 6 réglages sur 6
  positifs, 4 mois sur 4, deux moitiés positives). Elon seul (−3,6 %) et 48 dernières heures (+1 %) : écartées. Elon et Trump ≈ 0.
  ~60 découpages regardés.
- **Arène** : `compteur_tweets_non` (nouveau réglage `only_no` / `skip_nyc` dans `CompteurTweets`, avec test) ; `nf_sport_patiente_vainqueur` ;
  les trois filles de la feuille de mission (`nf_court_soir`, `nf_court_football_soir`, `nf_sport_patiente_12_18h`).
- **Reste ouvert** : consigner la raison d'abstention de chaque stratégie à chaque cycle (pour trancher `cotes_bookmakers`) ; la mère
  `compteur_tweets` n'a que 3 opérations en direct ; piste suivante : mentions (« the announcers », « anyone »).

## 2026-10-20 (passage chercheur, ~20 h UTC)

- **Enquête** (détail : `experiments/enquetes/2026-10-20_soir_copie_et_deux_camps.md`) : aucun nouveau défaut de code.
  - Obligation « le 18/10 fait 84 % du gain » : déjà traitée à 15 h (z 1,86 / meilleur de 35, contrôle `selection_multiple`) ; rien de nouveau.
  - Copie du principal (famille 1) : 33 jetons, 0 absent du fantôme, mise médiane = 0,34 de celle du fantôme (0,21-0,44).
  - Deux camps : 11 marchés, principal compris (Safiullin/Shimabukuro, −20 €) ; le 2e achat a rapporté +67 € sur 9 paires
    hors teneur de marché : pas de blocage créé. Le contrôle automatique ignore le principal.
  - `cotes_bookmakers` muette depuis le 19/10 04 h (≈ 40 h) : tous ses paris étaient des handicaps pris pour le vainqueur,
    avant le correctif #81. Non tranché si le filtre retire tout ou si le rattachement est cassé.
- **Recherche** (`experiments/nba.md`) : fatigue NBA, 1 222 matchs 2025-26 (basketball-reference + Gamma + prices-history), règlement
  relu 1 231/1 231. Pente repos +0,007/jour (t +0,5) ; 7 découpages dans des sens opposés : **écartée**.
- **Arène** : trois filles de la feuille de mission : `nf_court_football`, `nf_tennis_12_18h`, `nf_sport_patiente_72_168h_12_18h`.
- **Reste ouvert** : abstentions de `cotes_bookmakers` ; refaire le contrôle des deux camps à 30 paires ; la piste n° 1 de PISTES.md est
  maintenant `compteur_tweets, filles`.

## 2026-10-20 (session avec Etienne, ~16 h UTC) : achat échelonné et façons d'entrer / sortir

- **Demande** : « acheter un petit bout, attendre, racheter… ; trouver des stratégies similaires ».
- **Recherche** : études (Vanguard, Kaminski & Lo, Polymarket et Kalshi) + 386 vrais paris (chemin
  minute par minute) + 2 152 matchs passés + vrais échanges. Échelonné, renfort en baisse ou en
  hausse, stops, prises de gain : écartés (prix juste après une chute). Découverte : favoris ITF
  −13,9 % aux vrais prix (5 semaines perdantes) ; outsiders ITF +17 % (indice, 150 matchs).
- **Arène** : `outsider_itf`, `nf_sport_patiente_sans_itf` ; filtres `sources` / `sources_exclues`.
- **Reste ouvert** : outsider_itf peut rester muette si le scan ne voit pas les matchs ITF (peu
  de volume) : l'enquête automatique le dira. Détail : `experiments/achat_echelonne.md`.

## 2026-10-20 (passage chercheur, ~15 h UTC, 1 h de travail)

- **Enquête** (détail : `experiments/enquetes/2026-10-20_championne_chance_et_en_jeu.md`) :
  - obligation « le 18/10 fait 88 % du gain » : la championne `nf_sport_patiente` gagne 86 paris pour 79,8
    attendus (z 1,86) ; c'est le **meilleur z de 35 stratégies** (≈ 2,1 attendu sans aucun avantage), et ses
    variantes non patientes ont le même rendement (+4,3 %). Le 18/10 : 29 gagnés sur 29 (probabilité 0,7 %).
    Pas un avantage prouvé. Nouveau contrôle `selection_multiple` ;
  - **84 % de ses achats sont faits après le coup d'envoi** (médiane « horizon » affichée 165 h = date de fin
    placeholder de Gamma, règlement réel 2,2 h après l'achat) : les filles « délai 72-168 h » mesurent la
    convention de date de chaque sport. Le journal inscrit désormais `depuis_coup_d_envoi_h` ; contrôle `achats_en_jeu` ;
  - deux camps d'un même match achetés (Falcons/BetBoom, Safiullin/Shimabukuro : −275 €), seulement par les variantes à
    ordre posé : contrôle `deux_camps` ;
  - 10 paris relus sur Gamma (règlement, camp, type de pari) : conformes ; copie à 100 % sur exécution partielle
    expliquée (ordre posé recopié à sa taille demandée, 2 paris sur 32, non corrigé) ; `positions_oubliees` ne
    regarde plus les stratégies coupées ni les teneurs de marché (faux positifs).
- **Recherche** (`experiments/tennis.md`) : piste n° 1 tennis, 6 131 matchs (Gamma + prices-history + vrais échanges),
  règlement relu (2 261 / 2 263 cohérents). Avant le match : rien (+0,6 %). Recalibrer le prix ne bat pas le marché hors
  échantillon. En jeu, favori 0,80-0,95 à +30 min, aux prix réellement payés : **+3,1 % par mise** (1 096 matchs, t +2,8,
  4 mois sur 4, mais 1re moitié +4,5 % et 2e +1,6 %, ~40 réglages essayés) → **indice**, fantôme `nf_tennis_debut_match`.
  E-sport (CS2/LoL/Dota/Valorant, 23 379 marchés) : **écartée** (−0,1 % à +0,6 %). Autres sports (14 097 marchés) : **écartée**
  (−1 % à −2 % par mise : l'effet du tennis n'est pas un biais général). Sackmann inaccessible.
- **Arène** : ajoutées `nf_tennis_debut_match` et les trois filles de la feuille de mission
  (`crypto_threshold_prix_bas`, `crypto_threshold_24_72h`, `nf_sport_patiente_prix_850_875`) ; coupées les éliminées
  `calibration` (v2) et `choc_sans_nouvelle`.
- **Reste ouvert** : la championne est-elle encore bonne en dehors de la chance ? (regarder ses paris à partir du
  21/10) ; écart de classement au tennis (autre source que Sackmann) ; pourquoi le tennis en jeu seul bat les frais ; suivi des paris en jeu (`depuis_coup_d_envoi_h`) dans l'enquête dans 2 jours.

## 2026-10-20 (session avec Etienne, ~14 h UTC) : enquête et chercheur « profond »

- **Demande** : « que le chercheur fasse des recherches plus profondes, cherche les problèmes comme
  celui du principal qui augmentait les mises, et de vraies recherches sur les nouvelles
  stratégies ; pousse-le beaucoup plus ». Constat : les 5 routines duraient 1 à 2 minutes.
- **Enquête** (journaux publiés, 101 fantômes + principal) : achats sur carnet périmé (estimation
  0,98, payé 0,817, 8,9 % du principal) → corrigé (`relecture.chute_max`) ; la championne fait 95 %
  de son gain le 18/10 et n'a plus d'avantage mesurable depuis ; filles jugées sur une autre
  période que leur mère ; « demi-mise » ne fait pas les mêmes paris ; plage de prix contournée par
  les ordres posés ; copie à 100 % sur exécutions partielles. Détail :
  `experiments/enquetes/2026-10-20_carnet_perime.md`.
- **Outils** : `enquete.py` (11 contrôles, dans la feuille de mission), `scripts/enquete.py` et
  `scripts/fetch_data.sh` (sans clé), `idea_test.verdict`, `experiments/PISTES.md`, scripts des
  vingt pistes rangés en exemples. Consigne du chercheur réécrite (A enquête, B une piste
  jusqu'au verdict, C arène ; 45 à 90 minutes).
- **Reste ouvert** : obligation « championne sans avantage depuis le 19/10 » (cause à trouver) ;
  piste n° 1 de PISTES.md (tennis).

## 2026-10-20 (passage chercheur, ~10 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, feuille de mission (09:49 UTC) : capital réalisé 813,67 (palier 1500, 4,9 jours sans palier),
  champion nf_sport_patiente (78 opérations, +228). Obligations : 3 filles de l'entonnoir 80/20 (`pareto.md`).
- **Fait** : les 3 filles, sans nouveau code, chacune dans son fantôme : `nf_sport_patiente_72_168h` (délai 72-168 h, 45 op., +11,4 %
  par mise), `nf_sport_patiente_matin` (achat 6-12 h UTC, 28 op., +7,1 %), `crypto_threshold_non` (issue non, prix <= 0,80, 9 op.,
  très petit échantillon ; la mère est en pause, la fille a 2 propositions par cycle). Test de configuration mis à jour, 407 tests verts.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire ». `nf_sport_patiente_jour`/`soir` toujours sans résultat.
- **Limites** : les morceaux gagnants sont des pistes (échantillons petits, z < 2), pas des preuves ; rien vérifié en réel.

## 2026-10-20 (passage chercheur, ~06 h UTC)

- **Lu** : CLAUDE.md, METHODE.md, CHANTIERS.md, feuille de mission (04:49 UTC) : capital réalisé 804,43 (palier 1500, 4,7 jours
  sans palier), champion nf_sport_patiente (73 opérations, 1184 en fantôme). Aucune obligation.
- **Fait** : variante `nf_sport_patiente_jour` (sans nouveau code : champion sport + ordre posé, seulement 0-18 h UTC),
  complément de `nf_sport_patiente_soir`. Test de configuration mis à jour.
- **Pas fait** : chantier n°0 étape 3 sport, Kalshi/Manifold : restent « à faire » (passage court).
- **Limites** : échantillon nul au départ ; ordres posés, markout à surveiller. Rien vérifié en réel.

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
