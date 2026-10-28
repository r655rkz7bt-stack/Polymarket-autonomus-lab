# 28/10/2026 (midi) — `moins_de_cartes` : que fait l'« indice » depuis sa confirmation ?

Famille 5 du README (deux résultats comparés sur la même période). Script : `scripts/moins_de_cartes_blocs_28_10.py` (journal signé publié, paiement par part, 50-50 compté 0,5).

## Constat
Le 25/10 au soir, `moins_de_cartes` (Under des totaux de cartes d'e-sport) était « confirmée en direct » : 54 paris hors échantillon, +29,7 %, z 2,59.
Depuis, 33 paris de plus ont été réglés :

| Paris | n | payé / attendu par les prix | z | rendement par mise |
|---|---|---|---|---|
| avant le 25/10 20 h (ceux de la « confirmation ») | 57 | 41,0 / 32,3 | +2,33 | +26,7 % |
| depuis le 25/10 20 h | 33 | 18,0 / 18,4 | −0,13 | −5,6 % |
| tout | 90 | 59,0 / 50,7 | +1,77 | +11,2 % |

Par blocs de 15 paris : z +0,15, +0,95, +2,25, +1,36, −1,30, +0,95 (rendements +8 %, +4 %, +34 %, +35 %, −27 %, +25 %) : pas de tendance claire, mais
les deux gros blocs positifs (paris 31 à 60, 24-25/10) sont ceux qui ont porté la « confirmation ».

## Lecture
- L'avantage de `moins_de_cartes` reste un **indice** (z +1,77 sur 90 paris, test sur le passé +7,7 % avec t 2,0) ; il n'est ni démenti ni confirmé.
  Le +26,7 % du direct est probablement une moitié de chance : si le vrai avantage est ≈ +8 % (test sur le passé), 33 paris à −5,6 % sont tout à fait plausibles (écart-type d'un bloc de 33 paris ≈ 25 points).
- Aucun défaut de code : la copie du principal et le plancher de copie ont été vérifiés le 28/10 matin.
- Conséquence pour le principal : la mise suit déjà « l'avantage mesuré » (`mise_avantage_mesure`) ; rien à changer. Ne pas écrire « confirmée » avant ~150 paris directs.
- Les filles `moins_de_cartes_lol` (5 paris, 5 gagnés pour 2,8) et `_bo5` (2 pour 1,0) sont trop petites pour dire quoi que ce soit ; `_franche` n'a pas encore de pari réglé.

## Contrôle automatique
Aucun nouveau : `selection_multiple` regroupe déjà par jour. Ce constat est une relecture, pas un défaut.
