"""Backtest crypto : cas de décision construits à partir de la collecte (collect.py), sans regard vers le futur.

Un cas = un marché résolu vu à un instant de décision t (N heures avant l'échéance) :
  - prix du « Oui » = dernier point de l'historique CLOB à t ou avant (6 h au plus) ;
  - prix au comptant = clôture de la dernière bougie horaire Binance terminée à t ;
  - volatilité réalisée = écart-type des 168 rendements horaires précédents (comme la production) ;
  - volatilité implicite = DVOL Deribit (BTC, ETH) à t ; SOL et XRP : réalisée × (DVOL BTC / réalisée BTC) ;
  - barrières : cas écarté si la barrière a déjà été touchée entre le début de la période et t
    (le marché est alors déjà réglé) ; plus haut / plus bas lus sur les bougies horaires.
Le découpage apprentissage / jugement se fait sur le JOUR D'ÉCHÉANCE (un même marché vu à
plusieurs instants reste entièrement d'un seul côté).
"""
import bisect, gzip, json, math, re, sys
from datetime import datetime, timezone
from pathlib import Path

from polymarket_agent import idea_test as it
from polymarket_agent.crypto_model import parse_question

H = 3600
OFFSETS = {"echelle": (72, 48, 24, 12, 6, 2), "barriere_jour": (20, 12, 6, 2),
           "barriere_semaine": (144, 96, 48, 24, 12),
           "barriere_mois": (480, 336, 168, 72, 24)}
SHORT = {"bitcoin": "btc", "ethereum": "eth", "solana": "sol", "xrp": "xrp"}


def _load(wd, name):
    return json.loads(gzip.decompress((Path(wd) / name).read_bytes()))


