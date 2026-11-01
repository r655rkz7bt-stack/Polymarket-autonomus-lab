# « Trust the process » : le principal lâchait ses stratégies au premier creux (01/11/2026)

Demande d'Etienne (01/11/2026) : « Est-ce que tu ne coupes pas le modèle quand il commence à perdre, quand sa confiance est
basse, sans lui laisser le temps de se rattraper ? Essaie de plus trust le process, trouve des solutions, applique sans me
demander si ça ne touche pas le noyau. »

Point de départ (tableau de bord du 01/11 11 h 17 UTC) : principal 698 € estimés (709 € réalisés), 17 jours sans palier.

## Ce qui coupait trop vite (lu dans le code)
1. **Seule la championne avait un seuil de maintien** (`arena.allocation`, `kept`) : les 4 autres stratégies suivies devaient
   repasser le seuil d'ENTRÉE (12 opérations, croissance ≥ +2 %, t ≥ 1) à chaque recalcul horaire ; au premier creux, elles
   sortaient, et le principal passait à une autre. La championne elle-même sortait dès croissance < 0 ou t < 0.
2. **Mise à proportion de l'avantage mesuré avec un plancher de 0** (`mise_avantage_mesure.part_min`) : une stratégie dont
   l'avantage mesuré devient négatif ne misait plus rien.
3. **Retrait des fantômes** (`retirer_perdantes`) : dès 20 opérations si la confiance ≤ −1,5 ou le capital < 750 €.

## Rejeu (`confiance_processus/rejeu_patience.py`, journaux du 15/10 12 h au 01/11 11 h, moitié au 23/10 23 h 46)
Même outil et mêmes approximations que `audace/rejeu_regles.py` (paris réels des fantômes, frais compris, sans carnet).

| règle | paris | 1re moitié | 2e moitié | total |
|---|---|---|---|---|
| en vigueur (mise prorata, sans mise mesurée) | 768 | +18 € | −190 € | **−172 €** |
| garder chaque stratégie suivie tant que croissance ≥ −10 % | 1 096 | +84 € | −101 € | **−17 €** |
| idem, seuils −5 % … −15 % (8 réglages) | 1 065-1 100 | | | −23 € à −2 € |
| idem, −20 % / −25 % / jamais de sortie | 1 130-1 187 | | | −122 € / −113 € / −72 € |
| engagement minimal 3 ou 7 jours | 658-701 | | | −134 € / −162 € |
| **avec la mise mesurée** (plus proche du réel) : en vigueur, plancher 0 | 564 | +41 € | −92 € | **−51 €** |
| sortie sous −10 %, plancher 0 / **0,25** / 0,5 / 1 | 945-1 096 | +63 à +84 € | −34 à −101 € | +28 / **+32** / +19 / −17 € |
| sortie sous −5 % / −15 % / −20 %, plancher 0,25 | 1 065-1 179 | | | +25 / +31 / −46 € |

Lecture : changer sans cesse de stratégie coûtait cher (on sortait au creux, on rentrait sur la suivante au sommet). Garder
une stratégie suivie jusqu'à −10 % fait mieux dans **les deux moitiés** et sur tout un plateau de seuils (−5 à −15 %) ; au-delà
(−20 %), on garde aussi les vraies perdantes. Un plancher de mise de 0,25 garde la stratégie active sans la faire miser fort.
Limites : un seul relevé de 17 jours ; ~25 réglages regardés ; le rendement reste petit (+32 € sur 4 090 € misés) : c'est
surtout moins de pertes, pas un avantage prouvé.

## Appliqué (config/promotion.yaml, arena.py, main.py ; tests)
- `keep_log_growth: -0.10`, `keep_t_stat: null` ; `arena.allocation(..., holders=)` : chaque stratégie suivie au recalcul
  précédent (`repartition_principal`) garde sa place tant qu'elle tient ce seuil ; dans un creux, elle n'a que sa part égale
  (pas de part « au mérite » négative) ; si aucune n'a de croissance positive, parts égales (avant : plus rien de suivi).
- `mise_avantage_mesure.part_min: 0.25`.
- `retirer_perdantes: {min_operations: 40, confiance_max: -2.0, capital_min: 600}` (fantômes : coût nul pour le principal).
- Inchangés : l'ENTRÉE (12 opérations, +2 %, t ≥ 1), la période d'essai, le garde-fou par jour, la réserve de liquidités et la
  règle n°1 (noyau). À rejouer vers le 08/11 avec les nouveaux paris.
