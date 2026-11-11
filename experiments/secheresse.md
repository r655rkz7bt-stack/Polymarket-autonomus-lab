# Sécheresse exceptionnelle (D4) par État (piste n° 24, 11/11/2026, passage de 11 h)

**Question.** Les marchés hebdomadaires « Exceptional drought (D4) by state — week of <mardi> » (un marché OUI/NON par État, 33 à 40
États selon la saison, `weather_fees`) cotent-ils correctement ce que la carte de la semaine d'AVANT, déjà publiée, dit déjà ?

**Règle (événement 1319882, lue en entier).** OUI si la carte US Drought Monitor « de la semaine » (carte du mardi, publiée le jeudi à
8 h 30, heure de l'Est) met au moins 0,05 % de la surface de l'État en D4 ; première publication finale ; en dessous de 0,05 % = bruit de
frontière, NON. L'événement se ferme le jeudi vers 14 h UTC.

**Source.** API de l'université du Nebraska, sans clé : `usdmdataservices.unl.edu/api/StateStatistics/GetDroughtSeverityStatisticsByAreaPercent?aoi=<FIPS,…>&startdate=M/J/AAAA&enddate=…&statisticsType=2`
(en-tête `Accept: application/json` ; catégories exclusives none/D0…D4 en %). 48 États × 2000-2026 = 67 344 cartes (`analyse.py`, `releve.py`).

**Loi de transition (2000-2025, tous les États).** Chance d'avoir D4 >= 0,05 % une semaine plus tard selon la carte connue :

| case de la carte connue | 1 semaine | 2 semaines | cartes |
|---|---|---|---|
| D4 >= 5 % | 0,980 | 0,958 | 3 107 |
| D4 0,05-5 % | 0,920 | 0,852 | 1 959 |
| D4 < 0,05 % | 0,142 | 0,191 | 80 |
| pas de D4, D3 >= 10 % | 0,044 | 0,081 | 3 271 |
| D3 1-10 % | 0,015 | 0,031 | 4 137 |
| D3 < 1 % | 0,004 | 0,011 | 1 268 |
| D2 au plus | 0,000 | 0,000 | 51 362 |

**Marchés réglés.** 12 événements (semaines du 25/08 au 03/11/2026), 466 marchés, 433 clos. **Règlement retrouvé 433/433** avec la
carte du mardi de la semaine. 2 311 vrais échanges (data-api v2, `event_id`).

**Aux prix payés, sans regard vers le futur.** Chaque échange est classé selon la dernière carte PUBLIÉE à son heure (jeudi 8 h 30 ET) :
1 275 échanges avant la publication (carte de la semaine d'avant connue), 1 022 après (réponse connue). Le preneur achète un jeton
(ou vend l'autre : on aurait pu acheter le côté opposé à 1 − prix) ; frais 5 % × p(1 − p).

- Avant publication, tous les échanges que la loi dit bons d'au moins 0,05 : 223 échanges, 84 marchés, **213 gagnés pour 211,0 attendus
  par la loi et 150,1 par les prix**, +42 % ; les échanges contre la loi : 30 gagnés pour 32,8 attendus et 69,7 payés, −56 %.
  La loi est calibrée ; les prix ne le sont pas.
- **Un achat par marché** (premier échange bon), `idea_test.verdict`, 16 réglages (seuil 0,02/0,05/0,10/0,20 ; prix >= 0 ou 0,10 ;
  >= 0 ou 20 parts) : **tous « retenue »**, 43 à 141 paris, z des prix +7,0 à +9,3. Référence (seuil 0,05, prix >= 0,10) : 83 paris,
  8 semaines, **+113 % par mise**, confiance par semaine 3,12, z des prix +7,05, 3 mois sur 3 ; sans la meilleure semaine (15/09) +94 %.
  Par prix : 0,10-0,30 +425 % (17), 0,30-0,70 +74 % (23), >= 0,70 +9,6 % (43).
- Après publication (réponse connue, marché encore ouvert) : 16 échanges bons, 16 gagnés, +27 % ; petit.
- Tailles : 10 266 parts, 6 974 $ échangés dans le bon sens en 8 semaines ; >= 100 parts : 31 échanges, +44 %.
- Les seuls perdants : Utah semaine du 22/09 (D4 0,05-5 % → disparu), Wisconsin (D3 >= 10 % → D4), Caroline du Sud 25/08.

**Pourquoi ça marche (hypothèse).** Personne ne lit la carte : les carnets sont tenus par un teneur de façade (0,01 / 0,99, 5 parts) et
quelques joueurs qui échangent au milieu (0,5) ou parient à l'instinct ; la carte bouge d'au plus une catégorie par semaine.

**Limite majeure.** Les échanges avant publication se sont arrêtés : 48-384 par semaine de fin août au 06/10, 11 la semaine du 20/10,
**0 depuis** (le 11/11 : 33 marchés, tous à 0,01/0,99 sauf Arizona OUI vendu 0,28 — pas de D3, loi 0,000 : il faudrait vendre le OUI,
personne n'achète). Le volume de l'événement est passé de 25 k$ (01/09) à 460-837 $ (novembre). L'avantage est mesuré mais peut ne plus
être disponible.

**Verdict : retenue sur le passé** (règlement 433/433, loi calibrée, 16 réglages, 3 mois) **mais non exécutable aujourd'hui** →
fantôme `secheresse_d4` (Kelly entier sur la borne basse, `strategies_v3.SecheresseD4`, source `usdm`, étiquette 105721) qui n'achète
que si un vendeur revient à un prix faux. Pas d'entrée au principal (`validated_strategies`) tant qu'il n'a pas de paris réels.

**Suite du même passage : « How many states will be in D4 — week of … »** (`secheresse/nombre_etats.py`, 8 semaines, 48 tranches).
Loi du nombre = somme de Bernoulli indépendantes (loi par État, carte de la semaine d'avant) : moyenne 9,8-11,6 pour 10-12 réalisés ;
règlement 48/48. Un achat par tranche (prix >= 0,10) : seuil 0,02 → 9 paris, 8 gagnés pour 8,0 (loi) et 6,4 (prix), +33 % ; 0,05 → 7
paris, +42 % ; 0,10 → 4 paris, +96 %. **Trop peu de paris (4-9, 30 échanges par semaine au plus) : non concluant, pas de stratégie.**

**Cycle local (11/11, 2 cycles).** Source `usdm` « ok (144 prix relevés) » ; référence `secheresse` rattachée à 31 marchés ;
`secheresse_d4` : 0 proposition, abstentions « issue hors de la plage de prix ou carnet vide » 28 (cotes de façade 0,99) et « avantage net
insuffisant » 3 (OUI vendus 0,25-0,28 pour des États sans D3 : le bon côté serait le NON, que personne ne vend) : conforme.

**À reprendre.** Les autres marchés de la même source : « Percent of Corn / Cattle / Hay … in drought » (statistiques agricoles du même USDM : 8 marchés à 6 tranches
par semaine en octobre, quelques centaines de $ chacun), « Peak Severe Drought in Minas Gerais » (Brésil, autre source).
Scripts : `secheresse/releve.py` (relevé), `analyse.py` (loi, règlement, échanges), `verdict.py` (16 réglages) ; résultats :
`secheresse/resultats_11_11.txt`.
