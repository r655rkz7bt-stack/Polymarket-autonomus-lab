# Enquête du 22/10/2026 (après-midi) : le principal copie-t-il la championne à la bonne taille ? Des positions ne sont-elles jamais réglées ?

Déclencheurs : les 6 obligations de la feuille de mission (mêmes que ce matin : `champion_sans_avantage` ×3, `chance` ×3, déjà
traitées dans `2026-10-22_championne_biais_et_mises.md` et `..._midi_...`), un constat « à regarder » (mise de fantôme à 45 % de son
capital : `nf_sport_patiente`, « Alex Michelsen », 475 €, 22/10 14 h 05) et la famille du jour (22 % 6 + 1 = 5, puis 6). Scripts
reproductibles : journal signé du principal et du fantôme dans `published_data/ledger/` (comparaison jeton par jeton).

## 1. Copie du principal (famille 1/5) : jeton par jeton, cycle par cycle
- 56 achats du principal (`nf_sport_patiente`, 1 560 €) contre 145 du fantôme ; depuis le 19/10 02 h 28 le fantôme fait 88 achats, **67 jetons
  copiés** (5 253 € sur 6 786 €), 21 non copiés (13 d'entre eux datent du 22/10 : copie faite au cycle suivant).
- Taille copiée : **médiane 0,338 de la mise du fantôme** (51 jetons ; 0,32-0,38 à tous les prix de 0,85 à 0,93) = la part de l'avantage mesuré
  sur l'avantage supposé (`mise_avantage_mesure`). Deux extrêmes expliqués : mises du fantôme de 12 € copiées à 94-111 % (ticket minimal de
  ~10 €), et mises énormes du fantôme copiées à 2-8 % (10-11 € pour 474 € à 0,924 et 122 € à 0,81).
- **Conclusion : pas de défaut de copie.** Le principal n'a pas pris la mise de 475 € du fantôme (10,6 €). Les mises à 45 % du capital
  restent dans les fantômes : elles gonflent leurs euros (déjà géré : confiance sur le rendement par mise, contrôle `mises` et `estimation_gonflee`).
- Limite connue : le ticket minimal (~10 €) donne aux petites convictions un poids relatif supérieur ; effet de l'ordre de 100 € sur 1 560 €, pas d'action.

## 2. Ce qui ne tourne plus / positions jamais réglées (famille 6)
- 405 marchés avec une position ouverte depuis plus de 24 h dans les 136 journaux ; **121 sont déjà clos sur Gamma**, mais 105 d'entre eux
  appartiennent à des fantômes éliminés ou désactivés (dernier battement de cœur plus ancien que 18 h : plus de cycle, donc plus de règlement : normal).
- Sur les fantômes encore actifs : 16 marchés clos, tous « resolved » sur Gamma ; les marchés de température (fin 20/10 12 h UTC) ne passent
  « resolved » que le 22/10 entre 07 h et 11 h (litige UMA de 2 jours : le règlement du code attend bien `umaResolutionStatus = resolved`,
  `settlement.resolution_payout`). Aucune position jamais réglée par défaut de code.
- Les deux cas qui ressemblaient à des fantômes « éteints sans être marqués » (`nf_sport_patiente_demi_mise`, `nf_sport_tres_court`, dernier battement 21/10 20 h 22) sont déjà `enabled: false` : cohérent.

## Résultat
Aucun défaut nouveau ; ce qui a été vérifié et comment sont écrits ci-dessus. Aucun changement de code. Prochain contrôle utile : le même
rapport copie/mise à chaque passage si la mise du principal change (`mise_avantage_mesure`).
