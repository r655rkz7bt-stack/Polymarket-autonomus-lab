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
1. **Champions de saison contre Pinnacle** (golf, F1, football européen : outrights de The Odds API).
2. **Classements « status quo »** : « quel modèle d'IA sera n° 1 du classement LMArena », « n° 1
   Spotify / Billboard » : le leader actuel reste-t-il plus souvent que son prix ne le dit ?
   (historiques publics des classements).
3. **Données économiques** : inflation (CPI) et emploi contre la prévision « nowcast » de la Fed de
   Cleveland (gratuite) et contre Kalshi (kalshi_reference).
4. **Prix de l'essence (AAA) / pétrole** au jour près : modèle de marche aléatoire calibré, comme
   le test crypto (attention : le test crypto a été négatif, marché suivi par des robots).

5. **Mots nouveaux par type d'événement** (rallye, conférence, mois entier) : reste de l'ancienne piste n° 1 ;
   les « annonceurs » et « anyone » sont jugés (ci-dessous).
6. **Matchs de NFL, suite** : `mots_prononces_nfl` (fantôme) à confirmer sur de nouveaux matchs ; si oui,
   tester les mots à seuil (« Referee 5+ times ») séparément des mots simples.

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
| mentions « annonceurs » NFL (14 matchs) | indice | +21 % à +91 % par achat sur 6 réglages, t par match +0,8 à +4,8 ; 2 mois, marchés minces : fantôme `mots_prononces_nfl` | mentions_annonceurs.md |
