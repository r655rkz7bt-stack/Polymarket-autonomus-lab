"""Inventaire des événements OUVERTS de Gamma dont la règle cite une source officielle lisible (domaine de l'URL dans la
description ou `resolutionSource`), hors sport et crypto. But : trouver d'autres « compteurs officiels à lecture directe »
(piste n° 8 : rougeole, séismes, sécheresse, tornades…). Relevé par `/events/keyset` (jamais `offset`).
Sortie : releves/inventaire_AAAA-MM-JJ.json et résumé par domaine (événements, liquidité)."""
import json, re, time, collections, datetime as dt
from pathlib import Path
import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).resolve().parent / "releves"
OUT.mkdir(exist_ok=True)
URL = re.compile(r"https?://(?:www\.)?([a-z0-9.-]+\.[a-z]{2,})", re.I)
EXCLU = ("polymarket.com", "binance.com", "coinbase.com", "chain.link", "pyth.network", "x.com", "twitter.com", "truthsocial.com",
         "espn.com", "nba.com", "nfl.com", "mlb.com", "nhl.com", "ufc.com", "hltv.org", "liquipedia.net", "atptour.com",
         "wtatennis.com", "premierleague.com", "uefa.com", "fifa.com", "youtube.com", "coingecko.com", "coinmarketcap.com",
         "tradingview.com", "google.com", "yahoo.com", "bloomberg.com", "reuters.com", "apnews.com")
rows, cur, n = [], None, 0
while True:
    params = {"closed": "false", "limit": 500, "order": "volume24hr", "ascending": "false"}
    if cur:
        params["after_cursor"] = cur
    d = requests.get("https://gamma-api.polymarket.com/events/keyset", headers=H, params=params, timeout=60).json()
    evs = d.get("events") or d.get("data") or []
    for e in evs:
        txt = (e.get("description") or "") + " " + (e.get("resolutionSource") or "")
        doms = sorted({m.lower() for m in URL.findall(txt)} - set())
        doms = [x for x in doms if not any(x.endswith(ex) for ex in EXCLU)]
        if doms:
            rows.append({"id": e["id"], "titre": e.get("title"), "fin": (e.get("endDate") or "")[:10],
                         "liquidite": float(e.get("liquidity") or 0), "volume": float(e.get("volume") or 0), "domaines": doms})
    n += len(evs)
    cur = d.get("next_cursor")
    if not cur or not evs or n > 30000:
        break
    time.sleep(0.2)
jour = dt.date.today().isoformat()
import gzip
with gzip.open(OUT / f"inventaire_{jour}.json.gz", "wt") as fh:
    json.dump(rows, fh, ensure_ascii=False)
agg = collections.defaultdict(lambda: [0, 0.0, []])
for r in rows:
    for x in r["domaines"]:
        agg[x][0] += 1; agg[x][1] += r["liquidite"]; agg[x][2].append(r["titre"])
print(n, "événements lus,", len(rows), "avec une source officielle citée")
for x, (c, liq, t) in sorted(agg.items(), key=lambda kv: -kv[1][1])[:60]:
    print(f"{x:38s} {c:4d} év. {liq:12,.0f} $  ex. {t[0][:60]}")
