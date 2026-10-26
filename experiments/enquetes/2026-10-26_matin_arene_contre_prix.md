# 26/10/2026 (matin) : l'arène entière gagne-t-elle autant que les prix qu'elle paie ?

Famille du jour (26 % 6 + 1 = 3) déjà faite à 1 h ; ce passage : **famille 2** (la mesure récompense-t-elle la chance ?) sur toute l'arène, plus les obligations.
Script : `experiments/enquetes/scripts/arene_contre_prix_26_10.py` (un pari par jeton, le plus ancien de tous les fantômes, paiement réel `pay` 0 / 0,5 / 1).

## Obligations de la feuille de mission
- **copie_fidele** (1 achat du principal sans jumeau, « Team Yandex », 22 h 35 le 25/10) : c'est l'ordre posé périmé déjà corrigé cette nuit (`2026-10-26_ordre_pose_perime_du_principal.md`) ; l'achat est antérieur au correctif.
- **champion_sans_avantage** (`nf_court_soir`, `nf_sport_patiente_6_24h`) et **chance** (`nf_court_football_soir`, `nf_sport_patiente*`, `nf_sport_prix_haut_3_6h`) : même mécanisme qu'aux passages précédents (mises ∝ 1/(1 − prix), favoris qui gagnent comme leur prix). Le calcul d'ensemble ci-dessous le confirme sur 2 239 paris.

## Constat (2 239 jetons distincts, 1 368 événements)
- Toute l'arène : **1 527,5 gagnés pour 1 557,8 attendus par les prix payés** (−1,4 point par pari, z −1,76, t par événement −1,69). Aucune famille ne bat ses prix de façon sûre :
  `nf_sport` −0,6 pt (556 paris, z −0,45), `nf_tennis` −0,8 pt (286, z −0,38), `nf_court` −3,4 pts (140), `news_momentum` +4,0 (83, z +0,95), `contrer_crypto` +5,3 (143, z +1,66), tweets +17,2 (26 paris sur 9 événements, z +2,2), « autres » −3,9 pts (877, z −2,94).
- Par période, les `nf_*` restent à −0,8 / −1,5 / −1,9 points (avant le 22/10, 22-24/10, depuis le 25/10) : pas d'effet qui s'use, pas d'effet du tout.
- Par bande de prix (`nf_*`) : 0,80-0,85 : −3,9 pts (307 paris, z −1,81) ; 0,85-0,90 : −0,6 ; 0,90-0,95 : +1,1 (437, z +0,86). Toutes les bandes à moins de 2 z.
- Dans « autres », les pertes viennent de stratégies déjà connues : `news_momentum_patiente` −7,3 pts (102), `calibration` −13,7 (46), `meteo_prevision` −4,0 (103), `suivre_politique` −22,4 (18). Seule **`moins_de_cartes` bat ses prix : +15,2 pts, 57 paris, z +2,33, t par événement +2,70** (+26,7 % de rendement, +109 € sur 409 €) ; ~90 stratégies : un z de 2 est ce que le meilleur de 90 obtient seul (contrôle `selection_multiple`), mais le test sur le passé et les 54 paris hors échantillon du 25/10 vont dans le même sens.
- Conclusion chiffrée : **le classement du brief (capital réalisé 1 434 € pour le premier) mesure surtout des mises ∝ 1/(1 − prix) sur des favoris qui gagnent à leur prix** ; en nombre de paris gagnés l'arène est à −1,4 point de ses prix, et ce n'est pas l'estimation de chaque stratégie qui est en cause mais le fait qu'il n'y a pas d'avantage à ces prix.

## Défaut de code trouvé en route
- `enquete.estimation_gonflee` comptait un règlement à 0,5 comme une défaite (`payout > 0.5`) : les 11 marchés à 50-50 de l'arène faisaient baisser les « gagnés » (1 522 au lieu de 1 527,5) et le z (−11,0). Corrigé : paiement réel par part ; le titre donne aussi le z contre les prix payés (celui qui compte, −1,8). Test : `tests/test_enquete.py::test_fifty_fifty_settlements_count_half_a_win_in_the_arena_calibration` (échoue sans le correctif).

## Autres vérifications
- `saison_non` (muette depuis sa naissance le 23/10) : pas prouvée sourde : parmi les 2 044 événements que Gamma rend pour une fin à 9-19 jours (lecture limitée à 2 100 lignes, donc partielle), les seuls événements de sport sans « vs » sont des Grands Prix (Mexique, Malaisie) et une annonce de la NBA, aucune échelle de gagnant de saison. À relire quand une fenêtre s'ouvre.
- `cpi_tranches`, `jobs_favori_non` : abstentions « hors de la fenêtre avant la publication » (leurs marchés sont à plus d'une semaine de la publication), rien à corriger.
- Relevés relancés : rougeole (CDC : toujours 4 588 cas au 22/10), essence (0 jour ajouté).

## Famille 6 et audit (vérifiés à la main)
- 6 positions ouvertes « bien après l'échéance » = 3 marchés : référendum de l'Alberta (5475240, 5475242 : prix 0,99 mais pas de règlement Gamma, déjà vu le 25/10) et « US x Yemen ceasefire » (5693642 : `umaResolutionStatus: proposed` depuis 5 jours, prix 0,9995). Litiges / règlements UMA lents, pas de défaut de code.
- Audit : 198 « réglé alors que le marché n'est pas clos » + 2 achats à 0,001 (corrigés le 24/10). Relu sur deux marchés réglés ce matin (5330019, 4824600) : le règlement du journal tombe 1 à 2 minutes **après** le `closedTime` de Gamma (05:04:46 → 05:05:58 ; 05:19:22 → 05:20:59), les prix finaux sont nets ; l'audit a lu le marché avant que Gamma n'affiche `closed`. Même cause que `proposals/2026-10-22_audit_reglements_trop_tot.md` (audit = noyau, non modifiable ici).
- `crypto_threshold_patiente`, `favori_politique*` (arrêtées depuis le 16-18/10) : « pas un marché crypto à seuil ×389 » et « favori hors de la plage de prix » : univers vide au moment du cycle, rien à corriger.

## Piège de lecture trouvé en route (outil, pas arène)
- `experiments/meteo_ensemble/evaluer_releve.py` lisait l'événement d'un marché dans `/markets/<id>` → `events`, que Gamma ne rend plus : tous les marchés tombaient dans un seul « événement » (`None`), le contrôle du règlement donnait « 0 événement sur 4 » et les paris liés auraient été comptés comme un seul. Corrigé : l'événement vient de la base (`meteo_ensemble_releves.evenement`) ; le relevé du 26/10 donne maintenant « 236 événements sur 236 avec exactement une tranche gagnante ». La production n'est pas touchée (le règlement ne lit pas `events`).
