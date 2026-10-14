"""Jeu de données historique des marchés résolus (backtests et calibration).

Sources (docs.polymarket.com vérifiée le 14/10/2026, confirmée par appels réels) :
  - Gamma `GET /events/keyset` : événements clos, leurs tags et leurs marchés
    (pagination par curseur `after_cursor` / `next_cursor`, 100 maximum par page).
  - CLOB `GET /prices-history?market=<jeton>&startTs&endTs&fidelity=60` : série
    horaire (fenêtre limitée : 3 jours OK, 30 jours refusés).

Chaque marché retenu : binaire, résolu nettement à 1/0, volume suffisant, avec
le prix de l'issue n°0 (« Yes ») sur les 72 h précédant la limite de décision.
Les prix sont stockés en (décalage en secondes par rapport à la limite, prix) :
un backtest ne lit jamais un point postérieur à l'instant de décision.

LIMITE : le prix `p` de l'historique est un prix de référence, pas le prix
exécutable. Le backtest ajoute donc toujours un coût d'écart et de slippage.
"""

from __future__ import annotations

import gzip
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

from polymarket_agent.http_client import HttpClient

log = logging.getLogger(__name__)

# Taux de frais par catégorie (docs.polymarket.com/trading/fees, 14/10/2026).
# Utilisés seulement pour les anciens marchés sans `feeSchedule`. En cas de doute,
# on prend le taux le plus élevé (prudence) : la géopolitique n'est gratuite que si
# aucune catégorie payante ne correspond.
TAG_FEE_RATES: list[tuple[str, tuple[str, ...], float]] = [
    ("crypto", ("crypto", "bitcoin", "ethereum", "solana", "xrp", "crypto-prices"), 0.07),
    ("sports", ("sports", "soccer", "nba", "nfl", "mlb", "nhl", "tennis", "esports", "ufc",
                "cricket", "golf", "f1", "boxing", "ncaa", "cfb", "epl"), 0.05),
    ("economics", ("economy", "economics", "macro-indicators", "fed", "inflation", "cpi"), 0.05),
    ("culture", ("pop-culture", "culture", "movies", "music", "celebrities", "awards"), 0.05),
    ("weather", ("weather", "climate"), 0.05),
    ("finance", ("finance", "stocks", "earnings", "business", "ipos"), 0.04),
    ("politics", ("politics", "elections", "trump", "us-politics", "global-elections"), 0.04),
    ("mentions", ("mentions",), 0.04),
    ("tech", ("tech", "ai", "science"), 0.04),
    ("geopolitics", ("geopolitics", "world", "world-affairs", "middle-east", "ukraine"), 0.0),
]
DEFAULT_CATEGORY = ("other", 0.05)
HISTORY_HOURS = 72


def _ts(text: str | None) -> int | None:
    if not text:
        return None
    try:
        value = datetime.fromisoformat(text.replace("Z", "+00:00").replace(" ", "T"))
    except ValueError:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return int(value.timestamp())


def _json_list(value) -> list | None:
    if isinstance(value, list):
        return value
    try:
        parsed = json.loads(value) if isinstance(value, str) else None
    except ValueError:
        return None
    return parsed if isinstance(parsed, list) else None


def categorize(market: dict, tags: list[str]) -> tuple[str, float]:
    """Catégorie et taux de frais taker. Le vrai barème du marché est prioritaire."""
    schedule = market.get("feeSchedule")
    fee_type = str(market.get("feeType") or "")
    if market.get("feesEnabled") is True and isinstance(schedule, dict) and "rate" in schedule:
        category = fee_type.split("_")[0] if fee_type else DEFAULT_CATEGORY[0]
        return category, float(schedule["rate"])
    tagset = set(tags)
    matches = [(name, rate) for name, keys, rate in TAG_FEE_RATES if tagset & set(keys)]
    paying = [m for m in matches if m[1] > 0]
    if paying:
        return max(paying, key=lambda m: m[1])
    if matches:
        return matches[0]
    return DEFAULT_CATEGORY