class Series:
    def __init__(self, klines):
        self.k = klines  # [ouverture ms, ouv, haut, bas, clôture]
        self.close_t = [int(k[0] // 1000) + H for k in klines]  # fin de chaque bougie (s)

    def idx(self, t):
        """Indice de la dernière bougie TERMINÉE à t (ou avant)."""
        return bisect.bisect_right(self.close_t, t) - 1

    def spot(self, t):
        i = self.idx(t)
        return self.k[i][4] if i >= 0 and t - self.close_t[i] < 2 * H else None

    def rv(self, t, n=168):
        i = self.idx(t)
        if i < n:
            return None
        closes = [k[4] for k in self.k[i - n:i + 1]]
        rets = [math.log(b / a) for a, b in zip(closes, closes[1:])]
        m = sum(rets) / len(rets)
        return math.sqrt(sum((r - m) ** 2 for r in rets) / (len(rets) - 1))

    def extremes(self, t_from, t_to):
        lo = bisect.bisect_left(self.close_t, t_from + H)  # bougies commencées à t_from ou après
        hi = self.idx(t_to)
        ks = self.k[lo:hi + 1]
        if not ks:
            return None, None
        return max(k[2] for k in ks), min(k[3] for k in ks)


def dvol_at(points, t):
    """Clôture du dernier point horaire DVOL terminé à t, en volatilité HORAIRE."""
    ts = [p[0] // 1000 + H for p in points]
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > 3 * H:
        return None
    return points[i][1] / 100 / math.sqrt(24 * 365)


def price_at(hist, t, window=6 * H):
    ts = [p[0] for p in hist]
    i = bisect.bisect_right(ts, t) - 1
    if i < 0 or t - ts[i] > window:
        return None
    return hist[i][1]


def window_start(row):
    """Début de la période d'une barrière (jour : échéance − 24 h ; semaine : − 7 j ; mois : le 1er à 0 h ET)."""
    if "-hit-on-" in row.event_slug:
        return row.end - 86400
    if "-hit-in-" in row.event_slug:
        end = datetime.fromtimestamp(row.end, tz=timezone.utc)
        month = end.month - 1 or 12
        year = end.year if end.month > 1 else end.year - 1
        return int(datetime(year, month, 1, 4, tzinfo=timezone.utc).timestamp())
    return row.end - 7 * 86400


def build_cases(wd, src=None):
    wd = Path(wd)
    rows = [it.Resolved(**r) for r in _load(wd, "rows.json.gz")]
    kl = {a: Series(v) for a, v in _load(wd, "klines.json.gz").items()}
    dv = _load(wd, "dvol.json.gz")
    cases, skipped = [], {"sans prix": 0, "prix extrême": 0, "barrière déjà touchée": 0, "données": 0}
    for r in rows:
        q = parse_question(r.question)
        m = re.match(r"^(?:what-price-will-)?(bitcoin|ethereum|solana|xrp)-", r.event_slug)
        if q is None or not m:
            continue
        asset = m.group(1)
        typ = ("barriere_jour" if "-hit-on-" in r.event_slug else "echelle" if "-above-on-" in r.event_slug
               else "barriere_mois" if "-hit-in-" in r.event_slug else "barriere_semaine")
        hp = wd / "hist" / f"{r.yes_token[-24:]}.json"
        hist = json.loads(hp.read_text()) if hp.exists() else []
        s = kl[asset]
        for off in OFFSETS[typ]:
            t = r.end - off * H
            p = price_at(hist, t)
            if p is None:
                skipped["sans prix"] += 1
                continue
            if not 0.01 <= p <= 0.99:
                skipped["prix extrême"] += 1
                continue
            spot, rv = s.spot(t), s.rv(t)
            if spot is None or rv is None:
                skipped["données"] += 1
                continue
            if typ != "echelle":
                start = window_start(r)
                if t < start:
                    continue
                hi, lo = s.extremes(start, t)
                touched = (q.kind == "touch_up" and (spot >= q.threshold or (hi or 0) >= q.threshold)) or \
                          (q.kind == "touch_down" and (spot <= q.threshold or (lo or 1e18) <= q.threshold))
                if touched:
                    skipped["barrière déjà touchée"] += 1
                    continue
            cur = "BTC" if asset not in ("ethereum",) else "ETH"
            iv = dvol_at(dv[cur], t)
            if iv is not None and asset in ("solana", "xrp"):
                rvb = kl["bitcoin"].rv(t)
                iv = rv * iv / rvb if rvb else None
            c = it.Case(r, p, SHORT[asset], it.day_of(r.end))
            c.q, c.spot, c.rv, c.iv, c.hours, c.typ, c.t = q, spot, rv, iv, float(off), typ, t
            c.dist = math.log(q.threshold / spot) / (rv * math.sqrt(off))  # distance en écarts-types
            cases.append(c)
    return cases, skipped



def attach_trades(wd, cases, look=3600):
    """Ajoute à chaque cas le dernier prix RÉELLEMENT payé par un preneur dans l'heure avant t, de
    chaque côté : c.ask = prix d'achat du Oui (achat du Oui, ou 1 − vente du Non), c.bid = prix de
    vente du Oui (vente du Oui, ou 1 − achat du Non) ; None si aucune transaction de ce côté.
    c.ask_case / c.bid_case : le même cas recalculé À L'INSTANT EXACT de cette transaction (prix au
    comptant de la bougie d'une minute terminée avant, volatilités et horizon à cet instant) : le
    modèle ne voit ainsi rien de postérieur au prix qu'il compare (le « prix du marché » de ces cas
    est le prix de la transaction elle-même)."""
    import copy
    wd = Path(wd)
    k1 = {SHORT[a]: v for a, v in _load(wd, "klines1m.json.gz").items()}
    k1t = {a: [r[0] + 60 for r in v] for a, v in k1.items()}  # fin de chaque bougie d'une minute
    kl = {SHORT[a]: Series(v) for a, v in _load(wd, "klines.json.gz").items()}
    dv = _load(wd, "dvol.json.gz")

    def at(c, tau, price):
        i = bisect.bisect_right(k1t[c.group], tau) - 1
        if i < 0 or tau - k1t[c.group][i] > 180:
            return None
        d = copy.copy(c)
        d.t, d.spot, d.hours, d.price = tau, k1[c.group][i][1], (c.row.end - tau) / H, price
        d.rv = kl[c.group].rv(tau) or c.rv
        iv = dvol_at(dv["ETH" if c.group == "eth" else "BTC"], tau)
        if iv is not None and c.group in ("sol", "xrp"):
            rvb = kl["btc"].rv(tau)
            iv = d.rv * iv / rvb if rvb else None
        d.iv = iv or c.iv
        return d if d.hours > 0 else None

    by_event = {}
    for c in cases:
        by_event.setdefault(c.row.event_id, []).append(c)
    for ev, group in by_event.items():
        p = wd / "trades" / f"{ev}.json.gz"
        trades = json.loads(gzip.decompress(p.read_bytes())) if p.exists() else []
        cond_of = {t[3]: t[1] for t in trades if t[2] == 0}  # jeton du Oui -> marché
        per_market = {}
        for t in trades:
            per_market.setdefault(t[1], []).append(t)
        for lst in per_market.values():
            lst.sort(key=lambda t: t[0])
        for c in group:
            c.ask = c.bid = c.ask_case = c.bid_case = None
            ask_t = bid_t = None
            for ts_, _, outcome, _, side, price, _ in per_market.get(cond_of.get(c.row.yes_token), []):
                if ts_ > c.t:
                    break
                if ts_ < c.t - look:
                    continue
                if (outcome == 0) == (side == "BUY"):  # le preneur a pris le côté vendeur du Oui
                    c.ask, ask_t = (price if outcome == 0 else 1 - price), ts_
                else:
                    c.bid, bid_t = (price if outcome == 0 else 1 - price), ts_
            if ask_t is not None:
                c.ask_case = at(c, ask_t, c.ask)
            if bid_t is not None:
                c.bid_case = at(c, bid_t, c.bid)
            if c.ask_case is None:
                c.ask = None
            if c.bid_case is None:
                c.bid = None
    return cases
