# Mots prononcés (orateurs nommés) aux prix payés (23/10/2026)

**Question** : `mots_prononces` (« retenue » : +19 % par achat, t +2,8, +27 % à 12 h, `vingt_pistes.md`) a été mesurée avec le prix CLOB horaire deux heures après l'ouverture.
Le 21/10 le même défaut (carnets vides à 0,50) avait ruiné les orateurs « the announcers » et « anyone » (+31 % → −6,7 %), mais les **orateurs nommés** (Trump, etc.) n'avaient pas été refaits aux
prix des échanges. Les voici.

**Données** (scripts : `experiments/mots_prix_payes/`, données ignorées par Git) : 22 013 marchés « mentions » réglés (Gamma keyset, tag `mention-markets`), dont 5 160 d'orateurs nommés
dont le mot a déjà au moins 3 précédents chez le même orateur ; échanges réels de chacun (data-api, filtre `market=<conditionId>`). 3 991 marchés jugés (T avant la dernière heure du marché).
Règle de `MotsPrononces` inchangée : taux du mot chez l'orateur (marchés réglés AVANT T) mélangé au taux de l'orateur (poids K), achat si le taux dépasse le prix payé de `marge` et si
le billet coûte au moins 0,30 ; frais du barème (0,04·p·(1−p)) et +0,01 d'écart comme le 21/10. T = premier échange du marché + `délai` ; **prix payé = premier échange du jeton dans les
`fenêtre` heures qui suivent T** ; aucun échange = pas d'achat (2 000 à 4 600 côtés sans échange : marchés très minces).

## Résultats (par achat ; t de la moyenne par achat)
| délai / marge / K / précédents / fenêtre / prix min | achats | tous | OUI | NON |
|---|---|---|---|---|
| 2 h / 0,05 / 2 / 3 / 6 h (référence) | 853 | +0,1 % (t +0,0) | −8,2 % (−1,5) | **+7,9 % (+1,5)** |
| 2 / 0,05 / 2 / 3 / **2 h** | 533 | −3,1 % (−0,7) | −19,4 % (−2,9) | +13,5 % (+2,0) |
| 2 / 0,05 / 2 / 3 / **24 h** | 1 158 | +0,4 % (+0,1) | −6,8 % (−1,5) | +7,2 % (+1,6) |
| **12 h** / 0,05 / 2 / 3 / 6 | 679 | +0,4 % (+0,1) | +1,6 % | −0,7 % |
| **24 h** / 0,05 / 2 / 3 / 6 | 531 | −1,5 % (−0,3) | −10,5 % | +5,6 % (+0,9) |
| 2 / **0,08** / 2 / 3 / 6 | 693 | +1,2 % (+0,3) | −9,4 % | +11,2 % (+1,9) |
| 2 / 0,05 / **5** / **5** / 6 | 552 | −1,1 % (−0,2) | −3,8 % | +1,3 % |
| 2 / **0,03** / 2 / 3 / 6 | 956 | −1,6 % (−0,4) | −8,7 % (−1,7) | +5,1 % (+1,0) |
| 2 / 0,05 / 2 / 3 / 6 / **prix min 0,10** | 1 374 | −7,8 % (−2,0) | −18,0 % (−3,3) | +1,2 % |

Neuf réglages. **Les deux côtés ensemble (la règle de la stratégie) : −7,8 % à +1,2 % par achat, jamais significatif**, contre +19 % au test d'origine. Gagnés/attendus par les prix : 420/416 (référence).
Par prix payé (référence) : 0,3-0,5 +1,5 %, 0,5-0,7 +1,0 %, 0,7-0,98 −13,1 %. Trump fait 789 des 853 achats (−1,5 % par achat) : le résultat d'ensemble est celui de Trump.
Par mois (référence) : mai +28 %, juin +30 %, juillet −7 %, août +21 %, septembre +1 %, octobre +2 % : le gain d'origine se concentre sur les premiers mois et disparaît depuis.

**Asymétrie** : le côté OUI perd dans huit réglages sur neuf (−4 % à −19 %, t jusqu'à −3,3 : le taux historique surestime le OUI d'un mot ; 12 h : +1,6 %) et le côté NON va de −0,7 % à +13,5 % (t −0,1 à +2,0, six réglages sur
neuf à plus de +5 %). Cette asymétrie a été **trouvée après coup** (neuf réglages × deux côtés ≈ 18 regards) : c'est un indice, pas une preuve.

## Verdict
- Règle d'origine (deux côtés) : **écartée aux prix payés** (cinquième piste de suite faussée par le prix horaire du CLOB : météo, mentions « annonceurs », tranches, tweets, et celle-ci).
- Côté NON seul : **indice faible** (+5 à +13 %, t +1,0 à +2,0, 18 regards, mois récents à peine positifs) → fantôme `mots_prononces_non` (fille de `mots_prononces` : `only_no`), à confirmer sur de nouveaux marchés.
- `mots_prononces` (mère) reste en arène mais **ne doit pas entrer dans `validated_strategies`**.
