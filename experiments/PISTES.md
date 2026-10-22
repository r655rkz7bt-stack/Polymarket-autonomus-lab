# Pistes de recherche profonde (liste de travail du chercheur)

Une piste = une hypothèse qui peut rapporter, à TESTER SUR LE PASSÉ avec de vrais prix avant
d'entrer dans l'arène (protocole : docs/ROUTINE_CHERCHEUR.md, partie B ; exemples :
experiments/vingt_pistes/scripts/). À chaque passage, le chercheur prend la première piste « à
tester » (ou en ajoute une meilleure, en disant pourquoi), la mène jusqu'au verdict
(`idea_test.verdict` : retenue / indice / écartée) et met à jour son état ici, avec le chiffre.
Une piste écartée reste écrite : on ne la refait pas sans idée nouvelle.

Ordre : gain espéré × facilité de test. Les marchés répétitifs et peu liquides (tweets, mentions)
ont été les plus battables le 20/10 ; les marchés suivis par des robots (crypto au jour près) non.

## À tester
0. **Vingt-cinq pistes inédites du 21/10/2026** : `experiments/vingt_cinq_pistes.md` (ordre conseillé en fin de fichier ; 15 et 16 avant le 2e tour au Brésil, le 25/10). Faites le 22/10 : n° 2 (écartée), n° 11 (écartée), n° 14 (écartée), n° 10 (écartée), n° 9 (voir « Testées »), n° 1 (écartée, `score_exact.md`). n° 16 (relevé fait, voir « Testées »). Restent dans l'ordre : 3, 4, 5, puis 15 (nuit du 25/10).
1. **Champions de saison contre Pinnacle** (golf, F1, football européen : outrights de The Odds API).
2. ~~Classements « status quo »~~ : testés le 21/10 (soir), voir « Testées » ; reste Spotify mensuel (6 mois seulement) et les classements LMArena eux-mêmes (historique des scores non testé).
3. **Données économiques** : le CPI et l'emploi (NFP) sont testés (voir « Testées » : `cpi_tranches`, `jobs_favori_non`, `emploi_nfp.md`). Reste : le nowcast de Cleveland pour le CPI
   (historique par versions introuvable), une prévision indépendante (consensus, ADP) pour l'emploi, les demandes d'allocations chômage hebdomadaires (même mécanisme : tranches fines).
4. **Prix de l'essence (AAA) au jour près** : relevé commencé le 21/10 (`experiments/essence/releve.py` → `releve.csv`, à relancer à chaque passage). Marchés « Gas prices on <date> ? » (6 tranches
   de 1 cent du prix moyen AAA, ~700-2 200 $ de volume par jour, nés le 16/10/2026 : 6 jours seulement ; février 2025 : 2 jours) et « What will gas hit the week of… / by end of <mois> » (10-14 tranches,
   depuis mars 2026). **Pas encore testable** : AAA est inaccessible (403, pas de contournement), l'EIA hebdomadaire existe (`eia.gov/dnav/pet/hist_xls/EMM_EPMR_PTE_NUS_DPGw.xls`) mais pas au jour près.
   À reprendre quand ~40 jours sont réglés : le prix du jour tient-il son niveau de la veille (variation d'un jour = quelques cents, marché de tranches à 1 cent) ? Modèle de marche aléatoire calibré sur les
   gagnantes précédentes (aucune autre source nécessaire), comme le test crypto (négatif : marché suivi par des robots, mais ici les volumes sont minces).
5. **Mots nouveaux par type d'événement** (rallye, conférence, mois entier) : reste de l'ancienne piste n° 1 ;
   les « annonceurs » et « anyone » sont jugés (ci-dessous).
6. **Matchs de NFL, suite** : `mots_prononces_nfl` (fantôme) à confirmer sur de nouveaux matchs ; si oui,
   tester les mots à seuil (« Referee 5+ times ») séparément des mots simples.

7. **Autres données économiques à tranches** (21/10, `experiments/emploi_nfp/claims_releve.py`, `macro_releve.py`, `macro_favori.py`). **Demandes d'allocations hebdomadaires : écartée** (23 événements, tous de 2021-2022 sauf février 2025,
   811 échanges réels). **PIB américain et ISM (services, industrie) : écartée** (19 événements réglés, 14 avec heure de publication ; la tranche favorite gagne 8/5,5, 3/4,8, 4/4,8, 5/3,7 à T-6/24/72/168 h, z entre −1,0 et +1,4 :
   rien de régulier, et le sens inverse de celui des emplois : l'effet « tranche favorite surévaluée » n'est pas général, il tient peut-être aux seuls emplois). Reste : « Fed decision in <mois> » (16, bien piloté par les contrats
   à terme : pas de source gratuite). Méthode et scripts réutilisables : `experiments/emploi_nfp/` ; l'API `historical/` de Kalshi donne chiffres officiels et prix horaires (~3 s par appel).

