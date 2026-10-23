"""Piste n° 2 (toucher_avant_fin), partie b : modèle de barrière (principe de réflexion) contre le prix PAYÉ des marchés « toucher ».

Usage : .venv/bin/python experiments/toucher_avant_fin/barriere.py [dossier_données]
Même collecte que coherence.py (marchés réglés du 17/08 au 15/10/2026, bougies Binance, DVOL Deribit, échanges réels).
Question : crypto_threshold a échoué sur les échelles (experiments/crypto_backtest.md) ; les barrières sont-elles différentes ?

Un cas = une barrière vue à un instant t (jour : 20/12/6/2 h avant la fin ; semaine : 144/96/48/24/12 h ; mois : 20/14/7/3/1 j),
seulement si la période a commencé et que la barrière n'est pas encore touchée (bougies horaires puis d'une minute jusqu'à t).
Modèle : P(toucher) = min(1, 2 × P(finir au-delà)), marche sans dérive, σ = DVOL (volatilité implicite Deribit) × k ou
σ réalisée sur 7 jours × k ; SOL et XRP : σ réalisée × (DVOL BTC / σ réalisée BTC). Prix au comptant : bougie d'une minute avant t.
Décision : prix connus = derniers échanges réels dans l'heure AVANT t ; achat au PREMIER échange réel de la bonne sorte dans
l'heure APRÈS t (prix d'après), frais du marché. Réglage (σ, k, seuil) sur les 30 premiers jours, jugement sur les 30 suivants.
"""
import bisect
import gzip
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, "experiments/crypto_backtest")
from polymarket_agent import idea_test as it
from polymarket_agent.crypto_model import parse_question
from donnees import OFFSETS, Series, dvol_at, window_start  # outils sans regard vers le futur du test crypto du 16/10

WD = Path(sys.argv[1] if len(sys.argv) > 1 else "experiments/toucher_avant_fin/donnees")
H = 3600
SHORT = {"bitcoin": "btc", "ethereum": "eth", "solana": "sol", "xrp": "xrp"}


def load(name):
    return json.loads(gzip.decompress((WD / name).read_bytes()))


rows = [it.Resolved(**r) for r in load("rows.json.gz")]
kl = {a: Series(v) for a, v in load("klines.json.gz").items()}
k1 = load("klines1m.json.gz")
k1t = {a: [r[0] + 60 for r in v] for a, v in k1.items()}   # fin de chaque bougie d'une minute
dv = load("dvol.json.gz")


def spot1m(asset, t):
    i = bisect.bisect_right(k1t[asset], t) - 1
    return k1[asset][i][1] if i >= 0 and t - k1t[asset][i] <= 180 else None


def max_min_1m(asset, a, b):
    """Plus haut / plus bas des clôtures d'une minute terminées entre a et b (complète les bougies horaires)."""
    i, j = bisect.bisect_left(k1t[asset], a), bisect.bisect_right(k1t[asset], b)
    seg = [r[1] for r in k1[asset][i:j]]
    return (max(seg), min(seg)) if seg else (None, None)


# ---------------------------------------------------------------- échanges réels : séries « acheter OUI » / « acheter NON »
markets = []
for r in rows:
    q = parse_question(r.question)
    m = re.match(r"^what-price-will-(bitcoin|ethereum|solana|xrp)-hit-", r.event_slug)
    if q is None or not m or q.kind not in ("touch_up", "touch_down"):
        continue
    r.q, r.asset = q, m.group(1)
    r.typ = "jour" if "-hit-on-" in r.event_slug else "mois" if "-hit-in-" in r.event_slug else "semaine"
    markets.append(r)
by_event = defaultdict(list)
for r in markets:
    by_event[r.event_id].append(r)
buy_yes, buy_no = {}, {}
for ev, group in by_event.items():
    p = WD / "trades" / f"{ev}.json.gz"
    trades = json.loads(gzip.decompress(p.read_bytes())) if p.exists() else []
    cond_of = {t[3]: t[1] for t in trades if t[2] == 0}
    per = defaultdict(list)
    for t in trades:
        per[t[1]].append(t)
    for r in group:
        y, n = [], []
        for ts_, _, outcome, _, side, price, _ in sorted(per.get(cond_of.get(r.yes_token), []), key=lambda t: t[0]):
            if (outcome == 0) == (side == "BUY"):
                y.append((ts_, price if outcome == 0 else 1 - price))
            else:
                n.append((ts_, price if outcome == 1 else 1 - price))
        buy_yes[r.market_id], buy_no[r.market_id] = y, n


def before(series, t, w=H):
    i = bisect.bisect_right(series, (t, 2.0)) - 1
    return series[i][1] if i >= 0 and t - series[i][0] <= w else None


def after(series, t, w=H):
    i = bisect.bisect_right(series, (t, 2.0))
    return series[i][1] if i < len(series) and series[i][0] - t <= w else None


