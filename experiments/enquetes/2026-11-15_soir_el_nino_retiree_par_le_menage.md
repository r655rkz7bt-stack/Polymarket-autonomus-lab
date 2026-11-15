# 15/11/2026 (passage de 16 h) : `el_nino_cpc` retirée définitivement par le ménage de l'arène

Famille 6 (« ce qui ne tourne plus »), constat « à regarder » `retraits_inactifs` de l'enquête automatique, puis famille 4 à la main.

## Constat (chiffres)
- `el_nino_cpc_v2.0.0`, née le 12/11 (fantôme, expérience audacieuse, piste n° 39), **retirée le 15/11 à 11 h 31** : « inactive :
  aucune opération ni position en 3 jours » (`arena.retire_inactive`, `retirer_inactives_apres_jours: 3`). 0 achat, 0 € engagé.
- Le passage de 1 h l'avait vue « muette » (« avantage net insuffisant » ×3, le marché suit le CPC) et l'avait jugée **voulue**, sans
  voir que le ménage la retirerait 10 heures plus tard. Le retrait est définitif (même nom et même version ne reviennent jamais).
- **Même défaut que le 30/10** (`classement_appstore`, marchés du vendredi seulement, retirée à 3 jours juste après son vendredi,
  test `test_weekly_experiment_is_protected_from_the_inactivity_cleanup`) : une stratégie de calendrier ne peut pas acheter en
  dehors de sa fenêtre. `el_nino_cpc` ne lit qu'une discussion du CPC de moins de 7 jours (publiée le 2e jeudi du mois) :
  active ≈ 7 jours sur 30, prochaine fenêtre le **jeudi 10/12/2026**.

## Le fond relu (aucun euro faux)
Discussion du CPC du 12/11 relue à la source (robots.txt : permis) : 60 % pour « ≥ 2,5 » en OND et en NDJ (RONI). RONI d'ASO 1,97.
Marché « Over 2.5 » (peak RONI 2026-27) : acheteur 0,56, vendeur 0,60 ; borne de la stratégie 0,60 − 0,05 = 0,55 sous le vendeur ;
NON de « 2.0–2.25 » : borne ≥ 0,60 contre un vendeur à 0,965. Le marché a rejoint le CPC le jour même (août : 3 semaines ;
septembre : quelques jours ; octobre : un jour ; novembre : le jour même) : l'abstention de novembre était juste.

## Cause
`config/promotion.yaml` → `jamais_retirer` ne la listait pas ; le contrôle `muettes` ne disait pas qu'une muette non protégée
serait retirée, ni quand.

## Correctif
- `el_nino_cpc` relancée en **v2.1.0** (nouveau portefeuille) et ajoutée à `jamais_retirer` (expérience peu coûteuse : 3 fenêtres
  avant le règlement de mars-avril 2027 ; si le marché rejoint encore le CPC le jour même le 10/12, l'éteindre avec sa leçon).
- `enquete.muettes` reçoit les règles de l'arène (`enquete.regles_arene()`, lu dans `run`) : une muette non protégée porte
  « RETRAIT DÉFINITIF pour inactivité le <date> si elle n'achète rien : si elle attend une date…, l'ajouter à `jamais_retirer` ».
- Test du cas réel : `tests/test_enquete.py::test_silent_unprotected_strategy_announces_its_definitive_retirement`
  (née le 12/11 11 h 31, vue à 1 h le 15/11 → retrait annoncé pour 11 h 31 ; une stratégie protégée n'a pas d'annonce ;
  la configuration réelle la protège en version ≠ 2.0.0).

## Famille 4 à la main
`experiments/enquetes/scripts/filtres_v2_15_11.py 2026-11-15T00:50` : **27 achats** des fantômes v2 depuis le contrôle de 1 h
(compteurs de posts, `favori_politique_quasi_certain`, conviction Dota 2 achetée 0,867 à 11 h 17, `michigan_preliminaire`,
`rt_compte_critiques`, `seismes_annee`, `pluie_hk`, `non_aux_drames`) contre plages de prix, horizons, avantage net, borne basse,
mises : **0 écart** (réglages trouvés pour chaque stratégie).
