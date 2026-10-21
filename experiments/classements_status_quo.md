# Piste n° 2 : classements « status quo » (21/10/2026, soir)

**Question** : dans les marchés « qui sera n° 1 / n° 2 / n° 3 à la fin du mois » (modèle d'IA, plus grande entreprise, applis de l'App Store, artiste Spotify),
le leader du moment garde-t-il sa place plus souvent que son prix ne le dit ?

**Données** : 211 événements réglés (Gamma `public-search` puis `/events/<id>`) : IA 1er/2e/3e rang 25/11/8, plus grande entreprise 13/13/11, appli gratuite
63, appli payante 61, Spotify 6. Prix « Oui » de chaque case : CLOB `prices-history`, pas de 12 h (les marchés clos refusent les pas fins). Vrais échanges :
`data-api/trades?eventId=` (11 000 derniers échanges au plus). **Règlement relu** : exactement un « Oui » à 1 par événement, 209 / 211 (2 écartés : sans date de fin).
Aucun regard vers le futur : le leader à J-k est la case au prix le plus haut au dernier point connu avant J-k.

## 1. Contre le marché (prix historique, non exécutable) : gagnés contre attendus
| famille | J-30 | J-14 | J-7 | J-3 | J-1 |
|---|---|---|---|---|---|
| IA 1er rang | 17/15,0 | 19/18,6 | 24/23,2 | 25/24,2 | 25/24,5 |
| IA 2e rang | 8/7,0 | 11/8,3 (z +2,0) | 11/9,8 | 11/10,2 | 11/10,6 |
| IA 3e rang | 7/4,0 (z +2,4) | 8/5,4 (z +2,2) | 6/6,5 | 7/6,9 | 8/7,6 |
| plus grande entreprise (1er) | 10/8,9 | 11/10,8 | 12/12,4 | 12/12,6 | 12/12,9 (**z −2,9**) |
| appli gratuite n° 1 | – | – | 1/2,8 | 22/27,1 (**z −2,1**) | 36/39,1 |
| appli payante n° 1 | – | – | 4/3,4 | 24/23,8 | 32/31,5 |
| Spotify | – | 5/4,6 | 5/4,7 | 5/4,9 | 5/4,8 |

Lecture : le leader des classements d'IA gagne un peu plus que son prix à 14-30 jours (excès de +6 et +5,7 victoires sur ~78 cas à J-30 / J-14) puis plus rien près
de la fin (le prix a déjà tout intégré). À l'inverse, **l'appli gratuite n° 1 gagne moins que son prix** (J-3 : 22 pour 27,1 attendus ; l'ordre change souvent)
et la plus grande entreprise à J-1 perd sur un cas rare (12 sur 13 à 0,99).

## 2. Aux prix réellement payés (premier échange acheteur dans les 2 h après la décision, frais du marché)
Seuls 327 paris ont un échange (252 sans échange : marchés minces, ou échanges plus vieux que les 11 000 derniers). IA, leader 0,70-0,95 :
| décision | paris | gagnés / attendus par les prix payés | rendement par achat |
|---|---|---|---|
| J-14 | 12 | **12 / 10,6** | +13,0 % |
| J-14 + J-30 | 15 | 15 / 13,2 | +13,5 % |
| J-7 + J-14 + J-30 | 28 | 27 / 24,9 | +9,0 % |
| J-7 seul (IA, tous prix) | 24 | 21 / 21,1 | −5,3 % |
| J-3 seul (IA, tous prix) | 31 | 30 / 29,4 | +0,6 % |

Plus grande entreprise : J-14 +0,1 %, J-7 +3,5 %, **J-3 −13,2 %, J-1 −17,9 %** (t par événement −2,0 et −2,3). Applis : J-3 −10,1 %, J-1 −9,0 %. Ces trois familles : écartées.

## 3. Pourquoi « indice » et pas « retenue »
- `idea_test.verdict` répondait **« retenue »** (t par événement +6, 9 mois sur 9) : c'est un artefact. Quand aucun pari ne perd, l'écart-type des gains est minuscule et le t explose.
  Aux prix seuls, **P(les 12 gagnent) = 23 %** (produit des prix : 0,78 × 0,80 × … × 0,95). Les gagnés (12) ne dépassent pas les attendus (10,6) de plus d'un écart-type.
- ~45 découpages regardés (9 familles × 5 délais) : les cases à z ≈ +2 (IA 2e et 3e rang à J-14) sont ce que le hasard donne en 45 essais.
- Les trois rangs d'IA d'un même mois sont liés (même classement) ; 9 mois seulement ; les échanges ne couvrent que 17 des 40 cas à J-14 (biais de survie).
- Correctif du jugement : `idea_test.verdict` calcule maintenant `z_prix` (gagnés − Σ prix payés, divisé par √Σ p(1−p)) et ne dit « retenue » qu'avec `z_prix ≥ 1,5`
  (sinon « indice », raison écrite). Test : `test_verdict_does_not_retain_a_run_of_wins_the_prices_already_explain`.

## Verdict : **indice** (IA seulement) ; plus grande entreprise, applis, Spotify : **écartées**
Arène : fantôme `statu_quo_ia` (naive_favorite filtré : question contenant « best ai model », issue Oui, échéance 12 à 35 jours, prix 0,70-0,95, demi-Kelly).
Les cases « Company A/B » à 0,50 sans vendeur (ask 1,00) ne sont jamais achetées. Prochains marchés : fin novembre (prix de Google 0,58 aujourd'hui), fin décembre, 2026.
À confirmer sur ≥ 10 nouveaux mois avant toute promotion.

Scripts : `experiments/classements_status_quo/scripts/` (`chercher.py`, `releve.py`, `analyse.py`, `prix_payes.py` ; données dans `donnees/`, ignoré par Git).
