# Conviction sur un marché « échu » mais encore échangé : invisible (17/11/2026, passage de 1 h)

Famille 6 (« ce qui ne tourne plus » : jour 17 → 17 mod 6 + 1 = 6) et famille 3.

## Constat
- Trois convictions écrites ce passage (`ca26-marge-dem-25-30`, `ca01-marge-dem-15-20`, `ca03-marge-dem-15-20`, piste n° 66) :
  marges de districts californiens, vendeur 0,89-0,90, marché actif, pas clos, carnet ouvert (`acceptingOrders: true`).
- Premier cycle local (01 h 04) : `convictions_claude : 0 propositions, abstentions {'avantage net insuffisant': 5}` — les cinq
  convictions anciennes ; **les trois nouvelles n'apparaissent nulle part**.

## Cause
`market_scanner._add_conviction_markets` lit bien les marchés des convictions par identifiant, puis `classify` les juge avec
l'horizon du scanner : `end_min = maintenant + min_horizon_minutes (30)`. La date de fin Gamma de ces marchés est le **03/11 12 h**
(jour du vote) ; ils s'échangent pourtant jusqu'à la certification (mi-décembre). Verdict : « hors horizon », marché invisible, et
la stratégie n'écrivait rien pour une conviction dont le marché n'arrive pas.

## Ampleur
Relu les 20 convictions du fichier contre la date de fin Gamma (`endDate` < date d'écriture) : seules les trois nouvelles sont
touchées ; **aucun euro perdu**, défaut latent. Le même défaut aurait frappé la marge du gouverneur étudiée le 16/11 (« Becerra
30-35 % ») et toute conviction future sur un résultat en attente de certification (élections, chiffres « à publier »).

## Correctif
- `config/settings.yaml` → `scanner.conviction_markets.min_horizon_minutes: -86400` (marchés échus depuis 60 jours au plus, non clos).
- `ConvictionsClaude.propose` : une conviction active (ni abandonnée, ni expirée) dont le marché n'est pas vu s'abstient avec
  « marché de la conviction absent du scan (date de fin passée, fermé ou carnet indisponible) » : lisible dans le journal du cycle,
  `data.json` et l'enquête automatique (contrôle `acheteuses_arretees` / `muettes`, qui lisent les abstentions).
- Tests du cas réel : `test_market_scanner.test_conviction_market_past_its_gamma_end_date_but_still_trading_is_seen` (échoue sans le
  réglage) et `test_convictions.test_an_active_conviction_whose_market_never_arrives_says_so`.
- Second cycle local (01 h 06) : 3 propositions, 3 achats simulés (22,22 parts à 0,899, 22,22 à 0,889, 21,73 à 0,90, frais 0,08 chacun).

## Contrôle à la main (famille 6) : positions ouvertes des fantômes v2 relues sur Gamma
`experiments/enquetes/scripts/positions_v2_11_11.py` : **172 positions ouvertes, 0 sur un marché clos** (aucune position oubliée).
12 sont passées de leur échéance : 5 élection néo-zélandaise (officiel le 27/11), 1 cessez-le-feu Israël-Iran au 15/11, 6 semaine de
séismes 9-15/11 (UMA en cours, prix 0,97-0,9985 du bon côté) : attente normale. `taux_tresor_empirique` a fait ses deux premiers
achats en production à 00 h 09 (OUI 5 ans 5,25 % à ≈ 0,19 ; NON 30 ans sous 5,15 %). Sources vides (`meteo_metar`, `meteo_prevision`,
`mlb_stats`, `references_football`) : aucune stratégie vivante ne les lit ; PortWatch (« Token Required », puis « Too many requests ») :
déjà connu (`2026-11-03_apres_midi_portwatch_token.md`), aucune stratégie vivante. `encheres_estimation` et `pib_canada_anticipe`
« n'achètent plus » : leurs marchés sont déjà tenus (4 lots de la semaine des ventes, réglés les 18-20/11 ; 3 tranches du PIB du 30/11).
