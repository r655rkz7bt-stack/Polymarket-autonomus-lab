# 03/11/2026 (midi) : PortWatch « série trop courte » = erreur ArcGIS lue comme page vide (famille 3 : ce qui ne tourne plus)

**Constat** : `data.json` → `sources.etat.portwatch` = « indisponible : aucune série reçue (Ormuz et Bab el-Mandeb : série trop courte) » au cycle de 10 h 52 UTC.
**Mesure** : 6 appels de suite à la requête exacte de `PortWatchSource._series` : 3 réussissent (800 lignes, dernier jour 25/10), 3 rendent
HTTP 200 + `{"error": {"code": 400, "message": "Invalid URL"}}`, soit environ une fois sur deux. `parse_portwatch` lit ce corps comme 0 ligne, la série est
« trop courte », le détroit est sauté. Les stratégies de détroits (`detroits_tranches`, `detroits_non_normal`, `detroits_marche_log`) n'ont alors pas de série (0 opération pour les deux premières).
**Cause** : `sources/portwatch.py::_series` ne regardait pas le champ `error`. **Correctif** : `_page` réessaie jusqu'à 5 fois puis lève `SourceUnavailable`
(le mode dégradé existant s'applique). **Test** : `test_arcgis_invalid_url_error_with_http_200_is_retried_not_read_as_an_empty_series` (échoue sans le correctif).
**Contrôle** : `enquete.sources_indisponibles` (« à regarder ») liste toute source « indisponible » hors compte/clé absents et hors 404/410 (déjà GRAVE).
**Limite** : je n'ai pas mesuré depuis quand dure la panne (pas d'historique des statuts de sources dans les données publiées) ; la dernière date PortWatch (25/10) est celle d'une mise à jour du mardi normale.
Autres sources à « ok (0 observations) » (météo METAR/prévision, mlb, odds_api, inities) : déjà documentées (météo hors fenêtre, saison, clé absente).
