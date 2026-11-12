# Ventes aux enchères : prix final contre l'estimation basse (piste n° 45, 12/11/2026, passage de 21 h)

Idée neuve (jamais essayée au labo) : avantage de RÈGLE et de fréquence de base. Polymarket ouvre des marchés « <artiste>'s
“<œuvre>” Sale Price » (5 tranches) sur les grands lots des ventes de novembre à New York (étiquette `art-auction`, 1305 ;
9 événements ouverts le 12/11, 2-7 k$ par tranche, frais `culture_fees`). Règlement : prix final affiché par la maison (« Price
Realised » chez Christie's, « Lot Sold » chez Sotheby's, « Sold For » chez Phillips), FRAIS D'ACHETEUR COMPRIS ; lot retiré,
invendu ou prix inconnu au 30/11 → tranche la plus basse. La tranche basse commence à l'estimation basse de la maison.

## Sources
- `robots.txt` relu avant tout appel : Christie's autorise pages de lots et de ventes (interdit seulement /js, /css, /search,
  /AjaxPages…) ; Sotheby's autorise `/en/buy/…` ; Phillips répond 403 aux robots (pas de contournement : le Modigliani reste dehors).
- Les pages de vente de Christie's (`/en/auction/auction-<numéro>-nyr/browse-lots` ou adresse longue) embarquent tous les lots en
  JSON : estimation basse et haute, prix réalisé, retrait. Script `encheres/christies.py`, analyse `encheres/analyse.py`.
- 10 ventes du soir de New York, octobre 2020 → mai 2026 (20th et 21st Century, collection Weis) : **41 lots d'estimation
  basse ≥ 10 M$**. Les lots « estimation sur demande » (sans chiffre) et les lots retirés (absents de la liste) n'y sont pas.

## Résultat
Prix final / estimation basse (frais compris) : **médiane 1,16** ; déciles 1,04 / 1,09 / 1,12 / 1,14 / 1,16 / 1,17 / 1,23 / 1,37 /
1,53 ; 3 lots sous 1 (Guston 0,80, Freud 0,96, Turner 0,99) ; 3 au-dessus de 2 (Monet 2021, Rousseau 2023, Matisse 2025) ;
**3 invendus**, aucun garanti. Lots d'estimation basse ≥ 40 M$ : 1,04 / 1,11 / 1,14 / 1,14 / 1,15 / 1,43. Par saison : mai 2026
5 lots sur 5 entre 1,0 et 1,25 ; novembre 2025 (saison chaude) 4 sur 12.

Tranches de la semaine (`encheres/tranches.py`, lots garantis, retrait 2 %) contre le prix vendeur du OUI le 12/11 à 21 h UTC :

| lot (Christie's, 17-19/11) | estimation | « basse à +25 % » | au-dessus de +50 % |
|---|---|---|---|
| Kandinsky, Betonte Ecken | 60-80 M$, garanti | 0,62 contre **0,35** | 0,08 contre 0,18 + 0,11 |
| Klimt, Litzlbergkeller | 60-80 M$, garanti | 0,62 contre **0,25** | 0,08 contre 0,29 + 0,10 |
| Picasso, Le Baiser | 40-60 M$, garanti | 0,62 contre **0,33** | 0,08 contre 0,19 + 0,16 |
| Basquiat, Untitled (Leonardo…) | 30-50 M$, garanti | 0,70 contre 0,52 | 0,08 contre 0,18 + 0,10 |

Le marché attend des envolées (saison de novembre 2025 : Klimt de Lauder à 236 M$ chez Sotheby's, 1,57 fois l'estimation) ; le
passé de Christie's dit que les gros lots garantis se vendent le plus souvent un seul enchérisseur au-dessus de la garantie.

## Ce qui manque (pourquoi « expérience », pas « retenue »)
- Aucun marché de tableaux réglé sur Polymarket : pas de test aux vrais prix ni de comparaison de log-score contre le marché.
- 41 lots, une seule maison, saisons chaudes et froides mélangées ; lots retirés absents des listes (risque de retrait sous-estimé ;
  2 % ajoutés à la main).
- Convictions écartées : rapprochées de moitié vers le prix (méthode), les bornes basses (0,29-0,39) ne dépassent pas le vendeur
  de 5 points.

## Verdict
**Expérience audacieuse** → fantôme `encheres_estimation` (Kelly entier sur chance − 0,10 ; `config/encheres.yaml` : lots, estimation
basse, garantie, date de vente ; plus aucun achat à partir de 00 h UTC le jour de la vente). À relire après le 20/11 : 4 lots, prix
réalisés, tranches gagnées contre attendues. Sotheby's (Lichtenstein, Monet, Van Gogh « estimation sur demande », Rothko) : relever
d'abord ses ventes passées (pages autorisées) avant de l'ajouter.

## Cycle local (12/11, 21 h 17 UTC)
`encheres_estimation` : 4 propositions, 16 « avantage net insuffisant » ; achats simulés Klimt « 60-75 » 40 parts à 0,25 (partiel),
Picasso « 40-50 » 117 parts à 0,334, Kandinsky « 60-75 » 290 parts à 0,35 (≈ 102 €, 10 % du fantôme : plafond `mise_max_pari`
0,05 ajouté), Basquiat « 30-40 » 130 parts à 0,476. Sotheby's : les pages de ventes passées affichent `"sold":{"__typename":
"ResultHidden"}` aux visiteurs non connectés : pas de prix réalisés lisibles, Sotheby's reste hors du test (pas de contournement).

## Contrôle hors échantillon (même passage) : 29 lots de 2022-2023
Ventes trouvées ensuite par les pages « résultats » de Christie's : 20th et 21st Century de mai et novembre 2022, collections Bass
et Ammann (mai 2022), 21st de mai 2023, 20th de novembre 2023. 29 gros lots (aucun dans le premier échantillon) : 28 vendus,
1 invendu (Signac) ; **12 sur 28 entre 1 et 1,25 fois l'estimation basse (0,43, contre 0,62 sur le premier échantillon)**, 1 sous 1,
**8 au-dessus de 1,5** (Leutze 3,00, Renoir 2,44, Twombly 2,10, Degas 2,08, Monet 1,90 et 1,61, Picasso 1,72, Twombly 1,70) :
mai 2022 était une saison très chaude (Marilyn de Warhol). La règle tient en tendance mais dépend de la saison.

**Recalibré sur les 70 lots** (66 vendus, 4 invendus ; médiane 1,17 ; déciles 1,04 / 1,10 / 1,13 / 1,15 / 1,17 / 1,25 / 1,37 /
1,45 / 2,05) : tranche « estimation basse à +25 % » 0,53 (garanti) contre 0,25 (Klimt), 0,35 (Kandinsky), 0,33 (Picasso) ; Basquiat
0,58 contre 0,52 : plus d'achat (borne basse 0,48). Au-dessus de 1,5 fois : 0,16 contre 0,27-0,39 au marché. Le fantôme utilise
les 70 rapports (`encheres.RATIOS`, `INVENDUS = 4`).
