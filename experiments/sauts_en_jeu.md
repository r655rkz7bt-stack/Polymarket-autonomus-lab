# Sauts de prix en match, tennis et e-sport : contrarien ou suiveur ? (28/10/2026, passage du soir)

**Question.** Pendant un match de tennis ou d'e-sport, après un gros saut du prix « vainqueur » (un break, une carte, un set), le prix va-t-il trop loin (acheter le côté
qui vient de baisser) ou pas assez loin (acheter le côté qui vient de monter) ? Le football (22/10, `contrer_football.md`, 1 110 matchs) avait répondu « le marché suit le but et ne revient pas » ;
le tennis et l'e-sport (matchs courts, jeux à points) n'avaient pas été regardés.

**Données.** Gamma `/events/keyset` (séries ATP 10365, WTA 10366, CS2 10310, LoL 10311, Dota 2 10309, Valorant 10369), matchs réglés dont le coup d'envoi tombe entre le 01/08 et le 28/10/2026,
marché « vainqueur » seul à plus de 2 000 $ : 11 158 événements, leurs **échanges réels** (data-api, preneurs ; 11 158 fichiers). Scripts : `experiments/sauts_en_jeu/scripts/releve.py`
(relevé et échanges, ≈ 20 minutes), `analyse.py`. Résultats bruts : `resultats_tennis.txt`, `resultats_esport.txt` (les données sont dans `donnees/`, ignoré par Git).

**Contrôle du règlement.** Le dernier prix échangé du joueur 1 va dans le sens du règlement officiel : 5 627 sur 5 630 (tennis) et 5 126 sur 5 128 (e-sport) ; 153 et 223 matchs réglés 50-50
(2,6 % et 4,2 %) sont écartés des paris (ils auraient payé 0,5 : à compter à part si une piste en sortait, ce n'est pas le cas).

**Méthode.** Après le coup d'envoi (`gameStartTime`), à chaque minute (jusqu'à 200 min en tennis, 170 en e-sport) : saut = variation ≥ J du prix du joueur 1 en `regard` secondes
(prix de moins de 4 minutes). **Un seul saut par match (le premier)**. Entrée = prix du premier échange de preneur dans les 5 minutes qui suivent (saut + délai), plus les frais du marché
(`feeSchedule`) ; aucun regard vers le futur. Contrarien : on achète le côté qui vient de baisser ; suiveur : le côté qui vient de monter. 24 réglages par groupe : J ∈ {0,10 ; 0,15 ; 0,20 ; 0,30},
regard 5 min (délais 1 et 3 min) et 15 min (délai 1 min), deux sens : **48 réglages en tout**. `idea_test.verdict` pour la confiance par événement.

## Résultats (tennis : 5 785 matchs, 3 000 à 4 800 sauts par réglage ; e-sport : 5 352 matchs, 1 100 à 3 900 sauts)
| groupe | sens | rendement (24 réglages → 12 par sens) | meilleure confiance par événement | pire |
|---|---|---|---|---|
| tennis | contrarien | −2,7 % à −9,7 % (12 réglages sur 12 négatifs) | −1,05 | −2,86 |
| tennis | suiveur | −2,5 % à +0,8 % (7 réglages sur 12 négatifs ; z des prix −0,2 à +1,6) | +0,62 | −2,03 |
| e-sport | contrarien | −13,6 % à +0,2 % (11 réglages sur 12 négatifs ; J = 0,30 : −13 %, t −2,9 à −3,0) | +0,08 | −2,99 |
| e-sport | suiveur | −4,5 % à −0,4 % (12 réglages sur 12 négatifs ; z des prix −1,6 à +0,5) | −0,13 | −2,72 |

- Aucun des 48 réglages n'atteint « indice » (`idea_test.verdict` : 48 « écartée » ; un « indice » à t 1,1 était apparu sur un premier relevé partiel d'ATP seul, disparu avec WTA).
- Le contrarien perd : le saut de prix est de l'information (break, carte gagnée), pas un excès ; le suiveur n'a rien à gagner après frais et écart (le prix a déjà bougé).
- Cohérent avec le football (22/10) : le marché de sport suit l'action sans la dépasser.

