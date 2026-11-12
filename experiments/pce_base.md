# Piste n° 37 : PCE de base après le CPI et le PPI (12/11/2026, passage de 11 h)

**Question** : quand le CPI et le PPI du mois sont publiés (≈ 2 semaines avant le PCE), le marché « Core PCE MoM / YoY - <mois> »
paie-t-il trop peu la tranche que ces chiffres désignent ?

**Données** (`pce_base/scripts/releve.py`, `prix.py`, données dans `pce_base/donnees/`, ignoré par Git) : `public-search` de Gamma,
10 événements « Core PCE » (juin à octobre 2026 ; avant juin, aucun marché), 8 réglés, 7 tranches chacun (56 tranches) ;
prix horaires (`prices-history`, fidelity 60) de chaque OUI. Frais : `economics_fees` (septembre : `zero_fees`).

**Contrôle du règlement** : tranches gagnantes relues (`outcomePrices` 1/0, UMA « resolved » à 8 h 30 ET + 6 min).

## Résultat

Le PPI sort ≈ 14-16 jours avant le PCE. Tranche la mieux payée à J-10 (après CPI et PPI) :

| Événement | Favori à J-10 | Gagnant |
|---|---|---|
| MoM juin | 0,2 % à 0,58 | 0,1 % (0,18) |
| YoY juin | ≤ 3,3 % à 0,76 | oui |
| MoM juillet | 0,2 % à 0,55 | oui |
| YoY juillet | 3,3 % à 0,63 | oui |
| MoM août | 0,3 % à 0,71 | 0,2 % (0,28) |
| YoY août | 3,4 % à 0,32 | ≤ 3,0 % (0,06) |
| MoM septembre | 0,3 % à 0,65 | oui |
| YoY septembre | 3,1 % à 0,54 | oui |

**5 gagnés pour 4,75 attendus** : après le PPI, le marché est calibré. Les deux erreurs du MoM sont des tranches voisines à la
frontière d'arrondi (0,1/0,2 et 0,2/0,3) : seule une estimation au centième (« core PCE tracking 0,24 % ») pourrait les trancher.
Ces estimations existent (banques, reprises par FXStreet, TMGM, Reuters) mais **pas de source gratuite et lisible par script** :
FXStreet est derrière Cloudflare (pas de contournement, règle n° 7), Google Actualités ne donne que les titres. Sans elles,
rien à tester ; avec 4 mois, rien à conclure non plus.

**Cas d'août (YoY, ≤ 3,0 % gagnant à 0,04-0,07 la veille)** : le BEA a publié sa **mise à jour annuelle** (révision de tout
l'historique des prix) LE MÊME JOUR que le chiffre d'août (30/09, « PCE price revisions », Continuum ; article RBC du 24/09 sur
une « révision rétroactive »). Rien n'était lisible avant : pas d'avantage, mais un risque de règle : chaque fin septembre, les
tranches YoY portent un risque de révision que le marché ne paie pas (un cas, à relire en septembre 2027).

## Verdict

**Écartée en l'état** (marché calibré après le PPI, 5 pour 4,75 ; pas de source gratuite des estimations au centième ; 4 mois
réglés). À reprendre seulement si une source gratuite d'estimations « tracking » apparaît (la Fed de Cleveland publie un
« nowcast » du PCE de base, mais c'est un modèle, pas les composantes du PPI ; non testé ici). Octobre : PPI le 13/11, PCE le 25/11 ;
marché MoM 0,3 % à 0,58, 0,4 % à 0,35 (12/11).
