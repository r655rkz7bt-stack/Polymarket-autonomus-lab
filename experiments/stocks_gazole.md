# Stocks d'urgence de gazole de l'UE (piste n° 60, 14/11/2026, passage de 21 h, notée)

**Marchés** : « EU emergency diesel stocks end of <octobre / novembre / décembre> 2026? » (seuils 30M+ … 37M+, 55-80 k$ chacun,
`economics_fees`), nés après l'article de Reuters du 01/10 (pression américaine sur la France et l'Allemagne). Règle : première
valeur publiée par Eurostat (`nrg_stk_oilm`, UE à 27, « Gas oil and diesel oil », « Closing stock - EU emergency », milliers
de tonnes) ; révisions ignorées.

**Source** (API Eurostat, `robots.txt` permis, relu avec `scripts/robots_ok.py`) : script `stocks_gazole/serie.py`.
- Total UE publié jusqu'à **juillet 2026 : 36 494** (janvier 38 508 : −2,0 Mt en six mois).
- **Août 2026 n'a pas de total UE** (la Roumanie manque) mais 26 pays sur 27 sont publiés : **36 704 + Roumanie (≈ 460 en
  juillet) ≈ 37 160**, un rebond de +670 (Allemagne +153, Espagne +179, Italie +210, Grèce +186). Septembre : 5 pays seulement.
- Saison (2013-2025) : août → novembre **−767 en moyenne** (écart-type 561 ; 11 années sur 13 en baisse), juillet → novembre −540.
- Marchés liés au 14/11 : l'AIE n'a demandé à la France ni à l'Allemagne de libérer leurs stocks avant le 31/10 (réglés NON ;
  « d'ici le 31/12 » 0,21 et 0,075) ; pas d'interdiction américaine d'exporter le gazole au 31/10.

**Ce que le prix sait** : le marché de novembre (37M+ 0,056, 36M+ 0,365, 35M+ 0,635) ressemble à la tendance tirée de JUILLET
(36,49 − saison → ≈ 35,95 : P(≥ 36) ≈ 0,47, P(≥ 37) ≈ 0,03) ; le rebond national d'août n'y semble pas.
Depuis août (≈ 37,16 − 0,77 ± 0,56) : P(≥ 37) ≈ 0,14, P(≥ 36) ≈ 0,76, P(≥ 35) ≈ 0,99.

**Étude de conviction (novembre)**, carnets lus à 21 h UTC :
- 37M+ : estimations 0,14 / 0,05 / 0,54 / 0,05 / 0,15, médiane 0,14 ; rapprochée du prix (0,057) 0,10 ; borne ≈ 0,06 contre un
  vendeur à 0,081 : non.
- 36M+ : 0,76 / 0,47 / 0,91 / 0,45 / 0,65, médiane 0,65 ; rapprochée (milieu 0,365) 0,51 ; vendeur 0,56 : non.
- 35M+ : 0,99 / 0,955 / 0,97 / 0,85 / 0,93, médiane 0,95 ; rapprochée (milieu 0,635) 0,79, borne ≈ 0,74 contre un vendeur à 0,71
  (26 parts) : 3 points, **sous le seuil de 5**. Pas de conviction.

**Reste ouvert** : la valeur d'août (Roumanie) et de septembre au prochain envoi d'Eurostat (≈ 10 décembre) ; si le total d'août
confirme ≈ 37,1 et septembre ne baisse pas plus que la saison, 35M+ et 36M+ de novembre et décembre se relisent. Pas de test sur
le passé possible (série de marchés née en octobre 2026, aucun réglé).
