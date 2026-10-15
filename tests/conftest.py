"""Fixtures partagées : clé de test, journal temporaire, marchés et carnets factices."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from polymarket_agent.ledger import Ledger
from polymarket_agent.models import BookLevel, OrderBook
from polymarket_agent.safety_controller import RiskLimits

ROOT = Path(__file__).resolve().parents[1]
KEY = b"k" * 40
NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)
D = Decimal


@pytest.fixture
def key() -> bytes:
    return KEY


@pytest.fixture
def paths(tmp_path):
    return tmp_path / "ledger" / "ledger.jsonl", tmp_path / "ledger" / "BANKRUPT.lock"


@pytest.fixture
def ledger(paths) -> Ledger:
    return Ledger.create(paths[0], KEY, paths[1], "1000", now=NOW)


@pytest.fixture
def limits() -> RiskLimits:
    return RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")


def buy(ledger: Ledger, op_id: str = "op1", token: str = "tokA", shares="100", price="0.5",
        fee="0", event: str = "ev1", now: datetime = NOW):
    return ledger.record_buy(op_id=op_id, token_id=token, market_id="m-" + token, event_id=event,
                             outcome="Yes", shares=shares, price=price, fee=fee,
                             strategy_id="test", strategy_version="0", now=now)


def make_book(token: str = "tokA", bids=(("0.89", "500"),), asks=(("0.90", "100"), ("0.91", "200")),
              ts: datetime = NOW, fetched: datetime | None = None, tick="0.01", min_size="5") -> OrderBook:
    return OrderBook(
        token_id=token,
        bids=sorted((BookLevel(D(p), D(s)) for p, s in bids), key=lambda l: l.price, reverse=True),
        asks=sorted((BookLevel(D(p), D(s)) for p, s in asks), key=lambda l: l.price),
        timestamp=ts, fetched_at=fetched or ts, tick_size=D(tick), min_order_size=D(min_size),
    )


def raw_market(market_id: str = "1", yes_token: str = "tokA", no_token: str = "tokB",
               yes_price: str = "0.895", best_bid=0.89, best_ask=0.90, end: datetime | None = None,
               fees_enabled=True, schedule=None, event_id: str = "ev1", **overrides) -> dict:
    """Marché Gamma factice reproduisant le format réel observé le 14/10/2026."""
    end = end or NOW + timedelta(hours=24)
    raw = {
        "id": market_id, "conditionId": "0xabc", "question": f"Question {market_id} ?",
        "slug": f"q-{market_id}", "outcomes": json.dumps(["Yes", "No"]),
        "outcomePrices": json.dumps([yes_price, str(D(1) - D(yes_price))]),
        "clobTokenIds": json.dumps([yes_token, no_token]),
        "endDate": end.strftime("%Y-%m-%dT%H:%M:%SZ"), "active": True, "closed": False,
        "acceptingOrders": True, "enableOrderBook": True, "bestBid": best_bid,
        "bestAsk": best_ask, "spread": 0.01, "lastTradePrice": 0.9, "volume24hr": 50000, "volumeNum": 120000,
        "liquidityNum": 20000, "orderMinSize": 5, "orderPriceMinTickSize": 0.01,
        "negRisk": False, "feesEnabled": fees_enabled, "feeType": "politics_fees",
        "feeSchedule": schedule if schedule is not None else
        {"exponent": 1, "rate": 0.04, "takerOnly": True, "rebateRate": 0.25},
        "events": [{"id": event_id, "title": "Événement"}],
    }
    raw.update(overrides)
    return raw
