# Journal de recherche

Une entrée datée par session de recherche (routine « chercheur » ou session manuelle) :
ce qui a été lu, fait, testé, et ce qui reste ouvert. Les plus récentes en haut.

## 2026-10-27 (passage chercheur de midi, 10 h 55 → ~11 h 35 UTC ; durée dans `experiments/budget_chercheur.csv`)

- **Enquête** (fiche : `enquetes/2026-10-27_midi_plancher_et_nouvelle_part.md`). Deux faux positifs de la copie du principal, corrigés avec tests : les 8 « copies à 100 % sur une exécution partielle » étaient le plancher de copie (≤ 5 parts, 0,5 à 4,2 € chacune ; `enquete.PLANCHER_COPIE_PARTS`) ; « nf_moyen : 1 jeton copié sur 36 » comptait des paris d'avant sa part (`copie_absente` compte depuis la première copie). Contrôle à la main : depuis le plancher, 32 jetons copiés sur 52 (le reste : `nf_moyen` d'avant sa part, refus d'avant le plancher à relire demain). Aucune obligation « grave ».
- **Recherche** (`lol_kills.md`, nouveau type de marché) : totaux de kills d'e-sport (LoL 25 659 marchés, Dota 2, manches CS2 et Valorant), vrais échanges, frais payés. **Over : −12,2 % (1 769 paris, z −5,45), même signe dans 4 jeux** ; **Under** (LoL, 3 h, un pari par partie) **+10,1 %** (487 paris, deux moitiés +13,7 % / +8,1 %), 4 jeux ensemble +9,5 % (t 2,75) ; gain fondu à ≥ 400 parts (+4 %) ; seulement 9 % des marchés ont un échange dans l'heure avant le match. Verdict **indice**. Arbitrage entre lignes : écarté (3 paires sur 226).
- **Arène** : fantôme audacieux `moins_de_kills` (classe `MoinsDeKills`, demi-Kelly, une ligne par partie, LoL, 2-12 h avant) ; `series_pages` 10311 reçoit le type `kill_over_under_game` (marchés du lendemain pas encore créés au passage : à vérifier au cycle local suivant). Filles `contrer_crypto_patiente` « 0,10-0,20 » et « issue non » de la feuille de mission **non créées** : le contre-mouvement crypto est écarté (−4,2 %) et leur gain est celui du NON crypto, déjà joué par `crypto_non_10_20` et `crypto_non_bon_marche`. 615 tests verts. « À la une » mis à jour (aperçu : 0 px de débordement).
- **Leçons** : le « Over » des totaux d'e-sport est systématiquement trop cher ; un gain « indice » se lit à la profondeur (même schéma que le NON crypto). Aucune stratégie éliminée aujourd'hui (pas de ligne au carnet).
- **Reste ouvert** : premier jugement de `moins_de_kills` à 30 paris ; vérifier au prochain cycle qu'il voit des marchés ; manches de CS2 (carte 1) en fantôme à part si LoL confirme ; relire `refus_principal` demain (fenêtre entièrement après le plancher).

## 2026-10-27 (passage chercheur, 05 h 55 → 07 h 5x UTC ; durée dans `experiments/budget_chercheur.csv`)

