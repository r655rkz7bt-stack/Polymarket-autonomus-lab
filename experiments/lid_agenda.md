# Lids de la Maison-Blanche : lire l'agenda du Président avant le marché (10/11/2026, passage chercheur de 21 h)

**Question.** Les marchés quotidiens « Will the White House call a full lid by 6:30 PM on <date>? » (étiquette Gamma `lid` 103988,
un marché par jour, 300 à 4 000 $ de liquidité, frais `politics_fees` 0,04 × p × (1 − p)) sont-ils bien cotés, et l'agenda public du
Président, publié la veille, dit-il quelque chose que le prix ne dit pas ?

**Règle lue mot à mot.** Réglé sur « l'heure du premier full lid listée par Roll Call » (`rollcall.com/factbase/trump/calendar/`), Forth
en secours. Roll Call n'écrit jamais « full lid » : le lid de fin de journée y est « White House Press Office: Travel/Photo lid called »
(584 lignes), à côté des « Lunch lid until … » et « Dinner lid until … » qui ne comptent pas. Factbase publie tout son calendrier en JSON
(`media-cdn.factba.se/rss/json/trump/calendar-full.json`, lien donné par la page elle-même, sans clé, 7 173 lignes depuis le 18/01/2025).

## Données
- 215 marchés de lid sur Gamma (`public-search`), dont 210 réglés du 13/02 au 09/11/2026 ; prix horaires du CLOB (`prices-history`, fidelity 60) ;
  vrais échanges (data-api v2, filtre `condition`) : 10 551 échanges seulement (≈ 50 par marché, volume médian ≈ 900 $).
- Calendrier Factbase complet (agenda « President Schedule » et annonces « Pool Report Schedule »).
- Scripts : `experiments/lid_agenda/` (ordre : `releve_marches.py`, `lid_hist.py`, `lid_trades.py`, `lid_ana.py`, `lid_sim.py`,
  `lid_real.py`, `cases_agenda.py` ; données dans `donnees/`, ignoré par Git).

## Contrôle du règlement
Premier « Travel/Photo lid called » du jour ≤ 18 h 30 (heure de l'Est) contre le résultat officiel : **199 sur 210**. Les 11 écarts :
7 lids notés entre 0 h 44 et 4 h 04 sous la date suivante (lid de la veille au soir), 2 lids de journée sur des jours réglés NON
(27/02 à 16 h 29, 03/11 à 11 h 55, jour d'élection), 2 jours sans lid noté réglés OUI (28/02, 05/11 : règlement par Forth, ou décalage
d'un jour en février ?). Risque de règle : environ 2 % des jours. Les lids d'avant 6 h et les
heures « Local » (à l'étranger) sont écartés dans le code.

## Le marché contre la fréquence de base
Taux de OUI des 210 jours : 0,54-0,56 ; prix moyen 0,43-0,47 selon le délai. Calibration (prix horaire → taux de OUI) :

| délai | 0,0-0,2 | 0,2-0,4 | 0,4-0,6 | 0,6-0,8 | 0,8-1,0 | log-score marché / base du jour |
|---|---|---|---|---|---|---|
| 72 h | 0,07 (n 30) | 0,32 (34) | **0,65 (98), prix 0,47** | 0,78 (27) | 1,00 (5) | −0,580 / −0,697 |
| 24 h | 0,11 (47) | 0,38 (32) | **0,71 (75), prix 0,49** | 0,79 (33) | 0,94 (18) | −0,535 / −0,692 |
| 12 h | 0,07 (54) | 0,29 (28) | **0,73 (52), prix 0,50** | 0,77 (30) | 0,95 (43) | −0,434 / −0,691 |

Le marché bat nettement la fréquence de base (jour de la semaine) ; son seul défaut visible est la tranche 0,4-0,6 (souvent le 0,50 d'un
marché neuf que personne n'a encore échangé), où le OUI gagne 65 à 73 %.

**Achat du OUI à 0,30-0,60, prix horaires + 0,015 + frais** (16 réglages : 4 délais × 4 tranches) : 15 « retenue », 1 « indice » ;
exemple 24 h, 0,30-0,60 : 93 paris, **+35,8 %**, t par jour 3,37, z des prix 3,35, 8 mois sur 10, moitiés +37 % / +34 % ; octobre −75 %
(campagne des midterms : presque tous les jours NON).

**Aux prix réellement payés** (premier achat de preneur dans les 3 h après la décision) : 7 à 19 paris seulement (74 à 106 décisions sans
aucun échange dans les 3 h), prix payé moyen 0,46-0,83 pour un prix horaire de 0,43-0,49 : **non vérifiable**. Les prix horaires de ces
marchés sont surtout des milieux de carnet sans échange (même leçon que `outcomePrices` le 04/11).

## L'agenda de la veille (avantage d'information)
607 jours (mars 2025 - novembre 2026) avec un agenda publié, par case :

| agenda | lid ≤ 18 h 30 | 2025 | 2026 | prix du marché à 12 h (jours de marché) |
|---|---|---|---|---|
| sans voyage, dernier rendez-vous avant 17 h | **86 % (204/238)** | 84 % | 89 % | 0,73 (56 jours, OUI 0,88) |
| sans voyage, dernier rendez-vous ≥ 17 h | 47 % | 31 % | 58 % | instable |
| voyage (« departs » / « arrives »), avant 17 h | 49 % | 64 % | 42 % | instable |
| voyage, dernier rendez-vous ≥ 17 h | **14 % (21/149)** | 14 % | 14 % | 0,22 (46 jours, OUI 0,13) |

**Limite principale : regard vers le futur possible.** Le calendrier archivé est l'agenda FINAL ; un rendez-vous ajouté dans la journée
(un dîner, un déplacement) rend la case plus nette après coup qu'elle ne l'était la veille au soir. Factbase ne date pas ses lignes : seule
une lecture en direct le dira. Le 10/11 à 21 h UTC, l'agenda du 10/11 était publié, ceux des 11-13/11 pas encore.

## Verdict : **indice** → fantôme `lid_agenda` (expérience audacieuse)
- Contre le marché, sur les prix horaires : retenue (t 3,4, deux moitiés). Aux prix payés : invérifiable (trop peu d'échanges). Agenda :
  deux cases stables sur deux périodes, mais lues sur l'agenda final.
- Fantôme `lid_agenda` (classe `LidAgenda`, `src/polymarket_agent/lid.py`, source `factbase` toutes les 15 min, étiquette 103988 au scanner) :
  il ne lit que ce que Factbase montre AU MOMENT du cycle ; achète le OUI (case calme, 0,86) ou le NON (case chargée, 0,14) si la borne basse
  (− 0,04) dépasse le prix demandé + frais de 0,05 ; jusqu'à 30 h avant 18 h 30 ; demi-Kelly. Aussi : un lid déjà noté avant l'heure limite
  → 0,97 (si le marché traîne).
- Une perte apprendrait que l'agenda de la veille ne vaut pas l'agenda final, ou que les carnets n'offrent pas ces prix.
- Mesure du regard vers le futur : `lid.record_history` note dans la base (`lid:histo`, 60 jours) la PREMIÈRE case d'agenda vue pour chaque jour
  et la dernière ; dans 2-3 semaines, comparer la case de la veille au soir à la case finale (et le taux de lid de chaque case vue la veille).
- Non fait ici : un fantôme « OUI à 0,4-0,6 sans agenda » (biais de prix d'un marché neuf, la v2 n'en veut pas sans fait nouveau).
