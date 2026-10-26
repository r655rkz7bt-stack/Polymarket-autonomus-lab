# 26/10/2026 (midi) : la prudence d'un fantôme plafonnait aussi son total investi (famille 5 : comparaisons faussées / famille 6 : stratégie muette)

Point de départ : le contrôle `acheteuses_arretees` / `muettes` dit que `nf_sport` (la mère de ~25 filles) n'a acheté **aucune fois depuis le 21/10 à 21 h 37**, alors que sa fille `nf_sport_925_950`
(mêmes réglages, filtre de prix en plus) achète 9 à 25 fois par jour. Les abstentions de la mère ne disent rien de plus (« hors du filtre familles », « favori hors de la plage de prix »…, 0 proposition).

## Constat (`scripts/budget_prudence_fantomes_26_10.py`, journaux signés du 26/10 11 h UTC)
- `nf_sport` : prudence ¼ (avance mesurée −0,0012 sur 68 prévisions jugées), capital estimé 1 120,9, **310,6 investis** dans 3 positions ouvertes, cash 799 : un cycle local lancé à 11 h 10 la fait proposer 3 paris.
  En production, rien. Plafond ¼ × 1 120,9 = 280,2 < 310,6.
- **38 fantômes sur 163 sont dans ce cas** (149 ont une prudence < 1) : `naive_favorite` (investi 831 pour un plafond de 281), `nf_sport_football`, `suivre_politique`, `nm_prix_bas`,
  `nf_sport_patiente_avant_match` (549,7 investis pour un plafond de 492,7)… et une trentaine d'autres juste au bord (budget entre −2 et 0 : ils investissent exactement `prudence × capital`, plus rien ensuite).

## Cause
`main.Weighted._scale` écarte tout achat quand `budget = poids × capital estimé − déjà investi ≤ 0`. Ce plafond a été écrit le 18/10 pour le PRINCIPAL (poids = sa part du capital). Le même `Weighted`
enveloppe les fantômes dans `_apply_health` avec comme poids la PRUDENCE (¼, ½, 1, × renfort) : la prudence réduit déjà chaque mise (`shares × facteur`), et en plus le total investi d'un fantôme ne pouvait plus dépasser
prudence × capital. Une stratégie qui avait acheté quand sa prudence était plus haute (½ avant 20 prévisions jugées, puis ¼ dès que son avance devenait négative) restait bloquée jusqu'au règlement de ses positions,
sans raison notée dans les abstentions (le plafond agit après le décompte des raisons).

## Effet sur les résultats
- Une mère muette n'est plus comparable à ses filles (la fille à prudence 1 investit tout son capital, la mère 25 %) : le contrôle `filles_periode` jugeait des stratégies qui n'avaient pas les mêmes moyens.
- Les stratégies à prudence ¼ ou ½ (avance négative ou non prouvée) voyaient moins de paris : moins de données pour prouver (ou réfuter) leur avantage, donc un avantage « non prouvé » qui se perpétue.
- Le principal n'est pas touché (il copie les fantômes avec sa propre part et son propre plafond, cas préservé : `Weighted(...)` sans `cap_budget=False`).

## Correctif
`Weighted(..., cap_budget=False)` pour les fantômes (`main._apply_health`) : la prudence ne fait plus que réduire chaque mise ; le total investi n'est limité que par le cash du journal et par les règles de la stratégie.
Test : `tests/test_principal.py::test_a_ghost_with_low_prudence_is_not_capped_at_prudence_times_capital` (300 investis, prudence ¼ : ancien code → 0 achat, nouveau → 25 parts ; le principal reste plafonné). 593 tests verts.

## Reste ouvert
- Les ~38 fantômes vont se remettre à acheter au prochain cycle de production : leurs rendements des prochains jours ne sont pas comparables à ceux d'avant (à lire avec la date 26/10 midi).
- La part du principal dans une stratégie copiée dépend des paris du fantôme : une mère plus active copiée plus souvent (mêmes plafonds de part, donc pas de risque de mise supplémentaire).

## Contrôle à la main (famille 3/4) : les achats du principal sont-ils exécutables aux vrais échanges ?
`scripts/principal_prix_meilleur_que_reel_26_10.py` : les 252 achats du principal comparés aux échanges publics du même jeton à ±120 s (data-api, 500 derniers échanges par marché : les anciens achats
n'ont pas d'échange dans la fenêtre, 155 sur 252). Sur les 97 comparables : **3 seulement à un prix sous le plus bas échange réel** (0,761 contre 0,827 ; 0,83 contre 0,85 ; 0,864 contre 0,871, chaque fois 1 seul échange
dans la fenêtre : marché mince, carnet non observé). Deux cas relus en détail (`MOUZ` 0,879 et `Brute` 0,9036 sur des cartes de CS2, prix qui sautent de 0,88 à 0,999 en 10 secondes) : le prix simulé est dans la fourchette réelle
à la seconde près. Rien d'anormal ; les marchés « carte » d'e-sport bougent de 10 points en quelques secondes, ce qui rend la latence de l'achat décisive (voir `moins_de_cartes`).

## Preuve par les filles (`scripts/filles_sans_mere_26_10.py`, `scripts/budget_prudence_fantomes_26_10.py`)
Une fille à filtre seul (même classe, mêmes paramètres) ne devrait acheter que des jetons que sa mère achète aussi. Part des jetons de la fille absents du journal de la mère : `nf_tennis_vainqueur` 100 % (194 jetons),
`nf_tennis_12_18h_vainqueur` 100 %, `nf_sport_925_950` 94 % (67/71), `nf_sport_18_24h` 89 %, `nf_sport_prix_haut_3_6h` 88 % (88/100), `nf_sport_football` 90 %. Mères muettes avec leur dernier achat : `nf_sport_court` 20/10,
`nf_sport` et `nf_tennis` 21/10, `nf_sport_patiente_tennis` 24/10 (toutes à prudence ¼ ou ½ ; `nf_tennis_prix_bas` est suspendue : prudence 0, légitime).
**Conséquence sur le jugement des filles** : « `nf_sport_prix_haut_3_6h` +4,9 % contre sa mère +0,3 % (99 et 26 opérations) » ou « `nf_court_soir` +2,2 % contre `nf_court` −1,7 % » comparent une fille qui joue tout à une mère qui ne joue plus :
les « filles qui battent leur mère » de la feuille de mission depuis le 21/10 étaient en partie un artefact du plafond (le contrôle `filles_periode` ne le voyait pas ; il compare sur la même période mais pas sur les mêmes paris).
Nouveau contrôle `enquete.mere_muette_fille_active` (test `test_a_silent_mother_whose_filter_daughter_keeps_buying_is_flagged`) : 9 mères signalées sur le rapport de 11 h ; il doit tomber à 0 une fois les mères revenues.
