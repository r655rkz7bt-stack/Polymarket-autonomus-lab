"""Échanges réels des 972 échelles quotidiennes (Bitcoin / Ethereum / Solana / XRP « above ___ on <date> ? ») du relevé : data-api, cache gzip, 8 fils. Racine du dépôt."""
import json, re, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
sys.path.insert(0, "src")
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test as it
OUT = Path("experiments/crypto_apres_midi/donnees")
DAILY = re.compile(r"^(Bitcoin|Ethereum|Solana|XRP) above ___ on \w+ \d+\?$")
ids = [json.loads(l)["id"] for l in open(OUT / "echelles.jsonl") if DAILY.match(json.loads(l)["title"])]
http = HttpClient(min_interval=0.05)
def un(i): it.fetch_event_trades(http, OUT / "echanges", str(i)); return 1
with ThreadPoolExecutor(8) as ex: print("échanges", sum(ex.map(un, ids)), "sur", len(ids), flush=True)
