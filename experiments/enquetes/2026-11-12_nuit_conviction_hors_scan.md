# 12/11/2026 (passage de 21 h) : une conviction sur un marché lent n'était jamais lue par le scanner ; contrôle « muettes » des fantômes v2

Famille 6 (ce qui ne tourne plus : stratégie sourde). Jour 12 → famille 1, déjà faite au passage de 16 h.

## 1. Conviction hors du scan
**Constat.** Conviction `dette-us-41000-avant-2027` (marché 665519, « Will the U.S. national debt hit $41 trillion before 2027? »,
`experiments/dette_us.md`). Le scanner lit les pages triées par volume du jour (15 pages, échéance ≤ 30 jours) et les
étiquettes de `tag_pages` ; ce marché a 0 $ de volume du jour, échéance dans 49 jours, écart 0,40, 884 $ de liquidité, et ses
seules étiquettes sont politics, economy (639 marchés ouverts d'ici le 02/01, il est 631e) et recurring (2 100+). Aucune page
ne l'amène : `convictions_claude` ne l'aurait jamais vu, sans aucune abstention écrite (la stratégie ne voit que les marchés
qu'on lui montre).

**Ampleur.** Les 9 convictions écrites depuis le 07/11 visaient des marchés amenés par une étiquette ajoutée exprès
(drought, global-temp, spotify…) ou par les pages de volume : aucune perdue à ce jour, mais chaque nouvelle conviction exigeait
de trouver une étiquette, et un marché sans étiquette précise était injouable.

**Cause.** `market_scanner.scan` n'a aucune entrée « par identifiant » ; `ConvictionsClaude.candidates` ne fait que filtrer
les marchés déjà scannés.

**Correctif.** `market_scanner._add_conviction_markets` + réglage `scanner.conviction_markets` (`config/settings.yaml`) : les
marchés des convictions non expirées sont lus par identifiant (`GammaClient.markets_by_ids`, qui garde l'événement), avec
leurs propres filtres (liquidité 0, écart 1,0, horizon 4 400 h), en `extra_only` (seule la stratégie qui les demande les voit) ;
un marché déjà lu mais exclu par les seuils généraux est relâché pour elle seule. Test :
`test_conviction_markets_are_read_by_id_and_shown_only_to_the_strategy_that_asks` (cas réel : 631e de l'étiquette, écart 0,40).
Vérifié en direct : 5 marchés de convictions lus, 665519 éligible.

**Ce que le correctif ne règle pas : le carnet calme.** Cycle local de 21 h 04 : la proposition (NON à 0,54) est refusée
« carnet périmé (1 369 s > 120 s) » : le carnet n'a pas bougé depuis 23 minutes, l'horodatage Polymarket est celui de la
dernière modification (`proposals/2026-11-11_carnet_calme_juge_perime.md`, en attente de la décision d'Etienne). Deuxième cas
chiffré de cette proposition (après `seismes_pays` le 11/11) : une conviction prête à 4 % du fantôme, bloquée. Pas de
contournement ici : le changement touche l'entrée du contrôle du noyau.

**Contrôle automatique.** Pas de nouveau contrôle : `copie_absente`/`muettes` ne voient pas une conviction jamais jouée. Le
cas est maintenant impossible par construction (le marché est lu par identifiant) ; le refus « carnet périmé » reste visible
dans le journal du cycle.

## 2. Fantômes v2 sans opération (14 sur 20) : abstentions relues (`published/data.json`, cycle 20 h 40)
- `secheresse_d4` : « aucun marché vu n'a la référence » ×228. Gamma n'a **pas encore créé** l'événement « week of November
  17 » : celui du 10/11 a été créé le 05/11 à 14 h et fermé le 12/11 à 14 h ; les précédents étaient créés à l'heure où le
  précédent fermait. À 21 h UTC, rien (étiquette 105721 et recherche plein texte). Pas un défaut du labo ; à relire au
  prochain passage.
- `taux_tresor_barriere` : même raison, voulu (chance donnée de 00 h à 12 h UTC seulement).
- `suivre_inities` : aucune grappe, voulu (fiche du 09/11).
- Les 11 autres ont des raisons chiffrées (avantage insuffisant, déjà en position, carnet vide) : rien de muet sans cause.
- Positions de `favori_politique_quasi_certain` « 112 h après l'échéance » : élections néo-zélandaises, marchés relus
  (`closed: false`, résultats officiels le 27/11), déjà connues.
