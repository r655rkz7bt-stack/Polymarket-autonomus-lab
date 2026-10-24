# 24/10/2026 (minuit) : un contrôle qui criait pour rien, et ce que vaut l'arène « au hasard »

Famille du jour : 23 % 6 + 1 = **6 (« ce qui ne tourne plus »)**, puis les obligations de la feuille de mission et le contrôle `estimation_gonflee` (z −10,9).
Scripts : `experiments/enquetes/scripts/gonflee_par_famille_23_10.py`, `experiments/enquetes/scripts/tweets_ecart_23_10.py`.

## Obligations de la feuille de mission
- `apres_echeance` (22 gagnés pour 28,9), championne `nf_sport_patiente` (3 paris = 131 % du gain, le 18/10 = 234 %), `contrer_crypto_patiente` (5 pour 6,1) : causes déjà écrites les 22 et 23/10
  (achats après le coup d'envoi ; biais fixe et 3 paris ; billets à moins de 0,10 sans gain). Rien de neuf, non refaites.

## Famille 6 : ce qui ne tourne plus
- **`loterie_meteo` (météo en `zero_fees`, corrigée le 23/10 à 15 h 38)** : le cycle de 23 h 45 la montrait encore avec 377 marchés « famille de marchés exclue » sur 382. Vérifié que ce n'est **pas** un défaut :
  la liste de 382 à 450 marchés est celle de tous les marchés surveillés, dont 94 % ne sont pas de la météo ; les 5 à 12 marchés de température sont écartés pour « hors de la fenêtre de temps » (6 h avant la fin, échéances à 12 h UTC) et
  « hors de la plage de prix ». Preuve : sur 300 marchés de température réels (Gamma, tag 84) `market_family` rend `weather` pour les 94 marchés de température du jour, et `candidates()` en rend 30, tous dans la fenêtre à 8 h UTC
  (`_window_ok`). À confirmer en direct dans la matinée du 24/10 (6-12 h UTC) : un achat de `loterie_meteo`.
- Sources météo : le statut publié passe de « ok (0 observations) » à « meteo_metar ok (5 observations), meteo_prevision ok (3 observations) » : la correction de `STATION` fonctionne.
- Stratégies sans achat depuis plus de 36 h ou jamais : 25 actives, dont 17 jamais (cpi_tranches CPI le 11/11, jobs_favori_non le 6/11, kalshi_reference, social_sentiment (Gemini en pause), etc.) : toutes déjà connues (`muettes`, `jamais_retirer`).

## Défaut 1 : `estimation_perimee` signalait surtout des stratégies à modèle propre (6 constats sur 6 dans le rapport publié)
- **Constat** : le contrôle compare l'écart « estimation − prix payé » à l'écart médian de la stratégie + 8 points. Pour `naive_favorite`/`nf_*` (estimation = prix + biais fixe) c'est exact (écart interquartile 0,000 à 0,02,
  le 20/10 il a trouvé les carnets périmés). Pour un modèle qui calcule sa propre probabilité (tweets, mots, détroits, cotes, météo) l'écart varie d'un pari à l'autre **par construction** : écart interquartile de 0,04 à 0,25.
  Rapport publié (achats des 3 derniers jours) : 6 constats, tous de ce genre (compteur_tweets ×3, decroissance_temps, detroits_marche_log, mots_prononces). Sur toute la période des journaux : 16 stratégies signalées, dont 11 de ce genre (en plus : crypto_threshold_non, cotes_bookmakers, meteo_prevision ×2, choc_sans_nouvelle) ; les 5 autres sont `market_structure`, `nf_tennis*`, `nf_sport_patiente` et le principal.
- **Ce que valent ces grands écarts** (`experiments/tweets_fin_periode.md`, 189 périodes passées) : pour les tweets, les achats à écart < 0,10 perdent 4 %, ceux à 0,20-0,35 gagnent +29 % et ceux à ≥ 0,35 +25 % :
  le grand écart est le signal, pas une erreur. Le cas du 23/10 (CZ 40-59, estimé 0,81, payé 0,10, 33 minutes avant la fin) reste une valeur extrême à surveiller, pas une erreur de carnet démontrée.
