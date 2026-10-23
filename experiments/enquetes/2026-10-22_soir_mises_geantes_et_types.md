# Enquête du 22/10/2026 (soir) : mises géantes des fantômes et types de marchés

Passage chercheur 19 h 55 UTC. Famille du jour : n° 5 (comparaisons faussées), plus un constat « à regarder » (11 mises de fantômes au-dessus de 25 % de leur capital).
Les trois obligations de la feuille de mission (championne `nf_sport_patiente`, `nf_tennis_prix_bas`, concentration de `nf_sport_patiente_prix_850_875`) sont les mêmes que ce matin :
déjà traitées dans les fiches du jour (`2026-10-22_championne_biais_et_mises.md`, `2026-10-22_midi_tennis_prix_bas_et_deux_camps.md`) ; rien de nouveau n'a changé leur cause.

## Constat 1 : trois mises à plus de 45 % du capital viennent d'une seule stratégie, avec le même biais fixe
`nf_court_prix_haut` (fantôme, moins de 24 h, prix ≥ 0,90) : 489 € (53 % du capital) sur « US x Iran ceasefire continues through October 22 » à 0,946, 498 € (48 %) sur
« Exact Score : Bayern 1-0 Arsenal, NON » à 0,94, 242 € sur « Will LASK Linz win ? NON » à 0,94 (perdu). Cause : `bias` 0,05 fixe dans `config/strategies.yaml`, donc une estimation à
prix + 0,045 et une mise de Kelly ∝ 1/(1 − prix) (même mécanisme que la championne, voir la fiche du matin). Le principal ne copie pas cette stratégie : pas d'effet sur le capital réel.

## Constat 2 : aucun type de marché ne bat son prix (un jeton = un pari)
Relevé : 4 610 couples (stratégie, jeton) des 136 fantômes, 1 896 marchés relus sur Gamma (`sportsMarketType` et question), 1 383 jetons réglés distincts, 3 065 couples réglés.
Gagnés contre attendus par les prix payés, jetons distincts : moneyline 356 / 366,7 (z −1,5) ; spread 87 / 93,5 (z −1,7) ; « autre » 245 / 257,9 (z −1,4) ; « X gagne le 〈jour〉, NON » 59 / 59,1 (z 0,0) ;
totaux 70 / 68,9 (+0,4) ; score exact 37 / 35,0 (+1,2) ; crypto au-dessus de X 34 / 36,0 (−0,7). Aucune catégorie n'est significativement au-dessus de son prix.
Par tranche de mise (couples réglés) : mises < 50 € : −3,2 % (1 409 gagnés pour 1 434 attendus), 50-100 € : −0,6 %, 100-200 € : −5,8 %, ≥ 200 € : −2,6 % (79 gagnés pour 81,4, 89 paris).
Total : 2 300 gagnés pour 2 347,5 attendus par les prix et **2 542 annoncés** par les estimations ; −4 503 € de gain. L'écart entre « annoncés » et « attendus » est ce que mesure déjà
`estimation_gonflee` (z −9,7 à −10,1) : il est présent dans **toutes** les tranches de mise et tous les types, ce n'est pas un défaut d'un seul type de marché.
Les « 0 gagné sur 7 » des touchdowns (anytime_touchdowns, −358 €) sont un seul marché acheté par 7 fantômes (DeMario Douglas, NON à 0,86), pas 7 paris.

## Constat 3 : doublons
2,2 couples (stratégie, jeton) par jeton réglé en moyenne (3 065 couples pour 1 383 jetons) : les résultats par stratégie ne sont pas indépendants (déjà couvert par `selection_multiple` ; ici chiffré).

## Correctif / suite
Pas de défaut de code nouveau : la cause est le `bias` fixe (décision d'Etienne en attente sur la championne, voir `experiments/journal_recherche.md`). Une sœur `nf_court_prix_haut_biais_faible`
(biais 0,02, mêmes filtres) est ajoutée à l'arène pour comparer **sur la même période** ; aucune modification du noyau. Scripts : `experiments/enquetes/scripts/2026-10-22_types_releve.py` puis `..._analyse.py` (relevé Gamma de 1 896 marchés, 2 minutes ; il écrit dans /tmp ;
il lit `published_data/`).
