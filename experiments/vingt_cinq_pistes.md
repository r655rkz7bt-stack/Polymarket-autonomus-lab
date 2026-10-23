# Vingt-cinq pistes inédites (21/10/2026, soir)

Demande d'Etienne : « Trouve des nouvelles stratégies inconnues/inédites (25) ».

Méthode : inventaire des 121 stratégies de `config/strategies.yaml` et des pistes déjà testées
(`vingt_pistes.md`, `PISTES.md`, `CHANTIERS.md`) pour ne rien refaire. Puis relevé des 395 séries
d'événements ouverts sur Polymarket (Gamma, 21/10 vers 17 h 40 UTC, triés par volume du jour)
et recherche web.

**Rien n'est testé ici.** Chaque piste passe d'abord par un test sur le passé aux prix réellement
payés (`idea_test.taker_cost`), puis par un fantôme. Données : gratuites seulement ; une clé
gratuite est signalée « clé » (à proposer à Etienne, jamais à demander dans la conversation).
Aucune aspiration de site sans API ni flux (règle n° 7).

Ce que dit la recherche (à vérifier, pas des preuves) :
- [Favori-outsider sur Polymarket (arXiv 2609.12878)](https://arxiv.org/pdf/2609.12878) : les
  outsiders rapportent à 5 min / 1 h / 1 jour mais perdent nettement au règlement.
- [Kalshi (Bürgi, Deng, Whelan 2025)](https://www.ucd.ie/economics/t4media/WP2025_19.pdf) : les
  contrats bon marché gagnent moins souvent que leur prix, les chers plus souvent.
- [Échéances longues (arXiv 2602.21091)](https://arxiv.org/pdf/2602.21091) : plus l'échéance est
  lointaine, plus les prix sont tirés vers 0,50 (le coût d'immobiliser l'argent).
- [Arbitrages sur Polymarket (résumé)](https://stafforini.com/works/craig-2025-polymarket-users-lost/) :
  ~40 M$ de gains sans risque sur des issues dont la somme ≠ 100 %, surtout en sport.

## Les vingt-cinq pistes

### A. Cohérence entre marchés (données Polymarket seules)
| # | Nom proposé | Idée | Marchés vus le 21/10 |
|---|---|---|---|
| 1 | `score_exact_poisson` | Les marchés « vainqueur » et « plus/moins de 2,5 buts » d'un match donnent le nombre de buts attendu de chaque équipe ; une loi de Poisson en déduit la chance de chaque score exact. On achète les scores exacts vendus nettement sous ce calcul. | « Exact Score » : Ligue 1, Bundesliga, Serie B, Eredivisie… |
| 2 | `toucher_avant_fin` | « Le Bitcoin touchera-t-il X ce mois-ci ? » vaut au moins « sera-t-il au-dessus de X à la fin ? », et en gros le double (principe de réflexion d'une marche au hasard). On compare les deux séries de la même date. | `bitcoin-hit-price-*`, `btc-multi-strikes-weekly`, Ethereum |
| 3 | `marge_coherente` | Les tranches « marge de victoire » d'une élection, additionnées par candidat, doivent redonner le prix « vainqueur ». Écart → acheter le côté le moins cher. | Brésil 2e tour, Bulgarie 1er tour |
| 4 | `bo3_coherence` | Dans un match en 2 manches gagnantes, la chance de gagner la série se déduit de la chance de gagner une carte (loi binomiale). On compare « vainqueur de la série » et « carte 1 ». | Counter-Strike, LoL, Dota 2 (BO3, BO5) |
| 5 | `tennis_sets_coherence` | Même calcul au tennis : « gagne le 1er set », « gagne en 2 sets » et « gagne le match » doivent s'accorder. La championne gagne au tennis : un prix de match plus juste l'aiderait. | ATP, WTA, ITF |
| 6 | `ufc_coherence` | « Gagne par KO », « par soumission », « aux points » : leur somme doit redonner « gagne le combat ». | UFC 333 |
| 7 | `monte_carlo_tournoi` | « Qui ira en quart / en demie ? » se recalcule en jouant 10 000 fois le reste du tournoi avec les prix des matchs. Écart → acheter. | Ligue des champions : « Team to advance » |
| 8 | `courbe_de_risque` | « Le cessez-le-feu tiendra-t-il jusqu'au… ? » : on ajuste une courbe de risque régulière à toutes les dates ; la date qui sort de la courbe est mal cotée. Plus fin que `echelle_dates`, qui ne voit que l'ordre. | Iran, Israël-Iran, Russie-Ukraine |

### B. Formes des prix (données Polymarket seules)
| # | Nom proposé | Idée |
|---|---|---|
| 9 | `lissage_tranches` | Dans un marché à tranches (température, tweets, entrées en salle, vues), les chances forment presque toujours une seule bosse. Une tranche qui fait un creux ou un pic isolé est mal cotée : on l'achète ou on achète son NON. |
| 10 | `queues_de_tranches` | Généraliser `cpi_tranches` : sur tous les marchés à tranches, les cases improbables (3 à 25 %) gagneraient deux fois moins que leur prix → acheter leur NON. |
| 11 | `non_aux_drames` | « Les États-Unis confirmeront-ils l'existence des extraterrestres ? », « faillite d'Anthropic », « invasion de Taïwan » : le OUI à 2-15 % sur une longue échéance serait trop cher (étude Polymarket ci-dessus) → acheter le NON, qui touche souvent la récompense de détention. |
| 12 | `chiffres_ronds` | Les acheteurs posent leurs ordres sur des prix ronds (0,50, 0,90, 0,95). Poser son ordre un cran au-dessus passe devant la file et sera servi plus souvent, pour un cran de prix. Test : les ordres posés de notre journal. |
| 13 | `contrer_football_en_jeu` | Comme `contrer_crypto`, mais pendant les matchs de football : après un gros saut de prix (but, carton rouge), le prix dépasserait sa juste valeur puis reviendrait un peu. |
| 14 | `proposition_uma` | Gamma signale `umaResolutionStatus: proposed` (5 des 100 marchés les plus actifs le 21/10) : un résultat est proposé et sera payé dans environ 2 h sauf contestation. Si l'issue proposée coûte encore 0,90-0,98, on l'achète. Ce n'est pas `apres_echeance`, qui part de la date et non de la proposition. |

### C. Avec une source gratuite
| # | Nom proposé | Idée | Source |
|---|---|---|---|
| 15 | `depouillement_officiel` (**écartée le 22/10** : Polymarket fixe le prix bien avant la certitude, `bresil_second_tour.md`) | Pendant le dépouillement, l'organisme officiel publie les résultats en direct. Quand l'avance dépasse ce qui reste à compter, on achète le gagnant avant que Polymarket suive (comme `fin_de_match`, pour les élections). **2e tour au Brésil le 25/10/2026.** | TSE (Brésil), CIK (Bulgarie) : flux publics |
| 16 | `etats_comme_avant` (**écartée le 22/10** : déjà dans les prix, `bresil_second_tour.md`) | « 1re place dans l'État d'Amapá » : un État vote presque toujours comme au tour d'avant ; on compare au résultat officiel du 1er tour. | TSE (données ouvertes) |
| 17 | `battre_resultats` | « IMAX battra-t-il ses résultats ? » : environ 3 entreprises sur 4 battent la prévision des analystes. On mesure ce taux sur les marchés Polymarket déjà réglés, par entreprise, et on achète le OUI vendu en dessous. | Polymarket (historique) |
| 18 | `kpi_tendance` | « Croissance des paiements de Visa ce trimestre ? » : la croissance d'un trimestre ressemble à celle du précédent. On centre la courbe sur le dernier chiffre publié. | Rapports trimestriels (SEC EDGAR, gratuit) |
| 19 | `fed_taux_courts` | Décision de la Fed : les taux des bons du Trésor à 1-3 mois (FRED) disent combien de baisses les marchés financiers attendent. On compare aux prix Polymarket. | FRED (clé gratuite) |
| 20 | `rotten_tomatoes_omdb` | « Note Rotten Tomatoes du film ? » : passé 40 critiques, la note bouge très peu. OMDb donne la note actuelle ; on achète la tranche qui la contient. | OMDb (clé gratuite) |
| 21 | `vues_youtube` | « Nombre de vues de la bande-annonce de GTA VI en une semaine ? » : l'API YouTube donne le compteur ; on prolonge la courbe des premières heures. | YouTube Data API (clé gratuite) |
| 22 | `precurseurs_oscars` | Les prix des syndicats (acteurs, réalisateurs, producteurs) annoncent souvent les Oscars. On compte combien de ces prix chaque film a gagnés. | Wikipédia (API officielle) |
| 23 | `premarche_jetons` | « Valeur de Predict.fun un jour après son lancement ? » : les marchés « avant lancement » de Hyperliquid donnent déjà un prix. | Hyperliquid (API publique) |
| 24 | `blessures_nba` | La NBA publie un rapport officiel des blessés. Quand une vedette est déclarée absente, le prix du match met du temps à bouger : on achète l'adversaire. | Rapport officiel NBA (gratuit) |
| 25 | `compositions_football` | Les compositions officielles tombent environ 1 h avant le coup d'envoi. Si une vedette est sur le banc, on achète l'adversaire avant que le prix suive. | API-Football (clé gratuite, 100 appels/jour) |

## Ordre conseillé
1. **Tout de suite (données Polymarket seules, tests sur le passé possibles)** : 14, 1, 2, 9, 10, 11, 3, 4, 5.
2. **Avant le 25/10** : 15 et 16 (2e tour au Brésil ; sinon il faudra attendre la prochaine élection).
3. **Ensuite** : 7, 8, 12, 13, 17, 6, puis les sources avec clé (19, 20, 21, 25 : à proposer à Etienne).
4. **Plus tard** : 18, 22, 23, 24.
