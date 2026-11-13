# 13/11/2026 (passage de 6 h) : achats de la nuit (famille 4), `lid_agenda` (famille 6), position décrite à tort dans une conviction

Feuille de mission de 05 h 47 : aucune obligation. Constats « à regarder » de l'enquête automatique (`estimation_perimee` de
`taux_tresor_barriere`, `muettes`, `capital_bloque`, `reglements_50_50`, `positions_oubliees` néo-zélandaises, `audit` « pas clos »)
déjà élucidés aux passages du 11 au 13/11 (fiches `2026-11-13_nuit_max_par_evenement_entre_cycles.md`,
`2026-11-12_matin_inities_raison_et_prix_payes_v2.md`) : rien de neuf. Jour 13 → famille 2, faite au passage de 1 h ; contrôles de ce
passage : familles 4 et 6.

## Famille 4 : le filtre filtre-t-il ? Les trois achats des fantômes depuis 01 h UTC

| heure | fantôme | marché (relu sur Gamma) | côté, prix, parts | estimation | contrôle |
|---|---|---|---|---|---|
| 01 h 35 | `taux_immobilier_barriere` | 6324662 « 30-year Mortgage hit 8.00% (HIGH) by Dec 31 » | NON 0,90 × 21,47 (partiel) | 0,967 (borne 0,947) | 1,9 % du fantôme ≤ 5 % ; règle relue (fenêtre depuis la création) |
| 04 h 47 | `encheres_estimation` | 6766309 Basquiat « $30m-$40m » (vente du 19/11) | OUI 0,401 × 58,93 | 0,579 (borne 0,479) | estimation basse 30 M$ (`config/encheres.yaml`) ; 2,4 % ≤ 5 % ; pas le jour de la vente ; tranches de l'événement : <30 0,03, 30-40 0,455, 40-50 0,28, 50-60 0,18, 60+ 0,081 |
| 05 h 26 | `compteur_tweets` | 6921763 Khamenei « 0-4 posts » du 13 au 20/11 (XTracker) | OUI 0,93 × 11,76 | 0,957 | plage de prix, compte et période conformes |

Basquiat était « sorti » le 12/11 (0,58 contre 0,52 : écart 0,06 sous l'avantage exigé) ; le prix est tombé à 0,40, l'écart (0,18)
passe le seuil : achat voulu. **Aucun écart.**

## Famille 6 : `lid_agenda` muette depuis sa naissance (10/11)

Calendrier Factbase relu à 06 h 20 UTC : agendas du 12, 13 et 14/11 publiés (« sans voyage », chance 0,86 ; lid réel du 12/11 à
18 h 00, avant 18 h 30). Le 12/11, le marché est resté à 0,84-0,85 toute la journée (modèle 0,86 − 0,04 de prudence : rien à
acheter) ; le 13/11, carnet 0,21 / 0,84 (aucun vendeur sous 0,76). L'abstention « agenda du jour pas encore publié » de 05 h 47 :
l'agenda du 13/11 est arrivé entre 05 h 47 et 06 h 20 UTC (≈ 00 h 47-01 h 20 à Washington). **Muette faute de prix faux, pas sourde.**

## Défaut de lecture (aucun euro) : une conviction décrivait une position qui n'existait plus

`rhin-kaub-avant-15-11-v3` et `-v4` (12/11 16 h, 13/11 1 h) écrivaient « Déjà en position (NON à 0,362) ; ne décide que de la
revente ». Le journal de `convictions_claude` montre que les 39,94 parts avaient été revendues à 0,49 le 12/11 entre 11 h 51 et
12 h 07 (revente par la conviction expirée, défaut corrigé le 12/11 midi). Effet nul (la v4 n'aurait acheté que sous 0,38 − 0,04 ;
le NON valait ≈ 0,55-0,95), mais une conviction doit partir des positions RÉELLES du journal, pas de la mémoire du passage d'avant.
Correctif de méthode : `rhin-kaub-avant-15-11-v5` dit « AUCUNE position » et cite la vente ; à chaque relecture de conviction,
lire `published_data/ledger/fantome_v2/convictions_claude_v2.0.0.jsonl` (achats et ventes du marché) avant d'écrire.

Le Rhin lui-même : le marché « avant le 15/11 » est passé de 0,41 à 0,05 entre 03 h et 05 h UTC. Lectures PegelOnline : l'onde
amont est passée (Maxau 378 → 352, Worms 59 → 56, Mannheim 149 → 144, Mainz plafonne à 165-166) ; Kaub ≈ Mainz − 97 → pic ≈ 68-72 cm
pour un seuil à 77, la prévision WSV du 12/11 (78 le 14/11) est dépassée. Pas de pluie avant le 15/11 (Open-Meteo). v5 : NON 0,95.
