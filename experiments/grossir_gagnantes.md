# Grossir les gagnantes (21/10/2026, soir)

Demande d'Etienne : « Une stratégie qui prouve plus d'avantage qu'elle n'en suppose mise plus, avec
un plafond. » Mesures faites sur les journaux publiés du 21/10 au soir (branche data).

## Ce qu'on a trouvé en chemin : le juge des prévisions était trop lent
La mise d'un fantôme dépend de sa « santé » (`strategy_health.py`, décision du 15/10) : ½ mise tant
que 20 prévisions ne sont pas jugées, puis mise entière si elle prévoit mieux que le marché (Brier),
¼ sinon. Mais le juge n'interrogeait Gamma que pour **15 marchés par heure pour toute l'arène** :
la championne avait **15 prévisions jugées pour 97 paris réglés**, et **aucune stratégie** n'atteignait
les 20 jugées. Toutes misaient donc à moitié depuis le début.

Correction : un pari réglé (SETTLE) dans le journal du fantôme dit déjà ce qu'il a payé ; il est jugé
tout de suite (`settled_outcomes`). Gamma ne sert plus qu'aux prévisions revendues ou en cours.

Effet immédiat (37 stratégies avec au moins 20 paris réglés) :
- **11 passent à la mise entière** (prévoient mieux que le marché) : contrer_crypto, contrer_crypto_patiente,
  nf_sport_patiente (championne), nf_sport_patiente_2crans, nf_sport_patiente_vainqueur, nf_tennis,
  nf_tennis_prix_bas, nf_court_prix_haut, nm_demi_mise, nf_sport_prix_haut, nf_sport ;
- **26 passent au quart** (prévoient moins bien que leur prix : météo, calibration, news_momentum,
  nf_court…), comme le prévoyait la règle du 15/10.

## Le renfort
Renfort = avantage mesuré ÷ avantage supposé, entre 1 et 2, seulement après 30 opérations et avec une
confiance par jour d'au moins 80 %. Avantage mesuré = Σ(gagné − prix payé) / (opérations + 30).
- **Fantôme** (`config/settings.yaml` → `sante_strategies.renfort`) : mise × renfort.
- **Capital principal** (`config/promotion.yaml` → `mise_avantage_mesure`, `part_max: 2`, `renfort`) :
  sa part copiée peut dépasser 100 % dans les mêmes conditions ; toujours au plus 70 % du capital par
  stratégie.
- Le principal copie **toujours à la mise de base** (il divise par la prudence du fantôme, `Weighted`
  avec `base`) : la mise entière ou le renfort d'un fantôme ne se répercutent pas deux fois. Son risque
  reste celui simulé avec Etienne (`experiments/taille_des_mises.md`), sauf pour les stratégies renforcées.

| Stratégie | Paris | Confiance par jour | Renfort | Mise du fantôme (avant : ½) | Part copiée par le principal |
|---|---|---|---|---|---|
| contrer_crypto | 47 | 95 % | 1,66 | 1,66 | 166 % (pas encore qualifiée) |
| contrer_crypto_patiente | 60 | 95 % | 1,49 | 1,49 | 149 % |
| nf_sport_patiente (championne) | 97 | 87 % | 1 (prouve moins que supposé) | 1 | 67 % (inchangé) |
| nf_tennis_prix_bas | 76 | 81 % | 1 | 1 | 64 % |

**Honnêtement** : aujourd'hui, seules les deux stratégies crypto sont renforcées, et elles misent de
toutes petites sommes (1,40 € par pari) ; le renfort les fait passer à environ 4 € dans leur fantôme.
Le plus gros effet est la mise entière des 11 stratégies prouvées : elles grandiront plus vite dans
l'arène (classement, part au mérite). Le capital principal ne change presque pas.