def parse_resolved(market: dict, event: dict, min_volume: float) -> dict | None:
    """Métadonnées d'un marché binaire résolu exploitable, sinon None."""
    outcomes = _json_list(market.get("outcomes")) or []
    tokens = _json_list(market.get("clobTokenIds")) or []
    prices = _json_list(market.get("outcomePrices")) or []
    if len(outcomes) != 2 or len(tokens) != 2 or len(prices) != 2:
        return None
    if market.get("closed") is not True or market.get("umaResolutionStatus") not in (None, "resolved"):
        return None
    if sorted(str(p) for p in prices) != ["0", "1"]:
        return None  # annulé, 50-50 ou non réglé : exclu (limite documentée)
    try:
        volume = float(market.get("volumeNum") or market.get("volume") or 0)
    except (TypeError, ValueError):
        return None
    end, closed = _ts(market.get("endDate")), _ts(market.get("closedTime"))
    start = _ts(market.get("acceptingOrdersTimestamp") or market.get("startDate"))
    if volume < min_volume or end is None or closed is None:
        return None
    tags = [str(t.get("slug")) for t in event.get("tags") or [] if isinstance(t, dict)]
    category, fee_rate = categorize(market, tags)
    return {
        "id": str(market["id"]), "event_id": str(event.get("id")), "question": market.get("question", ""),
        "slug": market.get("slug", ""), "series": event.get("seriesSlug") or "",
        "outcomes": [str(o) for o in outcomes], "yes_token": str(tokens[0]),
        "winner": 0 if str(prices[0]) == "1" else 1, "end": end, "closed": closed, "start": start,
        "volume": round(volume, 2), "category": category, "fee_rate": fee_rate, "tags": tags[:8],
        "neg_risk": market.get("negRisk") is True,
    }


def decision_limit(meta: dict) -> int:
    """Dernier instant de décision possible : avant l'échéance et avant la clôture."""
    return min(meta["end"], meta["closed"])


@dataclass
class HistoricalMarket:
    meta: dict
    points: list[tuple[int, float]]  # (décalage en secondes / limite de décision, prix Yes)

    @property
    def limit(self) -> int:
        return decision_limit(self.meta)

    def price_changes(self, ts: int, window: int = 24 * 3600) -> int:
        """Nombre de changements de prix dans la fenêtre ]ts − window, ts] (activité connue à ts)."""
        changes, previous = 0, None
        for offset, price in self.points:
            t = self.limit + offset
            if t > ts:
                break
            if t > ts - window and previous is not None and price != previous:
                changes += 1
            previous = price
        return changes

    def yes_price_at(self, ts: int, max_age: int = 2 * 3600) -> float | None:
        """Dernier prix connu à l'instant ts (jamais après). None si trop vieux ou absent."""
        best = None
        for offset, price in self.points:
            t = self.limit + offset
            if t > ts:
                break
            best = (t, price)
        if best is None or ts - best[0] > max_age:
            return None
        return best[1]


