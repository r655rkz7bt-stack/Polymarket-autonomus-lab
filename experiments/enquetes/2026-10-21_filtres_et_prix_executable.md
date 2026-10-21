# 21/10/2026 (soir) : le filtre ne filtre pas, et le prix historique n'est pas un prix

Famille 4 (« le filtre ne filtre pas », jour 21 : 21 mod 6 + 1) en contrôle à la main, plus un défaut de la
famille 3 trouvé en menant la recherche (mentions). Aucune « enquête obligatoire » dans la feuille de mission.

## 1. Constat : la plage de prix des filles n'était contrôlée nulle part
- Le contrôle `filtre_prix` ne lisait que `min_ask` / `max_ask` des paramètres. Les `filtres.prix_min /
  prix_max` des filles (`nf_sport_patiente_prix_haut`, `_prix_moyen`, `_prix_850_875`…) n'étaient jamais
  vérifiés.
- Relu à la main sur les 1 279 opérations clôturées de toutes les stratégies à plage de prix : **13 achats hors plage**
  (> 3 centimes), 9 gagnés, **+20,7 €** ; surtout les filles « patientes » : `nf_sport_patiente_prix_haut`
  (0,875-0,95) a acheté « mellren » à 0,783 (−66 €) et Tampa Bay Rays à 0,823 ; `_prix_moyen` (0,80-0,875)
  « GenOne » à 0,760 (−28 €) ; `_prix_850_875` Sloane Stephens et Moerani Bouzige à 0,84. La championne
  elle-même : 3 achats à 0,72-0,77 (+62 €).
- **Cause** : `Filtered` filtre le prix du vendeur (`p.max_price` de la proposition), puis `PatientOrders`,
  empilé AU-DESSUS (`strategy_engine.load_strategies`), pose l'ordre 1 cran au-dessus du meilleur acheteur,
  parfois 5 à 10 centimes plus bas. Une fille « prix payé 0,875-0,90 » n'achète donc pas ce prix-là, et sa
  comparaison avec la tranche de `pareto.md` (qui découpe sur le prix PAYÉ) n'a pas de sens.
- **Correctif** : filtre `prix_final: true` (avec `limit_ticks`) → le mode patient passe DANS la fille et le
  prix est lu sur l'ordre posé. Les trois filles créées ce soir l'utilisent ; les anciennes ne sont pas
  modifiées (leur journal resterait incomparable). Test : `test_favori.py::
  test_price_filter_of_a_patient_daughter_reads_the_posted_order_price`.
- **Contrôles** : `enquete.filtre_prix` lit maintenant aussi `filtres.prix_min / prix_max` ; nouveau contrôle
  `filtre_delai` (fenêtres `echeance_*`, `heures_*`, `heure_utc` des filles, achats au comptant). Tests :
  `test_enquete.py::test_daughter_price_filter_is_audited_like_the_strategy_range` et
  `::test_time_window_filters_are_audited_for_immediate_buys_only`.

## 2. Ce qui a été vérifié et qui est correct
- `echeance_min/max` : tous les achats au comptant avec `horizon_hours` sont dans la fenêtre (0 hors plage).
- `heures_min/max` (coup d'envoi) : cohérent avec `depuis_coup_d_envoi_h` (signe opposé) pour les achats
  qui portent le champ (une centaine d'achats ; le champ n'existe que depuis le 20/10 soir) ; `nf_tennis_debut_match` :
  14 achats sur 14 entre 0,26 et 0,60 h après le coup d'envoi.
- `heure_utc` : 5 achats « hors heure » sur 50 environ, tous des ordres posés servis plus tard que la
  décision (l'heure du journal est celle du service, pas de la décision). Pas un défaut ; le contrôle les ignore.

## 3. Défaut de la famille 3, trouvé en recherche : le prix historique des mentions
Le test du 20/10 sur les mentions (+29 % à +45 % pour « the announcers » et « anyone ») lisait le prix horaire
du CLOB. Refait avec 3 555 marchés : +31 % au prix horaire (t +6,8), **−6,7 % aux prix des vrais échanges**.
715 « prix » sont à exactement 0,50 (carnets vides). Détail : `experiments/mentions_annonceurs.md`. Même défaut
que la météo du 16/10 : **tout test sur un marché peu liquide doit se refaire aux prix des vrais échanges**
(`idea_test.taker_cost`) avant d'être cru. La conclusion du 20/10 sur ces deux orateurs est donc retirée.

## Reste ouvert
- Les deux copies « exécution partielle » du principal (Mannarino, Lynn Vision : le principal a la même
  taille que le fantôme alors qu'il ne devrait en copier qu'une part) : non creusées ce soir.
- `mots_prononces` (mère) joue peut-être encore des annonceurs Coupe du monde : à suivre.
