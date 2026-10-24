# 24/10/2026 (passage chercheur, matin) : « sourde » ou « rien à faire » ? cross_market et les stratégies à abstentions vides

**Famille du contrôle à la main** : n° 6 « ce qui ne tourne plus » (la n° 1 du jour a déjà été traitée au passage de 4 h 55, `2026-10-24_principal_contre_fantome_copie.md`).

## Constat
Dans le rapport publié du cycle (`data.json` → `abstentions`), 20 stratégies actives affichent `raisons: {}` : aucune raison écrite. Un cycle local (même code) donne la même liste. Trois cas :
- **fenêtres horaires ou calendaires** (`nf_*_12_18h`, `nf_*_18_24h`, `nf_court_soir`, `fatigue_nhl`, `outsider_sport_apres_midi`, `saison_non`, `mots_prononces_nfl`) : le filtre `Filtered` écarte les marchés AVANT la stratégie (`heure_utc`, `echeance_min/max`, `un_match`), donc elle ne voit rien et n'écrit rien. Normal à 10 h UTC (fenêtres 12-24 h) ;
  `saison_non` (gagnants de saison de sport à 10-18 jours de la fin) : sur Gamma, 3-11/11/2026, les seules séries concernées sont des catégories du Ballon d'Or (8 événements) et des Grands Prix : rareté réelle du calendrier, pas un défaut.
- **`cross_market` (arbitrage d'échelles de seuils crypto, 8,9 jours, 0 opération)** : 424 marchés, abstentions vides. Le code ne dit « aucune échelle de seuils » que s'il n'y a AUCUN groupe ; quand des groupes existent mais qu'aucune paire n'a d'écart après frais (cas ordinaire), il `continue` sans rien écrire. On ne pouvait pas distinguer « sourde » de « voit, rien à faire ».
- le reste (`manifold_reference`, `futurs_bookmakers`, `football_trois_issues`, `cotes_tennis`, `statu_quo_ia`, `mots_nouveaux`) : sources avec peu de rattachements ou sans clé, déjà tracées aux enquêtes des 22 et 23/10.

## Cause et correctif
`strategies_v2.CrossMarketLadder.propose` : les quatre `continue` (carnet absent, position déjà ouverte, frais inconnus, écart < `min_net_edge`) n'appelaient pas `out.abstain`. Elles écrivent maintenant « carnet indisponible », « position déjà ouverte », « frais inconnus » et « paire cohérente : aucun écart après frais » (même formule que `echelle_dates`).
Test : `tests/test_strategies_v2.py::test_cross_market_ignores_consistent_ladders` (échelle cohérente : une paire examinée, raison « paire cohérente »).

## Ampleur
Aucun euro en jeu (aucun pari n'était manqué : l'écart après frais n'existait pas), mais l'enquête automatique et le chercheur lisaient `{}` comme « stratégie aveugle » : plusieurs passages sans pouvoir conclure.

## Contrôle automatique
Pas de nouveau contrôle : les fenêtres horaires donnent aussi `{}` en toute légitimité (filtre de la fille), un contrôle « abstentions vides » ferait une douzaine de faux positifs chaque matin. La règle est dans la fiche : `{}` ne prouve ni la surdité ni la santé ; regarder si le filtre de la fille laisse passer des marchés (`Filtered._market_ok`) et si la stratégie écrit une raison pour chacun de ses `continue`.

## Les quatre obligations « chance / champion sans avantage » de la feuille de mission
Relues sur les journaux publiés de 9 h 47 : `nf_sport_patiente` +135 € au total, tout vient de trois paris (Uchijima +61 €, Fritz +37 €, Michelsen +37 €) et du 18/10 (+242 € ; 21/10 : −230 €) ; sur ses 30 dernières opérations 26 gagnées pour 26,4 attendues (−1,2 %) ;
`nf_sport_patiente_biais_faible` : +111 € le 23/10 sur +60 € au total. Même mécanisme que les 22, 23 et 24/10 (biais fixe +0,05 ou +0,03, mise ∝ 1/(1 − prix), favoris de sport qui gagnent autant que leur prix : `2026-10-22_championne_biais_et_mises.md`, `2026-10-24_principal_contre_fantome_copie.md`).
Aucun défaut de code nouveau ; le principal (760 €) reste sous son capital de départ : à ne pas lire comme un avantage de la championne.

## Dix paris au hasard (famille 3, relecture à la main)
Tirés au sort (graine 2410) parmi 685 achats des fantômes hors `nf_*`/`nm_*`/crypto/politique depuis le 21/10, marché relu sur Gamma : `apres_echeance` « Will Ukraine target Moscow on October 21 » NON à 0,964 (estimé 0,985) — le marché n'est toujours pas réglé 3 jours après sa date et cote OUI 0,18 (NON vaut 0,82 : −15 % sur 12,7 €) ; la stratégie est coupée depuis le 23/10 (`enabled: false`, aucun achat depuis), donc rien à corriger ;
`marche_neuf` « Trump dit "Drill Baby Drill" … (copy) » (marché dupliqué « (copy) » réglé NON gagné) et « Spread: Magic (−16.5) » Hawks ; `mots_prononces` « Iran 5+ fois » OUI gagné, « Russia ou Ukraine » NON perdu (0,408 pour 0,544 estimé) ; `vague_volume_*` (6 achats à 0,66-0,90, 4 marchés ouverts à échéance longue). Question, issue achetée et règle concordent dans les dix cas ; pas de mauvais rattachement.
