# 14/11/2026 (passage de 6 h) : la sécheresse a perdu ses marchés, la pluie du jour manque aux relevés « quotidiens »

Jour 14 → famille 3 (« la donnée n'est pas celle qu'on croit ») ; en plus, famille 6 (« ce qui ne tourne plus ») pour l'obligation.

## Obligation : `lid_agenda` retirée par l'arène (13/11, 21 h 15)
Aucune opération en 3 jours. Pas un défaut : la stratégie lisait l'agenda (3 marchés rattachés au dernier cycle) mais le marché cotait
déjà la case de l'agenda (12/11 : 0,84 pour 0,86 au modèle). Elle n'a jamais été testée sans regard vers le futur (l'agenda archivé
est l'agenda final). Retirée de la configuration (`enabled: false`), source `factbase` gardée.

## Famille 6 : `secheresse_d4` sourde depuis 3 jours
Abstentions « aucun marché vu n'a la référence » ×361. Cause : **Polymarket ne crée plus les événements hebdomadaires « Exceptional
drought (D4) by state — week of … »**. Ils naissaient chaque jeudi à 13-14 h UTC (11 semaines, du 20/08 au 05/11) ; le dernier (semaine
du 10/11, événement 1319882) a été clos le 12/11 à 15 h 31 ; celui de la semaine du 17/11 n'existe pas le 14/11 à 06 h (recherche
`public-search` « Exceptional drought », étiquette 105721 : seuls restent Mead, Powell, Minas Gerais, Mississippi, Grand Lac Salé, Rhin,
Danube). Les échanges avant publication s'étaient déjà arrêtés en octobre (`experiments/secheresse.md`). Aucun euro en jeu (aucun achat).
Correctif : `secheresse_d4` éteinte (`enabled: false`), à rallumer en v2.1.0 si les événements reviennent ; source `usdm` gardée.
Le contrôle `muettes` l'avait bien signalée : rien à ajouter à `enquete.py`.

## Famille 3 : achats et rattachements des fantômes depuis le 13/11 11 h
7 achats et 1 vente relus sur Gamma et à la source :
- `mississippi_plus_bas` : OUI « Saint-Louis −1,00 à 0,99 ft » à 0,12 (chance 0,277) : bonne question, bonne tranche ;
- `seismes_annee` : NON « 17-19 séismes ≥ 7,0 en 2026 » à 0,80 (chance 0,866) : 13 séismes ≥ 7 au catalogue USGS le 14/11, il en faut
  4 à 6 en 48 jours ; Poisson(1,9) → P(≥ 4) ≈ 0,13, conforme ;
- `non_aux_drames` : NON « un pays européen frappe l'Iran d'ici le 31/12 » à 0,955 ; `compteur_tweets(_72_168h)` : NON « < 40 » et
  « 40-64 » tweets d'Elon Musk du 14 au 16/11, OUI « 0-4 posts » de Khamenei : questions et fenêtres conformes ;
- `convictions_claude` : NON Rhin à 0,862 (v5, avantage 0,03) ; vente de 45,63 parts OUI « Rihanna n° 2 » à 0,305 (le marché payait
  plus que la conviction) : conforme.
Aucun écart.

## Famille 3, cas réel : la pluie « du mois » à Hong Kong
En préparant une conviction sur « Precipitation in Hong Kong in November? », le Daily Extract de l'Observatoire (source du règlement)
donnait 3,2 mm au 12/11 et le marché payait 0,02-0,05 les tranches « < 5 mm » et « 5-10 mm » : avantage apparent énorme. Faux : le
Daily Extract a **2 jours de retard** ; le bulletin RYES donnait 7,9 mm pour le 13/11, et les METAR de l'aéroport (VHHH) montraient
des averses fortes (+SHRA, cumulonimbus) de 01 h à 06 h le 14/11, que le marché avait vues (OUI « 95 mm+ » acheté 0,66 à 00 h 20 UTC).
Aucun euro (rien d'écrit) ; la nouvelle stratégie `pluie_hk` additionne la pluie du jour heure par heure et ne calcule aucune chance
sans toutes les heures (test `test_no_chance_without_every_hour_of_the_day`).

**Règle** : une source « quotidienne » a un retard ; avant de croire un écart, lire la donnée la plus fraîche (bulletin de la veille,
relevé horaire, METAR) jusqu'à l'heure présente.

## Contrôle préventif (famille 6) : `pluie_hk` verra-t-elle toutes les heures ?
La pluie de l'heure (observation hh:45) reste affichée environ une heure ; la source est relue toutes les 20 minutes. Battements du
principal depuis le 07/11 : 2 096 cycles, écart médian 4,96 min, 3 écarts > 20 min, 1 > 40 min (50 min au plus), aucun > 60 min :
chaque heure sera relevée au moins une fois. Si `pluie_hk` reste muette (« aucun marché vu n'a la référence »), chercher d'abord une
heure manquante dans le journal `pluie_hk:heures`.
