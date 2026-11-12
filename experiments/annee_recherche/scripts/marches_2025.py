"""Marchés « Year in Search » 2025 réglés (Polymarket) : prix de chaque candidat à J-30, J-7, J-1 avant
la publication (04/12/2025 ≈ 07 h UTC) et issue. Sortie : releves/marches_2025.json"""
import json, time, datetime as dt
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).resolve().parents[1] / "releves" / "marches_2025.json"
EVENTS = [59297, 64121, 62580, 59787, 59790, 63206, 85772]
PUB = dt.datetime(2025, 12, 4, 6, 0, tzinfo=dt.timezone.utc)


def prix(tok, t):
    ts = int(t.timestamp())
    h = requests.get("https://clob.polymarket.com/prices-history", timeout=30,
                     params={"market": tok, "startTs": ts - 24 * 3600, "endTs": ts, "fidelity": 60}).json().get("history", [])
    return h[-1]["p"] if h else None


res = []
for eid in EVENTS:
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    for m in e["markets"]:
        if float(m.get("volume") or 0) < 100:
            continue
        op = json.loads(m["outcomePrices"]); tok = json.loads(m["clobTokenIds"])[0]
        row = {"event": eid, "titre": e["title"], "nom": m.get("groupItemTitle"), "volume": float(m["volume"]),
               "issue": float(op[0])}
        for j in (30, 7, 1):
            row[f"p{j}"] = prix(tok, PUB - dt.timedelta(days=j))
        res.append(row)
    print(eid, e["title"], len(res), flush=True)
OUT.write_text(json.dumps(res, ensure_ascii=False, indent=0))
