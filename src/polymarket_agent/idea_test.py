"""Tester une idée sur le passé, avant l'arène (outil générique, 16/10/2026).

Même méthode que le test météo (experiments/meteo_backtest.md), réutilisable par le chercheur :
1. `fetch_resolved` : marchés RÉSOLUS d'une famille (tag Gamma, motif de slug, dates), avec leur
   source de résolution, leurs règles et leur barème de frais ; gardés en cache (gzip).
2. `price_at` : prix du « Oui » à un instant donné, d'après l'historique public du CLOB, en ne
   lisant JAMAIS un point postérieur à cet instant ; gardé en cache (SQLite).
3. `evaluate` : la probabilité du modèle (fonction fournie) contre le prix du marché, réglée
   sur les premières dates et JUGÉE sur les suivantes ; simulation 1 part par pari avec frais
   réels du marché et un écart achat-vente simulé ; détail par type de pari et par jour.
4. `fetch_event_trades` + `taker_cost` : prix RÉELLEMENT payés par les preneurs. À utiliser
   TOUJOURS en vérification : le 16/10/2026, la météo gagnait +28 % avec l'historique (point 2)
   et perdait −6 % aux prix des vrais échanges (gain venu de marchés sans échange : carnets vides,
   prix périmés ; experiments/meteo_backtest.md, experiments/crypto_backtest.md).
Les prix historiques ne sont pas des prix exécutables : seule l'arène (carnets réels) confirme.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

from polymarket_agent.http_client import HttpClient, SourceUnavailable

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
TRADES = "https://data-api.polymarket.com/trades"


def _jl(value) -> list:
    if isinstance(value, list):
        return value
    try:
        out = json.loads(value) if isinstance(value, str) else []
    except ValueError:
        return []
    return out if isinstance(out, list) else []


def _ts(text: str | None) -> int | None:
    if not text:
        return None
    try:
        return int(datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


@dataclass
class Resolved:
    market_id: str
    event_id: str
    event_slug: str
    question: str
    yes_token: str
    won: int                 # 1 si « Oui » a gagné, 0 sinon
    end: int                 # échéance annoncée (secondes Unix)
    resolution_source: str = ""
    description: str = ""
    fee_rate: float = 0.0    # barème « rate » (frais = rate × p × (1 − p) par part, preneur)
    neg_risk: bool = False
    extra: dict = field(default_factory=dict)  # libre : ce que le modèle veut garder


def parse_event_market(event: dict, m: dict) -> Resolved | None:
    """Marché binaire réglé net à 1/0 ; None sinon (50-50, litige, issue multiple)."""
    prices = [str(p) for p in _jl(m.get("outcomePrices"))]
    tokens = [str(t) for t in _jl(m.get("clobTokenIds"))]
    if len(tokens) != 2 or sorted(prices) not in (["0", "1"],):
        return None
    if m.get("umaResolutionStatus") not in (None, "", "resolved"):
        return None
    fs = m.get("feeSchedule") if isinstance(m.get("feeSchedule"), dict) else {}
    rate = float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0
    end = _ts(m.get("endDate")) or _ts(event.get("endDate"))
    if end is None:
        return None
    return Resolved(str(m.get("id")), str(event.get("id")), str(event.get("slug", "")), str(m.get("question", "")),
                    tokens[0], 1 if prices[0] == "1" else 0, end, str(m.get("resolutionSource") or ""),
                    str(m.get("description") or ""), rate, bool(m.get("negRisk")))


def fetch_resolved(http: HttpClient, cache_dir: Path, start: str, end: str, tag_id: int | None = None,
                   slug_pattern: str | None = None, max_pages: int = 40) -> list[Resolved]:
    """Événements clos entre `start` et `end` (AAAA-MM-JJ), filtrés par tag et motif de slug."""
    key = hashlib.sha256(json.dumps([start, end, tag_id, slug_pattern]).encode()).hexdigest()[:16]
    path = Path(cache_dir) / f"resolus_{key}.json.gz"
    if path.exists():
        rows = json.loads(gzip.decompress(path.read_bytes()))
        return [Resolved(**r) for r in rows]
    pattern = re.compile(slug_pattern) if slug_pattern else None
    out: list[Resolved] = []
    for page in range(max_pages):
        params = {"closed": "true", "limit": 100, "offset": page * 100,
                  "end_date_min": f"{start}T00:00:00Z", "end_date_max": f"{end}T23:59:59Z"}
        if tag_id is not None:
            params["tag_id"] = tag_id
        batch = http.get_json(f"{GAMMA}/events", params=params)
        if not isinstance(batch, list):
            break
        for ev in batch:
            if pattern and not pattern.search(str(ev.get("slug", ""))):
                continue
            for m in ev.get("markets") or []:
                r = parse_event_market(ev, m)
                if r:
                    out.append(r)
        if len(batch) < 100:
            break
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps([r.__dict__ for r in out]).encode()))
    return out


class PriceCache:
    """Prix du « Oui » à un instant : dernier point de l'historique CLOB AVANT cet instant."""

    def __init__(self, path: Path, http: HttpClient):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path))
        self.db.execute("CREATE TABLE IF NOT EXISTS prix (jeton TEXT, ts INTEGER, fenetre INTEGER, p REAL, "
                        "PRIMARY KEY (jeton, ts, fenetre))")
        self.http = http

    def price_at(self, token: str, ts: int, window: int = 6 * 3600) -> float | None:
        row = self.db.execute("SELECT p FROM prix WHERE jeton=? AND ts=? AND fenetre=?", (token, ts, window)).fetchone()
        if row:
            return None if row[0] < 0 else row[0]
        try:
            raw = self.http.get_json(f"{CLOB}/prices-history", params={
                "market": token, "startTs": ts - window, "endTs": ts, "fidelity": 10})
        except SourceUnavailable:
            return None  # pas mis en cache : réessayé la prochaine fois
        points = [pt for pt in (raw or {}).get("history") or [] if pt.get("t", 1e18) <= ts]
        p = float(points[-1]["p"]) if points else -1.0
        self.db.execute("INSERT OR REPLACE INTO prix VALUES (?,?,?,?)", (token, ts, window, p))
        self.db.commit()
        return None if p < 0 else p


