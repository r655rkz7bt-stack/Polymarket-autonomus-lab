# 31/10/2026 (matin) : l'arène contre les prix payés, 5 jours après le 26/10

Constat « à regarder » `estimation_gonflee` (z −12,5 contre les estimations, z −2,8 contre les prix payés). Script : `scripts/arene_contre_prix_26_10.py`, relancé sans changement sur les journaux du jour (un pari par jeton, paiement réel).

- 3 666 jetons : 2 518,5 gagnés pour 2 771,3 annoncés par les estimations, 2 580,4 attendus par les prix payés (−1,7 pt par pari). Les estimations sont donc au-dessus des prix (c'est le principe d'une stratégie), mais ce sont les prix qui comptent : l'écart au prix est faible.
- Par bande : 0,00-0,60 exactement à leurs prix (+0,1 / 0,0 pt) ; 0,80-0,95 −2,7 / −0,1 / −0,8 pt ; **0,60-0,80 : −5,5 pts (352 paris, z −2,27, t par événement −2,09)**, surtout `nf_*` à 0,60-0,80 (71 paris, −11,8 pts). 7 bandes regardées, un z de 2,3 sur l'une d'elles est ce qu'on attend du hasard (≈ 1 chance sur 3 d'en voir un) : pas un défaut, pas de correctif.
- Périodes `nf_*` : −0,8 / −1,5 / −1,4 pt avant le 22/10, du 22 au 24, depuis le 25 : stables, pas d'usure.
- `moins_de_cartes` : +5,5 pts (145 paris, z +1,33) contre +15,2 (57 paris, z +2,33) le 26/10 : l'« indice » fond avec les paris neufs, comme pour une régression vers la moyenne.
- Faibles confirmés : `suivre_politique` −18,7 pts (43), `calibration` −13,7 (46), `news_momentum_patiente` −7,3 (102) ; toutes éliminées ou en bas du classement.

Verdict : aucun défaut de code ; l'arène ne bat pas ses prix, comme prévu. Rien d'autre à corriger.
