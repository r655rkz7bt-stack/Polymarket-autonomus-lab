# Scores Rotten Tomatoes : le compte exact des critiques contre le seuil (piste n° 56, 14/11/2026) — EXPÉRIENCE

Passage du chercheur du 14/11/2026, 11 h UTC. Idée neuve (avantage de RÈGLE et de source) : « Will "<film>" score at least <N> on the
Rotten Tomatoes Tomatometer? » (étiquette Gamma `101453`, 5 à 8 seuils par film, frais `culture_fees`) se règle sur le Tomatometer
« All Critics » **affiché** à 10 h (heure de l'Est) le dimanche ou le lundi après la sortie. Le pourcentage affiché est un ARRONDI ;
la page du film donne aussi le compte exact (`likedCount`, `notLikedCount` dans le JSON `criticsScore`).

## Source et règles lues
- `robots.txt` de rottentomatoes.com lu AVANT tout appel par script : `/m/<film>` permis (interdits : `/m/*/pictures`, `/search`,
  pages de compte ; `/napi/` interdit seulement à Google-Extended, mais déjà refusé par le serveur le 10/11 : jamais appelé).
- Piège des homonymes : `/m/ebenezer` est un film de **1997**, `/m/how_to_rob_a_bank` un film de **2008** (le bon :
  `how_to_rob_a_bank_2026`). On essaie `<titre>_<année>` puis `<titre>`, et on n'accepte qu'une page dont la date de sortie
  (`dateCreated` du JSON-LD) tombe entre 150 jours avant et 60 jours après aujourd'hui. La bonne page d'« Ebenezer » est `ebenezer_2026`
  (62/117, 53 %).

## Photo du 14/11, 11 h UTC (règlement lundi 16/11, 15 h UTC, ≈ 52 h)

| Film | Compte | Affiché | Seuil | Marché (acheteur / vendeur du OUI) | Simulation (part des nouvelles 0,65-0,75, 2-25 critiques) |
|---|---|---|---|---|---|
| Victorian Psycho | 62 / 83 (74,70 %) | 75 % | 75+ | 0,37 / 0,43 | 0,28-0,58 (0,43 au centre) |
| Victorian Psycho | | | 73+ | 0,39 / 0,84 | 0,61-0,96 (0,84) |
| Ghost Soldier | 5 / 14 | 36 % | 30+ / 40+ / 50+ | 0,43/0,86 · 0,07/0,78 · 0,01/0,82 | 0,65-0,91 · 0,19-0,52 · 0,02-0,14 |
| How to Rob a Bank (2026) | 28 / 85 | 33 % | 45+ et plus | 0,002 / 0,008 | ≈ 0 |
| Ebenezer (2026) | 62 / 117 | 53 % | 50+ / 55+ | 0,56/0,94 · 0,067/0,93 | 0,91-0,997 · 0,04-0,13 |
| I Play Rocky (sortie LIMITÉE le 06/11, réglé le 23/11) | 115 / 133 | 86 % | 83+ / 85+ | 0,59/0,82 · 0,38/0,81 | 0,96-0,999 · 0,86-0,97 **sans garde-fou** |

Victorian Psycho avait 78 % sur 50 critiques quelques jours plus tôt (journal du 10/11) : les 33 critiques suivantes n'étaient
positives qu'à 70 % (23 sur 33). **Le prix sait sur le seuil liquide** (75+ à 0,40 pour ≈ 0,42) ; aucun achat possible aujourd'hui
au-delà de l'incertitude. Les carnets des autres seuils sont très larges (écarts de 0,4 à 0,8) : un vendeur pressé peut s'y tromper.

## Le piège trouvé au cycle local : la sortie limitée (« I Play Rocky »)
Premier cycle local (11 h 11 UTC) : la première version **a acheté « I Play Rocky 83+ » OUI à 0,80** (24,45 parts, chance 0,973,
borne basse 0,933). Le film n'est sorti qu'en salles LIMITÉES le 06/11 (page : « Release Date (Theaters) Nov 6, 2026, Limited ») ;
le marché se règle le 23/11, après la sortie large, quand une vague de critiques arrive. À 75 % de critiques positives pour 80
nouvelles, le score tomberait à (115 + 60) / 213 = 82,2 % : sous 83. Le marché (≈ 0,6-0,7) le savait, le rythme a priori (0,03 critique
par heure pour un film de 8 jours) non. Deux garde-fous avant toute mise en service :
- **sortie limitée → aucune chance** (`salles == "Limited"`, lu sur la page) ;
- **glissement de −5 points** de la part positive des critiques à venir (Victorian Psycho : 78 % sur les 50 premières, 70 % sur les
  33 suivantes) ; avec lui, « 75+ » vaut 0,41-0,48 (marché 0,40) et « 73+ » 0,71-0,91 (marché 0,39/0,84).
Cycles locaux suivants (11 h 15, source relue) : 22 seuils chiffrés, « I Play Rocky » exclu, 0 achat (17 « hors plage ou carnet vide », 5 « avantage net insuffisant ») ; la position de test reste dans le journal local, ignoré par Git.

## Pourquoi une expérience et pas un test
Les comptes de critiques ne sont archivés nulle part gratuitement (l'API interne est refusée, Wayback est bloqué depuis la routine) :
seuls les pourcentages finaux et les prix Polymarket le sont. Un test aux prix passés demanderait le compte à chaque instant. Le
fantôme `rt_compte_critiques` (Kelly entier sur la borne basse, 4 % au plus par pari, écart minimal 0,06 après incertitude 0,04)
achète seulement quand le vendeur demande nettement moins que la simulation, et le journal `rt:histo` (une ligne par nouveau compte)
mesurera le rythme réel des critiques pour étalonner l'a priori (0,4 / 0,12 / 0,03 critique par heure à ≤ 3, ≤ 10, > 10 jours de la
sortie) et la part positive des critiques tardives.

## Ce qu'une perte apprendrait
- rythme a priori faux (trop de critiques simulées : la part bouge plus que prévu) ;
- critiques tardives plus froides que la Bêta (la dérive de Victorian Psycho : 78 % → 75 %) ;
- les vendeurs qui nous servent savent quelque chose (critiques sous embargo, agrégation en retard de quelques heures).

## Code
`src/polymarket_agent/rotten_tomatoes.py` (source `rotten_tomatoes`, toutes les 60 min ; `attach_rt`), classe `RtCompteCritiques`,
`tests/test_rotten_tomatoes.py` (vraies pages du 14/11, extraits dans `tests/data/rt_2026-11-14.json`).
