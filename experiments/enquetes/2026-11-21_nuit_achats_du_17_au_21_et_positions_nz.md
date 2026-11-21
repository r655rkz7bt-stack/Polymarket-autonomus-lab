# Enquête du 21/11/2026 (passage de 1 h) : achats du 17 au 21/11 relus, positions « oubliées » de Nouvelle-Zélande

Jour 21 → famille (21 mod 6) + 1 = **4** (rattachements et achats relus à la source). Aucune « Enquête obligatoire » dans la feuille
de mission (seule obligation : idée radicalement différente, aucun palier depuis 8,5 jours).

## Constat « positions ouvertes bien après l'échéance » (`favori_politique_quasi_certain`, 5 positions, +308 h)

Les 5 marchés (2118145, 2116493, 2116494, 2117123, 2117124) relus sur Gamma `/markets/<id>` : tous sont l'élection législative
néo-zélandaise (« National most seats », « Labour second-most seats », marges du vote populaire 0-5 %), `closed: false`, `endDate`
08/11 04 h 59 = date provisoire. Le résultat officiel (Electoral Commission, bulletins spéciaux compris) est attendu le 27/11 : le
marché attend sa source, pas un règlement manqué. **Pas de défaut.** Ces positions expliquent en partie le constat `capital_bloque`
(27 € disponibles sur 1 019 €, 31 positions) : voulu pour une stratégie qui achète à 0,96-0,98 et attend le règlement.

## Famille 4 à la main : 32 achats des fantômes v2 depuis le passage du 17/11 à 21 h

Liste tirée des journaux signés publiés (`published_data/ledger/fantome_v2`). 15 achats relus contre Gamma et, pour le Maryland,
contre la page officielle (`elections.maryland.gov`, « Last refreshed 11/20/2026 06:47:33 PM ») :

| stratégie | marché | achat | relu |
|---|---|---|---|
| marges_californie | MD-06 D « 20-25 % » OUI | 0,908 (chance 0,99) | marge officielle **21,69** (dans la tranche) ; Gamma affiche 0,5/0,5 = milieu d'un carnet vide, pas un prix |
| marges_californie | MD-04 D « 85-90 % » NON | 0,907 (0,99) | marge **83,29** (hors tranche) ; Gamma 0,385/0,615 = milieu |
| marges_californie | CA-30 D « 50-55 % » NON, CA-43 « 65 %+ » OUI | 0,75 / 0,90 | dans les plages de la stratégie, chances écrites conformes au calcul |
| taux_tresor_empirique | 6 barrières (30 ans 5,49/5,53, 2 ans 4,92/4,97, 5 ans < 4,56, 10 ans < 4,82) | 0,07-0,57 | dans `min_price` 0,05 - `max_price` 0,90, `max_per_event` 2 respecté (2 par événement) ; un achat à 0,07 : permis par la config (0,05), pas sous le plancher |
| indice_cotes | Démocrates 2028 « 66-68 % » OUI, « 68-70 % » NON (27/11) | 0,38 / 0,864 | deux tranches d'un même événement (= plafond 2) ; chances 0,48 / 0,96 cohérentes entre elles |
| michigan_preliminaire | « 52,0-54,9 » OUI | 0,194 (0,285) | réglé NON le 20/11 (final hors tranche) ; les deux autres tranches de la stratégie ont gagné (+14,9 €, +2,3 €) |
| seismes_queues_audace | « plus de 13 séismes ≥ 5,5 » OUI | 0,11 (0,169) | dans sa plage 0,05-0,30 |
| taux_immobilier_barriere | 30 ans fixe « 7,50 % d'ici le 31/12 » NON | 0,68 (0,775) | conforme |
| convictions_claude | Rihanna n° 2 Spotify du mois OUI | 0,21 (0,29) | conviction écrite avant l'achat, conforme |

**0 écart.** Rappel déjà connu, revu en vrai : `outcomePrices` de Gamma n'est pas un prix sur un marché mince (fiche du 04/11).

## Ce qui reste

- Nouvelle-Zélande : règlement attendu après le 27/11 (relire alors les 5 positions).
- `compteur_truth` et `compteur_tweets_72_168h` (coupées le 16/11) n'ont plus de position : **éteintes** ce passage (`enabled: false`).
