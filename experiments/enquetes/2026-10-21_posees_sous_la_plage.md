# 21/10 (midi) : les ordres posés servis SOUS la plage de prix perdent, et un marché en litige bloque 5 portefeuilles

Famille 4 (« le filtre ne filtre pas »), contrôle à la main + deux constats « à regarder » de l'enquête automatique.
Script : `experiments/enquetes/scripts/plage_posee_21_10.py` (lecture seule des journaux signés).

## 1. Achats posés sous la plage (`filtre_prix`, 11 achats signalés sur la famille nf_sport_patiente / nf_tennis)
Constat : les mères (`min_ask 0,80`) posent leur ordre 1 à 2 crans au-dessus du meilleur acheteur ; quand le carnet est écarté, l'ordre est servi à
0,62-0,78. Ce n'est pas un bug de filtre (la plage porte sur le prix du vendeur, voulu pour les mères) mais ces achats sont-ils bons ?

| prix payé | paris distincts (jeton, prix) | misé | rendement | t |
|---|---|---|---|---|
| < 0,80 (hors plage) | 44 | 1 601 € | **−11,9 %** | −1,2 |
| 0,80-0,875 | 155 | 7 897 € | +6,7 % | +1,9 |
| 0,875-0,95 | 108 | 9 692 € | −2,9 % | −0,3 |

Lecture : cohérent avec la règle « ordres posés = vendeur qui sait » (METHODE.md, 17/10) ; **indice, pas preuve** (44 paris, paris communs à plusieurs
fantômes dédoublonnés par (jeton, prix arrondi), pas par événement). Pas de défaut de code : pas de correctif ; la fille `nf_sport_patiente_72_168h_850_875`
et les nouvelles filles utilisent déjà `prix_final`. Si les nouveaux paris confirment (< 0,80 toujours négatif), appliquer `prix_final` aux mères.

## 2. `positions_oubliees` : marché 5167158 (« Will Russia target Kyiv on October 17, 2026? »), 5 portefeuilles, 78 h de retard
Gamma : `umaResolutionStatus = disputed`, `closed = false`, prix NON 0,9455. Résolution en litige UMA : l'argent est bloqué légitimement, aucune erreur de
règlement chez nous. Leçon : ces marchés « Will X target Y on <date> ? » (règle subjective) sont des placements à litige possible ; 5 stratégies y étaient (dont
`favori_politique_patiente`). Rien à corriger ; le contrôle signale déjà la position.

## 3. Autres constats vérifiés
- `copie_fidele` (4 copies à 100 % sur exécution partielle : Mannarino, Lynn Vision ×3) : déjà noté le 21/10 matin ; le principal pèse plus lourd que prévu
  sur les marchés minces ; non corrigé (effet de quelques euros), reste ouvert.
- `estimation_perimee` : tous les écarts sont des modèles (tweets, `choc_sans_nouvelle`), pas des carnets périmés.