def fetch_event_trades(http: HttpClient, cache_dir: Path, event_id: str, max_pages: int = 11) -> list[list]:
    """Échanges des preneurs d'un événement : [[heure, jeton, côté, prix, parts], ...] (cache gzip).
      GET https://data-api.polymarket.com/trades?eventId=<id>&limit=1000&offset=..  (public)
    L'API refuse un décalage au-delà de 10 000 : au plus 11 pages (les plus anciens manquent alors)."""
    path = Path(cache_dir) / f"echanges_{event_id}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    rows: list[list] = []
    for page in range(max_pages):
        try:
            batch = http.get_json(TRADES, params={"eventId": event_id, "limit": 1000, "offset": page * 1000})
        except SourceUnavailable:
            break
        if not isinstance(batch, list) or not batch:
            break
        rows += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])]
                 for t in batch if t.get("timestamp") and t.get("price") is not None]
        if len(batch) < 1000:
            break
    Path(cache_dir).mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(rows).encode()))
    return rows


def taker_cost(trades: list[list], token: str, other_token: str, ts: int, window: int = 2 * 3600,
               after: bool = False) -> float | None:
    """Prix réellement payé pour ACHETER `token` : achat de `token` au prix p, ou vente de l'autre
    issue au prix p (= `token` à 1 − p). Dernier échange dans `window` secondes AVANT `ts` (prix
    connu à la décision) ou, avec `after`, premier échange dans `window` APRÈS (prix qu'on aurait payé)."""
    pts = sorted((t[0], t[3] if t[1] == token else 1 - t[3]) for t in trades
                 if (t[1] == token and t[2] == "BUY") or (t[1] == other_token and t[2] == "SELL"))
    if after:
        sel = [p for when, p in pts if ts <= when <= ts + window]
        return sel[0] if sel else None
    sel = [p for when, p in pts if ts - window <= when <= ts]
    return sel[-1] if sel else None


