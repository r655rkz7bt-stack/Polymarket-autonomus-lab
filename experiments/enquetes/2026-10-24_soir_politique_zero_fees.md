# 24/10/2026 (soir) : la politique est passée en « zero_fees » : cinq stratégies de politique aveugles depuis le 20/10

Famille 6 (« ce qui ne tourne plus »), trouvée en cherchant pourquoi le fantôme `candidats_non` ne voyait pas les élections du 03/11.

## Constat
- `favori_politique` : dernier achat le 16/10 à 21 h 57 ; `favori_politique_nuit` 17/10, `favori_politique_patiente` 18/10, `favori_politique_quasi_certain` 17/10 ; seul `favori_politique_quasi_certain_connu` a acheté le 22/10 (un seul achat).
  `suivre_politique` achète encore (mais il n'a pas de filtre `familles`). Les abstentions publiées disent toutes « famille de marchés exclue : 360 » sur 491 marchés.
- Watchlist du 24/10 : 150 marchés, **69 en famille `zero`** (le barème `zero_fees`), dont 32 des 36 marchés de politique que le scan montre (« Balance of Power », « Texas Senate », « California Governor »…) ; seuls 4 sont « sans frais » (`sans_frais`).
- Dans le scan complet (4 205 marchés) : **2 377 marchés `zero`, dont 859 de politique** (adresse d'événement : élection, sénat, gouverneur, Premier ministre…).

## Cause
`strategy_engine.market_family` tire la famille du barème de frais Gamma. Le 19-20/10 Gamma a regroupé la météo, la politique et la finance sous `feeType: zero_fees` (taux 0). L'enquête du 23/10 (`2026-10-23_meteo_zero_fees_famille.md`) a rattrapé la météo (adresse d'événement) et noté la politique comme
« décision de recherche, pas un bug » (« élargirait leur univers à tous les marchés sans frais : Fed, culture, tech »). Or reconnaître la politique à l'adresse de l'événement ne l'élargit pas : c'est restituer l'univers d'AVANT le 20/10, qui est celui pour lequel ces stratégies ont été créées et jugées.
Effet : `favori_politique*` et `parking_politique` (`familles: [politics, sans_frais]`) ne voyaient que 94 marchés sur 393 ; un des cinq stratégies du principal (`favori_politique`) était muette depuis 4 jours.

## Correctif
`strategy_engine.POLITICS_SLUGS` + `market_family` : un marché `zero` dont l'adresse d'événement contient élection, sénat, gouverneur, maire, mi-mandat, primaire, nominé, Premier ministre, présidentielle, parlement, « win-the-house », marge de victoire, coalition… est de famille `politics`.
Test : `tests/test_favori.py::test_zero_fee_political_markets_are_politics_again` (Sénat du Texas, Chambre 2026, Premier ministre de Serbie, marge de victoire : politics ; décision de la Fed, IPO, « White House posts » : restent `zero` ; la température reste `weather`).
Vérification en cycle local (24/10, 21 h 04) : `favori_politique` 3 achats (Alaska : Kreiss-Tomkins OUI 0,864 ; Peltola « final round 3-6 % » NON 0,858 ; Floride, tranche de marge NON 0,869), `parking_politique` 2 (Kamala Harris et Josh Shapiro 2028 NON à 0,935 et 0,949), `favori_politique_quasi_certain` 3 (Hilton Californie NON 0,973, Idaho OUI 0,97, pétrole + Sénat NON 0,972), `favori_politique_patiente` 3 ordres posés : marchés et côtés relus à la main, conformes à ce que ces stratégies faisaient avant le 20/10.

## Ce que ça change pour l'arène
- Ces cinq stratégies se remettent à jouer : leurs comparaisons « avant / après le 20/10 » ne portent pas sur le même univers. Leur capital est resté bloqué dans des positions longues (`favori_politique` 81 € disponibles sur 1 043, `_nuit` 7,6 € : contrôle `capital_bloque`), donc leur reprise sera lente.
- `favori_politique` fait partie des stratégies copiables par le principal (plafond 10 % par achat, 40 % par famille) : la copie reprendra avec les politiques de novembre ; plafond de famille : la politique redevient une famille à part de `zero` (finance, tech…).
- Les frais de ces marchés valent 0 depuis le 20/10 : leurs anciens chiffres « après frais » sont un peu pessimistes.

## Reste ouvert
- `familles: [zero, …]` reste nécessaire pour les stratégies qui veulent aussi la finance, la tech, la culture (nm_hors_crypto, `candidats_non`, 1367 de strategies.yaml).
- Un contrôle automatique « une famille nommée par des stratégies perd soudain la moitié de ses marchés » aurait trouvé le 20/10 ce qui a demandé quatre jours : à écrire (compare la part de chaque famille dans la watchlist d'un jour à l'autre).
