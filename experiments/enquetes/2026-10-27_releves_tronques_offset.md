# 27/10/2026 (soir) : les relevés de matchs du 23 au 26/10 étaient tronqués en silence (Gamma refuse `offset` au-delà de ≈ 2 100)

Famille 3/4 (tirage, comparaisons faussées) trouvée en préparant la piste « tennis : Total Sets O/U 2.5 » : mon premier relevé ne rendait que 1 673 matchs ATP, tous de septembre-octobre,
alors que Gamma compte 10 971 matchs ATP réglés depuis le 15/01. Script : `experiments/totaux_sports/scripts/releve_complet.py`.

## Constat
- `GET /events?series_id=…&closed=true&order=endDate&ascending=false&limit=100&offset=N` répond **422 `offset too large, use /events/keyset for deeper pagination`** dès N ≈ 2 100
  (2 000 passe, 4 000 non ; le texte de ROUTINE_CHERCHEUR.md le disait déjà pour `/events` mais les scripts de relevé n'en tenaient pas compte).
- Tous les relevés écrits sur le modèle `while off < 30000: b = get(...); if not isinstance(b, list) or not b: break` prennent cette réponse (un dictionnaire d'erreur) pour la **fin de la liste** :
  ils ne lisent que les ≈ 2 100 événements les plus récents (par date de fin Gamma) de chaque série. 30 scripts d'`experiments/` paginent ainsi (liste dans `tests/test_releves_gamma.py`).
- Ampleur sur `totaux_sports.md` (26/10) : relevé par curseur des mêmes 37 ligues, mêmes types de marchés : **fenêtre février-août : 36 789 événements avec totaux, le relevé du 26/10 en avait 11 024 (30 %)** ;
  **fenêtre août-octobre : 23 858 contre 10 833 (45 %)**. Avec échanges réels : 18 646 événements contre 5 879 (hors échantillon), 6 237 contre 4 614 (découverte).
  Les séries absentes ou presque de la fenêtre février-août : MLB (2 001 événements avec totaux, 939 paris à 3 h), tennis ITF / ATP / WTA (7 795 / 6 337 / 3 258 événements), CS2 (5 867), NFL, Valorant.
- Autres études bâties sur la même boucle (à rouvrir si elles servent encore) : `ecarts_sports`, `btts`, `sous_marches_football` (surtout les séries de plus de 2 100 événements), `avant_match_50_50`, `apres_fin_match`, `tennis*`, `saison_sport`, `primaires`, `seismes`, `courbe_de_risque`, `elections_non`, `ufc_coherence`.
  Le défaut ne fausse pas le signe d'un résultat (la coupure se fait sur la date de fin, pas sur l'issue) : il réduit l'échantillon et retire les séries les plus fournies.

## Cause
`while off < 30000 … if not isinstance(b, list) or not b: break` (modèle copié de `experiments/apres_fin_match/scripts/releve.py`, 23/10) : une erreur 422 sort de la boucle sans bruit.
`bo3_coherence/releve_evenements.py` lisait déjà `/events/keyset` (« au-delà de 5 000 » le 23/10 : la limite a baissé à ≈ 2 100 depuis).

## Correctif
- `experiments/totaux_sports/scripts/releve_complet.py` : `/events/keyset` (`order=endDate&ascending=false`, `after_cursor`), 83 129 événements des 37 ligues depuis le 15/01 en 3 minutes ; arrêt après 1 500 événements d'avant la coupure.
- Test `tests/test_releves_gamma.py` : tout nouveau script d'`experiments/` qui pagine `/events` par `offset` fait échouer les tests (les 30 anciens sont listés ; le test vérifie aussi qu'il reconnaît le script du 26/10).
- Astuce ajoutée à `docs/ROUTINE_CHERCHEUR.md`.

## Ce que ça change pour les conclusions (voir `experiments/totaux_sports_complet.md`)
Voir le compte rendu de recherche : les totaux de sport sont rejoués sur le relevé complet.

## Autres vérifications du même passage
- `toucher_metaux` « aucune raison notée » : pas un défaut de calendrier mais de journal : la stratégie ne notait aucune abstention quand aucune barre n'avait de prix rattaché (la semaine du 26/10 est née le 23/10 à 22 h, avant le premier relevé du 24/10 : le rattachement exige que le journal couvre le marché depuis sa création, `matieres.COUVERTURE_H`). Elle écrit maintenant la raison (test `test_strategy_says_why_when_no_bar_is_attached`). Les barres de la semaine du 02/11 naîtront vers le 30/10 à 22 h UTC.
- `compteur_tweets` OUI « 200+ posts de Trump du 27/10 au 03/11 » à 0,417 pour une estimation de 0,779 (42 €) : hypothèse « la moyenne des 168 h / 336 h est gonflée par des journées de rafale (122 posts le 22/10, 77 le 20/10) » **testée et réfutée** (`experiments/rafales_tweets/scripts/biais_rythme.py` : 34 semaines, total prédit par la formule de production contre réalisé, biais log +0,003, 16 sur 34 sur-prédites ; après une journée à plus de 3 × la médiane +0,10 à +0,17, 10-11 sur 16-18 sur-prédites : un léger excès, pas un défaut ; les moyennes robustes sous-prédisent de 10 à 20 %). Se règle le 03/11.
- `contrer_crypto_patiente` (146 paris, z +2,0 par les prix, −28 € en euros) à mise fixe : +20,9 % par mise (t +1,07), côté NON +43,8 % (56 paris), côté OUI +6,6 % ; la perte en euros vient de quelques grosses mises (−67 € de règlements le 23/10) : indice faible, rien à corriger (`enquetes/scripts/contrer_crypto_27_10.py`).
- `copie_absente` (`moins_de_cartes`, 0 sur 50) : le fantôme n'a acheté qu'une fois depuis le correctif de 16 h 34 (16 h 04, avant) ; le plancher de copie n'a pas encore pu servir. Contrôle à refaire demain.
