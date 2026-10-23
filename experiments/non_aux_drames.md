# Piste n° 11 `non_aux_drames` : acheter le NON des OUI à 2-15 % longtemps avant la fin (22/10/2026)

**Question** : un OUI à 2-15 % sur un marché long (drames, « faillite », « invasion »…) est-il trop cher, c'est-à-dire
son NON rapporte-t-il plus que son prix ?

**Données** : Gamma, événements clos du 1/04 au 22/10/2026, hors sport, 1 à 3 marchés par événement, réglés nets
(30 319 marchés ; 686 avec volume ≥ 5 000 $ et vie ≥ 14 jours). Historique `prices-history` du CLOB (pas de 12 h, par
tranches de 15 jours : le CLOB refuse les fenêtres longues), prix du OUI au dernier point connu AVANT T0 = fermeture − k jours.
Pari : NON au prix 1 − OUI + écart (0,01 ou 0,02) + frais du marché (`feeSchedule`). Scripts : `experiments/non_aux_drames/`
(`releve.py`, `prix.py`, `analyse.py` ; sorties `resultats*.txt`).

**Contrôle du règlement** : le dernier prix de l'historique est du bon côté pour 652 marchés sur 686 (les 34 autres : historique
coupé avant le règlement, prix proche de 0,5 à la fermeture ; ils restent réglés selon Gamma).

## Résultats (≈ 40 réglages : 4 horizons × 4 tranches de OUI, puis 2 horizons × 3 volumes × 2 écarts)
- T-7 j : OUI 5-10 % −8,9 % (t −2,0), 2-15 % −4,9 % ; T-14 j : −2,9 % ; T-30 j : −0,3 % (volume ≥ 100 000 $ : −8,5 %, 57 paris).
- T-60 j, OUI 2-15 % : +2,8 % (122 paris, z des prix +1,3) avec écart 0,01, **+1,7 % avec écart 0,02**, aucune confiance par
  événement ≥ 1,5 une fois l'écart à 0,02 (le « retenue » de `verdict` pour T-60 j / 5-10 % est un artefact : tous les NON gagnent,
  l'écart-type est minuscule, t explose ; z des prix +1,65 seulement).
- Un capital immobilisé 60 jours pour +1,7 à +2,8 % ne bat pas les pistes courtes.

**Verdict : écartée.** Le OUI à 2-15 % n'est pas trop cher de façon régulière : aucun horizon ne reste positif aux deux écarts et
aux trois volumes. **Limite** : prix du CLOB à 12 h, pas les vrais échanges (les marchés longs dépassent 10 000 échanges, les plus
anciens sont inaccessibles) : le prix payé réel aurait été pire (règle du README des enquêtes : un test positif au CLOB est suspect, ici il est négatif ou nul).
