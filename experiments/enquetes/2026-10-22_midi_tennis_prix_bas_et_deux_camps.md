# Enquête du 22/10/2026 (midi) : `nf_tennis_prix_bas`, `nf_sport_patiente`, règlements relus, deux camps

Déclencheurs : obligations de la feuille de mission du 22/10 à 09 h 47 UTC (`champion_sans_avantage` sur `nf_tennis_prix_bas`,
`chance` : 3 paris = 86 % du gain de `nf_sport_patiente` et 122 % de celui de `nf_tennis_prix_bas`, un jour = 168 % / 195 %).
Famille du jour : 22 % 6 + 1 = 5 (comparaisons faussées) ; contrôle à la main aussi en famille 3 (la donnée est-elle celle qu'on croit).
Script : `experiments/enquetes/scripts/charge_fantome.py` (un pari = un jeton, journal signé).

## Constat (journaux signés du 22/10, 09 h 50 UTC)
- **`nf_tennis_prix_bas`** : 86 paris clôturés, +66 €, 4 478 € misés. Gagnés **73 pour 70,8 attendus** par les prix. Sans les 3 meilleurs paris
  **−14,6 €**, sans les 5 meilleurs −55 €, sans les 10 meilleurs −130 €. Les 30 derniers : 24 gagnés pour 24,8 attendus, **−121 €** (1 954 € misés).
  Par jour de règlement : 20/10 +80 €, 21/10 +131 €, **22/10 −144 €** (9 paris : 3 pertes de 120, 134 et 3 €).
  Par prix payé : 0,80 : +76 € (33 paris, 29 gagnés pour 26,7), 0,825 : +8 €, 0,85 : −2 € ; 0,775 : −11 € ; l'avantage tient dans une tranche de 33 paris.
- **`nf_sport_patiente`** (championne) : 107 paris, +144,5 €, 9 036 € misés, 98 gagnés pour 92,6. Sans les 3 meilleurs **+20,8 €**, sans les 5 meilleurs −30 €,
  sans les 10 meilleurs −145 €. Par jour de règlement : 17/10 −101, **18/10 +298**, 19/10 −40, 20/10 +173, 21/10 −84, 22/10 −101. Les 30 derniers paris : −69 €.
  Par prix : 0,80-0,90 : +574 € (67 paris) ; **0,90-0,95 : −531 € (34 paris, 29 gagnés pour 31,4)**.
- Même mécanisme que l'enquête du matin du 22/10 ([fiche](2026-10-22_championne_biais_et_mises.md)) : `bias` 0,05 fixe → mise ∝ 1/(1 − prix) →
  les paris les plus chers sont les plus gros et ne rapportent rien. Aucun écart nouveau à corriger dans le code.

## Contrôles à la main (rien de nouveau, mais chiffré)
1. **Règlements relus (famille 3)** : 16 paris tirés au hasard (graine 22) parmi 7 fantômes ; marché relu un par un sur Gamma (`/markets/<id>`, `outcomePrices`
   et `clobTokenIds`) : **16 règlements sur 16 identiques** (tennis, e-sport, football « exact score », handicap NFL, bitcoin). Types de marché vus : moneyline,
   child_moneyline, spreads, soccer_exact_score, soccer_halftime_result ; 
2. **Copie du principal (famille 1)** : `nf_sport_patiente` : 50 jetons côté principal, 48 en commun avec les 58 du fantôme depuis le 19/10 ; part moyenne
   0,34 (min 0,08, max 0,94) ; `nf_tennis_prix_bas` : 5 jetons communs sur 13, part 0,08-0,17 : la mise sur l'avantage mesuré (`mise_avantage_mesure`) réduit bien
   la copie quand l'avantage mesuré est faible. Les 44 achats du principal sur `nf_sport` (18/10 16 h-21 h) sont antérieurs à la copie fidèle (PR #76) : défaut déjà
   connu, rien de nouveau. Principal : 794,8 € (713 € en caisse, 86 € en jeu) ; ses pertes viennent de `nf_court` (−145 € sur 18 paris) et `meteo_prevision` (−58 € sur 39), toutes deux
   anciennes ; depuis la copie fidèle il fait −19 € (`nf_sport_patiente`, 48 paris), +10,5 (`nf_sport`), +10,6 (`nf_tennis_prix_bas`).
3. **Deux camps d'un même match (famille 5)** : tous les fantômes confondus, seulement **6 matchs** où une même stratégie a acheté les deux camps du même marché. Le premier
   camp n'a gagné que 1 fois sur 6 (−393 €), le second camp −11 €. C'est la forme attendue d'un renversement en cours de match (le favori du début perd, l'autre devient
   favori à son tour) : le premier camp perd par construction, le second ne rapporte pas non plus (le prix du second camp inclut déjà le renversement). Exemple du jour : marché 5966837,
   Mary Stoiana achetée à 0,80 à 04 h 32 (gagnée, +20 €) puis Moyuka Uchijima à 0,82 à 05 h 46 (perdue, −120 €). Pas assez de matchs pour bloquer le camp opposé
   (même conclusion que le 21/10) ; **aucun correctif**. À refaire à 20 matchs.

4. **Audit indépendant (famille 6, ce qui ne tourne plus comme prévu)** : `audit/etat.json` contient **62 anomalies**, toutes « réglé alors que le marché N n'est pas clos », apparues le 21/10
   à 16 h 15 UTC (13 audits). Relu un par un sur Gamma : les 62 marchés sont aujourd'hui `closed`, `resolved` ; le règlement du journal tombe **17 à 225 s (médiane 78 s) après le `closedTime`**
   officiel, jamais avant, avec **le bon paiement 62 fois sur 62**. Le cycle n'a rien réglé trop tôt (`settlement.resolution_payout` exige `closed is True`) : l'audit (`scripts/audit_fills.py`, **protégé**)
   lit `closed` avant que Gamma l'affiche. Chaque alerte fait échouer le job d'audit (e-mail à Etienne) et noie une vraie anomalie. Correctif côté noyau : `proposals/2026-10-22_audit_reglements_trop_tot.md`
   (réessayer pendant 30 minutes). Côté libre : contrôle `audit_anomalies` dans `enquete.py` (fausses alertes « à regarder », autres anomalies « graves ») + test `test_audit_settled_before_gamma_shows_closed_is_a_false_alarm_not_a_grave_finding`.

5. **Par type de pari (famille 3)** : les 107 paris de la championne rangés par `sportsMarketType` (Gamma) : **89 « moneyline » = 7 434 € misés, +8 € (+0,1 %)**, 81 gagnés pour 77 attendus ;
   18 paris annexes = +136 € (child_moneyline 5 paris +66 €, totaux 3 paris +36 €, 2 sans type +39 €, exact score NON 2 paris +21 €, totaux d'équipe +16 €, handicaps 4 paris −43 €).
   Le gain de +145 € de la championne vient de **18 paris annexes sur 107** ; sur son vrai terrain (le vainqueur du match) elle ne rapporte rien. Même constat que la fiche du 21/10 (types annexes).
   Les scores exacts (piste n° 1, `experiments/score_exact.md`) ne rapportent rien non plus au prix.

## Correctif
Aucun changement de stratégie de stratégie ce passage (les chiffres ci-dessus ne distinguent pas −1 % de +3 % ; la décision sur `bias` reste à Etienne, voir la fiche du matin).
Script de chargement des journaux ajouté (`experiments/enquetes/scripts/charge_fantome.py`) pour que les enquêtes suivantes ne le réécrivent pas.
