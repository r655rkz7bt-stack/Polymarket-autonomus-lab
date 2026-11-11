# 11/11/2026, passage de 11 h : « catalogue en retard » sur des séismes d'octobre (faux constat) ; famille 6, ce qui ne tourne plus

## 1. Constat « à regarder » `catalogue_en_retard` (enquête automatique de 10 h 42)

**Constat.** 4 achats de `seismes_marche` v2 (09/11 14 h 41, 09/11 20 h 07, 10/11 12 h 07, 10/11 19 h 32) signalés « faits avant que
notre catalogue USGS ne voie un séisme déjà arrivé » : « séisme 5.5 de 08/10 06:46 lu seulement à 06:45 ». Un séisme du 8 OCTOBRE lu
le 11/11 à 06 h 45.

**Cause.** `seismes.first_seen` (ajouté au passage de 6 h) donnait `vu = maintenant` à tout séisme absent de l'ancien relevé OU présent
sans `vu`. Au premier relevé après la mise en service (11/11 vers 06 h 45), les ~230 séismes déjà au relevé (10 jours d'USGS, 3 d'EMSC)
ont tous reçu `vu = 06 h 45` ; `enquete.catalogue_en_retard` (achat entre l'heure d'origine et `vu`) voyait alors tous les achats
des 3 derniers jours comme « en retard ». Même faute pour la mesure prévue vers le 18/11 (retards comparés USGS / EMSC) : les reprises
auraient donné des « retards » d'un mois.

**Ampleur.** Aucun euro : instrument de mesure seulement (contrôle de l'enquête et journal `vu`). Sans correctif, le constat aurait
reparu à chaque passage pendant 3 jours, et la comparaison USGS / EMSC aurait été fausse.

**Correctifs.** (1) `first_seen` : un séisme connu sans `vu` (relevé d'avant le champ), ou tout le relevé quand il n'y a pas d'ancien
relevé, reste sans `vu` (première lecture inconnue). (2) `catalogue_en_retard` ignore un `vu` plus de 6 h après l'heure d'origine (reprise,
pas retard : l'USGS publie en 10-30 min) — nécessaire aussi pour les `vu` de 06 h 45 déjà écrits dans la base. Tests :
`test_first_seen_does_not_date_quakes_known_before_the_field_existed`, `test_catalogue_en_retard_ignores_quakes_dated_by_the_first_sighting_run`
(cas réel du rapport), collecteur mis à jour. Après correctif, l'enquête locale ne montre plus le constat.
**Pour la comparaison du 18/11** : ne compter que les séismes dont `vu − t` < 6 h.

## 2. Contrôle à la main, famille 6 (ce qui ne tourne plus)

- **Positions ouvertes des 10 fantômes v2 relues sur Gamma** (`scripts/positions_v2_11_11.py`) : 93 positions ; aucune sur un marché
  clos non réglé. Échéance dépassée : les deux marchés « semaine 2-8/11 » de `seismes_marche` (fin 09/11 04 h 59, pas encore réglés par
  UMA, 54 h) et 5 marchés de l'élection néo-zélandaise (`favori_politique_quasi_certain`, résultats officiels le 27/11, déjà connu).
- **Abstentions du dernier cycle** (`published/data.json`) : `convictions_claude` et `suivre_inities` muettes voulues ;
  `lid_agenda` « agenda du jour pas encore publié » pour les marchés des jours suivants (normal) ; `seismes_pays` « carnet périmé »
  (proposition en attente d'Etienne).
- **Sources** : `appstore` indisponible (ReadTimeout sur rss.applemarketingtools.com) — aucune stratégie v2 ne la lit ; `meteo_metar`
  « 0 observations » — aucune stratégie météo en v2. Rien à corriger.
