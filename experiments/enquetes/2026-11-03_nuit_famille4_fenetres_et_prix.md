# 2026-11-03 (nuit) — famille 4 : fenêtres de temps et plages de prix

**Contrôle à la main** (jour 3 → famille 4), scripts existants relancés sur les journaux publiés du 03/11 à 01 h UTC :
`fenetres_25_10.py` et `filtres_prix_24_10.py`.

- Fenêtres (`echeance_min/max`, `heure_utc`) : 1 997 premiers achats, 32 stratégies à fenêtre. Écarts : 21 achats
  (`nf_sport_patiente_12_18h` 9/171, `nf_sport_patiente_matin` 6/68, `outsider_sport_apres_midi` 5/30, une fille 72-168 h 1/158),
  tous d'avant le 27/10 et déjà expliqués le 25/10 (ordres posés servis des heures plus tard, heure lue à la pose).
- Plages de prix, achats depuis le 31/10 : 1 119 achats, 52 stratégies. 24 hors plage, tous des **ordres posés** à 0,78-0,79 pour une
  plage 0,80-0,95 (ou 0,84 pour 0,85, `favori_politique_patiente` 6/19) : le prix payé est un cran sous la plage, comme pour
  le contrôle `filtre_prix` du 21/10 (la plage est jugée sur le prix de pose du vendeur, pas sur le prix servi). `toucher_metaux` 1/9 :
  0,507 pour une plage 0,08-0,50 (écart de 0,7 centime, ordre au marché).
- Verdict : aucun défaut de code, rien de nouveau. Pas de correctif, pas de contrôle ajouté.
