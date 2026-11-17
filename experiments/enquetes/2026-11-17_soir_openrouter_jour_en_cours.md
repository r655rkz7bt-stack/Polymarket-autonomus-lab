# OpenRouter : le graphique de la semaine contient le jour EN COURS, et un lancement a fait payer 0,42 un NON perdu d'avance (17/11/2026, passage de 16 h)

Famille 4 à la main (« le prix payé est-il celui que la stratégie croit payer ? ») sur les 8 achats des fantômes v2 depuis 10 h, puis
famille 3 (« la donnée n'est pas celle qu'on croit »). L'enquête automatique n'avait rien signalé : `estimation_perimee` ne regardait
que les stratégies à 5 achats ou plus (`openrouter_semaine` en a 4).

## Constat
| heure (UTC) | marché | côté | payé | estimé | mise | marché à 16 h |
|---|---|---|---|---|---|---|
| 17/11 12 h 57 | 6942353 « 240T or more … week of November 16 » | NON | 0,4247 × 44,17 | **0,973** | 19,2 € | OUI 0,84 (NON 0,16) |
| 17/11 12 h 57 | 6942351 « between 220T and 230T » | OUI | 0,20 × 5 | 0,41 | 1,0 € | 0,10 |

Avantage annoncé : 0,48 sur le premier. Le marché avait raison.

## Ce que dit la source (lu à 15 h 49 UTC, robots.txt permis)
- Vue « jour » (dernier jour fini, lundi 16/11) : **32,13 T**. Vue « 7 jours » (10-16/11) : 213,80 T. Semaine du 9/11 : 211,28 T.
- Graphique, semaine du 16/11 : **69,71 T**, soit lundi + **37,6 T du mardi en cours** (15,8 h). Modèle par modèle : deepseek-v4.1-flash
  15,15 T au graphique pour 9,13 T lundi (mardi partiel 6,0 = son rythme habituel) ; **tencent/hy4-flash-20261116** (lancé le 16/11)
  17,59 T au graphique pour 1,88 T lundi : **15,7 T mardi en 16 h**, la moitié du trafic normal d'une journée entière à lui seul.
- Le journal de production `openrouter:histo` le confirme pour toutes les journées depuis le 13/11 : le « partiel » de la semaine
  contient toujours le jour en cours (0,15 T le lundi 16/11 à 00 h 40 ; 210,22 T le dimanche 15/11 à 23 h 40 pour une semaine finale
  de 211,28 T).

## Cause
`openrouter.projection` prenait le graphique pour « les k jours finis » (k lu dans la vue « jour »). Avec k = 1, P = lundi + mardi
partiel : fin de semaine précédente = 7 jours − P, trop petite ; début = semaine précédente − fin, trop grand ; total ≈ P × semaine
précédente / (semaine précédente − 7 jours + P) ≈ 219-220 T. La forme de la semaine passée ne pouvait de toute façon pas voir le
lancement de hy4-flash : le jour en cours le montrait, la projection l'écrasait.
Le passage du 13/11 avait vu le même phénomène (134,43 puis 141,16 T sans nouveau jour fini) et conclu « ampleur nulle » : c'était
vrai cette semaine-là parce que le jour en cours ressemblait au jour d'avant ; c'est faux dès qu'il ne lui ressemble plus.
Deuxième défaut caché : la borne de cohérence « fin / début entre 0,1 et 3 » refusait tout lundi seul (6 jours / 1 jour ≈ 6) ; elle ne
passait que grâce au jour partiel ajouté.

## Ampleur
- 2 achats, **20,2 €** (2 % du fantôme) ; perte attendue ≈ 17 € au prix du marché (NON 0,16, tranche 220-230 à 0,10). Le principal
  n'a rien copié (aucun champion).
- Les 2 achats du 13/11 (semaine du 9/11, 10,25 parts, −4,24 € réglés) : même lecture, projection 209,75 contre ≈ 209,8 avec les vrais
  jours finis : sans effet.

## Correctif (`src/polymarket_agent/openrouter.py`)
- `detail(row, histo)` : jours finis = **somme des totaux quotidiens du journal** `openrouter:histo` (lundi seul : la vue « jour ») ; un
  jour fini absent du journal = pas de projection (raison écrite).
- **Rupture** : si le jour en cours (graphique − jours finis), ramené à 24 h, dépasse 1,5 fois le dernier jour fini (après 3 h UTC),
  la stratégie s'abstient (« lancement ou panne, la fin de semaine passée ne dit plus rien »). Mesures du journal : 0,4-1,0 les jours
  ordinaires, **1,7-1,8 le 17/11**.
- Total projeté jamais sous le graphique ; borne de cohérence relative au nombre de jours ((7 − k) / k × 0,3 à 3).
- La référence porte la raison (`refus`) et `SeismesMarche.propose` l'écrit en abstention : cycle local de 16 h 05 →
  « OpenRouter : jour en cours à 1.7 fois le rythme d'hier (37.6 T en 16.1 h) » ×4.
- Tests du cas réel (`tests/test_openrouter.py`, données réduites `tests/data/openrouter_2026-11-17.json`) ; ils échouent sans le correctif.

## Contrôle automatique
`enquete.estimation_perimee` : une stratégie à moins de 5 achats est maintenant signalée pour tout achat estimé **0,30 ou plus**
au-dessus du prix payé (test `test_new_strategy_with_a_huge_gap_is_flagged`). Sur les journaux du jour : ce cas, la rougeole du 14/11
(déjà relue le 15/11, conforme) et `seismes_pays` du 16/11, qui a mené à l'enquête suivante
(`2026-11-17_soir_references_avant_collecte.md`).
