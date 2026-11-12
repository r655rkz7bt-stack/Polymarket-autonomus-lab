# Freins du principal et « bat-elle ses prix ? » : rejoués avant d'appliquer (12/11/2026)

Demande d'Etienne (12/11/2026, après la remise à zéro du labo v2) : appliquer deux changements proposés le même jour :
(1) choisir les stratégies du capital principal sur « bat-elle ses prix ? » plutôt que sur leurs euros ; (2) alléger les
freins du principal. Rejeu avant d'appliquer (`confiance_processus/rejeu_patience.py`, fonction `v2`), sur les journaux de la
v1 du 15/10 12 h au 07/11 18 h (moitié au 27/10), mise mesurée comprise.

| règle du principal | paris | 1re moitié | 2e moitié | total |
|---|---|---|---|---|
| **en vigueur** (12 opérations, +2 %, t ≥ 1 ; maintien −10 % ; essai ; plancher 0,25) | 1 565 | +65 € | −23 € | **+42 €** |
| idem, mises pleines dans les creux (plancher 1) | 1 565 | +85 € | −64 € | +21 € |
| freins allégés (8 opérations, sans période d'essai) | 1 748 | +15 € | −19 € | −3 € (plancher 1 : −31 €) |
| bat ses prix : zp ≥ 1 ou 1,5, 12 ou 20 opérations, maintien −10 % ou zp ≥ 0 (5 réglages) | 879-1 040 | | | −32 à −139 € |
| bat ses prix + freins allégés (2 réglages) | 879-914 | | | −37 à −57 € |

**Décision d'Etienne (12/11) : garder les règles du principal**, et afficher « bat-elle ses prix ? » (gagnés contre attendus
d'après les prix payés, z) pour chaque stratégie de l'arène (`arena.price_beat`, tableau de bord). Choisir sur ce critère
sélectionnait surtout le contre-mouvement crypto, qui battait ses prix un temps avant de s'effondrer ; alléger les freins fait
entrer des stratégies sur de la chance. Limite : données de la v1 (surtout des favoris) ; à rejouer quand les stratégies de la
v2 auront 30 paris réglés chacune.
