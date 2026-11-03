# 03/11/2026 (après-midi) : PortWatch « Token Required » = la série quotidienne des détroits n'est plus publique (famille 4/3 : ce qui ne tourne plus)

**Constat** : `data.json` → `sources.etat.portwatch` = « indisponible : erreur ArcGIS répétée (Token Required) » (Ormuz et Bab el-Mandeb) au cycle de 15 h 40 UTC.
**Mesure** (4 appels espacés de 20 s, requête exacte de `PortWatchSource._series`, puis la couche seule sans filtre) : HTTP 200 + `{"error": {"code": 499, "message": "Token Required"}}` à CHAQUE appel,
y compris `Daily_Chokepoints_Data/FeatureServer?f=json`. À 11 h, le même service répondait encore une fois sur deux (« Invalid URL », fiche du midi) : c'était le début du retrait, pas un caprice du serveur.
**Autres couches du même compte ArcGIS** : `PortWatch_chokepoints_database` (fiche des détroits, sans les passages), `Daily_Trade_Data_TEST4` / `Daily_Trade_Data_WLD` / `Daily_Regional_Data`
(escales de ports et pays, aucun détroit : « Hormuz » rend 0 ligne) restent publiques ; `Daily_Chokepoints_Data_V2` n'existe pas (« Invalid URL »). Aucune autre adresse publique trouvée
(recherche hub.arcgis.com : rien d'IMF pour les détroits).
**Conséquence** : `detroits_tranches`, `detroits_non_normal`, `detroits_marche_log` n'ont plus de série (refus « aucun marché vu n'a la référence »), et aucun règlement hebdomadaire PortWatch
ne peut plus être lu par nous. Le suivi AIS (`hormuz.data-tracking.net`) reste une donnée d'appoint (corrélation 0,1 à 0,3 avec PortWatch : jamais un arbitre).
**Ce que je n'ai PAS fait** : générer un jeton anonyme ou contourner l'accès (interdit n° 7). Le code sait déjà dire « indisponible » (correctif du midi) : le contrôle `sources_indisponibles` l'affiche, pas de défaut de code à corriger.
**À faire si l'accès revient ou si le FMI publie un CSV** : brancher la nouvelle adresse dans `sources/portwatch.py::URL`. En attendant, les trois fantômes de détroits ne peuvent rien apprendre (ni gain ni perte) ; ils ne coûtent rien au principal.
**Autre vérification** : source `inities` « ok (0 prix relevés) » : essai en direct avec la Data API v2, 19 événements à initiés ouverts, 119 à 454 échanges lus par événement (Spotify, Billboard, Miss Universe) : la source marche, il n'y a simplement aucune grappe de comptes neufs en ce moment.
