# UFC : somme des méthodes de victoire et accord entre marchés (piste n° 6 de `vingt_cinq_pistes.md`, 23/10/2026)

**Question** : dans un combat UFC, « KO ou TKO » + « soumission » + « aller à la distance » doivent valoir 1 ; « KO du combat » = « KO du combattant A » + « KO du
combattant B ». Un trio de jambes qui paie un montant connu pour moins que son prix est un arbitrage ; achète-t-on de tels trios aux vrais prix ?
Trios : **A** OUI(KO)+OUI(soumission)+OUI(distance) paie 1 ; **B** les trois NON paient 2 ; **C** OUI(KO combat)+NON(KO A)+NON(KO B) paie 2 ; **D** NON(KO combat)+OUI(KO A)+OUI(KO B) paie 1.

**Données** (scripts : `experiments/ufc_coherence/`, données ignorées par Git) : 687 événements UFC clos (série 38), dont 620 depuis juin 2025 ; 549 combats avec les cinq
marchés nécessaires ; **893 438 échanges réels** (data-api). Gain = paiement RÉEL (résultats lus, pas supposés) − prix des échanges − frais (0,05·p·(1−p) par jambe).

## Historique, aux prix des échanges (chaque jambe = premier échange dans une fenêtre W après l'heure d'achat, de J−3 au coup d'envoi)
| fenêtre W | trio A | trio B | trio C | trio D |
|---|---|---|---|---|
| 30 min | 31 instants, 0 positif | 9 instants, 5 positifs (gain moyen −0,4 %) | 10, 5 positifs | 19, 2 positifs |
| 2 h | 297, 4 positifs | 121, 44 positifs | 186, 56 positifs | 178, 15 positifs |
| 6 h | 1 399, 48 positifs | 850, 260 positifs | 1 048, 275 positifs | 1 028, 114 positifs |

Gain moyen par instant : −0,2 € (A), −0,07 € (B), −0,06 € (C), −0,15 € (D) par euro de paiement. Les instants « positifs » (+17 % à +57 % par euro)
viennent d'échanges de jambes éloignés de plusieurs heures (prix périmés) : avec 30 minutes d'écart il n'y a presque plus d'instants, avec 6 heures le « gain »
grandit, signe de prix non simultanés et non d'un arbitrage. **Les échanges sont trop rares** (un combat de 9 marchés : médiane 1 034 échanges en tout) pour tester ces trios
au prix payé ; la seule mesure juste est celle des carnets.

## En direct (carnets du 23/10, 28 combats ouverts, `direct.py`)
Coût (meilleurs vendeurs + frais) de chaque trio moins son paiement : **aucun trio n'est un arbitrage**, le meilleur est à −0,047 par euro (trio B), les trios A et D à
−0,3 à −1,9 (somme des meilleurs vendeurs OUI de 1,2 à 1,7 : écarts larges entre vendeurs et acheteurs). Les combats de la carte d'après-demain ont des carnets quasi vides (0,99).

## Verdict : **écartée**
Pas d'arbitrage dans les carnets actuels, et l'historique ne permet pas d'en voir (échanges trop dispersés dans le temps). Rien dans l'arène. À reprendre seulement si un relevé de
carnets toutes les 5 minutes (le cycle les lit déjà : table `book_snapshots`) montre un trio sous son paiement.
