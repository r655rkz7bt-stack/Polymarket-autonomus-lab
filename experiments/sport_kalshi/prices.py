"""Test sport Kalshi, étape 3 : historiques de prix AVANT le coup d'envoi, sur les deux plateformes.

Usage : python3 -I experiments/sport_kalshi/prices.py <dossier_de_travail> src
Pour chaque proposition de props.json (étape 2), de 30 h avant le coup d'envoi jusqu'au coup d'envoi :
- Polymarket : historique public du CLOB (`prices-history`, pas d'une minute) du jeton « équipe A / Oui » ;
- Kalshi : chandeliers d'une minute (`/series/{série}/markets/{ticker}/candlesticks`, sans clé) :
  meilleur acheteur et meilleur vendeur du « Oui » à la FIN de chaque minute, et dernier échange.
Rien n'est lu après le coup d'envoi. Cache compact : <dossier>/prix/<plateforme>_<id>.json.gz.
"""
import gzip, json, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
W, SRC = sys.argv[1], sys.argv[2]
sys.path[:0] = [str(Path(__file__).resolve().parent), SRC]
from common import CLOB, KALSHI, http  # noqa: E402
from polymarket_agent.http_client import SourceUnavailable  # noqa: E402

BEFORE = 30 * 3600
OUT = Path(W) / "prix"
OUT.mkdir(parents=True, exist_ok=True)
props = json.load(open(f"{W}/props.json"))


def _save(path, rows):
    path.write_bytes(gzip.compress(json.dumps(rows).encode()))


def pm_job(p):
    path = OUT / f"pm_{p['pm_token'][:40]}_{p['start']}.json.gz"
    if path.exists():
        return 1
    try:
        raw = http(SRC).get_json(f"{CLOB}/prices-history", params={
            "market": p["pm_token"], "startTs": p["start"] - BEFORE, "endTs": p["start"], "fidelity": 1})
    except SourceUnavailable:
        return 0
    _save(path, [[pt["t"], pt["p"]] for pt in (raw or {}).get("history") or [] if pt.get("t", 1e18) <= p["start"]])
    return 1


def _f(d, k):
    try:
        return float((d or {}).get(k))
    except (TypeError, ValueError):
        return None


def k_job(args):
    series, ticker, start = args
    path = OUT / f"k_{ticker}_{start}.json.gz"
    if path.exists():
        return 1
    try:
        raw = http(SRC).get_json(f"{KALSHI}/series/{series}/markets/{ticker}/candlesticks", params={
            "start_ts": start - BEFORE, "end_ts": start, "period_interval": 1})
    except SourceUnavailable:
        return 0
    rows = [[c["end_period_ts"], _f(c.get("yes_bid"), "close_dollars"), _f(c.get("yes_ask"), "close_dollars"),
             _f(c.get("price"), "close_dollars"), _f(c, "volume_fp")]
            for c in (raw or {}).get("candlesticks") or [] if c.get("end_period_ts", 1e18) <= start]
    _save(path, rows)
    return 1


kjobs = sorted({(p["series"], t, p["start"]) for p in props for t in (p["k_ticker"], p["k_opp"]) if t})
with ThreadPoolExecutor(4) as pool_pm, ThreadPoolExecutor(3) as pool_k:
    f_pm = pool_pm.map(pm_job, props)
    f_k = pool_k.map(k_job, kjobs)
    ok_pm, ok_k = sum(f_pm), sum(f_k)
print(f"Polymarket : {ok_pm}/{len(props)} historiques ; Kalshi : {ok_k}/{len(kjobs)} historiques")
