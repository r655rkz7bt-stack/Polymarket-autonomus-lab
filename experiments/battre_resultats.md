# Piste n° 17 `battre_resultats` : « La société X battra-t-elle ses résultats trimestriels ? » (22/10/2026)

**Question** : environ 3 sociétés sur 4 battent la prévision des analystes. Le prix du OUI de ces marchés sous-estime-t-il, ou surestime-t-il, ce taux ?

**Données** : Gamma (recherche publique), **1 391 marchés « beat quarterly earnings » réglés** de septembre 2025 à octobre 2026 (taux de OUI 74,4 %) ; prix horaire du CLOB sur les 10 jours
avant l'échéance (`prix.py` : `interval=max` ne rend rien pour un marché clos, à retenir). Prix du OUI au dernier point connu avant T0 = échéance − 1, 3 ou 7 jours (écart ≤ 12 h).
Volume médian 5 800 $ (771 marchés > 5 000 $). Scripts : `experiments/battre_resultats/` (`releve.py`, `prix.py`, `analyse.py`, `resultats.txt`).

## Résultats
- **Calibration** (T-1 j, 1 355 marchés) : prix moyen contre OUI réalisés : 0,327 → 0,372 ; 0,583 → 0,647 ; 0,733 → 0,738 ; 0,853 → 0,853 ; 0,928 → 0,949. Le marché est calibré (T-3 j et T-7 j de même).
- **Achats simulés** (frais du marché, écart 0,01 ou 0,02 ; 5 tranches de prix × 3 horizons × 2 écarts = 30 réglages) : aucun ne donne « retenue » ; les seuls « indice » (OUI 0,80-0,90 à T-7 j : +2,9 %
  puis +1,7 %, t +1,4 / +0,9 ; OUI < 0,65 à T-1 j : +8,4 %, t +1,2) disparaissent à l'écart de 0,02 ou à l'horizon voisin. NON des favoris ≥ 0,90 : −36 % à T-1 j (t −2,2), +13 % à T-3 j : instable.
- Limite : prix du CLOB (mids horaires), pas de vrais échanges ; sur des marchés si minces le prix payé serait pire, donc le verdict ne peut que se confirmer.

**Verdict : écartée.** Le prix de ces marchés intègre déjà le taux de 3 sur 4 : pas d'avantage par entreprise ni par tranche de prix sur 1 391 marchés. Piste de rechange non testée : l'historique par société
(une société qui bat toujours) : demande les résultats passés de chaque société, pas de source gratuite sûre ici.
