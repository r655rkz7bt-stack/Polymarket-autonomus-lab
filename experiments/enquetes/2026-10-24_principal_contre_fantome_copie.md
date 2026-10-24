# 2026-10-24 (matin) : le principal (−23 %) contre sa championne (+16 %) — copie, hasard ou défaut ?

Famille du jour : n° 1, « le principal ne joue pas ce que l'arène mesure ». Point de départ : capital réalisé du principal 772 € (tableau du 24/10, 04 h 47 UTC) alors que
`nf_sport_patiente` (championne) affiche 1 161 € dans son fantôme. Données : `published_data/ledger/` (journaux signés).

## Constat
- Principal, paris réglés par stratégie (213 achats, 195 règlements) : `nf_court` −145 € (18 paris, du 18/10), `meteo_prevision` −58 € (41, avant le 19/10), `nf_sport_patiente` **−19,8 € sur 1 633 € misés (62 paris, −1,2 %)**,
  `nf_sport_patiente_prix_850_875` −22 € (3 paris), le reste ≈ 0. Total réglé −228 €.
- Fantôme `nf_sport_patiente` sur la même période : +161 € sur 13 585 € misés (+1,2 %, 178 paris).
- Même jeton, même stratégie : les 62 jetons du principal sont **tous** dans le fantôme (aucun jeton absent : la copie est fidèle, déjà vérifié le 22/10).

## Piste suivie : le principal copie-t-il un sous-ensemble biaisé ?
Depuis le premier achat du principal (19/10 02 h 28 UTC), le fantôme a fait 138 achats : 74 copiés, 50 non copiés (14 sans règlement).
- Copiés : −2,5 % (−167 € pour 6 704 € misés) ; non copiés : +5,1 % (+158 € pour 3 071 €). Écart apparent de 7,6 points.
- Il vient de la tranche 0,90-0,95 : copiés −15,6 % (27 paris), non copiés +8,0 % (20 paris) ; en 0,80-0,90 : +9,6 % contre +2,7 %.
- Mécanisme de sélection cherché : taille de la mise du fantôme (quartiles 1-20 €, 22-56 €, 57-91 €, 99-474 € : copiés 13/34, 17/35, 28/34, 23/35), prix moyen par quartile (0,885 / 0,853 / 0,871 / 0,880).
  **Pas de lien régulier** (le ticket minimal écarte surtout les petites mises, mais ne choisit pas les prix hauts). Conclusion : l'écart est du hasard d'échantillon (74 contre 50 paris,
  mises ∝ 1/(1 − prix), quelques gros paris à 0,93-0,945), pas un défaut de copie.

## Le vrai constat : aucun avantage mesurable de la championne à aucun prix (tous portefeuilles confondus)
Un jeton compté une fois (premier achat de toute l'arène, 1 798 jetons réglés depuis le 15/10), comparé aux prix payés :

| prix | jetons | gagnés | attendus | z |
|---|---|---|---|---|
| 0,60-0,80 | 204 | 128 | 142,8 | **−2,2** |
| 0,80-0,85 | 285 | 227 | 234,1 | −1,1 |
| 0,85-0,90 | 223 | 187 | 194,1 | −1,4 |
| 0,90-0,925 | 173 | 159 | 157,3 | +0,4 |
| 0,925-0,95 | 185 | 175 | 173,0 | +0,6 |
| 0,95-0,98 | 175 | 165 | 168,3 | −1,3 |

Les favoris de l'arène gagnent **exactement autant (ou un peu moins) que leurs prix** : la stratégie principale gagne ou perd selon la chance, comme déjà écrit les 22 et 23/10
(`2026-10-22_championne_biais_et_mises.md`). Les trois obligations « chance » de la feuille de mission (`nf_sport_patiente` : 3 paris = 84 % du gain, le 18/10 = 150 % ;
`nf_sport_patiente_biais_faible` : le 23/10 = 131 %) sont donc de la **même cause** : mises ∝ 1/(1 − prix) à biais fixe, pas d'avantage derrière ; rien de nouveau dans le code.

## Correctif et contrôle
- Aucun défaut de code : pas de correctif, pas de nouveau test. Le contrôle `copie_fidele` de l'enquête automatique aurait signalé une copie infidèle (aucune ici).
- Conséquence pour Etienne : tant qu'aucune stratégie validée sur le passé ne tient en direct (`validated_strategies` vide), le principal suit le « meilleur de 75 par chance »
  (z ≈ 1,5 attendu sans avantage). Les seules pistes prouvées sur le passé aux vrais prix sont les tweets (NON, écart large), les détroits et, depuis ce jour, un indice sur les séismes
  (`experiments/seismes.md`) : à promouvoir quand elles auront ≥ 20 opérations réglées en direct.
