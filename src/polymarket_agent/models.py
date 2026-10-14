"""Structures de données partagées (marchés, carnets d'ordres)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class FeeSchedule:
    enabled: bool | None  # None = inconnu
    rate: Decimal | None
    exponent: Decimal | None
    taker_only: bool = True
    fee_type: str | None = None


@dataclass
class MarketInfo:
    market_id: str
    condition_id: str
    question: str
    slug: str
    event_id: str
    event_title: str
    outcomes: list[str]
    token_ids: list[str]
    outcome_prices: list[Decimal]
    best_bid: Decimal | None  # du jeton n°0 (en général « Yes »)
    best_ask: Decimal | None
    spread: Decimal | None
    last_trade_price: Decimal | None
    volume_24h: Decimal
    volume_total: Decimal  # volume cumulé depuis l'ouverture
    liquidity: Decimal
    end_date: datetime | None
    active: bool
    closed: bool
    accepting_orders: bool
    enable_order_book: bool
    fees: FeeSchedule
    min_order_size: Decimal
    tick_size: Decimal
    neg_risk: bool
    issues: list[str] = field(default_factory=list)
    # Caractéristiques passées de l'issue n°0 (remplies par le cycle, None si inconnues).
    yes_price_6h_ago: float | None = None
    changes_24h: int | None = None
    eligible: bool = False
    exclusion: str = ""

    @property
    def data_ok(self) -> bool:
        return not self.issues


@dataclass(frozen=True)
class BookLevel:
    price: Decimal
    size: Decimal


@dataclass
class OrderBook:
    token_id: str
    bids: list[BookLevel]  # triés du meilleur (plus haut) au moins bon
    asks: list[BookLevel]  # triés du meilleur (plus bas) au moins bon
    timestamp: datetime | None  # horodatage fourni par le CLOB
    fetched_at: datetime
    tick_size: Decimal
    min_order_size: Decimal
    last_trade_price: Decimal | None = None

    @property
    def best_bid(self) -> Decimal | None:
        return self.bids[0].price if self.bids else None

    @property
    def best_ask(self) -> Decimal | None:
        return self.asks[0].price if self.asks else None

    @property
    def mid(self) -> Decimal | None:
        if self.best_bid is None or self.best_ask is None:
            return None
        return (self.best_bid + self.best_ask) / 2
