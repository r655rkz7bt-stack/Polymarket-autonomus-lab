# Rallies de Trump et marchés « dira-t-il tel mot ? » (26/10/2026)

**Verdict : indice (biais du OUI, confirmé sur un échantillon neuf mais pas aux vrais prix) → fantômes `rallies_non`, `rallies_non_favori`, `mentions_non`, `mentions_non_outsider` (quart de Kelly).** Le modèle « même mot aux meetings précédents » est écarté (il fait moins bien que le marché).

## Pourquoi cette piste
`mots_prononces` (retenue le 20/10 : +19 à +27 % par achat sur 3 000 marchés « mentions ») fait **+0,1 % sur 50 paris réglés en direct** (21 gagnés pour 23,4 attendus par les prix, z −0,7 ; 28 NON : −5,8 %), alors que
tout son direct est du même type : les meetings de mi-mandat de Trump (NC, SC, Iowa, Floride, Géorgie, Michigan : 20 mots par meeting, toujours la même liste : « Russia or Ukraine », « Hell 15+ times », « Iran 5+ times », « AI »…).
Son estimation dépasse ce qui arrive (27,4 gagnés annoncés, 21 réalisés) : `scripts/mots_prononces_direct_26_10.py` (dans `enquetes/scripts/`). Question : ce type d'événement, précis et répété, a-t-il son propre biais ?

## Données (`experiments/rallies_trump/scripts/releve.py`, `donnees/` ignoré par Git)
69 événements « What will Trump say during … rally », 2024 (campagne, 40 meetings à 0,4-1,7 M$ de volume) et 2026 (mi-mandat, ≈ 25 meetings à 20-80 k$) ; 1 371 marchés, 1 359 avec prix horaires du CLOB (14 jours par appel),
règlement lu sur Gamma (`outcomePrices` 0/1 : 1 371 sur 1 371 nets). Pas d'échanges réels relevés (marchés minces) : **les prix sont ceux du CLOB, pas des prix payés** (voir « Limites »).

## Résultats
1. **Modèle de gabarit** (`analyse.py`) : taux du mot sur les meetings PASSÉS de la même campagne (au moins 3 passages, lissé vers le taux de tous les mots, k = 2), prix à 6 h après l'ouverture : log-score **modèle −0,565 contre marché −0,515**
   (260 marchés). Achats quand le modèle s'écarte de 5 points : +2,6 % (t par meeting +0,2) ; à 10 points ou à 24 h : −6 à −13 %. **Écartée** : le marché connaît le gabarit.
2. **Biais du OUI** (`calibration.py`, 1 285-1 319 marchés) : prix moyen du OUI 0,51, réalisé 0,467 (−4,6 points), à 2, 6 et 24 h. Par tranche, le OUI réalisé est sous son prix dans 0,30-0,75 à tous les délais
   (0,45-0,60 : 0,517 → 0,414 à 2 h, 0,521 → 0,426 à 6 h, 0,522 → 0,439 à 24 h) ; en dessous de 0,15 le OUI perd plus encore mais son NON ne rapporte rien (+1 à +3 %) ; au-dessus de 0,75 rien.
3. **NON quand le OUI vaut 0,40-0,70** (frais 0,04·p(1−p) et écart 0,02 comptés), rendement groupé par mise, bootstrap par meeting : 6 h **+9,2 % IC95 [−1,4 ; +20,4]** ; 24 h **+11,2 % [+1,0 ; +20,9]** (66 meetings, ≈ 500 achats) ;
   2024 +5 à +18 % par achat et 2026 +9 à +13 % par achat (mêmes signes), mais par meeting t +0,3 à +1,6. Sur les seuls meetings de 2026 en heures avant la fin (26 meetings) : +4 à +16 %, IC95 de ±20 points (tous contiennent 0).
   Découpage : OUI à 0,50-0,70 (NON outsider 0,30-0,50) +6,6 % à 6 h, +13,7 % à 24 h [+1,3 ; +26,6] ; OUI à 0,40-0,50 (NON favori) +13,0 % à 6 h [−1,5 ; +26,8], +7,3 % à 24 h.
4. **Réglages regardés** : ≈ 35 (délais 2-48 h, bornes de prix, campagne, modèle k/marge) : le signe du NON est positif partout, la significativité nulle ou limite. **Aucun** ne dépasse t 2 par meeting.

