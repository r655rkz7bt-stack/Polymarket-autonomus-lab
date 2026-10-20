# Scripts des tests sur le passé des vingt pistes (20/10/2026)

Exemples de **recherche profonde** à reprendre pour une nouvelle piste (méthode :
docs/ROUTINE_CHERCHEUR.md, partie B). À lancer depuis la racine du dépôt avec
`.venv/bin/python experiments/vingt_pistes/scripts/<script>.py` ; les données téléchargées vont dans
`donnees/` (ignoré par Git : on garde les scripts et les chiffres, pas les fichiers bruts).
Écrits vite pendant la recherche : à adapter, pas une bibliothèque. Résultats : `../../vingt_pistes.md`.

| Piste | Ordre | Ce que fait chaque script |
|---|---|---|
| compteur_tweets | `tweets_releve_messages.py` → `tweets_calibrage.py` | messages XTracker de 7 comptes ; calibrage du modèle (rythme, dispersion) sur toutes les semaines passées, sans regard vers le futur |
| | `tweets_releve_marches.py` → `tweets_contre_marche.py <marches.json> <dispersion> <marge> <prix_min>` | prix horaires de 177 périodes passées ; log-score modèle contre marché ; achats simulés (frais 0,05·p·(1−p), demi-écart) par mois et par période |
| haut_ou_bas_crypto (écartée) | `crypto_releve.py` → `crypto_contre_marche.py <marge> <heures_vol> <queue>` | 444 marchés quotidiens, prix Binance (source de règlement) ; contrôle que notre lecture redonne le règlement |
| fatigue_nhl | `nhl_releve_calendrier.py` → `nhl_releve_prix.py` → `nhl_fatigue.py` | calendrier officiel (qui a joué la veille), prix Polymarket une heure avant le match, deux saisons |
| totaux NHL (écartée) | `nhl_releve_totaux.py` | lignes « plus ou moins » et leur calibrage |
| mots_prononces | `mentions_releve_evenements.py` → `mentions_releve.py` → `mentions_taux_historique.py <marge> <prior> <min_precedents> <delai_h> <prix_min> <sans_guillemets>` | taux historique par orateur et par mot, jugé marché par marché avec seulement les marchés réglés AVANT |
| mots_nouveaux | `mentions_releve_mots_nouveaux.py` → `mentions_mots_nouveaux.py <delai_h>` | mots jamais proposés pour l'orateur |

Ce qui a rendu les verdicts fiables (à refaire à chaque piste) :
1. **Contrôle du règlement** : notre lecture des données redonne-t-elle le résultat officiel ?
   (crypto : 443 sur 444 ; tweets : total XTracker = « Post Counter » sur 8 comptes).
2. **Jamais de regard vers le futur** : prix et données lus avant l'instant de décision.
3. **Contre le marché d'abord** (log-score), puis achats simulés avec les VRAIS frais du marché
   (`feeSchedule`) et un écart achat-vente ; plusieurs réglages, pas seulement le meilleur.
4. **Robustesse** : par mois / saison, moyenne PAR ÉVÉNEMENT (paris liés), tranches de prix
   (`idea_test.verdict`). Un seul réglage gagnant sur dix, ou un seul mois, ne prouve rien.
5. **Essai en direct** avant d'envoyer (rattachements relus à la main, propositions possibles).
