# Primaires américaines 2026 : les candidats sont-ils bien cotés ? (24/10/2026)

Scripts : `experiments/primaires/scripts/` (`releve_evenements.py`, `releve_prix.py`, `calibration.py`, `non_outsiders.py`, `echanges_non.py`, `non_vrais_prix.py`) ; chiffres bruts : `resultats_*.txt` ; données dans `donnees/` (ignoré par Git, 68 Mo).

## La question
Les marchés « <État> <parti> Primary Winner » se répètent par centaines (mars → septembre 2026) et leurs candidats ont des cotes très inégales. **Un candidat coté 10-30 % un mois avant le scrutin gagne-t-il moins souvent que son prix (le NON rapporte) ? Le favori à 0,85-0,97 gagne-t-il plus ?**
Même mécanisme que « gagnant de saison, NON des candidats à 10-30 % » (`saison_sport.md`, indice faible non répliqué), mais dans un autre domaine : la politique, où des sondages informent déjà le marché.

## Données
- Gamma : **393 événements de primaires et de runoffs** réglés (mars → septembre 2026, plus quelques-uns de 2024-2025), 1 658 candidats réels de **298 événements** de plus de 10 000 $ de volume (les « Person B / Candidate C » de remplissage sont écartés), prix finaux {0 ; 1} seulement.
- CLOB `prices-history` à l'heure (par tranches de 14 jours, le serveur refuse plus), de J-35 à la veille du scrutin (`endDate` = jour du scrutin 0 h UTC, donc J-1 = la veille au soir, avant tout dépouillement).
- Vrais échanges (data-api, par marché, tous récupérés) pour 327 candidats cotés 0,08-0,35 à J-7, J-14, J-21 ou J-30.
- Règlement : prix finaux Gamma (résolution UMA ; pas de seconde source).

## Calibration (prix horaire du marché à J-d contre résultat, `resultats_calibration.txt`)
Le marché est bien calibré : à J-14, 0,60-0,80 → 0,726 gagné pour 0,710 de prix ; 0,80-0,90 → 0,893 / 0,846 ; 0,90-0,97 → 0,952 / 0,944 ; ≥ 0,97 → 49 sur 49 (prix moyen 0,983). Seul écart visible : 0,10-0,20 à J-30 (4 gagnés pour 11,6 attendus, 84 candidats) et 0,10-0,20 à J-14 (8 / 12,9), tandis que 0,05-0,10 à J-1 et J-3 gagne PLUS que son prix (9 / 4,7 et 10 / 5,0) : signes opposés selon l'horizon, du bruit.
Favoris : 0,90-0,97 à J-1 : 58 / 62,5, mais J-3 65 / 67,7, J-7 63 / 63,0, J-14 59 / 58,5. Rien de stable.

## NON des candidats (achat du NON, frais du marché, écart d'achat supposé 1,5 point sur le prix horaire)
- Candidats cotés 0,10-0,30 : J-3 −2,7 %, J-7 +1,2 %, **J-14 +7,1 %** (132 paris, 103 événements, t par événement 2,02, z des prix 1,89, 10 mois sur 10 gagnants, sans les 3 pires +9,6 %), J-21 +7,0 %, J-30 +4,1 %. Avec un écart d'achat de 0 / 3 / 5 points : +9,1 / +5,2 / +2,7 %. `idea_test.verdict` : « retenue » à J-14, « indice » ailleurs.
- Autres fourchettes (0,05-0,15, 0,15-0,40, 0,05-0,40) : de −6,6 % à +4,8 % ; le seul autre « retenue » : 0,05-0,15 à J-30 (+4,0 %, t 2,13).
- **Aux vrais prix** (`non_vrais_prix.py`, premier échange preneur du NON dans les 6 ou 24 h qui suivent la décision) : seuls 25 à 77 des 132 signaux sont exécutables (les marchés cotés 10-30 % sont minces : 55 à 116 signaux sans échange du NON dans la fenêtre) ; rendement **+2,5 / +3,7 / +2,6 / +9,3 %** à J-7/14/21/30 (24 h, bande 0,10-0,30, t 0,4 à 1,8, z des prix 0,4 à 1,7) ; dans la fenêtre de 6 h : −2,3 / +17,3 / 0,0 / +21,0 % sur 22 à 53 paris (instable). Bande 0,15-0,40 : −5,9 / −5,0 / +2,6 / +12,2 %.
- Réglages regardés : 3 fourchettes × 5 horizons × (prix horaire, 6 h, 24 h) + 7 calibrations ≈ 60 cases ; deux « retenue » sur le prix horaire, aucune sur les vrais prix.

## Verdict : **indice faible, non joué**
Le NON des candidats à 10-30 % rapporte +4 à +7 % sur le prix horaire dans 10 mois sur 10, mais (1) le prix horaire n'est pas exécutable : à prix réels il reste +3 à +9 % avec t ≤ 1,8, (2) un signal sur deux n'a aucun échange du NON dans les 24 h, (3) ~60 cases regardées.
Il rejoint l'« indice » de `saison_sport.md` (+8 % à 14 jours, 120 événements) : même signe, même ordre de grandeur, deux domaines indépendants : **piste à garder en tête pour la prochaine saison de primaires (2028)**, pas de fantôme : la saison des primaires de 2026 est finie (dernier événement relevé : septembre ; les élections de novembre ont une autre structure : partis, pas candidats).
Prochaine étape quand il y aura des événements à jouer : un fantôme « NON des candidats à 10-30 % à 14-30 jours du scrutin » sur les événements ≥ 50 000 $ de volume.

## Contrôle : le même NON sur les élections qui ne sont pas des primaires (`experiments/elections_non/`, mêmes scripts)
499 événements réglés (Election Winner, Prime Minister, Mayor, Governor, Senate, Nominee… hors primaires, marges et combos ; 2024 → 2026 surtout), 3 562 candidats avec historique de prix.
NON des candidats cotés 0,10-0,30 (prix horaire, écart d'achat 1,5 point) : J-3 −3,7 %, J-7 −2,5 %, **J-14 +1,9 % (255 paris, 155 événements, t 0,26)**, J-21 −0,5 %, J-30 0,0 % ; 0,05-0,15 : −6,4 % à J-21 (t −2,7) ; 0,15-0,40 : +5,2 / +6,1 % à J-14 / J-21 (z 1,7-1,8) ; 0,05-0,40 : de −1,8 à +1,4 %.
**L'effet des primaires ne se retrouve pas dans les élections générales** (contrôle négatif de même forme : les primaires ont des champs de 5 à 20 candidats peu sondés, les élections générales deux ou trois). Le fantôme `candidats_non` joue les deux (il couvre les champs de candidats des élections du 03/11) : l'arène sert d'essai hors échantillon, et son résultat sur les élections de novembre ne doit pas être lu comme une confirmation des primaires.