# ---------------------------------------------------------------- cas
OFF = {"jour": OFFSETS["barriere_jour"], "semaine": OFFSETS["barriere_semaine"], "mois": OFFSETS["barriere_mois"]}
cases, skipped = [], defaultdict(int)
for r in markets:
    start = window_start(r)
    s = kl[r.asset]
    for off in OFF[r.typ]:
        t = r.end - off * H
        if t < start:
            skipped["période pas commencée"] += 1
            continue
        spot, rv = spot1m(r.asset, t), s.rv(t)
        if spot is None or rv is None:
            skipped["données"] += 1
            continue
        hi, lo = s.extremes(start, t)
        hi2, lo2 = max_min_1m(r.asset, max(start, s.close_t[s.idx(t)] if s.idx(t) >= 0 else start), t)
        hi = max(x for x in (hi, hi2, spot) if x is not None)
        lo = min(x for x in (lo, lo2, spot) if x is not None)
        if (r.q.kind == "touch_up" and hi >= r.q.threshold) or (r.q.kind == "touch_down" and lo <= r.q.threshold):
            skipped["déjà touchée"] += 1
            continue
        ky, kn = before(buy_yes[r.market_id], t), before(buy_no[r.market_id], t)
        if ky is None and kn is None:
            skipped["sans échange avant"] += 1
            continue
        iv = dvol_at(dv["ETH" if r.asset == "ethereum" else "BTC"], t)
        if iv is not None and r.asset in ("solana", "xrp"):
            rvb = kl["bitcoin"].rv(t)
            iv = rv * iv / rvb if rvb else None
        cases.append(dict(r=r, t=t, spot=spot, rv=rv, iv=iv, hours=(r.end - t) / H, ky=ky, kn=kn,
                          ay=after(buy_yes[r.market_id], t), an=after(buy_no[r.market_id], t), day=it.day_of(r.end)))
print(f"barrières : {len(markets)} ; cas : {len(cases)} ; écartés : {dict(skipped)}")


def model(c, vol, k):
    sig = (c["iv"] if vol == "dvol" else c["rv"])
    if sig is None:
        return None
    z = math.log(c["r"].q.threshold / c["spot"]) / (sig * k * math.sqrt(c["hours"]))
    phi = 0.5 * (1 + math.erf(z / math.sqrt(2)))
    p = 2 * (1 - phi) if c["r"].q.kind == "touch_up" else 2 * phi
    return min(0.999, max(0.001, p))


def run(sub, vol, k, edge):
    out = []
    for c in sub:
        pm, r = model(c, vol, k), c["r"]
        if pm is None:
            continue
        mois = datetime.fromtimestamp(c["t"], tz=timezone.utc).strftime("%Y-%m")
        if c["ky"] is not None and pm - c["ky"] - it.fee(c["ky"], r.fee_rate) > edge:
            if c["ay"] is not None:
                paid = c["ay"] + it.fee(c["ay"], r.fee_rate)
                out.append(dict(gain=r.won / paid - 1, evenement=r.event_id, cout=paid, mois=mois, sens="OUI", typ=r.typ, jour=c["day"]))
        elif c["kn"] is not None and (1 - pm) - c["kn"] - it.fee(c["kn"], r.fee_rate) > edge:
            if c["an"] is not None:
                paid = c["an"] + it.fee(c["an"], r.fee_rate)
                out.append(dict(gain=(1 - r.won) / paid - 1, evenement=r.event_id, cout=paid, mois=mois, sens="NON", typ=r.typ, jour=c["day"]))
    return out


days = sorted({c["day"] for c in cases})
cut = days[len(days) // 2]
train = [c for c in cases if c["day"] < cut]
test = [c for c in cases if c["day"] >= cut]
print(f"coupure : {cut} ; apprentissage {len(train)} cas, jugement {len(test)} cas")


def brier(sub, f):
    vals = [(f(c), c["r"].won) for c in sub]
    vals = [(p, y) for p, y in vals if p is not None]
    return sum((p - y) ** 2 for p, y in vals) / len(vals) if vals else float("nan"), len(vals)


# Précision : prix connu (milieu des deux derniers échanges quand les deux existent) contre modèle
both = [c for c in test if c["ky"] is not None and c["kn"] is not None]
mid = lambda c: (c["ky"] + 1 - c["kn"]) / 2
print(f"Brier sur le jugement ({len(both)} cas avec les deux côtés échangés) : marché {brier(both, mid)[0]:.4f} | "
      f"DVOL {brier(both, lambda c: model(c, 'dvol', 1.0))[0]:.4f} | σ réalisée {brier(both, lambda c: model(c, 'rv', 1.0))[0]:.4f}")

grid = [(v, k, e) for v in ("dvol", "rv") for k in (0.9, 1.0, 1.15, 1.3) for e in (0.03, 0.05, 0.08)]
print(f"réglages essayés : {len(grid)} (σ × k × seuil)")
res = []
for v, k, e in grid:
    tr, te = run(train, v, k, e), run(test, v, k, e)
    mt = sum(x["gain"] for x in tr) / len(tr) if tr else float("nan")
    ms = sum(x["gain"] for x in te) / len(te) if te else float("nan")
    res.append((mt, len(tr), v, k, e, ms, len(te)))
    print(f"   {v} k {k} seuil {e} : apprentissage {len(tr)} paris {100 * mt:+.1f} % | jugement {len(te)} paris {100 * ms:+.1f} %")
pos = sum(1 for x in res if x[5] > 0)
print(f"réglages gagnants sur le jugement : {pos} / {len(res)}")
best = max((x for x in res if x[1] >= 30), key=lambda x: x[0])
_, _, v, k, e, _, _ = best
te = run(test, v, k, e)
print(f"\nmeilleur réglage sur l'apprentissage : σ {v}, k {k}, seuil {e} → jugement :")
print(json.dumps(it.verdict(te), ensure_ascii=False))
for key in ("sens", "typ"):
    g = defaultdict(list)
    for x in te:
        g[x[key]].append(x["gain"])
    print(f"   par {key} :", {a: f"{len(b)} paris {100 * sum(b) / len(b):+.1f} %" for a, b in sorted(g.items())})
jours = defaultdict(float)
for x in te:
    jours[x["jour"]] += x["gain"] * x["cout"]
print(f"   jours gagnants : {sum(1 for g in jours.values() if g > 0)} / {len(jours)}")
