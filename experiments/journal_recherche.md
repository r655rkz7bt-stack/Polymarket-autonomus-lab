# Journal de recherche

Une entrée datée par session de recherche (routine « chercheur » ou session manuelle) :
ce qui a été lu, fait, testé, et ce qui reste ouvert. Les plus récentes en haut.

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