**Verdict : écartée** (48 réglages regardés, aucun signe stable). À ne pas refaire sans idée nouvelle (par exemple un score en direct plus fin que le prix : pas de source gratuite connue ;
séparer breaks et sets exige l'historique des points).

## Ce que ce test donne en plus
Les **échanges de 11 158 matchs** (août-octobre) peuvent resservir (`experiments/sauts_en_jeu/donnees/`, non versionné : à retélécharger, ≈ 20 minutes avec 8 fils).

# Suite : outsiders et favoris AVANT le match, tennis et e-sport (même soirée)

Mêmes 11 158 matchs (août-octobre) et leurs échanges ; à T = coup d'envoi − Δ (Δ = 1, 3, 6, 12 h), un pari par match sur le côté « outsider » (< 0,5) ou « favori » (≥ 0,5), au prix du premier
échange de preneur dans l'heure suivante, frais payés (`scripts/outsiders_avant_match.py`, résultats `resultats_outsiders.txt`, `resultats_favoris_milieu.txt`). 32 cases (4 délais × 4 tranches × 2 groupes) par côté.

- **Outsiders** : perdent partout. Tennis −1,6 % à −7,0 % (H-1 à H-12), e-sport −10,4 % à −13,8 % (t par événement −3,6 à −4,6) ; sous 0,10 : −17 % à −68 %. Le biais favori-outsider est le même qu'ailleurs : jamais d'outsider sans source.
- **Favoris du milieu en e-sport** : tennis rien (−3,2 % à +0,8 %). E-sport, tranche payée **0,65-0,80** : **H-3 +4,2 %** (1 178 paris, 891 gagnés pour 843,6, z +3,1, t par événement +2,4, « retenue » par `idea_test.verdict`),
  **H-6 +4,5 %** (902 paris, z +2,8, t +2,3), H-1 −0,8 %, H-12 +0,1 % : seuls deux délais voisins, sur un seul relevé de trois mois. Les favoris à 0,55-0,65 perdent (−3 % à −4,7 %).
- **Robustesse** (`favoris_esport_robustesse.txt`) : CS2 porte l'essentiel (+6,7 %, z +3,3), Dota 2 +7,1 % (139 paris), LoL +0,7 %, Valorant −6,4 % ; août −0,4 %, septembre +7,2 %, octobre +6,1 % ; deuxième moitié des dates
  +5,6 % contre +2,7 % ; **sensible à la bande** (0,60-0,75 : +0,6 % ; 0,62-0,78 : +1,9 % ; 0,67-0,82 : +4,0 %) ; 50-50 comptés à 0,5 : +3,3 % / +3,6 % (z +2,6 / +2,4).
- **Profondeur** (`favoris_esport_profondeur.txt`) : parts achetées par des preneurs à ≤ prix + 2 centimes dans l'heure : le gain tient avec la quantité (≥ 20 parts +4,9 %, ≥ 400 parts +5,9 %, ≥ 1 000 parts +4,7 % à H-3) :
  ce n'est pas un artefact d'échanges minces.
- **Piège évité (regard vers le futur)** : coupé par le volume FINAL du marché (`volumeNum`), le gain se concentrait dans le tiers le plus petit (+15,6 % et +17,9 %, z +5,5) et disparaissait dans les gros marchés (−3,9 %).
  Mais `volumeNum` compte aussi les échanges d'APRÈS T (un petit marché final = un match peu suivi après coup). Refait avec le notionnel échangé AVANT T (`favoris_esport_volume.txt`) : les trois tiers donnent
  +3,8 / +3,3 / +5,4 % (H-3) et +7,5 / +2,4 / +3,5 % (H-6) : **pas de concentration**. Leçon : jamais de coupe par un volume connu seulement à la fin.
- **Rejeu sur la période d'avant** (`favoris_esport_oos.py`, `favoris_esport_total.py` ; relevé février-juillet, 8 683 matchs à plus de 2 000 $ des quatre jeux) : voir le tableau ci-dessous.

## Rejeu sur la période d'avant (février-juillet, 8 549 matchs, jamais regardés) et relevé complet (13 901 matchs)
Tranche payée 0,65-0,80, un pari par match, vrais échanges, frais payés (`resultats_favoris_esport_oos.txt`, `resultats_favoris_esport_total.txt`).

| délai | août-octobre (découverte) | février-juillet (hors échantillon) | tout le relevé, 4 jeux | CS2 seul, février-juillet | CS2 seul, tout le relevé |
|---|---|---|---|---|---|
| H-1 | −0,8 % | −0,2 % (2 484 paris, z +0,5) | −0,4 % | +1,1 % (z +1,0) | +1,0 % |
| **H-3** | **+4,2 %** (1 178, z +3,1) | **+0,5 %** (2 019, z +0,9) | +1,9 % (3 197, z +2,6, t +1,7) | +1,6 % (859, z +1,1) | +3,8 % (1 520, z +3,0, t +2,4) |
| **H-6** | **+4,5 %** (902, z +2,8) | **−0,5 %** (1 638, z +0,2) | +1,3 % (2 540, z +1,8) | +1,6 % (635, z +1,0) | +4,1 % (1 136, z +2,8) |
| H-12 | +0,1 % | −1,5 % (1 003) | −0,5 % | +2,3 % | +4,0 % (650, z +2,1) |

- Par mois, février-juillet, H-3 : +2,2 / −6,5 / +0,5 / −1,8 / **+12,2 (juin)** / −3,8 % : un seul mois fort, les autres autour de zéro. Les jeux : CS2 +1,6 %, Dota 2 +3,2 %, LoL −0,8 %, Valorant −2,1 %.
- Les favoris à 0,55-0,65 perdent partout (tout le relevé : −4,8 % à H-3, t −3,2 ; −4,1 % à H-1) : près de 50-50, les frais et l'écart suffisent.

**Verdict : écartée pour les quatre jeux** (+4 % à la découverte, +0,5 % / −0,5 % hors échantillon aux deux délais gagnants ; ~40 cases regardées en tout). **Indice faible pour CS2 seul** (+1,6 %, z +1,1 hors
échantillon : même signe, un tiers de l'effet ; sous-ensemble choisi après coup) : fantôme `favori_esport_milieu` (CS2 seul, H-3 à H-6), expérience audacieuse, **jamais « retenue »** sans 100 paris de plus en direct.
Ce qui reste vrai : outsiders perdants partout ; favoris à 0,55-0,65 perdants ; tennis et e-sport après un saut de prix : le marché suit.