## Testées
| Piste | Verdict | Chiffre clé | Où |
|---|---|---|---|
| achat échelonné, renfort en baisse ou en hausse, stop-loss, prise de gain, stop suiveur | écartées | prix juste après une chute (2 152 matchs) ; tennis −5 à −6 % | achat_echelonne.md |
| favoris ITF (à éviter) | écartée | −13,9 % aux vrais prix, 5 semaines perdantes | achat_echelonne.md |
| outsider_itf | indice | +17 % aux vrais prix (150 matchs) | achat_echelonne.md |
| favoris e-sport | écartée | −0,4 % aux vrais prix | achat_echelonne.md |
| compteur_tweets | retenue | +12 % par achat, chaque mois gagnant (177 périodes) | vingt_pistes.md |
| mots_prononces | retenue | +19 à +27 % (billets ≥ 0,30) | vingt_pistes.md |
| mots_nouveaux | indice | +9 à +20 % (2 mois seulement) | vingt_pistes.md |
| fatigue_nhl | indice | +6 %, t +1,2 (2 saisons, même sens) | vingt_pistes.md |
| haut_ou_bas_crypto | écartée | −16 % par achat, t −8 | vingt_pistes.md |
| totaux de buts NHL | écartée | marché bien calibré | vingt_pistes.md |
| séries NHL | écartée | rien de régulier | vingt_pistes.md |
| vague d'opinion (presse) | écartée | −9,1 % | vague_opinion/ |
| copier les portefeuilles gagnants | écartée | −9,7 % ensuite | smart_money.md |
| Kalshi contre Polymarket en sport | écartée | prix identiques à 0,4 point | sport_kalshi.md |
| tennis, favori avant/pendant le match (6 131 matchs) | indice | en jeu à +30 min, favori 0,80-0,95 : +3,1 % par mise aux prix payés (t +2,8, ~40 réglages) ; avant le match +0,6 % ; recalibrage ne bat pas le marché | tennis.md |
| e-sport (CS2, LoL, Dota 2, Valorant), favoris avant/pendant le match (23 379 marchés) | écartée | favori 0,80-0,95 : −0,1 % à +0,6 % par mise après frais et écart, à tous les retards (−60 min … +60 min) ; le favori gagne un peu plus que son prix (z +1,5 à +2,2) mais l'écart ne couvre pas les frais | tennis.md |
| autres sports (NFL, NBA, NHL, MLB, football, UFC… 14 097 marchés), favori 0,80-0,95 | écartée | −1,1 % à −2,0 % par mise après frais et écart, avant et pendant le match (le favori gagne autant que son prix) | tennis.md |
| fatigue NBA (dos-à-dos, 3 en 4 soirs, écart de repos ; 1 222 matchs 2025-26) | écartée | pente repos +0,007 par jour (t +0,5), 7 découpages dans des sens opposés ; calendrier basketball-reference, règlement 1 231/1 231 | nba.md |
| compteur_tweets, filles (182 périodes, 7 comptes) | retenue : NON seulement, sans NYC Mayor | +16,3 % par achat, +12,8 % par période (t +3,9), 6 réglages sur 6 positifs, 4 mois sur 4 ; Elon seul −3,6 %, 48 dernières heures +1 % (écartées) ; Elon et Trump ≈ 0 | tweets_filles.md |
| mentions « the announcers » et « anyone », prix historique (3 555 marchés) | trompeuse | +31 % (t +6,8) au prix horaire du CLOB, −7 % aux prix des vrais échanges ; 715 prix à exactement 0,50 (carnet vide) | mentions_annonceurs.md |
| mentions « anyone » (Big Brother, Love Island, séries, résultats d'entreprise) | écartée | presque aucun échange réel (4 achats possibles) | mentions_annonceurs.md |
| mentions « annonceurs » Coupe du monde 2026 | écartée | 7 réglages sur 7 négatifs, −4 % à −34 % par achat (43-56 événements) | mentions_annonceurs.md |
| `proposition_uma` (n° 14 : acheter l'issue « proposed » à 0,90-0,98) | écartée | 36 marchés « proposed » ouverts le 22/10 : 33 à 0,9995 / 0,0005, aucune marge ; le seul cas à marge est un litige (`disputed`) | proposition_uma.md |
| `queues_tranches` (n° 10 : NON des OUI à 3-25 %, 990 événements à tranches, 17 796 marchés) | écartée | 18 réglages, −1,3 % à +0,9 % par pari, t par événement −1,9 à +0,7 ; seuls les OUI à 1-3 % sont sous leur prix mais leur NON ne rapporte rien après écart | queues_tranches.md |
| tranches moyennes (OUI 0,25-0,60 à T-72 h, NON) | trompeuse | +8,8 % au prix du CLOB (757 paris, z des prix +2,9), −0,6 % aux prix payés dans les 24 h (520 paris), 25-75 % des paris sans échange dans les 2 h ; ~55 réglages | queues_tranches.md |
| `lissage_tranches` (n° 9 : creux / pic isolé d'un événement à tranches, 679 événements) | trompeuse | NON des pics : +19 à +21 % (t +6) au prix du CLOB, mais 13 pics sur 58 seulement ont un échange réel avant T0 et +2,0 % (t +0,4, 25 paris) aux prix d'achat réels ; creux : rien (z +0,6) | queues_tranches.md |
| mentions « annonceurs » NFL (14 matchs) | indice | +21 % à +91 % par achat sur 6 réglages, t par match +0,8 à +4,8 ; 2 mois, marchés minces : fantôme `mots_prononces_nfl` | mentions_annonceurs.md |
| CPI américain (48 événements, 337 tranches) : NON sur les tranches à 5-30 % | indice | cases à 3-25 % gagnent ~moitié moins que leur prix ; NON +3 à +6 % par achat aux prix réels (12 réglages, 10 positifs ; mensuel/annuel, core négatif) ; 47 événements seulement : fantôme `cpi_tranches` | cpi_nowcast.md |
| classements « status quo » (211 événements : IA 1er-3e rang, plus grande entreprise, applis n° 1, Spotify) | indice (IA) ; autres écartées | IA, leader 0,70-0,95 à J-14 : 12 gagnés sur 12 pour 10,6 attendus aux prix payés (+13 %), mais P(tout gagner aux prix) = 23 % et ~45 découpages ; plus grande entreprise J-3/J-1 −13/−18 %, applis −9/−10 % ; `idea_test.verdict` corrigé (`z_prix`) : fantôme `statu_quo_ia` | classements_status_quo.md |
| emploi américain (NFP, 28 événements) et chômage (26) contre le marché et contre Kalshi | indice (tranche favorite des emplois) ; chômage écartée | tranche favorite des « jobs added » : 5 gagnées pour 11,1 attendues à T-24 h (z −2,4 ; Kalshi, non biaisé par le choix : −1,3), NON +20 à +50 % aux prix payés (9-15 paris, ~200 cellules regardées) ; chômage calibré ; règlement 27/28 (sept. 2025 faux chez Polymarket) : fantôme `jobs_favori_non` | emploi_nfp.md |
| `score_exact_poisson` (n° 1 : Poisson sur 1X2 + plus/moins 2,5 contre les scores exacts, 2 111 matchs, 36 501 paris aux prix des échanges) | écartée | log-score modèle −0,2301 contre marché −0,2307 ; OUI 0,03-0,30 : −8 à −20 % ; NON 0,70-0,97 : −0,6 % ; 16 cases sans motif régulier | score_exact.md |
| `etats_comme_avant` (n° 16 : 2e tour au Brésil, marchés « 1re place dans l'État », 27 États, votes du 1er tour TSE) | écartée en écart de prix ; indice en quasi-certain | favori = vainqueur du 1er tour dans 26 États sur 27 ; prix des 4 États incertains retrouvés à ±0,03 par la marge du 1er tour ; 22 États sûrs à 0,98-0,997 (gain 1-2 % en 3 jours) ; fille `favori_politique_quasi_certain_connu` ; à confirmer le 26/10 | bresil_etats.md |
| `non_aux_drames` (n° 11 : NON des OUI à 2-15 % sur marchés longs, 686 marchés hors sport) | écartée | ~40 réglages : T-7 j −4,9 %, T-30 j −0,3 %, T-60 j +2,8 % (écart 0,01) puis +1,7 % (écart 0,02), jamais positif aux deux écarts et aux trois volumes ; règlement 652/686 | non_aux_drames.md |
| `toucher_avant_fin` (n° 2 : « touche X dans la journée » contre « au-dessus de X à midi », BTC/ETH/SOL, 433 couples, 24 jours) | écartée | 27 561 points : 1 seul couple à plus de 2 cents d'arbitrage au milieu ; NON du « touche » 2-15 % +0,6 à +1,6 % (t par jour +0,1 à +0,55), 6 réglages | toucher_avant_fin.md |
