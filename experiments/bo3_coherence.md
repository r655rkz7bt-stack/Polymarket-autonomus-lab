# Piste n° 4 `bo3_coherence` : le prix du match est-il cohérent avec le prix de la carte 1 ? (22/10/2026)

**Question** : en BO3 / BO5, si les cartes sont des tirages indépendants à chance égale q, la chance de gagner la série est
q²(3 − 2q) (BO3) ou q³(10 − 15q + 6q²) (BO5). Le prix de « Carte 1 » donne q ; s'il s'écarte du prix du match, on achète le côté le moins cher.

**Données** : Gamma, séries LoL (10311), CS2 (10310), Dota 2 (10309), Valorant (10369), matchs clos des 45 derniers jours ayant à la fois « Match Winner »
et « Game/Map 1 Winner » réglés nets : **2 317 matchs**, et leurs **échanges réels** (data-api, par événement). Prix = dernier échange avant
T0 = coup d'envoi − retard (0, 30, 60, 180 min), fenêtre de 2 h, en équivalent « équipe A » (achat de A ou vente de B). Scripts :
`experiments/bo3_coherence/` (`releve.py`, `analyse.py`, `resultats.txt`).

**Contrôle du règlement** : le dernier prix échangé du match est du bon côté pour 2 290 matchs sur 2 291 (hors prix entre 0,2 et 0,8).

## Résultats (12 réglages : 4 retards × 3 seuils d'écart ; 589 à 1 372 matchs utilisables selon le retard)
- **Contre le marché d'abord** : log-score du prix du match 0,556 / 0,548 / 0,543 / 0,536 ; du modèle « carte 1 → match » 0,579 / 0,569 / 0,555 / 0,545 (à
  retard 0 / 30 / 60 / 180 min) : le modèle est **toujours moins bon**. Même la moyenne des deux (0,5574 / 0,5515 / 0,5457 / 0,5387) ne bat pas le prix du match.
  Écart moyen |match − modèle| : 0,071 à 0,036 : l'écart n'est donc pas une erreur du marché ; l'hypothèse « cartes équiprobables et indépendantes » est probablement trop simple (explication non testée).
- Achat simulé (frais du marché, écart 0,01) : seuil 0,03 → −1,5 % à −15,4 % ; 0,05 → +0,8 % à −17,6 % ; 0,08 → +5,0 % à −15,3 % ; confiance par match de
  −2,7 à +0,7 ; **aucun réglage avec le verdict « retenue » ou « indice »** ; 2 mois seulement, 0/2 mois gagnants dans 8 cas sur 12.

**Verdict : écartée.** Le marché « vainqueur du match » est mieux calibré que le calcul tiré de la carte 1 (2 317 matchs, vrais échanges, règlement 2 290/2 291). Ne pas refaire sans
un modèle plus fin des cartes suivantes (hypothèse non testée).