class HistoryStore:
    """Cache SQLite reprenable : si le script s'arrête, il reprend où il en était."""

    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS markets (id TEXT PRIMARY KEY, meta TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS histories (id TEXT PRIMARY KEY, points TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS days_done (day TEXT PRIMARY KEY, n INTEGER);
        """)

    def close(self) -> None:
        self.conn.close()

    def day_done(self, day: str) -> bool:
        return self.conn.execute("SELECT 1 FROM days_done WHERE day=?", (day,)).fetchone() is not None

    def save_day(self, day: str, metas: list[dict]) -> None:
        self.conn.executemany("INSERT OR REPLACE INTO markets VALUES (?, ?)",
                              [(m["id"], json.dumps(m, ensure_ascii=False)) for m in metas])
        self.conn.execute("INSERT OR REPLACE INTO days_done VALUES (?, ?)", (day, len(metas)))
        self.conn.commit()

    def missing_histories(self) -> list[dict]:
        rows = self.conn.execute(
            "SELECT meta FROM markets WHERE id NOT IN (SELECT id FROM histories)").fetchall()
        return [json.loads(r[0]) for r in rows]

    def save_history(self, market_id: str, points: list[tuple[int, float]]) -> None:
        self.conn.execute("INSERT OR REPLACE INTO histories VALUES (?, ?)",
                          (market_id, json.dumps(points, separators=(",", ":"))))

    def commit(self) -> None:
        self.conn.commit()

    def iter_complete(self) -> Iterator[HistoricalMarket]:
        for meta, points in self.conn.execute(
                "SELECT m.meta, h.points FROM markets m JOIN histories h USING(id)"):
            pts = [tuple(p) for p in json.loads(points)]
            if pts:
                yield HistoricalMarket(json.loads(meta), pts)


def iter_closed_events(http: HttpClient, base_url: str, day_start: datetime, day_end: datetime,
                       volume_min: float) -> Iterator[dict]:
    cursor = None
    while True:
        params = {"limit": 100, "closed": "true", "volume_min": volume_min,
                  "end_date_min": day_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                  "end_date_max": day_end.strftime("%Y-%m-%dT%H:%M:%SZ")}
        if cursor:
            params["after_cursor"] = cursor
        page = http.get_json(f"{base_url}/events/keyset", params=params)
        if not isinstance(page, dict):
            raise ValueError("events/keyset : objet attendu")
        for event in page.get("events") or []:
            if isinstance(event, dict):
                yield event
        cursor = page.get("next_cursor")
        if not cursor or not page.get("events"):
            return


def collect_day(http: HttpClient, base_url: str, day: datetime, min_volume: float) -> list[dict]:
    metas, seen = [], set()
    for event in iter_closed_events(http, base_url, day, day + timedelta(days=1), min_volume):
        for market in event.get("markets") or []:
            meta = parse_resolved(market, event, min_volume) if isinstance(market, dict) else None
            if meta and meta["id"] not in seen:
                seen.add(meta["id"])
                metas.append(meta)
    return metas


def fetch_points(http: HttpClient, clob_url: str, meta: dict,
                 hours: int = HISTORY_HOURS) -> list[tuple[int, float]]:
    limit = decision_limit(meta)
    raw = http.get_json(f"{clob_url}/prices-history", params={
        "market": meta["yes_token"], "startTs": limit - hours * 3600 - 3600,
        "endTs": limit, "fidelity": 60})
    points = []
    for item in (raw or {}).get("history") or []:
        try:
            t, p = int(item["t"]), float(item["p"])
        except (KeyError, TypeError, ValueError):
            continue
        if t <= limit and 0 <= p <= 1:
            points.append((t - limit, round(p, 4)))
    points.sort()
    return points


def export_monthly(store: HistoryStore, out_dir: Path) -> dict[str, int]:
    """Export compact (un fichier .jsonl.gz par mois de résolution), versionné dans Git."""
    out_dir.mkdir(parents=True, exist_ok=True)
    by_month: dict[str, list[str]] = {}
    for market in store.iter_complete():
        month = datetime.fromtimestamp(market.meta["end"], tz=timezone.utc).strftime("%Y-%m")
        record = dict(market.meta, points=market.points)
        by_month.setdefault(month, []).append(json.dumps(record, ensure_ascii=False,
                                                         separators=(",", ":")))
    for month, lines in by_month.items():
        lines.sort()
        with gzip.open(out_dir / f"markets_{month}.jsonl.gz", "wt", encoding="utf-8",
                       compresslevel=9) as handle:
            handle.write("\n".join(lines) + "\n")
    return {m: len(v) for m, v in sorted(by_month.items())}


def load_dataset(directory: Path) -> list[HistoricalMarket]:
    markets = []
    for path in sorted(Path(directory).glob("markets_*.jsonl.gz")):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    record = json.loads(line)
                    points = [tuple(p) for p in record.pop("points")]
                    markets.append(HistoricalMarket(record, points))
    markets.sort(key=lambda m: m.limit)
    return markets