- **Correctif** (`enquete.estimation_perimee`) : seuil = écart habituel + max(8 points, 3 × écart interquartile). Les stratégies à prix + biais fixe sont signalées comme avant ; un modèle à écart large ne l'est plus que pour un écart
  hors de son étendue habituelle. Rapport publié : 6 → 2 constats (les deux achats de CZ/tweets à 0,7 d'écart).
- **Test** : `tests/test_enquete.py::test_a_model_with_a_naturally_wide_gap_is_not_flagged_for_ordinary_spread` (une stratégie à écarts de 0,01 à 0,30 n'est pas signalée pour 0,30 ; une stratégie à biais fixe l'est pour un 0,14 ; l'écart de 0,71 est signalé).

## Défaut 2 (mesure de référence) : l'arène entière perd 3,8 % par mise hors frais, au hasard près de −2,4 écarts-types
`estimation_gonflee` (z −10,9 contre les estimations, 1 164 gagnés pour 1 310 annoncés) : **où se loge l'écart ?** (1 721 jetons distincts, 59 509 € misés).
- Contre les **prix payés** : 1 165 gagnés pour 1 207 attendus (z −2,8) ; gain −2 605 € (−4,4 %), dont 340 € de frais ; **hors frais −2 264 € (−3,8 %) pour un écart-type du hasard de ±945 €**.
  Autrement dit : un pari « moyen » de l'arène, tel que les stratégies le choisissent, perd la moitié de son écart d'achat (demi-écart) plus un peu d'adverse sélection. **Toute stratégie doit battre −3,8 %, pas 0.**
- Par famille (gagnés / annoncés / prix) : `nf_sport` 360 / 382 / 362 (z prix −0,3), `nf_tennis` 161 / 168 / 161, `meteo_prevision` 56 / 83,5 / 61 (z estimation −7,0 : modèle trop sûr, mais mal calibré seulement contre ses propres chiffres),
  `cotes_bookmakers` 3 / 9,7 / 5,3 (−368 €), `news_momentum` 61 / 73 / 68 (corrigé le 23/10), `apres_echeance` 148 / 154,6 / 151 (éteinte). Les écarts « annoncés − prix » sont partout de 2 à 4 points sur des favoris : **les estimations de
  la famille `naive_favorite` ne se réalisent pas** (biais fixe, déjà tracé le 22/10), le reste est de la variance.
- Par tranche de prix : toutes négatives en z contre les estimations (−5,0 à 0,90-0,95, −4,8 à 0,95+), contre les prix entre −0,2 et −1,6 : pas de tranche qui porte tout le déficit.
- Par jour d'ouverture : 18/10 −840 €, 19/10 −480 €, 17/10 −463 € (avant la copie fidèle, mises géantes) ; 21/10 +241 € ; pas de tendance à la baisse récente.
- `meteo_prevision` (154 achats, tous du 16 au 18/10 avant les pannes du 20/10) : estimations de 0,81 en moyenne pour 54 % de gagnés ; déjà écartée pour le rendement aux prix payés (−6 %, `meteo_backtest.md`). Rien de neuf.

Pas de correctif de code pour le défaut 2 : c'est une mesure de référence, notée ici pour que les comparaisons d'arène se fassent contre **−3,8 % hors frais**.

## Deuxième contrôle à la main : famille 4 « le filtre ne filtre pas » (`experiments/enquetes/scripts/filtres_prix_24_10.py`)
Chaque achat des 3 derniers jours (2 013 achats, 66 stratégies à plage de prix `min_ask`/`max_ask`/`min_price`) comparé à la plage de sa stratégie (premier niveau consommé et prix moyen, tolérance d'un cran) :
**39 achats hors plage (1,9 %, les mêmes paris comptés dans plusieurs fantômes)**, tous de 1 à 2 crans sous la borne basse (tennis à 0,78-0,79 pour une plage 0,80-0,95 : `nf_tennis*` 29 ; `mots_prononces_patiente` à 0,29 pour un plancher de 0,30 ; `outsider_sport_patiente` à 0,07 pour 0,08 ;
`contrer_crypto_patiente` à 0,039 pour 0,05) et un à 0,9566 pour un plafond de 0,95 (prix moyen de deux niveaux). Aucun achat éloigné de la plage de plus de 0,03. Cause probable : le filtre lit le prix du scan (milieu Gamma, jusqu'à un cycle de retard),
l'ordre est placé sur le carnet du moment (`candidates` accepte déjà `min_ask − 0,02`). Effet mesurable : nul (1,9 % des achats, à deux crans de la plage testée). **Aucun correctif**, noté pour le cas où une fille reposerait sur une plage fine (les filles 0,875-0,90 ont `prix_final`, déjà corrigé le 21/10).
