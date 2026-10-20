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
1. **Fatigue NBA** (dos-à-dos, 3 matchs en 4 jours, voyage) : même méthode que fatigue_nhl,
   calendrier `cdn.nba.com` (ou BALLDONTLIE_API_KEY) ; saison NBA en cours depuis le 21/10.
2. **E-sport, favoris par jeu** (CS2, LoL, Dota, Valorant) : beaucoup de paris de la championne
   (G2 Ares, LOUD, Lynn Vision…). Calibrage des favoris par jeu et par niveau de tournoi sur le
   passé (Gamma tag esports + prices-history ; PANDASCORE_API_KEY pour le niveau des équipes).
3. **compteur_tweets, filles** : sans NYC Mayor (perdant à tous les réglages), Elon seul, dernières
   48 h seulement, NON seulement. Données déjà prêtes (scripts tweets_*).
4. **Mentions : « the announcers » et « anyone »** (meilleurs morceaux sur le passé, +29 % à +45 %),
   et mots nouveaux par type d'événement (rallye, conférence, mois entier).
5. **Champions de saison contre Pinnacle** (golf, F1, football européen : outrights de The Odds API).
6. **Classements « status quo »** : « quel modèle d'IA sera n° 1 du classement LMArena », « n° 1
   Spotify / Billboard » : le leader actuel reste-t-il plus souvent que son prix ne le dit ?
   (historiques publics des classements).
7. **Données économiques** : inflation (CPI) et emploi contre la prévision « nowcast » de la Fed de
   Cleveland (gratuite) et contre Kalshi (kalshi_reference).
8. **Prix de l'essence (AAA) / pétrole** au jour près : modèle de marche aléatoire calibré, comme
   le test crypto (attention : le test crypto a été négatif, marché suivi par des robots).

## Testées
| Piste | Verdict | Chiffre clé | Où |
|---|---|---|---|
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
