"""Persistance SQLite : snapshots de marché, carnets, décisions, cycles.

Le capital n'est JAMAIS lu depuis cette base : la seule source de vérité est le
journal signé (ledger.py). La base sert à l'analyse, aux rapports et à
l'ancrage anti-troncature (dernière position connue du journal).
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS cycles (
    cycle_id TEXT PRIMARY KEY,
    started_at TEXT NOT NULL,
    finished_at TEXT,
    status TEXT,
    markets_scanned INTEGER DEFAULT 0,
    watchlist_size INTEGER DEFAULT 0,
    proposals INTEGER DEFAULT 0,
    accepted INTEGER DEFAULT 0,
    fills INTEGER DEFAULT 0,
    summary TEXT,
    error TEXT
);
CREATE TABLE IF NOT EXISTS market_snapshots (
    cycle_id TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    market_id TEXT NOT NULL,
    event_id TEXT,
    question TEXT,
    end_date TEXT,
    best_bid TEXT,
    best_ask TEXT,
    last_trade_price TEXT,
    volume_24h TEXT,
    liquidity TEXT,
    fee_type TEXT,
    eligible INTEGER,
    exclusion TEXT,
    issues TEXT
);
CREATE INDEX IF NOT EXISTS idx_market_snapshots_market ON market_snapshots(market_id, collected_at);
CREATE TABLE IF NOT EXISTS book_snapshots (
    cycle_id TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    book_time TEXT,
    token_id TEXT NOT NULL,
    best_bid TEXT,
    best_ask TEXT,
    bid_depth TEXT,
    ask_depth TEXT,
    levels TEXT
);
CREATE INDEX IF NOT EXISTS idx_book_snapshots_token ON book_snapshots(token_id, collected_at);
CREATE TABLE IF NOT EXISTS decisions (
    op_id TEXT NOT NULL,
    cycle_id TEXT NOT NULL,
    decided_at TEXT NOT NULL,
    strategy_id TEXT,
    strategy_version TEXT,
    market_id TEXT,
    token_id TEXT,
    side TEXT,
    est_probability TEXT,
    prob_low TEXT,
    prob_high TEXT,
    max_price TEXT,
    shares TEXT,
    net_edge TEXT,
    accepted INTEGER,
    reasons TEXT,
    checks TEXT,
    fill_status TEXT,
    filled_shares TEXT,
    avg_price TEXT,
    fee TEXT,
    proposal TEXT,
    PRIMARY KEY (op_id, cycle_id)
);
CREATE TABLE IF NOT EXISTS observations (
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    published_at TEXT,
    collected_at TEXT NOT NULL,
    url TEXT,
    title TEXT,
    text TEXT,
    author TEXT,
    domain TEXT,
    kind TEXT,
    sentiment REAL,
    reliability REAL,
    uncertainty TEXT,
    engagement INTEGER,
    dup_key TEXT,
    duplicate_of TEXT,
    delay_seconds REAL,
    market_ids TEXT,
    data TEXT,
    PRIMARY KEY (source, external_id)
);
CREATE INDEX IF NOT EXISTS idx_observations_time ON observations(collected_at);
CREATE TABLE IF NOT EXISTS source_runs (source TEXT PRIMARY KEY, last_run TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS llm_calls (day TEXT PRIMARY KEY, calls INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS stances (
    market_id TEXT NOT NULL,
    external_id TEXT NOT NULL,
    stance TEXT NOT NULL,
    collected_at TEXT NOT NULL,
    PRIMARY KEY (market_id, external_id)
);
CREATE TABLE IF NOT EXISTS ledger_anchor (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    seq INTEGER NOT NULL,
    hash TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def _s(value: Any) -> str | None:
    return None if value is None else str(value)


def _iso(ts: datetime | None) -> str | None:
    return ts.astimezone(timezone.utc).isoformat() if ts else None


class Database:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        # Base illisible : mise de côté (jamais effacée) et base neuve. Le capital n'en dépend
        # pas ; seul l'ancrage anti-troncature est perdu, ce qui est signalé.
        self.recovered_from: Path | None = None
        try:
            self._connect()
        except sqlite3.DatabaseError:
            self.conn.close()
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            self.recovered_from = self.path.with_name(f"{self.path.name}.corrompue-{stamp}")
            self.path.rename(self.recovered_from)
            self._connect()

    def _connect(self) -> None:
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        if self.conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise sqlite3.DatabaseError("quick_check en échec")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # ------------------------------------------------------------------ cycles

    def start_cycle(self, cycle_id: str, started_at: datetime) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO cycles (cycle_id, started_at, status) VALUES (?, ?, 'EN_COURS')",
            (cycle_id, _iso(started_at)))
        self.conn.commit()

    def finish_cycle(self, cycle_id: str, finished_at: datetime, status: str, *,
                     counts: dict[str, int] | None = None, summary: dict | None = None,
                     error: str | None = None) -> None:
        counts = counts or {}
        self.conn.execute(
            """UPDATE cycles SET finished_at=?, status=?, markets_scanned=?, watchlist_size=?,
               proposals=?, accepted=?, fills=?, summary=?, error=? WHERE cycle_id=?""",
            (_iso(finished_at), status, counts.get("markets", 0), counts.get("watchlist", 0),
             counts.get("proposals", 0), counts.get("accepted", 0), counts.get("fills", 0),
             json.dumps(summary or {}, ensure_ascii=False), error, cycle_id))
        self.conn.commit()

    # ------------------------------------------------------------------ données

    def save_markets(self, cycle_id: str, collected_at: datetime, markets) -> None:
        rows = [(cycle_id, _iso(collected_at), m.market_id, m.event_id, m.question,
                 _iso(m.end_date), _s(m.best_bid), _s(m.best_ask), _s(m.last_trade_price),
                 _s(m.volume_24h), _s(m.liquidity), m.fees.fee_type, int(m.eligible),
                 m.exclusion, json.dumps(m.issues, ensure_ascii=False)) for m in markets]
        self.conn.executemany(
            "INSERT INTO market_snapshots VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        self.conn.commit()

    def save_books(self, cycle_id: str, books) -> None:
        rows = []
        for book in books:
            levels = {"bids": [[str(l.price), str(l.size)] for l in book.bids[:10]],
                      "asks": [[str(l.price), str(l.size)] for l in book.asks[:10]]}
            rows.append((cycle_id, _iso(book.fetched_at), _iso(book.timestamp), book.token_id,
                         _s(book.best_bid), _s(book.best_ask),
                         str(sum(l.size for l in book.bids)), str(sum(l.size for l in book.asks)),
                         json.dumps(levels)))
        self.conn.executemany("INSERT INTO book_snapshots VALUES (?,?,?,?,?,?,?,?,?)", rows)
        self.conn.commit()

    def save_decision(self, cycle_id: str, decided_at: datetime, proposal, verdict,
                      fill=None) -> None:
        payload = {k: (list(v) if isinstance(v, tuple) else str(v))
                   for k, v in proposal.__dict__.items()}
        self.conn.execute(
            "INSERT OR REPLACE INTO decisions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (proposal.op_id, cycle_id, _iso(decided_at), proposal.strategy_id,
             proposal.strategy_version, proposal.market_id, proposal.token_id, proposal.side,
             str(proposal.est_probability), str(proposal.prob_low), str(proposal.prob_high),
             str(proposal.max_price), str(proposal.shares), str(proposal.net_edge),
             int(verdict.accepted), json.dumps(verdict.reasons, ensure_ascii=False),
             json.dumps(verdict.checks), fill.status if fill else None,
             _s(fill.filled_shares) if fill else None, _s(fill.avg_price) if fill else None,
             _s(fill.fee) if fill else None, json.dumps(payload, ensure_ascii=False)))
        self.conn.commit()

    # ------------------------------------------------------------------ observations

    def save_observations(self, observations) -> None:
        rows = [(o.source, o.external_id, _iso(o.published_at), _iso(o.collected_at), o.url, o.title,
                 o.text, o.author, o.domain, o.kind, o.sentiment, o.reliability, o.uncertainty,
                 o.engagement, o.dup_key, o.duplicate_of, o.delay_seconds,
                 json.dumps(o.market_ids), json.dumps(o.data, ensure_ascii=False, default=str))
                for o in observations]
        self.conn.executemany("INSERT OR IGNORE INTO observations VALUES "
                              "(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
        self.conn.commit()

    def recent_dup_keys(self, since: datetime) -> set[str]:
        return {r[0] for r in self.conn.execute(
            "SELECT dup_key FROM observations WHERE collected_at >= ?", (_iso(since),))}

    def recent_observations(self, since: datetime) -> list[dict]:
        cur = self.conn.execute("SELECT * FROM observations WHERE collected_at >= ?", (_iso(since),))
        return [dict(r) for r in cur]

    def source_last_run(self, source: str) -> datetime | None:
        row = self.conn.execute("SELECT last_run FROM source_runs WHERE source=?", (source,)).fetchone()
        return datetime.fromisoformat(row[0]) if row else None

    def set_source_run(self, source: str, when: datetime) -> None:
        self.conn.execute("INSERT OR REPLACE INTO source_runs VALUES (?, ?)", (source, _iso(when)))
        self.conn.commit()

    def get_value(self, key: str) -> str | None:
        """Petite mémoire entre cycles (ex. nom du modèle Gemini trouvé). Jamais de capital ici."""
        row = self.conn.execute("SELECT value FROM kv WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def set_value(self, key: str, value: str) -> None:
        self.conn.execute("INSERT OR REPLACE INTO kv VALUES (?, ?, ?)",
                          (key, value, datetime.now(timezone.utc).isoformat()))
        self.conn.commit()

    def get_stances(self, market_id: str, external_ids: list[str]) -> dict[str, dict]:
        """Classements Gemini déjà faits pour ce marché : on ne repaie jamais deux fois un texte."""
        if not external_ids:
            return {}
        marks = ",".join("?" * len(external_ids))
        rows = self.conn.execute(f"SELECT external_id, stance FROM stances WHERE market_id=? "
                                 f"AND external_id IN ({marks})", (market_id, *external_ids)).fetchall()
        return {r[0]: json.loads(r[1]) for r in rows}

    def save_stances(self, market_id: str, stances: dict[str, dict], now: datetime) -> None:
        self.conn.executemany("INSERT OR REPLACE INTO stances VALUES (?, ?, ?, ?)",
                              [(market_id, ext, json.dumps(v), _iso(now)) for ext, v in stances.items()])
        self.conn.commit()

    def llm_calls(self, day: str) -> int:
        row = self.conn.execute("SELECT calls FROM llm_calls WHERE day=?", (day,)).fetchone()
        return int(row[0]) if row else 0

    def count_llm_call(self, day: str) -> None:
        self.conn.execute("INSERT INTO llm_calls VALUES (?, 1) ON CONFLICT(day) DO UPDATE SET calls = calls + 1",
                          (day,))
        self.conn.commit()

    # ------------------------------------------------------------------ ancrage

    def get_anchor(self) -> tuple[int, str] | None:
        row = self.conn.execute("SELECT seq, hash FROM ledger_anchor WHERE id = 1").fetchone()
        return (row["seq"], row["hash"]) if row else None

    def set_anchor(self, seq: int, digest: str, now: datetime) -> None:
        self.conn.execute("INSERT OR REPLACE INTO ledger_anchor VALUES (1, ?, ?, ?)",
                          (seq, digest, _iso(now)))
        self.conn.commit()

    # ------------------------------------------------------------------ taille

    def prune(self, max_megabytes: float) -> bool:
        """Base tournante : supprime les plus vieux snapshots si la taille dépasse le plafond."""
        if self.path.stat().st_size <= max_megabytes * 1024 * 1024:
            return False
        for table in ("book_snapshots", "market_snapshots", "observations", "stances"):
            self.conn.execute(
                f"DELETE FROM {table} WHERE rowid IN (SELECT rowid FROM {table} "
                f"ORDER BY collected_at LIMIT (SELECT COUNT(*) / 4 FROM {table}))")
        self.conn.commit()
        self.conn.execute("VACUUM")
        return True
