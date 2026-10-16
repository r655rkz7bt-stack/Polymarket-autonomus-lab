"""Backtest crypto, étape 1 bis : transactions réelles (API publique data-api.polymarket.com/trades).

Usage : python3 -I experiments/crypto_backtest/collect_trades.py <dossier_de_travail> src
Pourquoi : l'historique « prices-history » donne un point toutes les 10 minutes même sans échange
(souvent le milieu d'un carnet vide, 0,50). Les transactions des preneurs donnent les prix
RÉELLEMENT payés : achat du Oui = prix du vendeur du Oui ; vente du Oui = prix de l'acheteur.
Un fichier par événement : [[horodatage, marché (conditionId), issue (0 = Oui), jeton, côté du preneur,
prix, quantité], ...].
L'API refuse un décalage au-delà de 10 000 : au plus 11 pages de 1 000 par événement.
"""
import gzip, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

WD = Path(sys.argv[1]); sys.path.insert(0, sys.argv[2])
from polymarket_agent.http_client import HttpClient, SourceUnavailable

rows = json.loads(gzip.decompress((WD / "rows.json.gz").read_bytes()))
events = sorted({r["event_id"] for r in rows})
out_dir = WD / "trades"; out_dir.mkdir(exist_ok=True)


def fetch(event_id):
    path = out_dir / f"{event_id}.json.gz"
    if path.exists():
        return 0
    http = HttpClient(timeout=40, min_interval=0.2)
    trades = []
    for page in range(11):
        try:
            batch = http.get_json("https://data-api.polymarket.com/trades",
                                  params={"eventId": event_id, "limit": 1000, "offset": page * 1000})
        except SourceUnavailable:
            break  # au-delà du décalage maximal ou panne : on garde ce qui est lu
        if not isinstance(batch, list) or not batch:
            break
        trades += [[int(t["timestamp"]), str(t["conditionId"]), int(t["outcomeIndex"]), str(t["asset"]),
                    t["side"], float(t["price"]), float(t["size"])] for t in batch]
        if len(batch) < 1000:
            break
    path.write_bytes(gzip.compress(json.dumps(trades).encode()))
    return len(trades)


with ThreadPoolExecutor(6) as pool:
    counts = list(pool.map(fetch, events))
print(f"événements : {len(events)}, transactions lues cette fois : {sum(counts)}")
