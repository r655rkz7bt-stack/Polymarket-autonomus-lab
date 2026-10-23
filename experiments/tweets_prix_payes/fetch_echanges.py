"""Compteur de tweets aux prix payés (23/10/2026) : pour chaque période (7 comptes, juillet à octobre 2026 ; liste recalculée
comme dans tweets_releve_marches.py), relit l'événement Gamma (jetons OUI/NON de chaque tranche, barème de frais) et télécharge
tous les échanges (data-api, au plus 11 000 par événement). Écrit donnees/xt/echanges_par_periode.json.
À lancer depuis experiments/tweets_prix_payes/ avec PYTHONPATH=../../src."""
import json, sys
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from polymarket_agent.http_client import HttpClient
from polymarket_agent import idea_test

D = Path("donnees/xt")
S = requests.Session()
S.headers["User-Agent"] = "curl/8"
http = HttpClient()
PREFIX = {"elonmusk": "elon-musk-of-tweets", "WhiteHouse": "white-house-of-tweets", "tedcruz": "ted-cruz-of-tweets",
          "ZelenskyyUa": "zelenskyy-of-tweets", "realDonaldTrump": "donald-trump-of-truth-social-posts",
          "NYCMayor": "nyc-mayor-of-tweets", "cz_binance": "cz-binance-of-tweets"}
ev = []
day = datetime(2026, 7, 1, 16, tzinfo=timezone.utc)
while day < datetime(2026, 10, 22, tzinfo=timezone.utc):
    if day.weekday() in (1, 4):  # périodes hebdomadaires qui commencent un mardi ou un vendredi
        end = day + timedelta(days=7)
        tag = f"{day:%B}-{day.day}-{end:%B}-{end.day}-{end.year}".lower()
        for h, p in PREFIX.items():
            ev.append({"compte": h, "debut": day.isoformat(), "fin": end.isoformat(), "slug": f"{p}-{tag}"})
    day += timedelta(days=1)

def one(e):
    r = S.get("https://gamma-api.polymarket.com/events", params={"slug": e["slug"]}, timeout=40).json()
    if not r:
        return e["slug"], None
    r = r[0]
    marches = []
    for m in r.get("markets") or []:
        tok = json.loads(m.get("clobTokenIds") or "[]")
        if len(tok) == 2:
            marches.append({"titre": m.get("groupItemTitle"), "yes": tok[0], "no": tok[1],
                            "frais": m.get("feeSchedule"), "final": m.get("outcomePrices")})
    trades = idea_test.fetch_event_trades(http, D / "cache", str(r["id"]))
    return e["slug"], {"compte": e["compte"], "debut": e["debut"], "fin": e["fin"], "event_id": r["id"], "marches": marches, "echanges": len(trades), "volume": r.get("volume")}

out = {}
with ThreadPoolExecutor(6) as pool:
    for slug, info in pool.map(one, ev):
        out[slug] = info
        print(slug, None if info is None else (info["event_id"], len(info["marches"]), info["echanges"]), flush=True)
json.dump(out, open(D / "echanges_par_periode.json", "w"))
