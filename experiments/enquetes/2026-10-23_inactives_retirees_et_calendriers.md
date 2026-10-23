# Stratégies retirées pour « inactivité » avant leur premier jour utile (23/10/2026, passage de l'après-midi)

Famille du jour : 6, « ce qui ne tourne plus » (jour 23 mod 6 = 5, + 1), puis famille 1 (le principal).

## Constat
- Le ménage de l'arène (`config/promotion.yaml` → `retirer_inactives_apres_jours: 3`, filles : 2 jours ; `arena.retire_inactive` /
  `retire_daughters`) retire **définitivement** (événement ELIMINATION signé, la stratégie n'est plus jouée) toute stratégie sans
  opération ni position. 13 retraits « inactive » depuis le 18/10, dont **10 sur les deux derniers jours** :
  `cotes_tennis` (22/10), `crypto_threshold_24_72h` (22/10), `mots_prononces_nfl` (23/10 05 h 21), `coherence_match`, `implication_politique`,
  `paire_oui_non`, `marches_jumeaux` (23/10 11 h 25), `kalshi_reference`, `futurs_bookmakers`, `football_trois_issues` (23/10 12 h 01).
- Trois sortes de silence très différentes :
  1. **Rareté** : les quatre arbitrages (cohérence, paire OUI/NON, jumeaux, implication) n'achètent que s'il existe un écart après
     frais ; « aucun écart en 3 jours » est le résultat attendu d'un marché efficace, pas une preuve que la stratégie ne sert à rien
     (`echelle_dates` : 163 paires cohérentes sans écart au dernier cycle).
  2. **Calendrier** : `mots_prononces_nfl` (mots de matchs NFL) retirée après 2 jours, entre le match du jeudi soir et ceux du
     dimanche ; et **cinq stratégies vivantes allaient l'être avant leur premier jour utile** : `cpi_tranches` (CPI le 11/11),
     `jobs_favori_non` (emploi le 6/11), `statu_quo_ia` (classements d'IA, ≥ 12 jours), `saison_non` (fenêtre de 10 à 18 jours avant la fin
     d'un marché de saison : seul « PGL Masters Bucharest » finit dans ce créneau, à 9,5 jours), `non_aux_drames` (OUI à 2-15 % sur 30 à 120 jours).
     Ce sont justement des pistes **testées sur le passé** (`cpi_nowcast.md`, `emploi_nfp.md`, `saison_sport.md`, `pistes_crypto_elections_drames.md`).
  3. **Source** : `cotes_tennis`, `football_trois_issues` dépendent du budget de cotes (crédits dépensés à midi jusqu'au 22/10 au soir,
     voir `2026-10-22_muettes_budget_cotes.md`) : silence dû à un défaut déjà corrigé, et clé absente hors production.
- Effet pour l'enquête : le contrôle `muettes` listait ces 11 retirées comme « muettes » à vie (bruit), et rien ne disait qu'elles avaient été
  retirées sans jamais avoir vu un candidat.

## Cause
`arena.retire_inactive` / `retire_daughters` ne regardent que « zéro opération, zéro position, N jours » ; seule la tenue de marché était épargnée
(`jamais_retirer: [market_maker]`). Aucun calendrier, aucune rareté, aucune raison d'abstention n'entre dans la décision.

## Correctif (config libre, hors noyau)
- `config/promotion.yaml` → `jamais_retirer` : + `cpi_tranches`, `jobs_favori_non`, `statu_quo_ia`, `saison_non`, `non_aux_drames`,
  `detroits_tranches`, `mots_prononces_nfl` (elles restent soumises à « perdante » et à l'élimination hebdomadaire).
- `mots_prononces_nfl` passe en version 1.1.0 (nouveau portefeuille : l'ancien est éteint pour toujours) ; les arbitrages, `kalshi_reference` et
  les deux stratégies de cotes **ne sont pas relancés** : leur silence est un résultat (pas d'écart) ou dépend de la clé en production.
- Contrôle `retraits_inactifs` (`enquete.py`) : liste les stratégies retirées pour inactivité **sans un seul achat** ces 4 derniers jours ; le
  contrôle `muettes` ne compte plus les retirées.
- Test `test_calendar_strategies_are_never_retired_for_inactivity` (config réelle : 7 protégées, `paire_oui_non` retirée) et
  `test_strategies_retired_for_inactivity_are_reported_once_and_not_called_silent`.

## Principal : pas de défaut (famille 1, contrôle à la main)
Gain réalisé du principal −235,7 € (764 € de capital) : 18/10 −134 € (60 paris), 17/10 −52 € (météo, éteinte), puis −2,4 % par mise du 19 au 23/10
(−43,6 € sur 1 784 € misés). Les gros trous du 18/10 viennent de `nf_court` (4 paris de 28 à 57 € perdus, **2 à 3 fois la taille du fantôme** :
57 contre 25, 55 contre 38, 48 contre 16) : c'est le défaut de copie déjà corrigé le 18/10 au soir (PR #76). Depuis, les pertes sont des favoris à
0,83-0,93 qui perdent (LASK Linz « NON » 59 €, BC.Game 41 €), compatibles avec l'absence d'avantage (la championne gagne ses prix, `22/10`).
Vérifié aussi : sur 470 achats de fantômes faits après le correctif du 23/10 au matin, **aucune** mise au-dessus de 26 % du capital et **aucun**
deuxième camp d'un même match (contrôles `mises` et `deux_camps` : les constats restants sont tous antérieurs au 23/10 00 h 30 UTC).

## Constaté, sans correctif
- 13 ordres posés restent « OUVERT » dans la base pour deux portefeuilles éteints depuis le 17/10 (`market_structure_patiente` 10,
  `naive_favorite_patiente` 3 ; ≈ 486 € « réservés ») : sans effet (ces portefeuilles ne tournent plus), à nettoyer si on veut une base propre.
- Marchés ouverts bloquant des positions : Cape Town 17 °C et 18 °C du 18/10 (`umaResolutionStatus: disputed`, comme le marché russe 5167158) et
  le référendum de l'Alberta (marchés 5475240/5475242, ni clos ni contestés 3 jours après l'échéance) : risque de règle déjà noté, 6 positions de fantômes.
