"""Backtest crypto, étape 1 : collecte (marchés résolus, bougies Binance, DVOL Deribit, historiques de prix).

Usage : python3 -I experiments/crypto_backtest/collect.py <dossier_de_travail> src
Tout est gardé en cache dans <dossier>/ : relancer ne retélécharge que ce qui manque.
  - marchés résolus (API Gamma) : échelles quotidiennes « au-dessus de K le <jour> » (12 h ET),
    barrières quotidiennes, hebdomadaires et mensuelles « atteindre / descendre à K » ;
  - bougies horaires Binance (data-api.binance.vision, source de résolution des marchés) ;
  - DVOL Deribit (volatilité implicite à 30 jours, BTC et ETH) ;
  - historique complet du prix du « Oui » de chaque marché (CLOB prices-history), un appel par
    jeton : le prix à un instant est lu ensuite SANS regarder après cet instant (evaluate.py).
"""
import gzip, json, re, sys, threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

WD = Path(sys.argv[1]); sys.path.insert(0, sys.argv[2])
from polymarket_agent import idea_test as it
from polymarket_agent.crypto_model import parse_question
from polymarket_agent.http_client import HttpClient, SourceUnavailable

START, END = "2026-08-17", "2026-10-15"
ASSETS = {"bitcoin": "BTCUSDT", "ethereum": "ETHUSDT", "solana": "SOLUSDT", "xrp": "XRPUSDT"}
LADDER = r"^(bitcoin|ethereum|solana|xrp)-(above|price)-on-[a-z]+-\d+-2026$"
BARRIER = r"^what-price-will-(bitcoin|ethereum|solana|xrp)-hit-"
WD.mkdir(parents=True, exist_ok=True)
http = HttpClient(timeout=40, min_interval=0.15)


def save(name, obj):
    (WD / name).write_bytes(gzip.compress(json.dumps(obj).encode()))


def load(name):
    p = WD / name
    return json.loads(gzip.decompress(p.read_bytes())) if p.exists() else None


def ts(day):
    return int(datetime.fromisoformat(day).replace(tzinfo=timezone.utc).timestamp())


# 1. marchés résolus, par tranches d'une semaine (le tag « multi-strikes » mêle actions et
#    échelles horaires : le motif de slug ne garde que les échelles quotidiennes des 4 actifs)
rows = []
d = datetime.fromisoformat(START)
while d.strftime("%Y-%m-%d") <= END:
    a, b = d.strftime("%Y-%m-%d"), min(END, (d + timedelta(days=6)).strftime("%Y-%m-%d"))
    for tag, pat in ((102516, LADDER), (102134, BARRIER)):
        rows += it.fetch_resolved(http, WD / "gamma", a, b, tag_id=tag, slug_pattern=pat)
    d += timedelta(days=7)
rows = list({r.market_id: r for r in rows}.values())
rows = [r for r in rows if parse_question(r.question) is not None]
print(f"marchés résolus utilisables : {len(rows)}")

# 2. bougies horaires Binance [ouverture ms, ouv, haut, bas, clôture, ...]
t0, t1 = ts("2026-07-15") * 1000, ts("2026-10-16") * 1000
klines = load("klines.json.gz") or {}
for name, sym in ASSETS.items():
    if name in klines:
        continue
    out, cur = [], t0
    while cur < t1:
        batch = http.get_json("https://data-api.binance.vision/api/v3/klines",
                              params={"symbol": sym, "interval": "1h", "startTime": cur, "limit": 1000})
        if not batch:
            break
        out += [[int(k[0]), float(k[1]), float(k[2]), float(k[3]), float(k[4])] for k in batch]
        cur = int(batch[-1][0]) + 3600_000
    klines[name] = out
    print(f"bougies {sym} : {len(out)}")
save("klines.json.gz", klines)

# 2 bis. bougies d'une minute (prix au comptant à l'instant exact d'une transaction), [ouverture s, clôture]
k1 = load("klines1m.json.gz") or {}
for name, sym in ASSETS.items():
    if name in k1:
        continue
    out, cur = [], ts("2026-08-08") * 1000
    while cur < t1:
        batch = http.get_json("https://data-api.binance.vision/api/v3/klines",
                              params={"symbol": sym, "interval": "1m", "startTime": cur, "limit": 1000})
        if not batch:
            break
        out += [[int(k[0]) // 1000, float(k[4])] for k in batch]
        cur = int(batch[-1][0]) + 60_000
    k1[name] = out
    print(f"bougies 1 min {sym} : {len(out)}")
save("klines1m.json.gz", k1)

# 3. DVOL (indice de volatilité implicite à 30 jours, % annualisé), points horaires [ms, ouv, haut, bas, clôt]
dvol = load("dvol.json.gz") or {}
for cur_name in ("BTC", "ETH"):
    if cur_name in dvol:
        continue
    pts, end = {}, t1
    while True:
        raw = http.get_json("https://www.deribit.com/api/v2/public/get_volatility_index_data",
                            params={"currency": cur_name, "start_timestamp": t0, "end_timestamp": end,
                                    "resolution": 3600})["result"]
        for p in raw["data"]:
            pts[int(p[0])] = float(p[4])
        if not raw.get("continuation") or not raw["data"]:
            break
        end = int(raw["continuation"])
    dvol[cur_name] = sorted(pts.items())
    print(f"DVOL {cur_name} : {len(pts)} points")
save("dvol.json.gz", dvol)

# 4. historique de prix du « Oui » de chaque marché (un appel par jeton, mis en cache)
hist_dir = WD / "hist"; hist_dir.mkdir(exist_ok=True)
local = threading.local()


def history(r):
    path = hist_dir / f"{r.yes_token[-24:]}.json"
    if path.exists():
        return 0
    monthly = "-hit-in-" in r.event_slug
    start = r.end - (32 if monthly else 8) * 86400
    if not hasattr(local, "http"):
        local.http = HttpClient(timeout=40, min_interval=0.15)
    points = {}
    cur = start
    while cur < r.end + 3600:  # le CLOB refuse un intervalle de plus de 14 jours : tranches de 12 jours
        stop = min(cur + 12 * 86400, r.end + 3600)
        try:
            raw = local.http.get_json(f"{it.CLOB}/prices-history", params={
                "market": r.yes_token, "startTs": cur, "endTs": stop, "fidelity": 60 if monthly else 10})
        except SourceUnavailable:
            return 1
        points.update({int(p["t"]): float(p["p"]) for p in (raw or {}).get("history") or []})
        cur = stop
    path.write_text(json.dumps(sorted(points.items())))
    return 0


with ThreadPoolExecutor(6) as pool:
    fails = sum(pool.map(history, rows))
print(f"historiques : {len(rows) - fails} / {len(rows)} (échecs : {fails})")
save("rows.json.gz", [r.__dict__ for r in rows])
