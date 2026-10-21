# Journal de recherche

Une entrée datée par session de recherche (routine « chercheur » ou session manuelle) :
ce qui a été lu, fait, testé, et ce qui reste ouvert. Les plus récentes en haut.

## 2026-10-21 (passage chercheur, soir : début 19 h 54 UTC)

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
