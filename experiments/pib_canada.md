# PIB mensuel canadien : l'estimation anticipée contre les tranches de l'officiel (12/11/2026, piste n° 36 : INDICE)

Passage du chercheur de 6 h (12/11/2026). Suite directe de la piste n° 35 (Michigan) : chercher d'autres marchés réglés sur un
chiffre dont la source publie une première valeur avant. Sur 64 événements économiques ouverts de l'inventaire
(`sources_officielles.md`), seul le Michigan se règle sur un « final » ; mais « Canada GDP: <mois> (MoM) » se règle sur le
communiqué officiel du mois, et le communiqué du mois d'AVANT donne déjà une estimation anticipée.

## Règle et source

« Will Canada's GDP growth rate MoM in September 2026 be between -0.2% and -0.1%? » (6 tranches de 0,2 point ; 2,5-3,6 k$ de
liquidité par tranche) : communiqué « Gross domestic product by industry » de Statistique Canada pour septembre (30/11/2026).
Le communiqué du 30/10 dit : « Advance information indicates that real GDP decreased 0.1% in September ». Le Quotidien
(`www150.statcan.gc.ca/n1/daily-quotidien/AAMMJJ/dqAAMMJJa-eng.htm`, « b » en fin de trimestre ; page d'index
`n1/dai-quo/ind1-eng.htm`) : `robots.txt` permet la lecture (délai de 2 s).

## Révisions 2022-2026 (`pib_canada/scripts/communiques.py` → `releves/communiques.json`)

40 communiqués relus (7 mois manquent : jour de sortie hors de la fenêtre), **33 paires anticipé → officiel**. Révision en dixièmes
de point : −3 : 2 ; −2 : 6 ; −1 : 5 ; **0 : 8** ; +1 : 8 ; +2 : 4. La révision est LARGE : la tranche de 0,2 point qui contient
l'estimation n'est juste qu'environ 4 fois sur 10.

## Test aux vrais échanges (`test.py SEUIL PARTS`)

Polymarket : 4 événements (juin → septembre 2026), 3 réglés (`marches.py`, `echanges.py`). Décision dès 16 h UTC le jour du
communiqué qui publie l'estimation ; chance d'une tranche = fréquence des révisions SANS le mois testé ; premier échange réel
de chaque jeton d'au moins PARTS parts à un prix ≤ chance − SEUIL − frais.

| réglage (seuil, parts) | tous les paris | un par tranche |
|---|---|---|
| 0,05 ; 10 | 27 paris, 18 gagnés pour 14,3 attendus, +24,5 % | **18 paris, 12 gagnés pour 9,3 attendus, +27,3 %** |
| 0,10 ; 10 | 21 paris, 13 pour 9,8, +31,4 % | 16 paris, 10 pour 7,8, +26,7 % |
| 0,05 ; 50 | 24 paris, 15 pour 12,1, +22,1 % | 16 paris, 9 pour 7,4, +19,8 % |
| 0,03 ; 10 | 29 paris, 18 pour 14,4, +23,2 % | 18 paris, 10 pour 7,7, +27,8 % |

Réserves : 3 mois seulement (tranches d'un même mois liées par une seule révision) ; la loi des révisions utilise aussi des mois
POSTÉRIEURS au mois testé (pas son propre résultat) ; les « chance 1,000 » d'avant lissage (tranches jamais atteintes en 33 paires)
sont trop sûres : la stratégie lisse (+0,5 par dixième de −4 à +4) et borne à 0,02-0,98. **Verdict : indice.**

## Septembre 2026, en direct (12/11 vers 07 h UTC)

Estimation −0,1 %. Chance (révisions lissées) : « < −0,2 » 0,23 ; « −0,2 à −0,1 » **0,37** ; « 0,0 à 0,1 » **0,35** ; « 0,2-0,3 » 0,03.
Marché : 0,135 / **0,485** / **0,245** / 0,03. Le marché croit trop à l'estimation. Conviction : non (rapprochés de moitié du prix,
OUI « 0,0 à 0,1 » 0,30 et NON de la tranche de l'estimation 0,57 : bornes basses sous le seuil de 5 points). Fantôme
`pib_canada_anticipe` : juste sous son seuil au carnet du 12/11 (marge 0,05 + frais), il achète si les prix s'écartent encore.

## Même famille, à chercher

Michigan (piste n° 35), PIB canadien (n° 36) : un chiffre qui sort deux fois. Autres candidats non vus sur Polymarket aujourd'hui :
inflation « flash » de la zone euro, PMI « flash ». Le PIB américain se règle sur l'« advance » (non concerné).