- **Enquête** (fiche : `enquetes/2026-10-27_matin_copie_expliquee_et_filtres_questions.md`). Obligation `copie_fidele` : l'achat « Team Yandex » (déjà corrigé le 26/10, ordre posé périmé) rouvrait une obligation « grave » à chaque passage → `enquete.COPIE_EXPLIQUEES` (liste d'achats élucidés, comme `AUDIT_EXPLIQUEES`) + test ; un autre achat sans jumeau reste grave.
  Contrôle à la main, famille 4 : 1 663 achats de 37 fantômes relus contre les filtres de question (`disciplines`, `issue`, `question_contient/exclut`, `sources`) : **0 hors filtre** ; `heures_min/max` (coup d'envoi, via `depuis_coup_d_envoi_h`) : 629 premiers achats, 4 « hors fenêtre » = ordres posés servis au coup d'envoi (voulu). Constat « à regarder » `crypto_threshold_prix_bas` (+228 €, −4 % par mise) : un seul pari (Bitcoin dip 80 000, OUI à 0,18, +224 €) fait le gain, pas de défaut.
- **Recherche** (piste 0c, suite : `contrer_crypto_passe.md`) : NON crypto à 0,10-0,45 remonté à 2024-2025 : 35 631 marchés avec vrais échanges, **4 167 paris, +15,8 %, 1 573 gagnés pour 1 414,8 (z +5,3, t par événement +4,4)**, 2025 seul +13,1 % (z +2,7) ; sans ses 5 meilleurs jours +10,0 %.
  Affaibli sur 2026-06 → 10 (+7,7 %) ; « 0,20-0,30 » (+40 % → −29 %) et « fin ≥ 96 h » (+31 % → −2 %) disparaissent : écartés. **Tranche payée 0,10-0,20 : +54 %, +62 %, +58 % dans les trois périodes** (730 paris, z +6,4). **Profondeur : le gain est dans les échanges minces** (730 paris à 0,10-0,20 : +58 % tous, +41 % si ≥ 20 parts achetables dans l'heure, +21 % ≥ 100, +1 % ≥ 400 : même piège que la météo du 16/10). Verdict : **indice** (z +5,3 mais gain concentré dans le mince ; ≈ 30 découpages regardés ; le pourquoi n'est pas vérifié).
- **Arène** : + `crypto_non_10_20` (expérience audacieuse, fille de `crypto_non_bon_marche`, Kelly entier, NON payé 0,10-0,20) ; + 3 filles de `compteur_tweets` (obligations de l'entonnoir : `_72_168h`, `_12_18h`, `_72_168h_12_18h`) : découpage a posteriori de 31 paris = 9 événements, trois tranches qui se recoupent = un seul tirage, fantômes d'expérience. Aucune retirée.
- **Leçons** : le test de ce matin refait ce que la leçon du 27/10 (nuit) demandait : plus de données ont CONFIRMÉ l'effet cette fois (z +2,7 → +5,3) alors qu'elles avaient fait disparaître le « contrer ». Mais les sous-tranches se sont comportées comme du bruit de découpage (deux sur trois ont changé de signe) : ne jouer que la tranche positive dans les trois périodes.
- **Reste ouvert** : juger `crypto_non_bon_marche` et `crypto_non_10_20` vers le 03/11 (30 paris en direct avant le principal) ; lire `crypto_non_10_20` en parts remplies (le carnet réel est-il assez profond ?) ; expliquer l'effet avec les prix Binance ; journaliser `spread` dans les achats pour relire `ecart_max`.

## 2026-10-27 (passage chercheur, 00 h 55 → 01 h 3x UTC ; heure de fin à compléter par `budget_chercheur.py fin`)

- **Enquête** (fiche : `enquetes/2026-10-27_passage_copie_ecarts_silencieux.md`). Obligations : `copie_fidele` (Team Yandex) déjà corrigée le 26/10 ; `copie_absente` (`moins_de_cartes`) = pas d'achat du fantôme depuis 16 h 04 (ses créneaux : 0 h-16 h UTC, aucun des 71 paris entre 17 h et minuit) ; le plancher de copie marche (16 copies, 74 € depuis 16 h 34).
  Contrôle à la main, famille 4 : prix payés contre plages de prix de tous les fantômes : rien (ordres posés servis hors plage). **Défaut (famille 6)** : `favori_politique` (14,3 % du capital) a eu 7 paris de fantôme le 26/10 sans un achat du principal et sans ligne de refus ; budget de la part, plafond de famille et marché déjà pris écartaient des paris sans rien écrire. Correctif : `Weighted.drops` + `_remember_drops` (48 h) → abstentions du principal et `refus_principal` ; tests. Cause exacte du cas du 26/10 non établie (code d'avant le plancher).
- **Recherche** (`experiments/contrer_crypto_passe.md`, 145 605 marchés relevés de juin à octobre, 8 974 avec vrais échanges, puis 12 150 de janvier à mai, 8 réglages de plage essayés + ~30 découpages de référence) : « contrer un mouvement de 0,05 en 6 h » à 0,10-0,45 **écartée** (1 492 paris, −4,2 %, 402 gagnés pour 405,1) ; un premier tirage à 2 880 marchés donnait +8 %. Sous-produit : NON des marchés crypto à 0,10-0,45 sans signal : juin-octobre +14,4 % (1 111 paris, z +2,7), refait sur janvier-mai +22,1 % (1 273 paris, z +4,2) ; la sous-tranche « touche » (+22,6 % d'abord) s'inverse (−1,1 %) : **indice** général, fragile (6 mois sur 10).
- **Arène** : + `crypto_non_bon_marche` (expérience audacieuse, Kelly entier, biais 0,05 ; fantôme, a acheté dès le premier cycle local). Aucune retirée.
- **Leçons** : un avantage vu sur 174 paris en direct et confirmé par un sous-échantillon (+8 %) a disparu à 8 974 marchés : refaire sur toutes les données avant d'écrire « confirmé ». Les deux « audace » `contrer_crypto*` restent en jeu pour trancher en direct.
- **Reste ouvert** : remonter le NON crypto à 2025 et l'expliquer ; juger `crypto_non_bon_marche` et les deux « audace » vers le 03/11 ; lire `refus_principal.favori_politique` au prochain achat de `favori_politique`.

## 2026-10-27 (session avec Etienne : « plus de liberté, les pertes sont des expériences »)

- **Enquête** : le principal n'engage que 16 % de son argent (124 € sur 756 €) et ne bouge plus depuis le 23/10. Ce n'est pas un
  défaut : ses stratégies n'ont pas d'avantage mesuré, il mise à proportion. Deux vrais freins sans raison trouvés : (a) l'enquête
  automatique transformait « chance » et « championne sans avantage » en obligations (7 sur 9 à chaque passage, même réponse) →
  « à regarder » ; (b) l'entonnoir 80/20 cherchait dans les euros (la chance des mises) et ne voyait qu'une tranche 0-0,80 →
  61 filles proposées, presque toutes des favoris sans avantage. Risque trouvé : un pari du principal pouvait laisser 0,07 €
  disponibles (faillite à 0 € disponible, même avec des positions) → réserve de liquidités de 3 % (test). **Défaut** : le renfort
  du principal (21/10) n'a jamais joué, un `min(1.0, …)` du 17/10 le coupait → `main._engaged_shares` (test ; fiche
  `enquetes/2026-10-27_renfort_annule_et_entonnoir.md`).
- **Recherche** (`experiments/audace.md`, scripts `experiments/audace/`, 38 réglages de rejeu essayés) : miser plus ou copier plus
  sur les stratégies d'aujourd'hui fait perdre plus (règle en vigueur −54 €, 10 € par pari −202 €, tout copier −1 382 €) ; tout
  résultat positif vient des deux « contrer » de la crypto (sans eux −89 €) ; Kelly sur l'avantage rétréci : replis de 56 à
  137 % ; écarter les favoris du principal : −290 € (leurs remplaçantes étaient pires ; les favoris copiés sont à l'équilibre,
  +6 € sur 4 394 € : réponse à la question du passage de la nuit). Les 58 stratégies de favoris ne diffèrent pas réellement
  (Q 58,7 pour 57, −1,6 point par pari). Prix payés : sous 0,10, 3 gagnés pour 10,8 attendus partout ; chez les « contrer »
  crypto, 0,10-0,45 fait 58 gagnés pour 39,3 attendus (174 paris ; tranche choisie après avoir regardé : hypothèse).
- **Arène** : + `contrer_crypto_audace` et `contrer_crypto_patiente_audace` (0,10-0,45, Kelly entier, a priori 0,08 : environ 9 fois
  la mise de la mère). Principal : renfort jusqu'à ×3, une stratégie peut porter tout le capital, réserve de 3 %. Entonnoir :
  morceaux à z ≥ 2, stratégies à z ≥ 1,5 disséquées même perdantes en euros, prix bas découpés (61 → 4 filles, dont 0,10-0,20
  de `contrer_crypto_patiente`, z +3,19).
- **Leçons** : nouveau `experiments/carnet_experiences.md` (11 expériences, ce qu'elles ont coûté, appris, et ce qu'on en fait) ;
  posture « cap sur l'objectif » dans `docs/METHODE.md`, `docs/ROUTINE_CHERCHEUR.md` et les fiches de méthode.
- **Reste ouvert** : vers le 03/11, relancer `experiments/audace/*.py` et juger les deux filles « audace » sur leurs nouveaux paris ;
  les filles de `compteur_tweets` proposées par l'entonnoir sont à juger par événement (tranches d'un même compteur).

## 2026-10-27 (passage chercheur, nuit : 20 h 56 → 22 h 22 UTC, 86 min, durée visée 114 min non atteinte : les pistes restantes attendent des matchs ou des publications, arrêt sans remplissage)

- **Enquête** (fiche : `enquetes/2026-10-27_releves_tronques_offset.md`). Obligations : `copie_fidele` (« Team Yandex », déjà corrigé le 26/10), `champion_sans_avantage`, cinq « chance » = mêmes mécanismes qu'avant ; `copie_absente` (`moins_de_cartes`, 0 sur 50) : le fantôme n'a pas acheté depuis le correctif du 26/10 à 16 h 34 (dernier pari 16 h 04), le plancher de copie n'a pas encore pu servir.
  **Défaut trouvé (famille 3/4, tirage)** : Gamma répond 422 « offset too large » dès `offset` ≈ 2 100 sur `/events` et les 30 scripts de relevé d'`experiments/` écrits sur le modèle `while off < 30000 … if not isinstance(b, list): break` prenaient cette erreur pour la fin de la liste : chaque série n'était lue que sur ses ≈ 2 100 événements les plus récents.
  Chiffré sur `totaux_sports.md` : **11 024 événements sur 36 789 pour février-août (30 %), 10 833 sur 23 858 pour août-octobre (45 %)** ; ATP lu du 14/09 au 26/10 seulement ; MLB, tennis, CS2, Valorant, NFL presque absents de la fenêtre « hors échantillon ». Correctif : `releve_complet.py` (`/events/keyset`, 83 129 événements en 3 minutes), test `tests/test_releves_gamma.py` (aucun nouveau relevé par `offset` ; les 30 anciens sont listés), astuce dans `docs/ROUTINE_CHERCHEUR.md`. La production lit au plus 2 000 événements par `offset` (`fetch_mention_history`, météo) : saine.
  **Autres** : `toucher_metaux` « aucune raison notée » = silence de journal (la semaine du 26/10 est née avant le premier relevé de prix) → elle note maintenant pourquoi (test). Hypothèse « le rythme de `compteur_tweets` est gonflé par les journées de rafale » (OUI « 200+ posts de Trump », 42 €, estimé 0,78 pour 0,42) **réfutée** sur 34 semaines (biais log +0,003 ; +0,10 à +0,17 après une rafale, 10-11 sur 16-18 sur-prédites) ; se règle le 03/11. `contrer_crypto_patiente` à mise fixe : +20,9 % par mise (t +1,07), rien de plus.
- **Recherche** : (a) **totaux de sport refaits sur le relevé complet** (`totaux_sports_complet.md`, 72 673 marchés avec échanges) : « Over » 12 h +11,7 % en août-octobre (364 paris, t 2,03) mais **−1,3 % en février-août (1 461 paris, t −0,44)** : écartée, verdict inchangé avec 1,6 fois plus de paris ; football d'août-octobre +10,5 % (448) mais −18,1 % au début de la saison 2025 : saison, pas loi ; toutes les lignes par tranche de prix : plat ; tennis « Under 2.5 sets » −8,3 % (229 paris, z des prix −4,35) : écartée.
  (b) **Favori acheté avant le match sur 30 000 marchés tirés au hasard (50 232 paris, `favoris_avant_match.md`)** : 25 cases sur 35 négatives, 0,85-0,875 à 3 h −1,2 % (435 paris), depuis août −5,5 % ; tennis −1,4 à −4,9 %, football −1,9 à −2,8 % : **écartée** ; le rang 1 de l'arène et les 28,7 % du principal sur `nf_sport_patiente_prix_850_875` n'ont pas de preuve passée. (c) Ensembles météo, rougeole, essence : rien de nouveau avant le 28/10 ; marchés d'IA de fin octobre : arena.ai répond 403 Cloudflare, LiveBench 2.0 sans CSV simple : non lisibles à la source.
- **Arène** : aucune stratégie ajoutée ni retirée (rien n'a été prouvé aux prix payés ce soir ; les seuls indices tenus, LoL « Under » et les NON des mentions, ont déjà leurs fantômes).
- **Reste ouvert** : demain, `scripts/enquete.py` : `copie_absente` doit se vider si `moins_de_cartes` achète ; relire `refus_principal`. Rejouer les analyses bâties sur les relevés par `offset` seulement si une conclusion en dépend (liste dans la fiche : `ecarts_sports`, `btts`, `sous_marches_football`, `avant_match_50_50`, `apres_fin_match`, `tennis*`). Question pour Etienne : le principal garde 28,7 % sur une stratégie de favoris sans avantage prouvé (−1 à −2 % par pari au comptant) ; faut-il lui préférer le cash tant qu'aucune stratégie n'a un avantage mesuré aux prix payés ? (`validated_strategies` est vide.) `moins_de_cartes_bo5` : premier BO5 le 27/10 à 16 h UTC.

## 2026-10-27 (session avec Etienne : ce qui marchait quand on était en croissance)

- **Enquête** : le principal n'a jamais vraiment été en gain (plus haut du 17/10 = paris météo pas encore réglés) ; la seule vraie
  croissance est celle de `nf_sport_patiente` du 15 au 21/10, rendue ensuite (chance). Les copies de `moins_de_cartes` refusées
  (« taille inférieure au minimum ») étaient déjà corrigées par le passage du 26/10 au soir (`plancher_copie`).
- **Recherche** : rejeu de la règle d'entrée sur 11 jours (refait comme prévu le 21/10) : aucune règle de choix ne gagne (en vigueur
  −262 €, « gagnés contre attendus » −300 € ou −9 € sans presque jouer). La taille des mises explique l'essentiel : les grosses mises
  copiées (favoris à 0,90 ou plus) perdaient −11,5 % par euro → **plafond des mises copiées à 5 % du capital du fantôme**
  (`principal.mise_fantome_max`) : −262 € → −46 €, −2,6 % → −1,0 % par euro au rejeu (`experiments/taille_des_mises.md`).
- **Arène** : rien de changé chez les fantômes.
- **Reste ouvert** : refaire le rejeu dans une semaine ; `contrer_crypto_patiente` (z +1,9 par mise, −28 € en euros) à regarder avec
  une mise fixe.

## 2026-10-26 (passage chercheur, soir : 15 h 55 → 16 h 30 UTC, 35 min, durée visée 110 min non atteinte : les pistes restantes attendent des matchs, des publications ou des jours de données ; arrêt sans remplissage)

- **Enquête** (fiches : `enquetes/2026-10-26_soir_copie_sous_le_minimum.md`, `enquetes/2026-10-26_soir_paris_lies_et_faux_signaux.md`). Obligations : `copie_fidele` (Team Yandex, déjà corrigé), `champion_sans_avantage` et cinq « chance » = mécanisme connu (`nf_court_football_soir` 35 gagnés pour 34,6 attendus, `nf_sport_patiente_6_24h` 30 pour 29,4).
  **Défaut trouvé (famille 1)** : `moins_de_cartes`, 14,6 % du capital principal, **0 pari copié sur 70** ; `compteur_tweets` 1 sur 52, `favori_politique` 0 sur 23. La copie à l'échelle de la part (0,5 part pour `moins_de_cartes`) tombe sous le minimum du marché (5 parts) et le contrôle de sécurité la rejette. Correctif : `principal.plancher_copie` (achète le minimum si ≤ 1 % du capital et dans le budget de la part), test, contrôle `copie_absente` (grave), `data.json` → `refus_principal`.
  **Autres** : `selection_multiple` comptait chaque jambe d'une échelle comme un tirage (`compteur_tweets` : 28 paris sur 9 événements, z +2,56 → +1,72 ; t par événement +1,0) ; contrôle `mere_muette_fille_active` : 3 mères sur 4 étaient éliminées ; contrôle `mises` : dénominateur périmé (47 faux « > 25 % »). Piste écartée en route : « la championne gagne hors match » (coupure par le champ `depuis_coup_d_envoi_h` = achats d'avant le 20/10, pas un type de marché).
  **Défaut de calendrier** : `statu_quo_ia` v1.0.0 retirée pour inactivité le 23/10 à 15 h 21, 17 minutes avant la protection `jamais_retirer` (15 h 38) ; elle devait jouer « best AI model end of November » (fenêtre 12-35 jours dès le 27/10). Recréée en v1.1.0.
- **Recherche** : ensembles météo, 2e jugement (jours 25 et 26, 102 événements, 314/314 règlements relus, 186 relevés avec un vrai échange) : log-loss 0,39-0,45 contre 0,27 pour le marché, achats −13 à −31 % : toujours **écartée** (prochain jugement à 5 jours). Rougeole (CDC) et essence : relevés à jour, rien de nouveau avant le 28/10.
- **Arène** : `statu_quo_ia` v1.1.0 (même filtres). Aucune autre stratégie ajoutée ou retirée.
- **Reste ouvert** : demain, `scripts/enquete.py` : `copie_absente` doit se vider pour `moins_de_cartes` ; lire `refus_principal` dans `published/data.json` (pourquoi `favori_politique` n'a pas été copié à 12 h 13 alors que 2 paris dépassaient 5 parts). Si `moins_de_cartes` perd en direct (z < 0 sur 50 nouveaux paris), retirer `plancher_copie`. Marchés d'IA fin octobre (31/10) : LiveBench / Text Arena Math / Code Arena WebDev ont des petits volumes (30-120 k$) et des sources lisibles : piste possible (lecture directe du classement contre le prix), non testée.

## 2026-10-26 (passage chercheur, midi : 10 h 55 → 11 h 58 UTC, durée visée 108 min non atteinte : les mentions ont donné leur verdict, le reste attend des paris en direct)

- **Enquête** (fiche : `enquetes/2026-10-26_midi_budget_prudence_des_fantomes.md`, scripts `budget_prudence_fantomes_26_10.py`, `filles_sans_mere_26_10.py`, `principal_*_26_10.py`). Obligations : `copie_fidele` = « Team Yandex » (déjà corrigé cette nuit) ; « champion sans avantage » et « chance » = mêmes mécanismes qu'avant ; **« audit » = les 2 achats du NON à 0,001 du 24/10, déjà corrigés** : ils rouvraient une obligation « grave » à chaque passage → `enquete.AUDIT_EXPLIQUEES` (liste des `op_id` élucidés, rapportés en « à regarder »).
  **Défaut trouvé (famille 5/6)** : `main.Weighted._scale` plafonnait le total investi d'un FANTÔME à *prudence × capital* (budget écrit le 18/10 pour le principal, appliqué aussi aux fantômes avec la prudence ¼ / ½ comme poids). **38 fantômes sur 163** avaient un budget épuisé sans raison notée dans les abstentions : `nf_sport` (310 € investis pour un plafond de 280 € à ¼) **muet depuis le 21/10** pendant que sa fille `nf_sport_925_950` (prudence 1) achetait 9 à 25 fois par jour ; mères muettes aussi : `nf_sport_court` (20/10), `nf_tennis` (21/10), `nf_sport_patiente_tennis` (24/10). 94 % des jetons de `nf_sport_925_950` et 88 % de `nf_sport_prix_haut_3_6h` n'étaient pas dans le journal de leur mère. **Conséquence : les « filles qui battent leur mère » de la feuille de mission (ex. `nf_sport_prix_haut_3_6h` +4,9 % contre +0,3 % sur 99 et 26 opérations) comparaient une fille qui joue tout à une mère qui ne jouait plus.** Corrigé (`Weighted(cap_budget=False)` pour les fantômes ; le principal reste plafonné par sa part) ; test qui échoue sans le correctif ; nouveau contrôle `enquete.mere_muette_fille_active` (9 mères signalées sur le rapport de 11 h). Les ~38 fantômes se remettent à acheter au prochain cycle : leurs rendements des jours suivants ne se comparent pas à ceux d'avant.
  Contrôle à la main (famille 3/4) : 252 achats du principal comparés aux échanges publics à ±120 s (97 comparables, 155 sans échange dans la fenêtre : 500 derniers échanges seulement) : 3 prix sous le plus bas échange réel (marchés minces, 1 échange chacun), 2 cas relus en détail (cartes CS2 qui sautent de 0,88 à 0,999 en 10 s) : rien d'anormal. `mots_prononces` direct (50 paris réglés, +0,1 %, 21 gagnés pour 23,4 attendus ; estimation moyenne 27,4 gagnés) : estimation gonflée, voir Recherche.
- **Recherche** (`experiments/rallies_trump.md`, scripts `experiments/rallies_trump/scripts/`) : piste née de l'enquête (`mots_prononces` « retenue » à +19-27 % fait 0 % en direct, tout son direct = meetings de Trump). (a) **Modèle « même mot aux meetings précédents » écarté** (69 meetings, 1 371 marchés : log-score −0,565 contre −0,515 pour le marché). (b) **Biais du OUI** : prix moyen 0,513 pour 0,467 réalisé ; NON quand le OUI vaut 0,40-0,70 : +9 % à 6 h [IC95 par meeting −1 ; +20], +11 % à 24 h [+1 ; +21]. (c) **Contre-épreuve sur un échantillon neuf : 13 513 marchés « What will X say… » de 745 événements** : OUI réalisé 0,458 pour 0,502 ; NON à OUI 0,30-0,60 : +4 à +9 % avec IC95 par événement > 0 à presque tous les délais ; sans frais (Gamma : mentions sans frais) **mots simples +12,1 % [+8,7 ; +15,4] (702 événements), deux moitiés (+8,6 / +10,1 %) et trois années (2024-26) positives, seuils « N+ times » −7,7 % [−14,7 ; +0,3] (même sens sur les meetings)** ; effet concentré à 3-96 h de la fin (fin − 3 h +20,0 % [+13,7 ; +25,7] ; 168 h +1,1 %). Hors 0,50 exact et prix datés : inchangé. **Aux prix réellement payés** : seulement 20-22 % des paris candidats ont un achat réel du NON dans les 2 h ; ceux-là +9,0 % [−2,8 ; +22] (tous les marchés) et +16,6 % [+7,1 ; +26,3] (mots simples), mais biaisés vers les NON gagnants : **indice, pas retenue** (≈ 40 réglages regardés).
- **Arène** : 4 fantômes en quart de Kelly (`rallies_non`, `rallies_non_favori`, `mentions_non`, `mentions_non_outsider` : `naive_favorite` à filtres, NON des mots simples, OUI 0,30-0,70, fenêtre 3-20 h pour les meetings et 3-48 h pour les autres, sans « + times », sans commentateurs), tests, vus au cycle local (4 marchés dans le filtre ce midi : les meetings de Trump reprennent avant le 03/11, des appels de résultats demain). Aucune stratégie retirée.
- **Reste ouvert** : lire les 4 fantômes sur leurs premiers paris réglés (une dizaine de meetings d'ici le 03/11, appels de résultats Verizon / Robinhood / Coca-Cola les 27-28/10, conférence de Warsh le 28/10) : si leur NON gagne aux vrais carnets (écart d'achat inclus), c'est la première stratégie « prouvée aux prix payés » de ce type ; sinon le coût d'exécution mange le biais du OUI (comme `mots_prononces` : NON −5,8 % sur 28 paris). `moins_de_cartes` : 58 paris, +28,3 %, z +2,42 (5 paris hors échantillon depuis hier : +15,5 %) ; premier BO5 le 27/10 (`moins_de_cartes_bo5`). Rougeole (mercredi 28/10), essence (13 jours réglés), props de joueurs (décembre) inchangés. Estimation de `mots_prononces` gonflée (27,4 annoncés, 21 réalisés) : sa part du capital principal est déjà nulle.

## 2026-10-26 (passage chercheur, matin : 05 h 56 → 07 h 12 UTC, 76 min, durée visée 107 min non atteinte : les pistes restantes attendent des données ou des matchs, arrêt sans remplissage)

- **Enquête** (fiche : `enquetes/2026-10-26_matin_arene_contre_prix.md`, script `enquetes/scripts/arene_contre_prix_26_10.py`). Obligations : `copie_fidele` = l'ordre posé périmé « Team Yandex » (22 h 35 le 25/10, avant le correctif de cette nuit) ; « champion sans avantage » et « chance » = mêmes mécanismes qu'avant.
  **Famille 2 sur toute l'arène (2 239 jetons, un par jeton)** : 1 527,5 gagnés pour 1 557,8 attendus par les prix payés (−1,4 pt, z −1,76) ; `nf_sport` −0,6 pt, `nf_tennis` −0,8, `nf_court` −3,4 : **aucune famille ne bat ses prix** ; seuls `moins_de_cartes` (+15,2 pts, 57 paris, z +2,33 ; par jeu CS2 +23,5 %, Dota 2 +25,4 %) et les tweets (26 paris, 9 événements) font mieux. Le classement du brief mesure des mises ∝ 1/(1 − prix) sur des favoris qui gagnent à leur prix.
  **Défauts trouvés** : (1) `enquete.estimation_gonflee` comptait un règlement 50-50 comme une défaite (corrigé, test qui échoue sans le correctif, le titre donne aussi le z contre les prix payés) ; (2) `meteo_ensemble/evaluer_releve.py` lisait l'événement dans `/markets/<id>` → `events`, que Gamma ne rend plus : tous les marchés dans un seul « événement » (corrigé : événement lu dans la base ; règlement relu 236/236 ; production non touchée). Famille 6 : 6 positions « oubliées » = Alberta (×2) et un cessez-le-feu au Yémen en `proposed` depuis 5 jours ; audit : 198 « pas clos » = règlement 1-2 minutes après le `closedTime` de Gamma (proposition du 22/10). `saison_non` muette : aucune échelle de saison à 10-18 jours.
- **Recherche** : (a) **1X2 du football et mi-temps** (17 ligues, 4 354 événements, 47 285 paris, vrais échanges, 50-50 comptés 0,5, `sous_marches_football.md`) : **écartée** (équipe Oui −3 à −5 % partout = coût ; nul Oui 1 h +3,4 % mais +6,5 % avant le 15/08 puis −1,2 % ; ~60 découpages). (b) **Props de joueurs** : 251 événements, 80 paris testables (marchés nés en septembre) : non testable, à refaire en décembre. (c) **Ensembles météo** (relevés du cycle, 84 événements du 25/10) : log-loss modèle 0,41-0,49 contre marché 0,32, achats −13 à −34 % : écartée ce jour-là, à refaire à 5 jours et plus. (d) **Mécanisme de `moins_de_cartes`** (`moins_de_cartes_direct.md`, `bo3_coherence/correlation_manches.py`) : les cartes sont corrélées. BO3 (577 matchs) : balayages réels 63,6 % contre 56,1 % binomial, marché 59,5 % (réel − marché +4,1 pts, z +2,07) ; **BO5 (122 matchs, 109 LoL) : 53,3 % contre 33,9 % binomial et 38,9 % pour le marché (+14,4 pts, z +3,4)**. Même échantillon que l'indice du 25/10 : cela l'explique, ne le confirme pas ; le direct (57 paris, +26,7 %) est la confirmation. Contre-épreuve : le handicap −1,5 du favori (732 BO3) a la même corrélation (+5,3 pts) mais le marché la paie déjà (réel − marché +1,5 pt, z +0,85) : le total mince suit mal le handicap, le gain attendu est modeste. Pas d'arbitrage non plus entre le total et le handicap (399 couples, aucune paire à moins de 0,97).
- **Arène** : aucune stratégie ajoutée ni retirée (la seule piste solide est déjà couverte par la mère et ses deux filles ; élargir son prix ou ses jeux serait choisir après coup). Chantier 3 (Deribit) noté « testé le 16/10 ». 591 tests verts.
- **Reste ouvert** : `moins_de_cartes_bo5` n'a toujours aucun pari (prochain BO5 : LGC Rising Playoffs, Vitality Rising Bees – Mental Rush, 27/10 16 h UTC) : c'est la lecture la plus utile de la semaine ; ensembles météo à rejuger quand 5 jours seront jugeables (le jour 24 est exclu par la règle « décision avant minuit local ») ; rougeole (mercredi 28/10) et essence (inchangés) ; props de joueurs en décembre.

## 2026-10-26 (passage chercheur, nuit : 00 h 54 → 02 h 00 UTC, durée visée 105 min non atteinte : plus de piste à données disponibles, arrêt sans remplissage)

- **Enquête** (fiches : `enquetes/2026-10-26_ordre_pose_perime_du_principal.md`, `..._famille3_tirage_donnees_externes.md`).
  **Défaut trouvé** : le contrôle `copie_fidele` signalait un achat du principal sans jumeau (« Team Yandex », 4,5 €). Cause : le fantôme `nf_sport_patiente_6_24h` remet son prix à jour à chaque cycle (0,83 → 0,82 → 0,81), mais la copie du principal n'est plus reposée (mise plafonnée / refus) et **l'ancien ordre du principal à 0,83 reste ouvert** jusqu'à 6 h : servi à un prix que la source n'accepte plus. Taux de copie des ordres de cette stratégie : 12/12 à midi, 0/24 à 23 h. Sur 42 ordres posés du principal exécutés depuis le 19/10, 2 périmés. Correctif : `_place_resting(source_orders)` annule l'ordre ouvert du principal quand sa copie du nouvel ordre du fantôme n'est pas posée (`Database.cancel_open_orders`), test qui échoue sans le correctif.
  Famille 3 (jour 26) : 12 paris à donnée externe relus sur Gamma, 12/12 conformes. `seismes_marche` « muette sans raison » : pas un défaut (semaine : fenêtre de 6,6 jours, jour : à partir de 6 h UTC). Obligations « chance » : même mécanisme (`nf_sport_patiente` +154 € → +18 € sans ses 3 meilleurs paris) ; `nf_sport_non` +243 € → −50 € à 0 h 51 (un NON à 0,933 de 314 € a perdu) : le classement du brief est une photo.
- **Recherche** (trois pistes, relevés et scripts versionnés) : (a) **totaux de sport** (`totaux_sports.md`, 4 614 puis 5 879 événements, 40 000 marchés, vrais échanges) : sur la découverte (août-octobre) « Over » à 12 h +10,1 % (312 paris, t 1,64), « Under » −5 à −24 % ; **hors échantillon février-août : « Over » 12 h −0,9 % (906 paris), « Under » −0,2 à −5 % : écartée**. (b) handicaps (`ecarts_sports.md`, 3 347 événements) : écartée. (c) « les deux équipes marquent » (`btts.md`, 1 327 événements) : écartée. Au passage, l'« Under » d'e-sport se retrouve hors échantillon (février-août : +4 à +13 %, t 0,8-1,5) : `moins_de_cartes` reste un indice, un peu mieux étayé (57 paris réglés en direct, 41,0 gagnés pour 32,3 attendus, +26,7 %).
- **Arène** : aucune stratégie ajoutée ni retirée. Un fantôme `totaux_over` a été écrit (3 propositions en cycle local) puis RETIRÉ avant fusion quand le test hors échantillon l'a démenti. Filles 80/20 de la feuille de mission non créées : mères pleines ou morceaux choisis après coup sur 30-60 paris (voir le contrôle `selection_multiple`). 590 tests verts.
- **Reste ouvert** : lire `moins_de_cartes_lol` / `_bo5` contre leur mère ; rougeole (mercredi 28/10) et essence (pas assez de jours) ; `seismes_marche` à 6 h UTC aujourd'hui (premier jour testable) et ce soir (semaine du 26/10) ; diagnostic d'abstention « hors plage horaire testée » pour les stratégies séismes (abstentions vides aujourd'hui) ; piste anytime-goalscorer / exact_score avec relevé en arrière (volumes minces : 228 marchés à plus de 500 $).

## 2026-10-25 (passage chercheur, nuit : 20 h 55 → 21 h 25 UTC, 30 min)

- **Enquête** (fiches : `enquetes/2026-10-25_nuit_audit_concentration_et_ordres_poses.md`, `..._filles_sourdes_et_filtres_silencieux.md`). Obligations : audit = les deux achats à 0,001 déjà corrigés le 24/10 (aucun nouvel achat de ce type) ; concentration des gains
  (`nf_sport_patiente`, `nf_court_soir`) : pas d'avantage au-delà du prix (156,5 gagnés pour 151,1, −22 € sans les 3 plus gros). Famille 2 rejouée ; principal contre championne jeton par jeton : copie fidèle (32 jetons communs −13,8 % / −13,1 %).
  **Défauts trouvés** : (1) `candidats_non` sourde aux élections du 03/11 (« win the 2026 » ne reconnaît ni « …Governor Election in 2026 » ni « …Senate race in 2026 ») : sa fenêtre s'est fermée le 25/10 à 5 h sans un achat ; (2) un filtre `Filtered` qui écarte tout n'écrivait
  aucune abstention (« muette » sans cause) : `hors du filtre X ×N` ; (3) cotes de champion NFL/NHL jamais rattachées (30 marchés sur 94) : libellés « NFL league championship » et « be named the 2026-27 NHL Stanley Cup Champion » ; (4) statut `goldapi` « ok (0 observations) » alors que 166 prix sont notés. Tous corrigés avec tests.
- **Recherche** : (a) `experiments/ordres_poses_en_jeu.md` : ordres posés contre achats immédiats sur 1 145 favoris de sport (un compte par jeton) : posés −6,8 % (239, z des prix −2,8), immédiats −0,2 % ; hors échantillon (22-25/10) −12,7 % (z −3,5) ; en cours de match −9,2 %, avant match 13 paris seulement.
  **Indice de sélection adverse** (pas un avantage), ~10 découpages regardés. (b) `moins_de_cartes_direct.md` : 54 paris hors échantillon, +29,7 %, z 2,59, t par match 2,97, règlements 54/54 relus : l'indice se confirme (signe, pas l'ampleur). (c) piste 1 `futurs_pinnacle.md` : champions NBA/NFL/NHL contre Pinnacle : écart moyen 0,1-0,5 pt, 5-8 mois de capital bloqué : **écartée**.
- **Arène** : sœur `nf_sport_patiente_avant_match` (championne sans ordre posé en cours de match, `heures_min: 0`) ; contrôle `posees_en_jeu` dans `enquete.py` (test) ; aucune stratégie retirée. 589 tests verts.
- **Reste ouvert** : relire `nf_sport_patiente_avant_match` contre la championne dans quelques semaines (peu de paris avant match) ; `meteo_prevision*` : ordres posés −23 % (indice faible, stratégies retirées) ; contrôle automatique « sourde » (toutes les abstentions = filtres, plusieurs cycles) ;
  `mots_prononces_nfl` : aucun marché « announcers » ouvert (derniers matchs : 11, 16, 19/10) ; rougeole (CDC : toujours 4 588 cas au 22/10, mercredi 28 prochain) et essence (une ligne ajoutée, 25/10) ; durée visée 102 min non atteinte (30 min faites) : arrêt volontaire sans remplissage.

## 2026-10-25 (passage chercheur, soir : 15 h 55 → 16 h 07 UTC, 12 min)

- **Enquête** (fiche : `experiments/enquetes/2026-10-25_soir_tirage_et_fenetres.md`) : **rien trouvé**. Obligations = celles de midi (mêmes mécanismes, non refaites).
  Famille 3 : 30 paris réglés tirés au hasard (graine 25) relus sur Gamma, 30/30 conformes au journal. Famille 4 : 716 premiers achats de 19 stratégies à fenêtre,
  tous dans `echeance_min/max` ; 4 hors `heure_utc` = ordres posés servis plus tard (voulu). `cotes_bookmakers` : coupée depuis le 21/10, pas muette.
  Suivi : `moins_de_cartes` 47 paris réglés, 33,5 gagnés pour 26,7 attendus (z 2,0, +19,7 %) ; encore un indice, pas une preuve.
- **Recherche** (piste 0b suite, `experiments/detroits_seuils.md`) : seuils d'Ormuz. 59 marchés réglés (prix horaire). 12 « returns to normal » = 12 NON (un seul chemin : détroit fermé
  depuis mars). Le NON à J-30 rendait +26 % (8 marchés), mais le OUI moyen est passé de 0,35 (mars-avril) à 0,01 (septembre) : **la prime a disparu**. Aujourd'hui OUI 0,055 (30/11) et 0,115 (31/12), de l'ordre du risque
  de réouverture. « On any day by » : NON +7 à +11 % à J-14/J-7, 8 événements, même régime. **Verdict : écartée** comme avantage (4 réglages, aucun ajusté).
- **Arène** : fantôme gratuit `detroits_non_normal` (quart de Kelly, NON de « traffic returns to normal », 0,80-0,95) pour voir si une prime revient ; test (échoue sans la config) ; cycle local : 1 proposition, 6,93 parts à 0,89. 587 tests verts.
- **Reste ouvert** : loi sur le maximum d'une période pour les seuils « on any day by » (à refaire quand la fermeture finira) ; rougeole (CDC : pas de nouvelle ligne depuis le 22/10), essence (pas de nouveau jour depuis le 24/10) ;
  durée visée 99 min non atteinte (12 min faites) : arrêt volontaire sans remplissage ; pistes suivantes bloquées par l'attente de données (voir PISTES n° 8, 4) ou par une clé (Pinnacle).

## 2026-10-25 (passage chercheur, midi : 10 h 54 → 11 h 51 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-25_midi_tirage_sans_5050_et_chance.md`, scripts dans `experiments/enquetes/scripts/`).
  - **Obligations** : les cinq « champion sans avantage / chance » et l'« audit » : même mécanisme qu'aux passages précédents (mises ∝ 1/(1 − prix)), anomalies d'audit = achats à 0,001 déjà corrigés le 24/10 ; non refaites. Constat « estimation périmée » des tweets : un achat de 7,5 € (NON estimé 0,81, payé 0,10) perdu, rien à corriger.
  - **Famille 2 (jour 25), à la main sur 159 journaux** : sur les 23 fantômes gagnants, 13 gagnent encore sans leurs 3 meilleurs paris, 11 sans leur meilleur jour ; la championne `nf_sport_patiente` +113 € → **−22 € sans ses 3 meilleurs paris, −185 € sans son meilleur jour**, z +1,2 ; aucun z > 2. Mon script comptait un règlement à 0,5 comme gagné (corrigé : `p['pay']`).
  - **Défaut trouvé : le test sur le passé de `moins_de_cartes` écartait les matchs réglés à 50-50 dès le tirage** (`series.regle` → `match_cas` → `releve_echanges` : un match dont tous les totaux sont à 50-50 ne peut même pas être tiré ; ≈ 4 % des matchs, 8 % des totaux CS2). En direct : 4 règlements 50-50 sur 42 paris (Gamma relu : 42 sur 42 conformes au journal). Correctif de la mesure : `series.INCLURE_50_50`, nouveau tirage de 2 755 matchs. « Retenue » (+13,5 %, t 2,75) devient **indice : +7,7 % (t 2,0, z 1,5)** ; sur 1 804 matchs jamais vus de la découverte : +8,3 % (t 1,84), **LoL +15,1 % (t 2,2)**, **BO5 +23 %** ; en direct 30 gagnés pour 23,9 attendus (z 1,9).
  - **Famille 5 en plus** : sur 30 filles, écart moyen de +7,1 points contre le reste de leur mère (t 2,05, mais filles corrélées) ; la championne perd −7,3 % sur 61 paris à 0,90 et plus (6 653 € misés) et gagne +6,8 / +8,9 % à 0,80-0,90 : le mécanisme des filles « prix 0,85-0,875 ». **Famille 4** : 12 achats `nf_*` faits plus de 24 h après le coup d'envoi (594 €, Test de cricket, deux ITF, tweets) : pas un défaut.
- **Recherche** (piste : « Under » des cartes d'e-sport, scripts et sorties dans `experiments/bo3_coherence/`) :
  - Refaite AVEC les 50-50 : indice, voir ci-dessus ; découpe : LoL BO5 +23,4 % (190 paris, z 2,8), LoL BO3 +4,2 % (t 0,8) ; prix « avant » BO5 +18,6 % (t 1,5).
  - **Sept autres jeux** (HoK, MLBB, CoD, R6, RL, SC2, OW ; 2 220 matchs, 3 227 totaux, aucun 50-50) : **écartée** (+2,1 %, t 0,69 ; « Over » −14,4 % comme dans le premier lot) : le mécanisme n'est pas général. MLBB seul +17 % (60 paris, t 1,84 : un jeu sur sept), refait avec tous ses matchs : +12,0 % (91 paris, t 1,45) : s'affaiblit.
  - Relevés CDC (rougeole) et essence relancés : rien de nouveau (le CDC n'a pas publié depuis le 22/10).
- **Arène** : nouveau filtre `titre_contient` (titre de l'événement ; « Games Total » ne nomme pas le jeu), filles `moins_de_cartes_lol` et `moins_de_cartes_bo5` (fantômes, mère à 2 filles sur 10) ; tests (le filtre échoue sans le code) ; cycle local : la fille LoL est vivante mais sans match LoL à moins de 6 h pour l'instant (Dplus KIA – Movistar KOI à 7,5 h), la BO5 attend les barrages de Worlds. 586 tests verts. « À la une » du tableau de bord mis à jour (aperçu : 0 px de débordement).
- **Reste ouvert** : (1) lire `moins_de_cartes_lol` et `_bo5` contre leur mère sur les mêmes marchés après ~40 paris ; (2) règlement de 5775544 (séismes, 26/10) ; (3) `compteur_truth` contre `compteur_tweets`, `candidats_non` après le 3/11, rapport `box_office_favori` ; (4) `moins_de_cartes` n'a eu AUCUN pari LoL en direct (42 paris : CS2 29, Dota 2 10, Valorant 3 ; gains +15,6 % et +29,5 %, jeux à zéro dans le passé) : le direct ne confirme pas le morceau LoL, la fille le dira ; (5) tout autre tirage de matchs qui exige un marché « réglé net » (tennis, football) a le même trou 50-50 : refaire les tests d'e-sport CS2 qui ont été « écartés » ? (6) MLBB « Under » : à regarder avec plus de matchs.

## 2026-10-25 (passage chercheur, minuit : 23 h 54 → 00 h 16 UTC environ)

- **Enquête** (fiche : `experiments/enquetes/2026-10-25_nuit_controles_famille_1_et_6.md`).
  - **Obligations** : les trois « champion sans avantage », les trois « chance » et l'« audit » : même cause qu'aux passages précédents (mises ∝ 1/(1 − prix), favoris qui gagnent comme leur prix ; les 2 anomalies d'audit sont les achats à 0,001 déjà corrigés le 24/10) ; non refaites.
  - **Famille 1** (jour 25 : n° 1, déjà faite deux fois le 24/10) refaite sur les journaux de 23 h 52 : prix payé du principal = celui du fantôme copié (−0,0007), 163 jetons réglés, gain −240 € contre −254 € au prix du fantôme.
  - **Famille 6** : positions bloquées = litiges UMA (Cape Town 17/18 °C) et référendum de l'Alberta, pas de défaut ; le correctif `zero_fees` de la politique a rouvert `parking_politique` (2 achats le 24/10 à 21 h 27) ; la météo n'entre plus dans les 150 surveillés mais arrive par `candidates()` (rien à corriger).
  - **Comptabilité** : trésorerie de 159 journaux rejouée au centime, 0 règlement en double → contrôle automatique `enquete.tresorerie_rejouee` + test. `idea_test.fetch_resolved` compte maintenant les marchés 50-50 écartés (`ECARTES_50_50`, reste ouvert n° 6 d'hier soir).
  - **Aucun défaut de code trouvé** dans ce passage ; vérifié comme ci-dessus.
- **Recherche** (3 comptes rendus, scripts et relevé de posts versionnés) :
  - **Posts Truth Social de Trump** (`experiments/truth_social.md`) : 70 événements réglés, archive publique trumpstruth.org (6 046 posts, règlement retrouvé 48 fois sur 62), 60 semaines utilisables, vrais échanges. Profil par heure de la semaine : écartée (8 réglages, −6 à +13 %).
    Formule de production de `compteur_tweets` : **+15,5 % par achat** (306 achats, t par événement +2,3, 6 mois sur 8, NON +21 %) mais **−5 % quand ≥ 100 parts s'échangent au prix** : l'effet vit dans les échanges minces. **Indice faible** → fantôme.
  - **`compteur_tweets_non` aux prix des vrais échanges** (`experiments/tweets_prix_payes.md`) : quatre comptes, mars-octobre, 186 périodes : **+10,5 % par achat, t +1,4** (6 réglages : +8 à +11 %), OUI+NON +0,7 % ; WhiteHouse −7 %, tedcruz +27 %, cz_binance +45 % ; ≥ 100 parts : −10 %. « Retenue » du 21/10 ramenée à **indice** (déjà fantôme, hors `validated_strategies`).
  - **Chômage hebdomadaire** : écartée sans test (4 événements à tranches, 195 à 16 700 $ ; 19 anciens seuils 2021-22). FRED (`fredgraph.csv?id=ICSA`) répond sans clé.
- **Arène** : fantôme `compteur_truth` (fille de `compteur_tweets`, `only_trump: 1`, réglages de la mère) ; cycle local : 1 proposition, achat de « 200+ posts du 23 au 30/10 » à 0,476 (marché 5957193, relu sur Gamma). Test dans `tests/test_references.py`. Pas d'autre création : mères pleines ou familles jugées sans avantage (comme les 24/10).
- **Reste ouvert** : (1) règlement de 5775544 (séismes, 26/10) ; (2) lire `compteur_truth` contre `compteur_tweets` après ~8 semaines ; (3) rapport `box_office_favori` du week-end 24-25/10 ; (4) `candidats_non` après le 3/11 ; (5) mesurer la profondeur réelle du carnet (pas seulement les échanges) pour les rejeux de comptage ; (6) fiche de méthode : tout test « retenu » sur prix CLOB horaires est à refaire aux échanges avec le volume au prix.

## 2026-10-24 (passage chercheur, soir : 19 h 54 → 21 h 30 UTC environ)

- **Enquête** (fiches : `experiments/enquetes/2026-10-24_soir_reglements_50_50.md`, `2026-10-24_soir_politique_zero_fees.md`, `2026-10-24_soir_seuils_etiquette_ignores.md` ; famille du jour n° 1 déjà faite à 14 h 54, donc dix paris du principal relus à la main (graine 2419, famille 3), puis famille 6).
  - **Obligations** : les cinq « champion sans avantage / chance » (nf_sport_patiente 3 paris = 131 % du gain, le 18/10 = 234 %…) : même mécanisme que ce matin et le 22-23/10 (biais fixe, mise ∝ 1/(1 − prix)), pas de défaut de code, non refaites. « Audit » : les 2 anomalies hors « pas clos » sont les achats à 0,001 de `crypto_threshold_non`/`_prix_bas` déjà corrigés à 14 h 54. Règlement de 5775544 (séismes, doublon) : pas encore réglé (fin le 26/10).
  - **Défaut 1, mesure : les règlements 50-50.** Parmi les dix paris relus, « 9INE Academy » (CS2, achat du principal 2,7 h après le coup d'envoi) est réglé 0,5/0,5. Dans toute l'arène : **9 marchés réglés à 50-50, 23 règlements de portefeuilles, 521 € perdus sur 1 252 € misés** (le principal −17 €). `history.parse_resolved` et `idea_test.parse_event_market` les écartent en silence.
    Taux Gamma des marchés « vainqueur » avec échanges (7 815) : CS2 8,2 %, Dota 2 5,9 %, WTA 4,9 %, ATP 2,4 %, ITF 2,3 %, football 0 %. Dans les `nf_*` : 16 règlements 50-50 sur 3 241 (−0,27 % de la mise) parce que 84-90 % des achats se font après le coup d'envoi. Contrôle `enquete.reglements_50_50` + test.
  - **Défaut 2, panne silencieuse : la politique est passée en `zero_fees` (19-20/10)**, comme la météo, mais seule la météo avait été rattrapée le 23/10. `favori_politique*` et `parking_politique` (`familles: [politics, sans_frais]`) ne voyaient que 94 marchés sur 393 ; `favori_politique` (copiable par le principal) n'avait plus acheté depuis le 16/10.
    Correctif : `POLITICS_SLUGS` dans `market_family` (adresse d'événement) + test ; cycle local : les cinq stratégies rachètent (Alaska, Californie, 2028…), marchés relus.
  - **Défaut 3, scanner : les seuils d'une étiquette ne valaient pas pour un marché déjà lu dans les pages normales.** 21 marchés exclus à tort (tranches du box-office du week-end, une tranche de séismes, mentions de Trump). Correctif `_add_tag_markets` + test (échoue sans lui). Aussi : `Filtered.candidates` appliquait le plafond de 25 marchés AVANT la fenêtre d'échéance.
- **Recherche** (3 pistes, comptes rendus et scripts versionnés) :
  - **Favori acheté AVANT le match, 50-50 compris** (`experiments/avant_match_50_50.md`) : 10 438 événements de 37 ligues, vrais échanges, 0,80-0,95, 1 à 24 h avant : −0,9 / −1,6 / −1,5 / −3,2 / +0,7 % (avec les 50-50 ; −0,3 à −2,6 % sans) ; les 50-50 coûtent 0,5-0,6 point (e-sport 1-2) ; ~100 cases. **Écartée.** Annexe « outsiders des marchés à 50-50 » : non concluante (puissance insuffisante).
  - **Primaires américaines 2026** (`experiments/primaires.md`) : 298 événements, 1 658 candidats, prix horaires CLOB et vrais échanges. Calibration correcte (≥ 0,97 : 49/49). **NON des candidats cotés 0,10-0,30 à J-14 : +7,1 % sur le prix horaire** (103 événements, t 2,0, 10 mois sur 10), **+3,7 % aux vrais prix** (t 0,7 ; un signal sur deux sans échange), l'effet croît avec le nombre de candidats (9 et plus : +9 à +12 %) ; même signe que `saison_sport` ; ~60 cases.
    **Contrôle négatif** : 499 événements d'élections hors primaires (`experiments/elections_non/`) : +1,9 % à J-14, t 0,3. **Indice faible**, restreint aux primaires.
  - Relevé essence mis à jour (24/10 : 4,29 $) ; rougeole : le CDC n'a pas publié depuis le 22/10.
- **Arène** : fantôme `candidats_non` (quart de Kelly, NON à 0,70-0,90, 10-18 jours avant la fin, champs de candidats `candidats_min: 2`, étiquette `midterms` 102289 ajoutée à `tag_pages` avec 12 pages et 20 jours d'horizon) ; cycle local : a acheté NON « Bernadette Wilson gagne le gouverneur d'Alaska » à 0,88 (OUI 0,13), relu. **C'est un essai hors échantillon** (les primaires sont finies ; le contrôle sur les élections générales est nul).
  Pas de fille de `crypto_threshold_prix_bas` « issue oui » : ses +281 € viennent d'un seul pari (OUI à 0,18, +227 €) ; pas de fille de `nf_sport_patiente` (mère pleine) ; 18 éliminées non recréées une à une (familles jugées sans avantage, comme ce matin). Tableau de bord : « À la une » mis à jour (aperçu : 0 px de débordement). 582 tests verts.
- **Reste ouvert** : (1) règlement de 5775544 (26/10) ; (2) lire `candidats_non` après le 3/11 (élections générales) ; (3) `favori_politique*` ont repris : vérifier leurs premiers règlements et les achats du principal copiés ; (4) un contrôle automatique « une famille perd soudain la moitié de ses marchés » (aurait trouvé la politique en `zero_fees` le 20/10) ; (5) le rapport `box_office_favori` du week-end 24-25/10 ;
  (6) compter les 50-50 écartés dans `idea_test.fetch_resolved` ; (7) la question à Etienne sur Yahoo/Pyth de ce matin reste posée.

## 2026-10-24 (passage chercheur, après-midi : 14 h 54 → 16 h 12 UTC)

- **Enquête** (fiches : `experiments/enquetes/2026-10-24_apres_midi_copie_prix_et_jetons.md`, `2026-10-24_seismes_doublon_entre_reseaux.md`, `2026-10-24_touche_deja_touchee_non_a_0_001.md` ; famille du jour n° 1, plus deux autres en famille 3).
  - **Famille 1, copie du principal au prix près** (217 achats, 151 jetons réglés) : prix payé identique à celui du fantôme (−0,0007 en moyenne pour la championne), gain réalisé −244 € contre −257 € au prix du fantôme ; les 48 jetons sans fantôme datent tous d'avant le 18/10 22 h UTC (copie fidèle, PR #76) ; 0 sur 111 achats depuis.
    Les cinq obligations « champion sans avantage / chance » : même cause que les 22 et 24/10 (mises ∝ 1/(1 − prix), favoris qui gagnent comme leurs prix) ; pas de défaut de code.
  - **Défaut trouvé (donnée)** : le catalogue USGS liste parfois un séisme deux fois (réseau `pt` 6,6 « Mi » et réseau `us` 6,3 « mww », Vanuatu 20/10 04:20) ; `seismes_marche` comptait 3 séismes ≥ 6,5 au lieu de 2 et a acheté NON « exactement 2 » à 0,259 (106 parts, chance estimée 0,97) contre un marché qui cote le OUI 0,76 (« plus de 13 » ≥ 5,5 à 0,80 : même écart d'un).
    Correctif : `seismes.dedup_rows`, `p_dedup`, abstention si l'écart dépasse 0,15 ; 2 tests. Exposition du fantôme : 27,5 € + 3 €. **À vérifier au prochain passage** : le règlement du marché 5775544 (compte avec ou sans le doublon ?).
  - **Défaut trouvé (obligation « audit », 3e enquête)** : `crypto_threshold_non` et `_prix_bas` ont acheté à 0,001 (29 900 parts, 30 € chacun) le NON de « Ethereum plonge à 2 300 $ le 24/10 », barre déjà touchée le matin : le modèle de barrière ignore les extrêmes déjà atteints dans la fenêtre. 8 achats du NON à 0,001-0,05 sur 8 perdus (−102 €) ;
    le « prix impossible » de l'audit venait d'un historique de prix en retard (proposition au noyau : `proposals/2026-10-24_audit_prix_marche_decide.md`). Correctif : `TOUCH_MIN_ASK` 0,05 dans `CryptoThresholdStrategy` + contrôle `enquete.jetons_sans_valeur` ; 2 tests (le premier échoue sans le garde-fou). Fiche : `2026-10-24_touche_deja_touchee_non_a_0_001.md`.
  - Positions bloquées : 812 € de capital de fantômes dans 20 positions sur 4 marchés non réglés depuis 4 à 6 jours (587 € sur « Cape Town 18 °C » en litige UMA, 3 fantômes `nm_*` à 188,6 €) : déjà documenté (23/10, `news_momentum`), pas de nouveau correctif.
- **Recherche** (4 pistes, comptes rendus et scripts versionnés) :
  - **Barres touchées de l'or, de l'argent, du pétrole et du gaz** (`experiments/commodites_toucher.md`) : 112 échelles hebdomadaires réglées sur Pyth (avril → octobre), prix horaires Yahoo pour le modèle, vrais échanges pour les achats, règlement relu 96 %. 328 paris, 98 événements, **+33,5 %, t par événement 2,35, z des prix 1,96**, 5 mois sur 7,
    +19 % sans les 3 meilleurs ; gain seulement sur les barres cotées 0,10-0,45 (le marché sous-cote les touches : +61 %, z 2,9), rien au-dessus de 0,40 ; hors échantillon : avril-juillet **+58 %** (z des prix 3,6) puis août-octobre **+8 %** (t 0,4) : l'effet s'efface ; échelles mensuelles : pas de répétition ; log-score du modèle moins bon que le marché ; ~25 regards. Verdict `idea_test` global « retenue », jugé **indice faible** → fantôme. Première version : une barre horaire en cours = regard d'une heure vers le futur (corrigé).
    **Contrôle négatif** (cryptos hebdomadaires, 197 semaines, 744 000 échanges, même méthode) : aucun effet (Bitcoin −3 à −18 %, Ethereum et Solana ≈ 0) : la méthode ne fabrique pas de gain sur des marchés suivis par des robots.
  - **SpaceX** (`experiments/spacex_cadence.md`) : compteurs « How many SpaceX launches in <mois / année> », Launch Library 2 contre spacex.com : règlement 9/9 ; 9 événements seulement, modèle −17 % à +35 % selon le réglage, paris quasi sûrs 7/7 gagnés (+10 %) : **indice faible** → fantôme `spacex_cumul`. En direct : « 140-159 » de l'année cotée 0,78 pour 0,87-1,00 de chance.
    Septembre 2026 n'a eu que 8 lancements : la loi des 120 jours est trop optimiste (0,945), la production prend la plus prudente de cinq lois.
  - **Détroits, course à la publication** (`experiments/detroits.md`) : écartée. Le gain apparent (+11 à +28 % à +0/+1 h de 11 h UTC) était un regard vers le futur : le marché saute en 3 secondes à la vraie publication (10 h 48 le 20/10, 12 h 20-12 h 57 la plupart des semaines, 15 h 19 deux fois).
  - **Température mondiale (NASA GISS)** : écartée sans test, volume tombé à 3-11 k$ et carnets vides (écart 0,07-0,28). Autres relevés (rougeole, essence) : aucune nouvelle donnée.
- **Arène** : trois fantômes ou corrections, tous à quart de Kelly :
  - `spacex_cumul` (nouvelle classe, source `ll2`, étiquette `spacex` 63 avec son propre horizon de 100 jours ; `market_scanner._add_tag_markets` accepte un `max_horizon_hours` par étiquette) ; cycle local : a acheté « 140-159 » à 0,78 (relu).
  - `toucher_metaux` (nouvelle classe, source `goldapi` : prix de l'or et de l'argent toutes les 5 minutes dans la table `prix_matieres`, étiquettes `gold` 101589 et `silver` 100733) ; ne joue que les marchés couverts par le journal depuis leur création : **premiers achats attendus pour la semaine du 02/11**. Pétrole et gaz : pas de source de prix libre.
  - `seismes_marche` : correctif du doublon (ci-dessus).
  - Obligations de la feuille de mission : les 18 stratégies éliminées « à remplacer » ne sont pas recréées une à une (leurs familles ont été jugées sans avantage) ; remplacées par deux familles nouvelles (la feuille demande une idée radicalement différente : nouvelle source et nouveau type de marché pour SpaceX et pour les barres de matières).
    Les trois filles 80/20 de `nf_sport_patiente` ne sont pas créées : 21 filles de `nf_sport_patiente` sont déjà configurées (l'arène en retire d'elle-même au-delà de 10 vivantes), la fille « 0,850-0,875 » existe sous une autre forme (`nf_sport_patiente_prix_850_875`), et l'enquête n'a trouvé aucun avantage derrière les chiffres de la mère (le z des favoris est celui de leurs prix) : ajouter des découpages de plus ne ferait que de la sélection.
  - `crypto_threshold*` : garde-fou `TOUCH_MIN_ASK` (voir Enquête) ; `idea_test.verdict` : jugement par moitié des mois (ramène « retenue » à « indice » si la seconde moitié rend moins du quart de la première : barres touchées).
  - Suivi en direct des stratégies « retenues » sur le passé (jetons réglés au 24/10, 16 h UTC) : `mots_prononces` 29 jetons, +12,8 % par euro misé mais −9,4 % par pari (z des prix −0,8) ; `compteur_tweets_non` 12 jetons +38 % (z +0,8) ; `compteur_tweets` 17 jetons +12,5 % (z +1,5) ; `detroits_marche_log` et `seismes_marche` : rien de réglé. Trop peu pour promouvoir ou retirer (≥ 20 par stratégie à viser).
  - Tableau de bord : « À la une » mis à jour (3 points remplacés) ; aperçu vérifié (0 px de débordement, téléphone et ordinateur). 578 tests verts.
- **Reste ouvert** : (1) règlement de 5775544 / « plus de 13 » ≥ 5,5 (doublon USGS) ; (2) relancer `commodites_toucher` quand octobre-novembre sont réglés (l'effet s'affaiblit-il ?) ; (3) pétrole et gaz : source libre de prix, ou clé Pyth gratuite (à demander à Etienne : `benchmarks.pyth.network` et `hermes.pyth.network/v2/updates/price/*` répondent 401) ;
  (3bis) **question pour Etienne** : le test des barres touchées a utilisé l'API de graphique de Yahoo Finance (non documentée) pour les prix horaires, en recherche seulement ; `CHANTIERS.md` écarte les API non documentées : si la règle vaut aussi pour la recherche, il faut une autre source pour refaire le test (Coinbase / Kraken pour les cryptos, une clé gratuite pour les matières) ; (4) lire `spacex_cumul` (position « 140-159 » jusqu'au 31/12) et `toucher_metaux` (premiers achats vers le 02/11) ; (5) rougeole : une ligne par mercredi du CDC (prochain : 28/10) ; essence : à relancer ; (6) mensuels de matières à écarter ou confirmer avec plus de mois ; (7) vrai modèle « touche » pour la crypto du jour (extrêmes déjà atteints depuis 0 h ET : gold-api donne aussi BTC et ETH, journal `prix_matieres` extensible) ; le garde-fou `TOUCH_MIN_ASK` n'écarte que le pire.

## 2026-10-24 (passage chercheur, matin : 09 h 54 UTC → voir fin de l'entrée)

- **Enquête** (fiche : `experiments/enquetes/2026-10-24_matin_cross_market_muette_sans_raison.md` ; famille 6 « ce qui ne tourne plus » + dix paris relus à la main, famille 3).
  - **Défaut trouvé (observabilité)** : 20 stratégies actives affichent des abstentions vides ; `cross_market` (0 opération en 8,9 jours, 424 marchés) ne disait pas si elle voyait des échelles sans écart ou rien du tout : quatre `continue` de `CrossMarketLadder.propose` sans raison écrite. Corrigé (« paire cohérente : aucun écart après frais »…) + test.
    Les autres `{}` sont des fenêtres horaires/calendaires de filles (`Filtered` écarte avant la stratégie) ou des sources sans rattachement : rien de faux ; `saison_non` n'a réellement presque aucun marché dans sa fenêtre (3-11/11 : Ballon d'Or, Grands Prix).
  - **Quatre obligations « chance / champion sans avantage »** : même mécanisme que les 22, 23 et 24/10 (biais fixe, mise ∝ 1/(1 − prix), 26 gagnés pour 26,4 attendus sur les 30 dernières opérations, −1,2 %). Pas de défaut de code.
  - **Dix paris au hasard** (685 achats hors `nf_*`/`nm_*`, graine 2410) : question, issue et règle concordent ; le seul perdant notable (`apres_echeance` NON à 0,964 sur « l'Ukraine vise Moscou le 21/10 », non réglé 3 jours après sa date, OUI à 0,18) vient d'une stratégie coupée depuis le 23/10.
- **Recherche** (`experiments/box_office.md`, `experiments/familles_tranches.md`, scripts versionnés) : **box-office du premier week-end** (240 films « Opening Weekend » réglés 2022-2026, leurs échanges réels : 6,7 Mo versionnés). Favorite (tranche la plus chère) : à 24 h de la fin 110 films, 100 gagnées pour 93,6 attendues, +7,5 % par pari aux prix du dernier achat réel et frais 5 % (t par film 1,96) ;
  signe positif de 12 à 96 h (+1 à +8 %), mais instable selon le jour de fin du marché (dimanche midi : −7 à +15 %) et selon l'heure : ancrée sur le week-end, dimanche 0 h → 16 h UTC +6,6 % (142 films, t 1,56), samedi 18 h → dimanche 16 h −2,0 %. ~40 réglages. NON des tranches basses (miroir du même biais), flux d'ordres (9 réglages) : écartés ; 2e week-end : non testé (27 films, libellés irréguliers).
  **Contrôle sur 6 autres familles à tranches répétitives** (Netflix 174, vues 241, Rotten Tomatoes 51, Billboard 75, Spotify 38, App Store 182) : aucun effet de favorite sous-cotée (−21 % à +5 %). L'App Store donne un « gagnant précédent trop cher » (z des prix −4,1) dont le NON est une loterie (sans les 3 meilleurs −48 à +62 %) : écartée.
  Test de permutation (2 000 tirages, 24 cases) : le meilleur rendement observé (+20,5 %, 24 h, favorite 0,5-0,8, 39 paris) dépasse le 95e centile du hasard (17 %), P = 0,022, mais le §7 de `box_office.md` (règle « premier achat » : −2 %, bande 0,5-0,8 −4 %) montre la fragilité.
  Verdict box-office : **indice faible → fantôme**, plafonné par le contrôle ; la confiance viendra des week-ends joués en arène (24-25/10, 30/10-1/11…).
- **Arène** : fantôme `box_office_favori` (nouvelle classe `BoxOfficeFavori`, quart de Kelly, dimanche 0 h → 16 h UTC, marché encore ouvert 1 h au moins, favorite sûre même si le scanner cache des tranches : masse cachée < favorite), étiquette `box-office` (51) dans `tag_pages` ;
  cycle local : voit 4 films (« une tranche cachée pourrait être la favorite » 1, « hors de la fenêtre » 2…) ; 2 tests. Pas de nouvelle fille de `nf_sport_patiente` (mère pleine : 10 filles vivantes). « À la une » : 5e point.
- **Reste ouvert** : lire `box_office_favori` après le week-end du 24-25/10 puis après celui du 30/10 (achats sur les films « Clayface », « Wildwood », « Klara and the Sun »…) ; refaire `box_office/scripts/releve.py` + `favori.py`/`fenetre.py` pour les films réglés depuis (≈ 3 par week-end) ;
  vérifier le règlement sur the-numbers.com (non lu aujourd'hui) ; séries « 2nd… weekend » (65 événements) quand les tranches seront comparables ; relevés essence/rougeole/ensembles météo (aucune échéance atteinte aujourd'hui) ;
  marchés de Hong Kong : sur 13 marchés scannés le 24/10, 1 seul éligible et aucun dans la liste de surveillance (6 « meilleur prix manquant » = tranches déjà jouées à 0,0005, 4 quasi certains, 2 sans liquidité) : le lecteur `meteo_hko` n'est appelé que s'il en voit un ; à surveiller avant de juger le relevé d'ensembles. La sauvegarde de la base du 24/10 (faite au premier cycle du jour) ne contient pas encore les tables `meteo_ensemble_*` : la première utilisable est celle du 25/10.

## 2026-10-24 (session avec Etienne : météo par ensemble et Hong Kong)

- **Enquête** : les marchés de température de Hong Kong se règlent par TRONCATURE du dixième (« 27°C » = 27,0 à 27,9), pas par arrondi :
  166 règlements sur 166 (`experiments/meteo_ensemble/hk_reglement.py`). Notre modèle supposait l'arrondi (erreur d'un demi-degré) :
  `weather_model.truncated`, `certain_side(..., truncation=True)`, testés.
- **Recherche** (`experiments/meteo_ensemble.md`) : Open-Meteo ne garde pas les prévisions d'ensemble passées (3 jours recollés des derniers
  passages : regard vers le futur) ; archives brutes NOAA GEFS / ECMWF sur AWS (GRIB2) possibles plus tard. Verdict : **pas testable aujourd'hui**.
- **Sources** : `meteo_hko` (arbitre de Hong Kong, maximum et minimum depuis minuit) ; `meteo_ensemble` (82 membres) avec relevé des probabilités
  par tranche ET des prix toutes les 6 h (tables `meteo_ensemble_releves` / `_membres`), vérifiés en vrai le 24/10.
- **Arène** : rien (pas de stratégie sans test).
- **Reste ouvert** : juger le relevé dans 5 à 7 jours (`experiments/meteo_ensemble/evaluer_releve.py --base …`, aux prix payés).

## 2026-10-24 (passage chercheur, matin : 04 h 55 UTC → voir fin de l'entrée)

- **Enquête** (fiche : `experiments/enquetes/2026-10-24_principal_contre_fantome_copie.md` ; famille du jour 1 « le principal ne joue pas ce que l'arène mesure », puis les trois obligations « chance »).
  - **Rien de faux trouvé dans la copie** : le principal (772 €, −228 € réglés) a bien joué 62 jetons de `nf_sport_patiente`, tous présents dans son fantôme (+161 € sur 13 585 €). Sur la même période, les paris copiés font −2,5 % (74 paris) et les non copiés +5,1 % (50) :
    l'écart (tranche 0,90-0,95 : −15,6 % contre +8,0 %) ne vient ni de la taille de mise ni du prix (copiés par quartile de mise 13/34, 17/35, 28/34, 23/35, prix moyen 0,85-0,89) : hasard d'échantillon.
  - **Constat de fond** : sur les 1 798 jetons réglés de toute l'arène (premier achat de chacun), les favoris gagnent autant que leurs prix à tous les prix (0,60-0,80 : 128 gagnés pour 142,8, z −2,2 ; 0,80-0,95 : z −1,4 à +0,6).
    Les trois obligations « chance » ont la même cause qu'aux 22 et 23/10 (mises ∝ 1/(1 − prix) à biais fixe, rien derrière). Aucun correctif de code, pas de nouveau contrôle.
- **Recherche** (`experiments/seismes.md`, scripts `experiments/seismes/scripts/`, chantier n°6 USGS) : marchés « plus gros séisme du jour » (27 jours réglés) et « combien de séismes cette semaine » (57 événements), règlement sur l'USGS.
  Règlement relu : jour 26/27, semaine 47/57 (les 10 écarts : marchés ≥ 5,5 où Polymarket compte un séisme de plus que le catalogue d'aujourd'hui). Modèle du jour étalonné sur 660 jours (|z| ≤ 1,6 par tranche) ; modèle de la semaine Gamma-Poisson (variance 3 × la moyenne).
  **Contre le marché** : jour, perte log 0,18-0,35 contre 0,29-0,50 au tableau brut, mais test apparié par événement non significatif (modèle meilleur 31 fois sur 56, t −1,3) ; semaine égalité (≥ 5,5 : t +1,2 en sa défaveur). **Aux prix payés** : jour 27 paris +69 % (13 jours, t 1,15), semaine ≥ 5,5 +24 % après frais (181 paris, 27 événements, t 2,05 ; sans les 3 meilleurs +8 %), ≥ 6,5 +7 % (t 0,6).
  ~30 découpages regardés, marchés minces (échange médian 8 $) : **indice faible → fantôme**, pas « retenue ».
- **Arène** : fantôme `seismes_marche` (quart de Kelly, `jamais_retirer`) avec lecteur `sources/usgs.py` (séismes M ≥ 5 des 10 derniers jours, toutes les 10 minutes), module `seismes.py` (lois du jour et de la semaine, tables `seismes_tables.json` à refaire chaque mois par `experiments/seismes/scripts/tables.py`),
  étiquette `earthquakes` (103038) dans `tag_pages`, 16 tests. Cycle local : 1er cycle « seismes 0 » (le catalogue est lu pendant le cycle, rattaché au suivant), 2e cycle : 6 marchés rattachés, 3 achats relus à la main (« plus de 13 séismes ≥ 5,5 » OUI à 0,42 pour 0,68, 11 déjà vus dont une réplique de 7,0 ;
  « 4 séismes ≥ 6,5 » OUI à 0,05 pour 0,27, 3 déjà vus ; « 12 séismes ≥ 5,5 » NON à 0,82 pour 0,89). Filles 80/20 de la feuille de mission : `nf_sport_patiente_6_24h_6_12h` et `nf_sport_non_900_925` (fantômes, 11-12 opérations : pistes, pas preuves) ;
  pas de fille de `nf_tennis` 0,80-0,85 (doublon de `nf_tennis_12_18h_vainqueur_800_850`, déjà en arène).
- **Tableau de bord** : « À la une » remis à jour ; bloc `entonnoir` replié au départ (8 900 px sur téléphone, près de la moitié de la page : la page passe de 18 400 à 9 600 px, aperçu `apercu_dashboard.py`, 20 tests du tableau verts).
- **Reste ouvert** : refaire `releve.py` + `hebdo.py` + `jour.py` dans un mois (≈ 25 jours de plus) ; comprendre l'écart de comptage ≥ 5,5 (10 semaines sur 28 : +1) avant de se fier aux tranches ≥ 5,5 ; marchés mensuels de séismes non testés ;
  évaluer les relevés d'ensembles météo quand Gamma les aura clos (aujourd'hui à 12 h UTC pour les premiers).

## 2026-10-24 (passage chercheur, minuit : 23 h 55 UTC → voir fin de l'entrée)

- **Enquête** (fiche : `experiments/enquetes/2026-10-24_ecart_estimation_et_reference_arene.md` ; famille du jour 6 « ce qui ne tourne plus », puis obligations et contrôle `estimation_gonflee`).
  - **Obligations** (`apres_echeance`, championne, `contrer_crypto_patiente`) : causes déjà écrites les 22 et 23/10, rien de neuf.
  - **Défaut trouvé : `estimation_perimee` signalait des erreurs qui n'en sont pas.** Les 6 constats du rapport publié (compteur_tweets ×3, decroissance_temps, detroits_marche_log, mots_prononces) concernent des stratégies à modèle propre dont
    l'écart « estimation − prix » varie par construction (écart interquartile 0,04 à 0,25 contre 0,00 à 0,02 pour les `nf_*`). Sur le passé des tweets, les achats à écart ≥ 0,20 sont les meilleurs (+25 à +29 %), ceux à écart < 0,10 perdent 4 %.
    Correctif : seuil = écart habituel + max(8 points, 3 × écart interquartile) ; test ; rapport 6 → 2 constats (le CZ du 23/10, estimé 0,81 payé 0,10 à 33 minutes de la fin, reste signalé).
  - **Référence** : l'arène entière (1 721 jetons, 59 509 € misés) perd 3,8 % par mise hors frais (−2 264 € pour un hasard de ±945 €) ; `estimation_gonflee` (z −10,9) vient surtout des estimations des `nf_*`/`naive_favorite` (biais fixe, déjà tracé le 22/10) et de `meteo_prevision`
    (154 achats, tous avant le 19/10 : 0,81 annoncé, 54 % gagnés). Toute stratégie doit se comparer à −3,8 %, pas à 0.
  - **Vérifié** : `loterie_meteo` voit bien les marchés de température (94 sur 94 classés `weather`, 30 candidats dans la fenêtre à 8 h UTC) ; les « 377 exclus par famille » du cycle de 23 h 45 sont les marchés non météo de la liste ; sources météo « ok (5 / 3 observations) » ;
    12 achats tirés au hasard parmi 195 (stratégies hors `nf_`/`nm_`) relus sur Gamma : bons marchés, bons côtés.
  - **Deuxième contrôle à la main (famille 4, filtres de prix)** : sur 2 013 achats des 3 derniers jours, 39 (1,9 %) sont 1 à 2 crans hors de la plage de leur stratégie (tennis à 0,78 pour 0,80-0,95) : filtre sur le prix du scan, sans effet mesurable, aucun correctif.
- **Recherche** (`experiments/tweets_fin_periode.md`, scripts `experiments/tweets_fin_periode/`) : compteur de tweets, 189 périodes (juillet → 20/10), rejeu heure par heure jusqu'à 10 minutes de la fin, règlement relu 185/189, échanges réels des 189 événements.
  - Dernières heures : **non démontré** (53 achats, 6 périodes, tous cz_binance, +17 à +38 % ; les 4 pertes en direct sont compatibles avec la malchance).
  - Écart exigé entre le calcul et le prix : plus il est grand, plus le rendement monte (NON sans NYC : 0,03 +11 %, 0,12 +20 %, 0,18 +23 % par achat). Aux prix réellement payés : **+41 % (288 achats, 57 périodes, tranches toutes fraîches) à +14 % (1 631 achats, 133 périodes, toutes tranches, t +2,1)**,
    « retenue » par `idea_test.verdict`, mais 13 % seulement des signaux ont un échange dans l'heure, le prix horaire d'une tranche peu échangée gonfle l'écart (21 % → 12 % au prix payé), WhiteHouse (−14,5 %) et Elon (−8,7 %) perdent, découpage issu d'une sélection (~60 coupes) : **indice fort → fantôme**. ~25 réglages regardés.
  - Relevé d'ensembles météo n° 3 versionné (2 024 marchés) ; toujours 0 marché réglé à minuit (les premiers finissent le 24/10 à 12 h UTC) : évaluation le 24/10 au soir.
  - `marge_coherente` (n° 3) : l'écart de +0,026 du 22/10 est refermé (−0,002 le 24/10 à 0 h) : **écartée**.
- **Arène** : fille `compteur_tweets_non_ecart_large` (fantôme, mère `compteur_tweets_non`, écart calcul − prix ≥ 0,15, sans Elon ni Trump, pas dans `validated_strategies`) ; cycle local : 467 marchés, 2 propositions relues à la main (Elon, avant l'ajout du filtre Elon/Trump).
- **Reste ouvert** : confirmer à 6-12 h UTC que `loterie_meteo` achète ; évaluer les relevés d'ensembles météo quand Gamma les aura clos (0 réglé à minuit) ; fille de `compteur_tweets_non_ecart_large` avec NON ≤ 0,60 et sans WhiteHouse seulement après 30 paris en direct ;
  rejeu des tweets aux échanges (pas aux prix horaires) pour Elon et Trump ; ordres posés sur les 13 % de signaux échangés.

## 2026-10-23 (passage chercheur, soir : 19 h 55 → 20 h 33 UTC)

- **Enquête** (fiche : `experiments/enquetes/2026-10-23_soir_news_momentum_certitude.md` ; famille du jour 6 « ce qui ne tourne plus », puis obligations).
  - **Défaut trouvé : `news_momentum` promet 0,999 pour un favori à 0,986.** En regardant les 27 positions « ouvertes bien après l'échéance » (990 € bloqués : marchés du Cap et de Kyiv en litige UMA, référendum d'Alberta en attente du résultat officiel),
    trois fantômes de la famille (`nm_hors_crypto`, `nm_demi_mise`, `nm_prix_haut`) avaient chacun misé 188,8 € (20 % de leur capital) sur « Non » à 0,986 pour la température du Cap, estimation 0,999, gain possible 1,3 point.
    Cause : `estimation = prix + 0,04`, puis bornes ramenées à 0,999 (la borne basse ne dépend plus de l'incertitude). Famille entière : 319 paris, 205 gagnés pour 216 attendus, −526 € ; prix ≥ 0,95 : −42 € pour 5 618 € misés ; 0,90-0,95 : −362 €.
    Correctif `_bump` (la continuation ne dépasse pas la moitié de l'écart à la certitude) pour `news_momentum`, `information_advantage`, `social_sentiment` ; tests (échouent sans le plafond) ; contrôle `certitude_promise` (27 paris à 0,995 et plus : −154 €).
  - **Obligations** : `apres_echeance` et la championne (jour du 18/10) : causes déjà écrites, rien de neuf ; `contrer_crypto_patiente` : 24 gagnés pour 18,4 attendus sur 97 paris, le déficit (−45,7 €) vient de 31 billets à moins de 0,10 (0 gagné, 12 % de chance) : variance, pas de défaut.
  - **Contrôle de la chance** sur les trois premières de l'arène : `nf_sport` (65 paris, +268 €, sans les 3 meilleurs +200 €, z des prix +0,49), `nf_tennis_12_18h_vainqueur` (40 paris, +175 €, sans les 3 meilleurs +99 €, z +0,93), `nf_sport_patiente_6_24h` (19 paris, +159 €, sans les 3 meilleurs +90 €, z +1,08) : gains qui survivent au retrait des 3 plus gros paris, mais z de 0,5 à 1,1 (aucun avantage prouvé, 75 stratégies en concurrence).
  - **Vérifié** : 10 achats tirés au hasard depuis 12 h UTC relus sur Gamma (bons jetons, bons marchés, 10/10) ; copie du principal : un seul constat automatique (ordre posé servi une minute avant, déjà connu) ; le plafond de 25 % tient (671 achats de fantômes depuis le 23/10 00 h 30 : 17 à 20 % ou plus, au plus 25 %) ; `loterie_meteo` : à 19 h 45 UTC aucun marché météo n'est dans sa fenêtre de 6 h (échéances à 12 h UTC) : elle ne peut pas acheter le soir, à relire demain entre 6 h et 12 h UTC pour vérifier que le correctif de la famille météo l'a réveillée.
- **Recherche** (`experiments/k_gagnants.md`) : somme des prix OUI = k (top N, qualifiés, relégués, huitièmes ; 121 événements, 3 713 marchés). Au premier relevé (prix du CLOB) : Σp/k 1,13-1,15 à J-14/J-30 et z −6 : carnets vides à 0,50 (défaut connu).
  Aux vrais échanges : Σp/k médian 1,00-1,03 (13 à 24 événements utilisables, les anciens échanges manquent), renormaliser gagne 0,0004-0,012 de log-score, 27 réglages, un seul « indice » (+31 %, 13 événements) non répliqué : **écartée, preuve insuffisante**.
  Relevé d'ensembles météo : 2e relevé (2 024 marchés, 184 événements) versionné, à évaluer le 24-25/10.
- **Arène** : deux filles 80/20 (fantômes, morceaux de 11-12 opérations : pistes, pas preuves) `nf_tennis_12_18h_vainqueur_800_850` et `nf_sport_patiente_6_24h_autre` (cycle local : la seconde pose 2 ordres, la première est hors de sa fenêtre 12-18 h) ; pas de fille de `nf_tennis` 0,80-0,85 (doublon de `nf_tennis_prix_bas_800_850`).
  Les 15 « éliminées encore configurées » de la feuille de mission : non remplacées (les retraits pour inactivité sont déjà traités par `jamais_retirer`, les autres sont des variantes de la famille sans avantage mesuré).
- **Reste ouvert** : vérifier `loterie_meteo` le 24/10 le matin ; évaluer les deux relevés d'ensembles ; rattachement d'actualités aux marchés météo (un « pic de mentions » sur une température du Cap) ; `k_gagnants` avec des échanges plus anciens ou des carnets relevés en direct.

## 2026-10-23 (session avec Etienne : détroits, sources « arbitres »)

- **Recherche** (`experiments/detroits.md`) : 96 événements réglés sur IMF PortWatch, dont 58 à tranches clos ; règlement relu 40/40 depuis juin
  (7/17 de mars à mai : PortWatch a révisé ses chiffres, exclus). PortWatch se met à jour le mardi vers 11 h UTC jusqu'au dimanche (retard de 2 à 9 jours).
  Tranches hebdomadaires et mensuelles, 16 réglages : **retenue mais fragile** (150 paris, +24 %, t par événement 2,13, z des prix 2,83 ; sans les 3 meilleurs +11,8 % ;
  regroupé par détroit et par mois t 2,77, vérifié à part). L'AIS d'Ormuz ne suit pas PortWatch (corrélation 0,1 à 0,3 sur 26 jours).
- **Arène** : fantôme `detroits_marche_log` (demi-Kelly, pas dans `validated_strategies`) ; scanner : étiquette `hormuz` (104139) ; cycle local : 22 marchés, 7 achats relus.
- **Reste ouvert** : marchés à seuil (« returns to normal », 20 événements clos) ; course à la publication du mardi ; comparaison AIS / PortWatch sur 60 jours.

## 2026-10-23 (passage chercheur, après-midi : 14 h 56 → 15 h 5x UTC)

- **Enquête** (fiches : `experiments/enquetes/2026-10-23_meteo_zero_fees_famille.md`, `2026-10-23_inactives_retirees_et_calendriers.md` ; famille du jour 6, puis famille 1).
  - Obligations de la feuille de mission (championne : 3 paris = 95 % du gain, le 18/10 = 170 % ; `apres_echeance` et `nf_sport_patiente_prix_850_875` sans avantage récent) : causes déjà écrites les 22 et 23/10, rien de neuf.
  - **Vérifié** : les correctifs du matin tiennent. Sur 470 achats de fantômes faits après leur mise en service (23/10 00 h 30 UTC) : aucune mise au-dessus de 26 % du capital, aucun deuxième camp d'un même match.
  - **Défaut 1 (famille 6) : deux pannes météo silencieuses.** Gamma a passé la météo en `feeType: zero_fees` (événements du 19-20/10) : `market_family`, qui tire la famille du barème de frais, ne la voyait plus ;
    `loterie_meteo` voit 371 marchés, en écarte 371, plus aucun achat depuis le 20/10 à 16 h 27. En même temps les marchés citent `aviationweather.gov/api/data/metar?ids=…` (199 événements sur 255)
    que `sources/weather.py` ne lisait pas : **`meteo_metar` et `meteo_prevision` « ok (0 observations) »** depuis. Politique et finance sont aussi en `zero_fees` (471/600 et 577/582). Correctifs : `market_family`
    (météo reconnue à l'adresse de l'événement), `STATION` (deux formes de lien), `resolution_sources` ; contrôles `familles_vides` et `sources_vides` (testés, ils signalent bien `loterie_meteo` et les deux sources sur les données publiées).
  - **Défaut 2 (famille 6) : le ménage de l'arène retire définitivement les stratégies « inactives » (3 jours, filles 2)** : 13 retraits dont 10 en deux jours (quatre arbitrages sans écart, `mots_prononces_nfl` entre deux matchs
    NFL, les deux de cotes à budget épuisé) ; cinq stratégies prouvées sur le passé et vivantes (`cpi_tranches` CPI le 11/11, `jobs_favori_non` le 6/11, `statu_quo_ia`, `saison_non`, `non_aux_drames`) allaient l'être avant leur
    premier jour utile. Correctif : `jamais_retirer` (config/promotion.yaml), `mots_prononces_nfl` en version 1.1.0, contrôle `retraits_inactifs`, test sur la config réelle.
  - Famille 1 à la main : gain réalisé du principal −235,7 € ; 18/10 −134 € (copie d'avant le correctif : paris à 2-3 fois la taille du fantôme sur `nf_court`) ; depuis le 19/10 −2,4 % par mise (1 784 € misés),
    des favoris à 0,83-0,93 qui perdent : pas de défaut de copie. Constaté sans correctif : 13 ordres posés « OUVERT » de deux portefeuilles éteints (≈ 486 € réservés, sans effet) ; marchés Cape Town 17 et 18 °C en litige UMA.
- **Recherche** : piste 0b, **détroits** (`experiments/detroits.md`) : verdict **indice, sans preuve**. Loi calculée sur 2 ans de PortWatch (800 jours en production) : la tranche 25-29 de Bab el-Mandeb, cotée 0,81, a 0,45-0,51 ; la même tranche de
    5 revient 51 % du temps à +13 jours ; mais **aucun prix passé** de ces marchés (2 événements ouverts). Ormuz : pas de loi (régime changé en mars, garde-fou). Relevé en direct des ensembles Open-Meteo
    pour la météo (`experiments/ensemble_meteo/releve.py`), à évaluer au prochain passage sur les marchés réglés (frais nuls depuis le 20/10, donc le « −6 % » du test météo est à refaire).
- **Arène** : fantôme `detroits_tranches` (indice, quart de Kelly ; premier cycle : NON de la tranche 25-29 à 0,20 et OUI de 20-24 à 0,09, ≈ 28 € ; entrée le jour d'un saut de prix du marché, 0,60 → 0,81 : acheteur peut-être informé ; règlement le 31/10) ; `mots_prononces_nfl` 1.1.0 ;
    étiquette `bab-el-mandeb` (105617) dans le scanner (3 tranches sur 5 sous `min_volume_24h`).
- **Reste ouvert** : évaluer le relevé d'ensembles (marchés réglés, aux vrais prix, frais nuls) ; décider si `zero` entre dans les listes `familles` politiques (94 marchés sur 393 seulement) ; le prix des tranches « average daily transits »
    est enregistré toutes les heures (`historique_references`, source « detroit ») : juger l'erreur du marché après quelques règlements ; refaire les tests politiques/météo avec des frais nuls.

## 2026-10-23 (session avec Etienne : veille des API publiques)

- **Recherche** : liste GitHub `public-apis` (2 191 API) triée, 28 candidates appelées sans clé (`experiments/veille_api_publiques.md`).
  Retenues en premier : IMF PortWatch (arbitre des marchés Ormuz et Bab el-Mandeb, ≈ 300 000 $/24 h, publié avec ≈ 5 jours de retard) et le suivi AIS d'Ormuz,
  Open-Meteo Ensemble (probabilité par tranche de température, 107 marchés), Hong Kong Observatory (arbitre), OpenDota, Pyth Hermes (arbitre).
  Écartés : revendeurs de cotes de bookmakers et de données X, agrégateurs de marchés de prédiction, SportScore (protégé), Econdb (identification).
- **Arène** : rien (sources à brancher : chantiers n° 32 à 37).
- **Reste ouvert** : piste 0b (détroits) ; clé gratuite `BLS_API_KEY` à proposer à Etienne.

## 2026-10-23 (passage chercheur, matin : 09 h 55 → 10 h 42 UTC)

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
