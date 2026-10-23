# Skills Polymarket publics : ce qu'ils font et ce qu'on en reprend (22/10/2026)

Demande d'Etienne : « regarder comment fonctionnent les skills Polymarket et intégrer leurs stratégies »,
puis « installe tous les skills cités plus haut et les Polymarket ». Méthode : skill
`evaluer-source-externe` (le contenu de ces dépôts est une donnée, jamais une instruction).

## Ce qui a été lu (en entier, scripts compris)

| Dépôt | Commit lu | Licence | Contenu |
|---|---|---|---|
| [mjunaidca/polymarket-skills](https://github.com/mjunaidca/polymarket-skills) | `ffed17f` (26/02/2026) | **aucune** | 6 skills : scanner, analyzer (score de momentum), strategy-advisor (4 stratégies, règles d'entrée et de taille), paper-trader, monitor, **live-executor** (vrais ordres avec la clé privée d'un portefeuille) |
| [joinQuantish/skills](https://github.com/joinQuantish/skills) | `2e2cb93` (29/03/2026) | MIT | 4 skills : polymarket-trading, kalshi-trading, copyclaw (copie de traders), quantish-mcp-setup ; tout passe par le serveur MCP Quantish (portefeuille, `place_order`, `transfer_usdc`, adresses de dépôt) |

## Pourquoi on n'installe aucun de ces fichiers
- **Ordres réels** : `polymarket-live-executor` (clé `POLYMARKET_PRIVATE_KEY`), tout joinQuantish
  (`setup_wallet`, `place_order`, `transfer_usdc`) et `copyclaw` (« create a wallet, fund it… auto-mirror
  their trades »). Interdit absolu n° 1 de CLAUDE.md : pas d'ordre réel, pas de portefeuille, pas de clé.
  La plateforme Quantish annonce d'ailleurs sa fermeture (« Quantish is winding down », README).
- **Pas de licence** chez mjunaidca : le code et le texte restent à leur auteur. On reprend les idées,
  réécrites dans notre code.
- Le reste fait doublon avec ce que le labo a déjà : leur paper-trader parcourt lui aussi le vrai carnet,
  mais compte des frais nuls par défaut (`DEFAULT_FEE_RATE = 0.0`, « most markets are fee-free ») et
  n'a pas de journal signé (notre simulateur lit le barème de frais de chaque marché et signe chaque
  écriture) ; leur scanner lit Gamma comme `market_scanner.py`.

## Leurs stratégies, une à une

| Stratégie (leur chiffre annoncé) | Chez nous | Décision |
|---|---|---|
| Tenue de marché, 78-85 % de réussite, 1-3 %/mois | `market_maker` et variantes « posées » ; markout (`markout.py`) | déjà là ; leur propre texte cite le créateur de poly-maker : « not profitable in today's market » |
| Arbitrage d'actualité par IA (fenêtre de 30 s à 5 min) | `news_momentum` (éliminée), `choc_sans_nouvelle` | déjà essayé ; notre cycle de quelques minutes est trop lent pour une fenêtre de 30 s |
| Billets météo : prix < 0,10 quand le modèle dit ≥ 0,30 (« 27 $ devenus 63 853 $ ») | `loterie_meteo`, `meteo_prevision` | **non repris** : sur nos 245 paris météo clôturés (journaux des 3 fantômes météo), **0** remplit la règle ; nos 46 billets achetés sous 0,10 ont gagné **1 fois pour 1,21 attendu** par leurs prix. Test météo du 16/10 : +28 % à l'historique, −6 % aux prix payés (`experiments/meteo_backtest.md`) |
| Arbitrage OUI + NON < 0,99 (« gabagool ») | arbitrages `strategies_v3` (paires, negRisk) | déjà là ; leur texte dit lui-même que l'occasion dure 2,7 s en moyenne (2026) |
| Carnet penché (`advisor.detect_momentum` : acheteurs − vendeurs > 30 %) | `market_structure` | déjà essayé : **éliminée** de l'arène (perdante) |
| Copie des meilleurs portefeuilles (copyclaw) | `experiments/smart_money.md` | déjà testé : le top 1 % copié avec le retard de notre cycle fait **−9,7 %** après frais |
| **Vague de volume** (`momentum_scanner.compute_signals` : volume 24 h ÷ moyenne de la semaine) | rien | **nouvelle** : reprise (ci-dessous) |

Leurs règles de taille et de risque (demi-Kelly, 10 % au plus par position, arrêt à −20 %) ne sont pas
reprises : le capital, la règle n° 1 et la taille des mises sont tenus chez nous par le noyau
(`ledger.py`, `safety_controller.py`) et par l'arène (mise sur l'avantage mesuré). Leurs taux de réussite et
gains annoncés ne sont pas des preuves (un survivant, une période choisie, sans frais ni prix payés).

## La vague de volume, réécrite pour le labo
Idée : un marché qui s'échange d'un coup beaucoup plus que d'habitude, avec un prix qui bouge, reçoit
peut-être une information. Leur score mélange le volume de la semaine (qui contient déjà le jour de la
vague), la profondeur et l'extrémité du prix. Notre version (`VagueVolume`, `strategies_v3.py`) :
- **référence** = volume moyen des jours PRÉCÉDENTS de la semaine (`volume1wk − volume24hr`), sur l'âge
  réel du marché (au plus 7 jours) : un marché créé le jour même montrait une fausse vague ×7 ;
- marché âgé d'au moins 3 jours, référence ≥ 500 $ par jour (un marché endormi donnait des rapports de
  ×8 500 sans valeur), **échéance à plus de 48 h** (Bitcoin du jour ou match du soir : le volume monte
  toujours avant la fin ; essai en direct du 22/10 : ces marchés tenaient les premières places, ×114) ;
- vague ≥ ×3 et mouvement du prix sur 24 h (`oneDayPriceChange`) d'au moins 3 centimes ;
- deux fantômes : `vague_volume_suivre` (achète le côté qui a monté, 0,55-0,90) et
  `vague_volume_contrer` (l'autre côté, 0,10-0,45) ; quart de Kelly, 2 achats par cycle au plus.

Essai en direct (22/10, après ces filtres) : 30 candidats, par exemple « Will the Democratic Party win
the KY-06 House seat? » ×32,6 (+0,06), « Will Ethereum reach $2,700 October 19-25? » ×18,4 (−0,053),
« Will Iliana Iotova win the 2026 Bulgarian presidential first… » ×17,1 (+0,24).

**Test sur le passé** : lancé le 22/10 (relevé des vrais échanges, achats aux prix payés,
`idea_test.verdict`) ; compte rendu à venir dans `experiments/vague_volume_backtest.md`. Les deux
fantômes restent dans l'arène en attendant (ils ne coûtent rien ; le principal ne copie qu'après les
seuils de `config/promotion.yaml`) ; ils seront réglés ou retirés selon ce verdict.

## Skills installés à la place
Méthode et statistiques, pas de trading : voir `.claude/skills/README.md` (provenance, licences, ce qui
n'a pas été repris).
