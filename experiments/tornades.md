# Tornades du mois (piste n° 21, 11/11/2026, passage de 6 h)

**Question.** Les marchés « How many Tornadoes in the US in <mois> ? » / « US Tornadoes in <mois> 2026 » (5 à 8 tranches,
`weather_fees`) se trompent-ils sur un décompte qu'on peut lire en partie avant la fin du mois ?

**Règle (lue en entier, marché 6422784).** Décompte mensuel de la page NCEI « U.S. Tornadoes Time Series » ; c'est la PREMIÈRE
valeur publiée après la date prévue (≈ 8-10 jours après la fin du mois) qui compte, même préliminaire.

**Source de règlement lisible** : `www.ncei.noaa.gov/access/monitoring/tornadoes/time-series/1/<mois>/data.json` (et `data.csv`),
sans clé. **La valeur préliminaire NCEI = la somme des rapports FILTRÉS du SPC** (`www.spc.noaa.gov/climo/reports/AAMMJJ_rpts_filtered_torn.csv`,
jour SPC = 12 h UTC → 12 h UTC) : identiques de janvier à septembre 2026 (23, 55, 211, 306, 174, 399, 137, 100, 57), octobre 53 contre 54.
MAIS des rapports tardifs s'ajoutent après le règlement : juillet vaut 137 aujourd'hui et a été réglé « 100-129 », août vaut 100 et a
été réglé « 80-99 ». Novembre et décembre 2025 sont passés en valeurs finales (12 et 14 contre 14 et 16 au SPC).

**Test (`tornades/test_passe.py`, `analyse.py`).** 10 mois réglés (novembre 2025 → août 2026), 65 tranches, 5 dates (jours 5, 10, 15,
20, 25 à 14 h UTC). Modèle : compte SPC des jours ≤ d − 2 + reste du mois tiré de la base finale SPC 1995-2024 (même fenêtre de jours,
30 années, lissage). Regard vers le futur connu : les fichiers SPC d'aujourd'hui contiennent les rapports tardifs ; testé avec le compte
réduit de 7 % et de 15 %.

| | jour 5 | jour 10 | jour 15 | jour 20 | jour 25 |
|---|---|---|---|---|---|
| log-loss modèle (compte × 0,93) | 0,331 | 0,342 | 0,285 | 0,205 | 0,160 |
| log-loss prix horaire du marché | 0,422 | 0,394 | 0,301 | 0,272 | 0,201 |

Aux vrais prix (premier achat preneur dans les 6 h, un pari par tranche au premier signal, frais 5 % × p(1−p)) :
seuil 0,05 → 11 à 14 paris selon le compte (× 1 / 0,93 / 0,85), gagnés 7-8 pour 7,2-8,7 attendus, rendement +27 % / +25 % / +7 %,
2 mois gagnants sur 5, t par mois 0,5-0,6 ; seuil 0,03 : +1 % / −5 % / −11 % ; seuil 0,10 : +35 % / +21 % / +9 %. 9 réglages essayés.
Achats de 10 à 20 parts (médiane) : marchés très minces.

**Paris de fin de mois seulement** (jour ≥ 15 ou ≥ 20) : 4 à 11 paris, de +36 % à −76 % selon la correction et le seuil ; jour ≥ 20 : 1 gagné sur 4-5 pour 1,7-2,0 attendus. Les prix de fin de mois intègrent déjà le compte.

**Verdict : indice faible, non concluant ; pas de fantôme allumé.** Le modèle lit mieux la distribution que les prix horaires (qui sont surtout
des milieux de carnets vides), mais aux prix payés l'avantage ne se distingue pas du hasard (5 mois avec des paris, t < 1) et dépend
du regard vers le futur des rapports tardifs. Deux pistes pour le rendre net : (1) relever chaque jour le compte SPC tel qu'il est
publié (journal versionné, plus de regard vers le futur) ; (2) utiliser les perspectives du SPC (jours 1 à 8) pour le reste du mois.

**Ce qui est en place.** Source `tornades` (cycle, toutes les 3 h : rapports SPC du mois et décompte NCEI, `n0` = premier compte lu de
chaque jour) et stratégie `tornades_mois` (`strategies_v3.TornadesMois`, `tornades.py`) écrite et testée mais **éteinte** : au cycle local
du 11/11 elle a acheté le NON « 10-24 » à 0,60 (loi 0,70) alors que les perspectives du SPC annoncent une semaine calme, ce que la loi
ignore. À rallumer quand le journal `n0` aura 2-3 mois et que la loi tiendra compte des perspectives (jours 1-8).

**Novembre 2026 (aujourd'hui).** 7 tornades au SPC du 1er au 10/11 ; perspectives SPC : risque marginal le 11, rien le 12, isolé au
Texas le 14-15 et en Californie / Arizona le 16-17. Loi (7 + semaine calme + climatologie du 19 au 30) : < 10 : 0-0,27 ; 10-24 :
0,5-0,73 ; 25-39 : 0,10-0,17 ; 40-59 : 0,03-0,07 ; 60+ : 0,10-0,17. Carnet : 60+ vendu 0,064 (milieu 0,034) : après rapprochement
vers le milieu (skill `prevoir-un-marche`), 0,067-0,10, sous le seuil d'une conviction.
