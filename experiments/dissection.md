# Entonnoir : découper ce qui marche pour trouver le morceau qui gagne (17/10/2026)

**Demande d'Etienne** : « Aujourd'hui il y a telle stratégie qui marche. On la découpe en petits bouts
et on regarde les parties qui fonctionnent le mieux par rapport à la stratégie mère, pour ensuite
spécifier au maximum : faire un petit entonnoir. »

## La méthode (3 étages)
1. **Mère** : une stratégie qui gagne dans l'arène (aujourd'hui `naive_favorite`, `news_momentum`).
2. **Filles (un morceau chacune)** : la mère, mêmes réglages, sur un seul morceau des marchés : un
   sujet (sport, politique…), une tranche de prix, un délai avant la fin, OUI / NON / équipe.
   Déclarées dans `config/strategies.yaml` (`mere`, `morceau`, `filtres`), sans nouveau code
   (`strategy_engine.Filtered`). Le tableau de bord (bloc « Entonnoir ») compare chaque fille à
   sa mère, équitablement : à ce que la mère a gagné depuis la naissance de la fille.
3. **Petites-filles (morceaux combinés)** : quand des filles battent nettement leur mère sur au moins
   20 opérations clôturées, on combine leurs morceaux (ex. sport + prix 0,875-0,95 + 1 à 7 jours)
   et on élimine les morceaux perdants. On recommence jusqu'à la version la plus précise.

## Dissection des paris déjà faits (17/10/2026, script `experiments/dissection/dissequer.py`)
Photographie de TOUS les paris des mères (réglés + encore ouverts au prix actuel). Peu de paris
réglés : des pistes, pas des preuves.

**naive_favorite** (26 paris, 8 réglés, +8,3 % de capital réalisé)
| morceau | paris (réglés) | rendement total |
|---|---|---|
| sport | 6 (4) | +4,9 % |
| culture | 2 (1) | +9,9 % |
| politique | 6 (0) | −0,7 % (latent) |
| prix 0,875-0,95 | 23 (8) | +3,9 % |
| prix 0,80-0,875 | 3 (0) | −0,8 % |
| 1 à 7 jours | 8 (4) | +6,3 % |
| plus de 7 jours | 11 (0) | −0,6 % |
| équipe / joueur | 3 (3) | +8,1 % |

**news_momentum** (16 paris, 7 réglés) : surtout de la crypto (+0,7 %) à des prix de 0,95 et plus
(+1,5 %) ; les prix 0,80-0,875 perdent (−18,8 %).
**news_momentum_patiente** (55 paris, 5 réglés) : 43 paris météo bon marché qui perdent (−7,4 % latent) ;
les prix 0,80-0,875 perdent (−12,2 %).

## Les filles dans l'arène
- `naive_favorite` → `nf_sport`, `nf_politique`, `nf_autres_sujets`, `nf_prix_bas`, `nf_prix_haut`,
  `nf_court`, `nf_moyen`, `nf_long`, `nf_oui`, `nf_non`, `nf_equipe` ;
- `news_momentum` → `nm_crypto`, `nm_hors_crypto`, `nm_prix_haut`, `nm_prix_bas`, `nm_court`, `nm_long`.
Déjà là et du même esprit : `naive_favorite_sans_fin` (≥ 24 h), `favori_politique` (politique avec un
autre réglage).

## Refaire la dissection
```
python3 -I experiments/dissection/dissequer.py <dossier_de_travail> src naive_favorite news_momentum …
```
