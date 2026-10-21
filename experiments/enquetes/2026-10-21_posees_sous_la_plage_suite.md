# 21/10 (soir) : ordres posés sous 0,80, suite (famille 4)

Suite de [2026-10-21_posees_sous_la_plage.md](2026-10-21_posees_sous_la_plage.md). Script : `scripts/posees_sous_plage_suite_21_10.py`
(lecture seule des journaux signés ; paris communs dédoublonnés par (jeton, prix arrondi)).

## Constat mis à jour (+ 8 h de paris)
- Famille nf_sport_patiente / nf_tennis : 49-50 paris distincts servis sous 0,80, 1 746 € misés, **−12,0 %** (t −1,36). Le matin : 44 paris, −11,9 %.
- Par jour d'achat : 18/10 **+82 €**, 19/10 −87 €, **20/10 −211 €** (28 paris), 21/10 −5 €. La perte est presque toute dans une seule journée.
- Par événement (42 événements, paris liés regroupés) : rendement moyen −8,2 %, **t −0,86**. Sans les 3 pires paris : **−2,5 %** (−39 € sur 1 585 €).
- Le **champion** `nf_sport_patiente` : 6 achats sous 0,80 (0,72-0,78), les 6 gagnés (+). Imposer `prix_final` aux mères lui aurait fait perdre
  6 gagnants. Le principal n'a que 1 achat de ce type dans la famille (0,761, gagné).

## Verdict
Indice de sélection adverse **affaibli** (chiffre concentré sur le 20/10, pas de régularité d'un jour à l'autre). Aucun correctif : on ne
passe pas les mères en `prix_final`. Reste à regarder : aucun achat sous 0,80 du champion depuis le 19/10 (le carnet est moins écarté ?).
Si le −10 % revient sur 20 nouveaux événements, ré-examiner.
