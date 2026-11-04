# 04/11/2026 (soir) — identité comptable des 191 journaux ; relevé de l'essence sans prix

Famille 5 (jour 4 modulo 6, + 1) : comparer ce qui doit être égal.

## 1. Identité comptable (rien trouvé, vérifié)
`experiments/enquetes/scripts/identite_comptable_04_11.py` rejoue chaque journal signé (principal + 190 fantômes) depuis le capital initial :
achats (prix × parts + frais), ventes (prix × parts − frais), règlements (parts détenues × paiement). Comparé au dernier cash écrit par le
journal (HEARTBEAT) : **191 journaux sur 191 égaux à la décimale près** (principal 435,8054360834 € des deux côtés). Aucun règlement double,
aucun règlement de parts jamais achetées, aucune vente en trop, aucun paiement hors 0 / 0,5 / 1. La comptabilité n'est donc pas la source d'un écart.

## 2. Défaut trouvé : le relevé de l'essence n'enregistrait aucun prix
`experiments/essence/releve.py` demandait `prices-history` en `interval=max, fidelity=60` ; pour un marché clos le CLOB rend `[]` (astuce déjà notée le
24/10). Résultat : les colonnes « prix à 24 h / 12 h » de `releve.csv` sont vides pour les 22 jours relevés depuis le 21/10, sans erreur ni alerte :
la piste n° 4 n'aurait jamais pu être testée. Correctif : fenêtre `startTs/endTs` (60 h avant la fin), `REDO=1` pour tout relire. Les prix à 12 h
reviennent pour 20 jours ; à 24 h les carnets sont vides (aucun échange).

## 3. Verdict de la piste n° 4 (indicatif, 11 jours)
Modèle : normale centrée sur la tranche gagnante de la veille (écart-type des jours précédents, 1,2 à 2,5 cents). Contre le prix du marché à 12 h :
log-score −1,65 (modèle) contre −1,18 (marché) sur 11 jours ; −1,45 contre −0,85 sur les 5 jours à carnets liquides (somme des prix 0,9-1,25). Les
jours minces (somme des prix 1,6 à 3,0) sont des milieux de carnets vides (cf. `outcomePrices`, 04/11 matin), pas des prix d'achat. Le favori à 12 h a
gagné 8 fois sur 8 sur les jours liquides (attendu 6,6, z +1,4) : un favori ordinaire. **Écartée**, le marché connaît déjà la valeur.