def fee(p: float, rate: float) -> float:
    return rate * p * (1 - p)


@dataclass
class Case:
    """Un marché au moment de la décision : prix du marché, probabilité du modèle, résultat."""
    row: Resolved
    price: float
    group: str = ""   # regroupement libre pour le détail (ville, sport, actif…)
    day: str = ""     # date de la décision (AAAA-MM-JJ) : découpage apprentissage / test


def brier(cases: list[Case], prob: Callable[[Case], float]) -> float:
    return sum((prob(c) - c.row.won) ** 2 for c in cases) / len(cases) if cases else float("nan")


def log_loss(cases: list[Case], prob: Callable[[Case], float]) -> float:
    def ll(c):
        p = min(0.999, max(0.001, prob(c)))
        return -math.log(p if c.row.won else 1 - p)
    return sum(ll(c) for c in cases) / len(cases) if cases else float("nan")


def split_by_day(cases: list[Case], train_share: float = 0.5) -> tuple[list[Case], list[Case]]:
    days = sorted({c.day for c in cases})
    if len(days) < 2:
        return cases, []
    cut = days[max(1, int(len(days) * train_share))]
    return [c for c in cases if c.day < cut], [c for c in cases if c.day >= cut]


def simulate(cases: list[Case], prob: Callable[[Case], float], edge: float = 0.05, spread: float = 0.01,
             sides: tuple[str, ...] = ("OUI", "NON")) -> dict:
    """1 part par pari : on achète le côté que le modèle juge sous-coté de plus de `edge`."""
    total = {"paris": 0, "gagnants": 0, "resultat": 0.0, "mise": 0.0}
    by_kind: dict[str, dict] = defaultdict(lambda: {"paris": 0, "resultat": 0.0, "mise": 0.0})
    by_day: dict[str, float] = defaultdict(float)
    by_group: dict[str, float] = defaultdict(float)
    for c in cases:
        pm, rate = prob(c), c.row.fee_rate
        yes, no = c.price + spread, 1 - c.price + spread
        if "OUI" in sides and yes < 1 and pm - yes - fee(yes, rate) > edge:
            side, cost, gain = "OUI", yes, c.row.won - yes - fee(yes, rate)
        elif "NON" in sides and no < 1 and (1 - pm) - no - fee(no, rate) > edge:
            side, cost, gain = "NON", no, (1 - c.row.won) - no - fee(no, rate)
        else:
            continue
        bucket = "<0,2" if cost < 0.2 else "0,2-0,8" if cost <= 0.8 else ">0,8"
        k = by_kind[f"{side} {bucket}"]
        for d in (total, k):
            d["paris"] += 1
            d["resultat"] += gain
            d["mise"] += cost
        total["gagnants"] += gain > 0
        by_day[c.day] += gain
        by_group[c.group] += gain
    pct = lambda d: round(100 * d["resultat"] / d["mise"], 1) if d["mise"] else None
    return {"total": dict(total, rendement_pct=pct(total), resultat=round(total["resultat"], 2),
                          mise=round(total["mise"], 2)),
            "par_type": {k: dict(v, rendement_pct=pct(v), resultat=round(v["resultat"], 2)) for k, v in sorted(by_kind.items())},
            "par_jour": {d: round(v, 2) for d, v in sorted(by_day.items())},
            "groupes_gagnants": sum(1 for v in by_group.values() if v > 0), "groupes": len(by_group)}


def evaluate(cases: list[Case], prob: Callable[[Case], float], edges=(0.03, 0.05, 0.08),
             spreads=(0.01, 0.02, 0.04), sides: tuple[str, ...] = ("OUI", "NON")) -> dict:
    """Jugement hors échantillon (seconde moitié des dates) : Brier, log loss, simulation."""
    _, test = split_by_day(cases)
    market = lambda c: c.price
    return {"cas": len(cases), "test": len(test),
            "brier_modele": round(brier(test, prob), 4), "brier_marche": round(brier(test, market), 4),
            "logloss_modele": round(log_loss(test, prob), 4), "logloss_marche": round(log_loss(test, market), 4),
            "simulations": {f"seuil {e} / écart {s}": simulate(test, prob, e, s, sides) for e in edges for s in spreads}}


