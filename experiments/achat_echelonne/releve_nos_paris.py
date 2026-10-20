"""Chemins de prix (1 minute) des paris « favori » réellement pris par nos fantômes."""
import glob, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
sys.path.insert(0, "src")
from polymarket_agent.reporting import closed_trades
D = "donnees/ech"
trades = {}
for p in glob.glob("published_data/ledger/fantome/*.jsonl"):
    name = os.path.basename(p)[:-6]
    if not name.startswith(("nf_", "naive_favorite", "favori_politique", "outsider_sport", "parking")):
        continue
    E = [json.loads(l) for l in open(p) if l.strip()]
    first_buy = {}
    for e in E:
        if e["type"] == "BUY":
            first_buy.setdefault(e["data"]["token_id"], e)
    for t in closed_trades(E):
        if t.get("payout") is None:
            continue
        b = first_buy.get(t["token_id"])
        if not b:
            continue
        x = b["data"].get("extra") or {}
        row = {"token": t["token_id"], "strategie": name, "ouvert": t["opened_at"], "ferme": t["closed_at"],
               "prix": float(b["data"]["price"]), "paiement": float(t["payout"]), "issue": t["outcome"],
               "pose": bool(x.get("order_type") or x.get("resting_order")), "evenement": t["event_id"],
               "horizon": float(x.get("horizon_hours") or 0)}
        if t["token_id"] not in trades or row["ouvert"] < trades[t["token_id"]]["ouvert"]:
            trades[t["token_id"]] = row
rows = list(trades.values())
print("jetons uniques", len(rows), flush=True)
s = requests.Session()
def ts(x): return int(datetime.fromisoformat(x).timestamp())
def hist(r):
    for k in range(4):
        try:
            h = s.get("https://clob.polymarket.com/prices-history", params={"market": r["token"], "startTs": ts(r["ouvert"]) - 60,
                      "endTs": ts(r["ferme"]), "fidelity": 1}, timeout=40).json()
            r["chemin"] = [(x["t"], x["p"]) for x in h.get("history") or []]; return
        except Exception:
            time.sleep(2 ** k)
    r["chemin"] = []
with ThreadPoolExecutor(4) as ex: list(ex.map(hist, rows))
json.dump(rows, open(f"{D}/paths.json", "w"))
print("fini", sum(1 for r in rows if len(r["chemin"]) > 3), flush=True)
