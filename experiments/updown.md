# Marchés « Bitcoin Up or Down » (fenêtres de 5 et 15 minutes) : le prix retarde-t-il le cours ?

Passage chercheur du 28/10/2026 (matin). Piste née de l'obligation « idée radicalement différente » : ce sont les marchés les plus échangés de Polymarket
(100 000 à 650 000 $ par fenêtre de 15 minutes), jamais testés (« up or down » était écarté de tous nos relevés crypto).

## Question

Le marché est tranché par le TWAP de 60 s du flux Chainlink BTC/USD (« Up » si le TWAP de la fenêtre ≥ le prix du début). Binance donne le même sous-jacent à la minute.
À l'instant T de la fenêtre, le prix du OUI retarde-t-il ce que dit le cours Binance déjà connu ? Si oui, acheter le côté sous-évalué.

## Données (scripts : `experiments/updown/scripts/`, données dans `donnees/`, ignoré par Git)

- `klines.py` : 1 minute BTCUSDT depuis le 25/08/2026 (miroir `data-api.binance.vision`, sans clé).
- `releve.py` : événements par leur adresse (`btc-updown-15m-<epoch>`, `btc-updown-5m-<epoch>`) puis tous les échanges des preneurs (data-api, jusqu'à 10 000 par marché).
  **15 minutes : 5 376 fenêtres (toutes, du 01/09 au 27/10) ; 5 minutes : 6 048 fenêtres (une sur deux, du 15/09 au 27/10).** 100 % réglées nettement (0/1).
- **Contrôle du règlement** : le « close de la dernière barre ≥ open de la première » de Binance redonne le résultat officiel 94,1 % du temps (15 min) et 86,5 % (5 min) : Binance n'est pas
  Chainlink (le TWAP de 60 s et la source d'arbitrage diffèrent) ; le modèle est donc une approximation, ce qui est justement ce qu'un acheteur du « retard » aurait.

## Méthode (sans regard vers le futur)

À chaque minute k de la fenêtre : mouvement m = ln(cours fini à T / ouverture), volatilité des 240 minutes AVANT la fenêtre, p = Φ(m / (σ √minutes restantes)) ; barres d'une minute FINIES seulement.
Prix payé = premier échange réel d'un preneur qui ACHÈTE le côté voulu dans les 60 s après T, taille ≥ 20 parts, frais crypto 0,07·p·(1−p) par part.

## Résultats

1. **Le marché bat le modèle à chaque minute** (log-score marché − modèle : +0,011 à +0,050 par minute sur 15 min ; +0,035 à +0,103 sur 5 min). Il lit Chainlink, pas Binance, et réagit plus vite que nos barres finies.
2. **Acheter le côté où modèle − prix − frais ≥ seuil** (4 seuils × 4 groupes de minutes, 16 réglages par durée) :
   15 min : −3,5 % à −7,7 % sur toutes les minutes (12 773 paris à seuil 0,03 : 4 159 gagnés pour 4 164 attendus par les PRIX et 5 628 par le modèle : le modèle est faux, les prix sont bons) ;
   5 min : −4,4 % à +7,3 %, de plus en plus positif avec le seuil mais jamais à t > 1,6 (seuil 0,15 : 1 815 paris, +7,3 %, t par marché +1,4 ; meilleure ligne : minute 3, +14,6 %, t +1,6) et non répliqué entre les durées.
   Seule ligne positive du 15 min : **la 14e minute (une avant la fin) +10 à +26 %, t +1,5 à +2,4** ; sur 5 minutes la minute 4 (équivalente) fait −1,2 à +1,2 % (t ≤ 0,2) : **non répliqué**, et la ligne est la meilleure de 16 réglages.
3. **Calibration sans modèle** (prix payés, toutes minutes) : gagnés ≈ attendus partout sauf les billets chers en espérance : **0,02-0,10 : −19 % (15 min : 335 gagnés pour 382,7, t −2,7 ; 5 min : 133 pour 151,5, t −2,3)**, 0,10-0,25 : −10 % puis −5 %.
   Les 0,90-0,98 rendent +0,35 % (15 min) et +0,02 % (5 min) : la moitié « vendre les billets de loterie » vaut zéro après frais.
4. **Aucune mémoire** : après une fenêtre Up la suivante est Up 48,9 % (z −1,2), après Down 50,2 % (z +0,2) ; part de Up par heure UTC entre 45 % et 56 % sans motif (24 heures, 5 376 fenêtres).

## Verdict : **écartée** (rien dans l'arène)

Le marché Up/Down est efficace par rapport au cours du sous-jacent à la minute, les frais (≈ 1,4 à 2,7 points aux prix du milieu) mangent tout, et le seul indice (14e minute) ne se répète pas sur 5 minutes.
Leçon chiffrée de plus pour la règle « jamais de billets sous 0,10 » : ici −19 % et −25 % sur des milliers de cas. Ne pas refaire sans une source plus rapide que Binance (Chainlink Data Streams demande une clé).