def markdown(title: str, report: dict) -> str:
    lines = [f"## {title}", "",
             f"Cas : {report['cas']} (jugés hors échantillon : {report['test']})", "",
             "| | modèle | marché |", "|---|---|---|",
             f"| Brier (plus bas = mieux) | {report['brier_modele']} | {report['brier_marche']} |",
             f"| Log loss | {report['logloss_modele']} | {report['logloss_marche']} |", "",
             "| Simulation | paris | rendement des mises | jours gagnants |", "|---|---|---|---|"]
    for name, sim in report["simulations"].items():
        t = sim["total"]
        days = sim["par_jour"]
        lines.append(f"| {name} | {t['paris']} | {t['rendement_pct']} % | "
                     f"{sum(1 for v in days.values() if v > 0)} / {len(days)} |")
    return "\n".join(lines) + "\n"


def day_of(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


def _t_stat(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / (len(values) - 1))
    return mean / sd * math.sqrt(len(values)) if sd > 0 else 0.0


def verdict(bets: list[dict], min_bets: int = 30) -> dict:
    """Jugement d'une piste à partir de paris simulés (protocole des vingt pistes, 20/10/2026).

    `bets` : {"gain": résultat par euro misé (frais et écart compris), "evenement": regroupement des
    paris liés (même événement, même période de tweets…), "mois": "AAAA-MM", "cout": prix payé}.
    Les paris d'un même événement sont liés : la confiance qui compte est celle de la MOYENNE PAR
    ÉVÉNEMENT, pas celle des paris (sinon 26 tranches d'une même semaine comptent pour 26).
    Verdict : « retenue » si le rendement moyen est positif, la confiance par événement ≥ 1,5 et au
    moins deux mois sur trois gagnants ; « indice » si positif avec une confiance par événement
    ≥ 0,8 (fantôme, l'arène tranchera) ; sinon « écartée ». Détail par tranche de prix : sur le
    passé, les billets à moins de 0,10 (tweets) ou 0,30 (mentions) perdaient presque toujours.
    """
    if not bets:
        return {"paris": 0, "verdict": "écartée", "raison": "aucun pari"}
    gains = [b["gain"] for b in bets]
    by_event: dict[str, list[float]] = defaultdict(list)
    by_month: dict[str, list[float]] = defaultdict(list)
    by_price: dict[str, list[float]] = defaultdict(list)
    for b in bets:
        by_event[str(b.get("evenement", ""))].append(b["gain"])
        by_month[str(b.get("mois", ""))].append(b["gain"])
        cost = float(b.get("cout", 0.5))
        by_price["< 0,10" if cost < 0.10 else "0,10-0,30" if cost < 0.30 else "0,30-0,70" if cost < 0.70 else "≥ 0,70"].append(b["gain"])
    events = [sum(v) / len(v) for v in by_event.values()]
    mean = sum(gains) / len(gains)
    t_event = _t_stat(events)
    months = {m: round(sum(v) / len(v), 4) for m, v in sorted(by_month.items())}
    winning = sum(1 for v in months.values() if v > 0)
    if len(bets) < min_bets:
        label, why = "écartée", f"moins de {min_bets} paris"
    elif mean > 0 and t_event >= 1.5 and winning * 3 >= 2 * len(months):
        label, why = "retenue", "positive, régulière par événement et par mois"
    elif mean > 0 and t_event >= 0.8:
        label, why = "indice", "positive mais encore fragile : fantôme, l'arène tranchera"
    else:
        label, why = "écartée", "pas d'avantage régulier après frais"
    return {"paris": len(bets), "rendement_moyen": round(mean, 4), "confiance_paris": round(_t_stat(gains), 2),
            "evenements": len(events), "confiance_evenements": round(t_event, 2),
            "mois": months, "mois_gagnants": f"{winning}/{len(months)}",
            "par_prix": {k: {"paris": len(v), "rendement": round(sum(v) / len(v), 4)} for k, v in sorted(by_price.items())},
            "verdict": label, "raison": why}