## Contre-épreuve sur un échantillon neuf : tous les marchés « What will X say … » (hors meetings)
`scripts/releve_mentions.py` : 884 événements, **13 513 marchés de 745 événements** (Trump hebdomadaire et discours, Leavitt, Starmer, Powell, NYT, MrBeast, commentateurs…), prix horaires du CLOB à 6 et 24 h après l'ouverture ; `scripts/biais_oui_mentions.py`.
OUI réalisé **0,458 pour un prix moyen de 0,502** (−4,4 points), 24 h : 0,457 pour 0,502. NON, frais 0,04·p(1−p) et écart 0,02 comptés, bootstrap par événement (IC95) :

| OUI | 6 h | 24 h |
|---|---|---|
| 0,15-0,30 | +4,9 % [+1,9 ; +7,7] | +5,9 % [+3,4 ; +8,4] |
| 0,30-0,45 | +8,9 % [+4,9 ; +12,6] | +8,0 % [+4,3 ; +11,3] |
| 0,45-0,60 | +4,1 % [0,0 ; +8,2] | +7,4 % [+3,1 ; +11,7] |
| 0,60-0,75 | −3,6 % [−11 ; +3] | −2,9 % [−10 ; +5] |
| 0,75-0,97 | −18 % [−28 ; −7] | −13 % [−24 ; −3] |
| 0,40-0,70 | +4,6 % [+1,0 ; +8,2] | +5,9 % [+2,0 ; +10,0] |

Sans les prix à exactement 0,50 (12 % des cas à 6 h : carnet vide) et avec les prix datés de moins de 3 h : +4,0 à +6,4 %, IC95 qui ne contient pas 0 (sauf « prix stable + hors 0,50 » à 6 h : [0,0 ; +8,3]). Sans frais (les mentions sont `feesEnabled false` chez Gamma) : +1 à +2 points de mieux.
Par orateur (OUI 0,40-0,70, 24 h) : Trump (2 720 paris) **+3,2 % [−2,6 ; +9,5]**, commentateurs −1,0 %, Starmer +0,1 %, Leavitt +12,5 %, NYT +27,6 %, MrBeast +23,1 % : l'effet est surtout hors Trump, donc hors du lot où les meetings pèsent le plus.
**Aux prix réellement payés** (`scripts/prix_payes_mentions.py`, 150 événements tirés, 1 053 paris candidats à 24 h) : seulement **231 (22 %)** ont un achat réel du NON par un preneur dans les 2 h ; à ce prix payé (moyenne 0,556, contre 0,48 au CLOB) : **+9,0 % [−2,8 ; +22,1]** (78 événements).
Le prix du CLOB sous-estime donc le coût du NON de 7 points dans le sous-échantillon qui s'échange, et le sous-échantillon est choisi par l'échange (un preneur qui achète le NON en sait peut-être plus : biais possible dans les deux sens) : **le gain n'est pas prouvé aux prix payés**, il est « indice ».
Les 4 fantômes sont la manière de le vérifier en direct, aux prix et aux carnets réels.

## Limites
- Prix du CLOB (pas de prix payés) : les marchés de 2026 sont minces (20-80 k$ par meeting, ≈ 2-4 k$ par mot) ; le NON à 0,30-0,60 s'achète-t-il vraiment à ce prix + 0,02 ? Les 28 NON de `mots_prononces` en direct (écart d'achat inclus) : −5,8 % (z −0,5, bruit).
- Les mots d'un meeting sont liés (durée du discours) : l'IC par meeting en tient compte, pas les ±5 points de la loi binomiale.
- Même famille que `mots_nouveaux` (NON +16 %, indice), `candidats_non`, `saison_non` : « le OUI est un peu trop cher quand il y a beaucoup d'issues ». Trois indices faibles de même sens ne sont pas indépendants (même biais OUI).

## Suite
Fantômes `rallies_non` (OUI 0,50-0,70, NON ≤ 0,50, `underdog`) et `rallies_non_favori` (OUI 0,40-0,50), 3 à 20 h avant le meeting, quart de Kelly, biais 0,05. Les meetings de Trump se succèdent jusqu'au 03/11 : une quinzaine de meetings d'ici là, soit 50-100 paris par fille.
À juger sur ces paris NEUFS (pas sur les chiffres ci-dessus) ; si le NON de `mots_prononces` reste négatif en direct (28 paris, −5,8 %), c'est que le coût d'exécution mange l'avantage du CLOB.
