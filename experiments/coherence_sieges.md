# Échelles de sièges de la Chambre contre les marchés de district (31/10/2026)

**Verdict : expérience en fantôme (`sieges_coherence`), pas de test sur le passé possible.** Idée neuve (mécanisme de cohérence entre deux familles de marchés),
demandée par la feuille de mission (« aucun palier depuis 15,9 jours : une idée radicalement différente »).

## La question
Le 03/11/2026 ont lieu les élections de mi-mandat. Polymarket cote, pour 19 États, une échelle « How many House seats will the Democrats win in <État> ? »
(tranches « moins de k », « exactement k », « k ou plus » ; sans frais, 0,4 à 38 k$ de volume par tranche) **et** un marché par district « XX-NN House Election Winner »
(20 à 300 k$ par district). Les deux familles disent la même chose : le nombre de sièges de l'État est la somme des districts. La **moyenne** de cette somme ne dépend
pas de la corrélation entre districts (somme des prix) ; seule la forme de la loi en dépend.

## Relevé (31/10/2026 ~11 h UTC, prix en direct, `scripts/releve.py`, `releve_echelles.json`)
19 échelles, 287 districts relevés (la Californie n'a que 49 marchés de district sur 52 : exclue). Écart « moyenne des tranches − somme des districts » (tranches ouvertes
comptées à leur borne : biais vers le bas d'environ −0,2 à −0,5 pour les États dont le haut de l'échelle pèse, d'où seulement les gros écarts ci-dessous) :

| État | districts | somme des districts | moyenne de l'échelle | écart |
|---|---|---|---|---|
| Caroline du Nord | 14 | 6,77 | 4,93 | **−1,85** |
| Floride | 28 | 9,34 | 8,03 | **−1,32** |
| New York | 26 | 19,91 | 18,86 | **−1,05** |
| Texas | 38 | 12,88 | 11,99 | −0,89 |
| Wisconsin | 8 | 3,60 | 3,28 | −0,32 |
| Colorado, Virginie, Nevada, Ohio, Alabama… | | | | −0,2 à +0,1 (d'accord) |

Probabilité de chaque tranche calculée avec un choc commun entre districts (logit + N(0, s²), s = 0 / 0,5 / 1,0 : `scripts/tranches.py`). Les plus gros écarts tiennent à tous les s :
- **Caroline du Nord « 6 ou plus »** : prix 0,376 ; calculé 0,83 / 0,79 / 0,73. **« exactement 5 »** : prix 0,385 ; calculé 0,13 / 0,15 / 0,15.
- Floride « exactement 4 » : prix 0,135 ; calculé 0,001 / 0,004 / 0,025. « exactement 5 » : 0,117 contre 0,007 / 0,019 / 0,053.
- Caroline du Sud « exactement 1 » : 0,595 contre 0,39. Texas « 14 ou plus » : 0,160 contre 0,31-0,40. Tennessee « exactement 1 » : 0,12 contre 0,28-0,31 (liquidité 514 $ : minces).

## Ce qui est prouvé et ce qui ne l'est pas
- **Prouvé** : à l'instant du relevé, les deux familles ne sont pas d'accord dans une dizaine d'États (écart de moyenne jusqu'à 1,85 siège). Ce n'est pas un effet de la corrélation (la moyenne n'en dépend pas).
- **Pas prouvé** : laquelle a raison. Les districts sont plus échangés ; mais l'échelle peut contenir une information que les districts n'ont pas (carte électorale contestée, un district
  absent du relevé…), ou ses prix peuvent être périmés (liquidité mince). Aucune échelle d'État n'a été réglée sur Polymarket (recherche des événements clos : aucune) : **pas de test sur le passé**.
- Un seul tirage (le 03/11), tranches liées d'un État à l'autre (une vague nationale les fait gagner ou perdre ensemble) : même un gain n'établirait pas un avantage.

## Ce qui a été fait
- `src/polymarket_agent/sieges.py` : relevé des prix démocrates des districts (Gamma, sans clé, 16 appels / 15 min), loi du nombre de sièges (choc commun, 41 quantiles, déterministe), rattachement aux tranches.
- Stratégie `sieges_coherence` (`strategies_v3.SiegesCoherence`, `config/strategies.yaml`) : achète le côté (OUI ou NON) dont la chance calculée, ramenée de 30 % vers le milieu du marché, dépasse le prix demandé d'au
  moins 0,10 ; au plus 2 tranches par État ; demi-Kelly. Fantôme seulement, sans copie du principal tant que rien n'est réglé.
- Cycle local (deux cycles, `--dev-key`) : 16 tranches rattachées, 4 achats (NC « exactement 5 » NON, etc.). Tests : `tests/test_sieges.py` (7).

## À lire le 04/11
Gagnés contre attendus (prix payés) des tranches achetées, État par État ; la somme réelle des sièges de chaque État contre la somme des districts (si les districts sont justes, l'écart de moyenne se referme sur
leur côté) ; carte électorale de la Floride et de la Caroline du Nord en cas d'écart. Extension non faite : « How many Republican Governors after the 2026 midterm » (event 101856) contre les 36 courses de gouverneur, « Senate and House seats »
(event 633839) contre les 435 districts.
