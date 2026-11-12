"""Vrais échanges (Data API v2, par événement) des événements Michigan ; sortie releves/echanges.json {event_id: [lignes v1]}"""
import gzip, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent import data_api
from polymarket_agent.http_client import HttpClient

R = Path(__file__).resolve().parents[1] / "releves"
ms = json.load(gzip.open(R / "marches.json.gz"))
http = HttpClient()
out = {}
for eid in sorted({m["event"] for m in ms}):
    rows = data_api.echanges_evenement(http, eid, pages=30)
    out[eid] = [{k: r.get(k) for k in ("asset", "side", "price", "size", "timestamp", "conditionId", "outcome")} for r in rows]
    print(eid, len(rows), flush=True)
gzip.open(R / "echanges.json.gz", "wt").write(json.dumps(out))
