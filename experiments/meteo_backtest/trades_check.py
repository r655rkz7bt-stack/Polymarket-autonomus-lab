"""Météo : le gain tient-il aux prix RÉELLEMENT payés ? (16/10/2026)

Usage : python3 -I experiments/meteo_backtest/trades_check.py <dossier_de_travail> src
Pourquoi : le test crypto (experiments/crypto_backtest.md) a montré que l'historique « toutes les
10 minutes » du CLOB peut inventer des gains (milieu de carnets vides, prix périmés). Ici, même
modèle que station_bias.py (prévisions de la VEILLE, biais et flou par station appris sur les
jours précédents), mais le prix du NON est celui d'un échange réel d'un preneur :
achat du NON au prix p, ou vente du OUI au prix p (= achat du NON à 1 − p).
  GET https://data-api.polymarket.com/trades?eventId=<id>&limit=1000&offset=..  (public, sans clé)
Deux fenêtres : dernier échange dans les 2 h AVANT le début du jour local (prix connu à la
décision), ou premier échange dans les 2 h APRÈS (prix qu'on aurait payé en agissant à ce moment).
"""
import glob
import gzip
import json
import os
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

SP = sys.argv[1]
sys.path.insert(0, sys.argv[2])
from polymarket_agent import idea_test as it  # noqa: E402
from polymarket_agent import weather_model as wm  # noqa: E402
from polymarket_agent.http_client import HttpClient, SourceUnavailable  # noqa: E402
from polymarket_agent.weather_calibration import station_params  # noqa: E402

D = json.load(open(f"{SP}/bt/data.json"))
fc = D["fc"]
events = {}
for f in glob.glob(f"{SP}/bt/ev_*.json"):
    for ev in json.load(open(f)):
        events[ev["slug"]] = ev
no_of = {}
for ev in events.values():
    for m in ev.get("markets") or []:
        toks = json.loads(m.get("clobTokenIds") or "[]")
        if len(toks) == 2:
            no_of[toks[0]] = toks[1]

os.makedirs(f"{SP}/bt/trades", exist_ok=True)


def fetch(slug):
    ev = events.get(slug)
    path = f"{SP}/bt/trades/{slug}.json.gz"
    if ev is None or os.path.exists(path):
        return 0
    http, rows = HttpClient(timeout=40, min_interval=0.2), []
    for page in range(11):
        try:
            batch = http.get_json("https://data-api.polymarket.com/trades",
                                  params={"eventId": ev["id"], "limit": 1000, "offset": page * 1000})
        except SourceUnavailable:
            break
        if not isinstance(batch, list) or not batch:
            break
        rows += [[int(t["timestamp"]), str(t["asset"]), t["side"], float(t["price"])] for t in batch]
        if len(batch) < 1000:
            break
    open(path, "wb").write(gzip.compress(json.dumps(rows).encode()))
    return len(rows)


with ThreadPoolExecutor(6) as ex:
    print("échanges lus :", sum(ex.map(fetch, sorted({r["event"] for r in D["rows"]}))))

no_prices = defaultdict(list)  # jeton NON → [(heure, prix payé pour le NON)]
for slug in {r["event"] for r in D["rows"]}:
    path = f"{SP}/bt/trades/{slug}.json.gz"
    if not os.path.exists(path):
        continue
    for t, asset, side, p in json.loads(gzip.decompress(open(path, "rb").read())):
        if side == "BUY" and asset in no_of.values():
            no_prices[asset].append((t, p))
        elif side == "SELL" and asset in no_of:
            no_prices[no_of[asset]].append((t, 1 - p))
for v in no_prices.values():
    v.sort()


def daily(st, date, kind, model):
    f = fc.get(st)
    if not f:
        return None
    h = f["hourly"]
    vals = [v for t, v in zip(h["time"], h.get(f"temperature_2m_previous_day1_{model}", []))
            if t.startswith(date) and v is not None]
    return (max(vals) if kind == "max" else min(vals)) if len(vals) >= 20 else None


truth = {}
for r in D["rows"]:
    if r["won"] == 1:
        q = wm.parse_question(r["q"])
        lo, hi = q.low, q.high
        v = (lo + hi) / 2 if lo != -wm.INF and hi != wm.INF else (lo + 0.5 if hi == wm.INF else hi - 0.5)
        truth[(r["station"], r["date"], q.kind)] = (v - 32) / 1.8 if q.unit == "F" else v
cases = []
for r in D["rows"]:
    q = wm.parse_question(r["q"])
    g, e = daily(r["station"], r["date"], q.kind, "gfs_seamless"), daily(r["station"], r["date"], q.kind, "ecmwf_ifs025")
    if g is None or e is None or r.get("t0") is None or r["yes"] not in no_of:
        continue
    cases.append((r, q, [g, e]))
err = defaultdict(dict)
for r, q, mem in cases:
    t = truth.get((r["station"], r["date"], q.kind))
    if t is not None:
        err[(r["station"], q.kind)][r["date"]] = t - sum(mem) / len(mem)
GLOBAL = {"max": (1.5, 0.5), "min": (1.8, 0.0)}


def prob_yes(r, q, mem):
    past = [v for d, v in sorted(err[(r["station"], q.kind)].items()) if d < r["date"]][-7:][::-1]
    s, b, _ = station_params(past, *GLOBAL[q.kind])
    return wm.probability(q, mem, s, b)


days = sorted({r["date"] for r, _, _ in cases})
test_days = set(days[len(days) // 2:])
print(f"cas : {len(cases)}, jours jugés : {min(test_days)} → {max(test_days)}")
for window in ("avant", "après"):
    for edge in (0.05, 0.08):
        for slip in (0.0, 0.01):
            g = c = k = 0.0
            by_day = defaultdict(float)
            seen = 0
            for r, q, mem in cases:
                if r["date"] not in test_days:
                    continue
                pts = no_prices.get(no_of[r["yes"]], [])
                t0 = r["t0"]
                if window == "avant":
                    sel = [p for t, p in pts if t0 - 7200 <= t <= t0]
                    price = sel[-1] if sel else None
                else:
                    sel = [p for t, p in pts if t0 <= t <= t0 + 7200]
                    price = sel[0] if sel else None
                if price is None:
                    continue
                seen += 1
                cost = price + slip
                if not 0.2 <= cost <= 0.8:
                    continue
                pn = 1 - prob_yes(r, q, mem)
                f = it.fee(cost, 0.05)
                if pn - cost - f <= edge:
                    continue
                gain = (1 - r["won"]) - cost - f
                g += gain; c += cost; k += 1; by_day[r["date"]] += gain
            print(f"| {window} | seuil {edge} | écart +{slip} | cas avec échange : {seen} | paris : {int(k)} | "
                  f"rendement : {100 * g / c if c else float('nan'):+.1f} % | jours gagnants : "
                  f"{sum(1 for v in by_day.values() if v > 0)} / {len(by_day)} |")
