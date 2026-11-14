# 14/11/2026 (passage de 16 h) : adresses interdites aux robots dans le code et dans mes relevés

Passage du chercheur du 14/11/2026, 15 h 54 UTC. Jour 14 → famille 3 (faite à 6 h), familles 4 et 2 faites à 11 h : ici
familles **3** (première mise d'une stratégie née le matin), **6** (stratégies qui n'achètent plus) puis un contrôle de la règle n° 7
(scraping) né d'une erreur de ma part.

## 1. Constats « à regarder » de l'enquête automatique

Tous déjà menés au bout par les passages précédents : `taux_tresor_barriere` « estimé 0,46 payé 0,088 » (désaccord voulu, 13/11
nuit), `suivre_inities` muette (gardée à la demande d'Etienne), `rougeole_compteur` et `el_nino_cpc` (« avantage net insuffisant » :
le marché est juste), `compteur_truth` (garde « rythmes en désaccord », 14/11 midi), positions néo-zélandaises (résultats le 27/11),
5 marchés 50-50 (connus).

## 2. Famille 3 : la première mise de `rt_compte_critiques` (15 h 18)

« Will "Ebenezer" score at least 55 on the Rotten Tomatoes Tomatometer? » NON, 5 parts à 0,76 (chance du NON calculée 0,88, borne
basse 0,84). Relu à la source à 15 h 55 : 62 critiques positives sur 117 = 52,99 %, affiché 53 % ; pour afficher 55 il faut ≥ 54,5 %,
soit au moins 4 nouvelles critiques toutes positives d'ici lundi 16/11 15 h UTC (41 h). Aucune critique nouvelle depuis 11 h (déjà
62/117). Règle relue (« displayed All Critics Tomatometer », 10 h ET le 16/11), film en sortie large (pas le cas Rocky). **Conforme.**

## 3. Famille 6 : `taux_tresor_barriere` n'a rien acheté la nuit du 14/11

17 achats la nuit du 13/11, aucun la nuit du 14/11 (00-12 h UTC), alors qu'aux prix de 16 h, recalculée avec les clôtures du 13/11,
la chance dépasse le prix vendeur de 0,09 à 0,30 sur 12 seuils. Les 12 sont dans des événements déjà pleins (plafond de 2 seuils par
événement, `_held_per_event` du 13/11 ; 3 événements ont 3 achats d'avant le correctif) ou déjà en position (« 10 ans ≥ 5,50 % »
détenu dans l'événement 79104). **Pas un défaut** : le plafond fait ce qu'on lui demande. `taux_immobilier_barriere` et `pluie_hk`
« aucun marché vu n'a la référence » à 16 h : voulu (nuit seulement ; journal des heures de Hong Kong complet à partir du 15/11 HKT).

## 4. Défaut trouvé : des pages interdites aux robots (règle n° 7)

### Comment je l'ai trouvé
En étudiant « Where will 2026 rank among the hottest years on record? » et le prix des œufs, j'ai lu deux fois un `robots.txt` **dans
la même commande** que le téléchargement : `data.giss.nasa.gov/gistemp/graphs/…/graph.txt` (interdit), `api.bls.gov` (`Disallow: /`,
et la réponse était un refus de quota). Puis, en écrivant l'outil `scripts/robots_ok.py`, il m'a dit que
`gistemp/tabledata_v4/GLB.Ts+dSST.txt`, que je croyais permis, l'est aussi : je lisais le `robots.txt` avec `head` et la ligne
`Disallow: /gistemp/tabledata_v4/` était plus bas. Fichiers supprimés, valeurs gardées seulement pour la note du journal.

### Audit des 96 adresses lues par `src/polymarket_agent` (62 sites, outil `robots_ok`)

| Adresse | robots.txt | Jugement |
|---|---|---|
| `www.weather.gov.hk/cis/dailyExtract/…` (`pluie_hk`, depuis ce matin) | `Disallow: /cis/` | **défaut corrigé** : remplacé par le bulletin RYES du portail de données ouvertes (`data.weather.gov.hk`, fait pour les programmes), un appel par jour manquant |
| `api.open-meteo.com`, `ensemble-api.…`, `previous-runs-api.…` (météo, `pluie_hk`) | `Disallow: /` | API documentée et gratuite (usage non commercial, quota par jour), faite pour être appelée par des programmes ; le `Disallow: /` écarte les moteurs de recherche. Gardé, **à confirmer par Etienne** |
| `news.google.com/rss/search` (`google_news`, `inities`) | `Disallow: /` sauf pages d'accueil et sujets | flux RSS fait pour des lecteurs automatiques, mais la recherche n'est pas dans les `Allow`. **Zone grise, décision d'Etienne** |
| `X.com` | interdit | modèle d'adresse d'un module éteint (X payant) : rien n'est appelé |

« pas de robots.txt lisible » (page d'erreur ou 404) : Coinbase, GDELT, Guardian (API à clé gratuite), portail de Hong Kong (redirige
vers `www.hko.gov.hk`), Launch Library, Factbase, PortWatch (ArcGIS), CDC, SPC de la NOAA : rien n'y interdit l'accès.

Recherche (hors production) : le test GISTEMP du 11/11 (`experiments/temperature_mondiale.md`) a été fait sur `GLB.Ts+dSST.txt`,
interdit aux robots ; ce fichier ne doit plus être relu par script.

### Correctif, tests, contrôle
- `pluie_hk.fetch_pluie_hk(http, now, connus)` : jours finis par RYES (`date=AAAAMMJJ` = jour observé), jours déjà connus du relevé
  précédent repris sans appel (`data_collector`), bulletin pas encore publié (avant 00 h 15 HKT, réponse texte) → jour absent au lieu
  d'une source en panne (avant : `SourceUnavailable` faisait tomber tout le relevé), « trace » en minuscules (bulletin du 06/11) = 0.
  Vérifié en direct : 1er-13/11 = 11,1 mm, la même somme que le Daily Extract + RYES de ce matin.
- Tests : `tests/test_pluie_hk.py` (le faux client refuse toute adresse `/cis/`, jours connus non redemandés, bulletin absent,
  « trace ») ; `tests/test_robots_ok.py` (cas réels NASA et BLS, et **`INTERDITS_CONNUS`** : la suite échoue si le code de
  production cite un chemin déjà trouvé interdit).
- Outil : `scripts/robots_ok.py <url>…` (à lancer SEUL, avant le premier appel) ; l'astuce de `docs/ROUTINE_CHERCHEUR.md` le dit.
- Pas de contrôle dans `enquete.py` : la règle se vérifie dans le code, pas dans les journaux ; le test de la suite fait ce travail.

## Ce qui reste ouvert
Décision d'Etienne sur Open-Meteo et la recherche de Google Actualités (robots.txt `Disallow: /` sur des API publiques gratuites).
