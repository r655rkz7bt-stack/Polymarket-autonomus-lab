# Enquêtes : les défauts qui faussent les résultats

Une enquête par fichier `AAAA-MM-JJ_<sujet>.md` : constat (chiffres), cause (fichier, fonction),
ampleur, correctif (ou proposition si noyau), test de non-régression, contrôle automatique ajouté
à `src/polymarket_agent/enquete.py`. Méthode : docs/ROUTINE_CHERCHEUR.md, partie A.

## Défauts trouvés jusqu'ici (à relire avant chaque enquête : ils reviennent sous d'autres formes)

| Date | Défaut | Effet | Correction |
|---|---|---|---|
| 16/10 | Gain de la météo mesuré sur l'historique « 10 minutes » du CLOB | +28 % au test, −6 % aux prix des vrais échanges | toujours vérifier aux prix payés (`idea_test.taker_cost`) |
| 18/10 | Le principal relançait la stratégie avec son argent au lieu de copier ses paris | Bitcoin misé 3× trop gros, anciens paris rattrapés : −89 € au lieu de −5 € | copie fidèle (PR #76) |
| 18/10 | Confiance de l'arène calculée en euros | les grosses mises chanceuses passaient pour un avantage | confiance sur le rendement par mise (PR #77) |
| 19/10 | cotes_bookmakers appliquait la cote « vainqueur » aux handicaps | −287 € sur 14 paris | vainqueur seulement, écart > 25 points refusé (PR #81) |
| 20/10 | Rattachements PredictIt erronés (« course la plus serrée », vice-président…) | références fausses | règles strictes (PR #93) |
| 20/10 | Modèle de tweets trop large (dispersion 4, rythme de 72 h) | −13 % par achat sur le passé | réglé sur le passé (PR #93) |
| 20/10 | Estimation calculée sur le carnet du début de cycle | mises +46 % sur les chutes de prix, 8,9 % du principal sur un pari | `relecture.chute_max` ([2026-10-20_carnet_perime.md](2026-10-20_carnet_perime.md)) |
| 20/10 | Fille jugée sur une autre période que sa mère ; « demi-mise » ≠ mêmes paris ; plage de prix contournée par l'ordre posé | conclusions fausses sur les filles | contrôles `filles_periode`, `meme_pari_prix_differents`, `filtre_prix` |
| 20/10 (soir) | Championne = meilleur de 35 (z 1,86 : chance de sélection), 84 % des achats en jeu malgré « horizon 165 h » (date placeholder Gamma), deux camps d'un match achetés (−275 €) | gain attribué à un avantage non prouvé ; filtres d'échéance sans sens pour le sport | contrôles `selection_multiple`, `deux_camps`, `achats_en_jeu`, champ `depuis_coup_d_envoi_h` ([fiche](2026-10-20_championne_chance_et_en_jeu.md)) |
| 21/10 | Les variantes « favori » gagnent 0,0 % sur le type vainqueur (28 837 € misés) et perdent sur les handicaps (−10,5 %) ; principal −14,9 % sur handicap | le gain de l'arène vient des types annexes, de la sélection et de la chance | fille `nf_sport_patiente_vainqueur` ([fiche](2026-10-21_type_de_pari_et_reglement.md)) |

## Familles de défauts (où chercher)
1. **Le principal ne joue pas ce que l'arène mesure** (copie, mise, ordre d'exécution, liquidité partagée).
2. **La mesure récompense la chance** (euros au lieu du rendement, quelques gros paris, un seul jour, une seule période).
3. **La donnée n'est pas celle qu'on croit** (mauvais marché rattaché, mauvais type de pari, prix historique non exécutable, carnet périmé, source en retard).
4. **Le filtre ne filtre pas** (plage de prix vérifiée sur un prix, pari pris à un autre ; fenêtre de temps sur la mauvaise date).
5. **Comparaisons faussées** (périodes différentes, fantômes au capital différent, paris liés comptés comme indépendants).
6. **Ce qui ne tourne plus** (stratégie muette, source en panne, position jamais réglée).
