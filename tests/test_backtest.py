"""Historique, backtest et calibration : anti-fuite temporelle, découpage, reproductibilité."""

from __future__ import annotations

import json
import random

import pytest

from conftest import ROOT
from polymarket_agent import calibration
from polymarket_agent.backtest import Decision, build_samples, simulate, split_by_event
from polymarket_agent.history import HistoricalMarket, categorize, parse_resolved

H = 3600
END = 1_790_000_000


def meta(i, winner=0, end=END, closed=None, event=None, category="sports", fee=0.05):
    return {"id": str(i), "event_id": event or f"e{i}", "end": end, "closed": closed or end + 2 * H,
            "start": end - 10 * 24 * H, "winner": winner, "category": category, "fee_rate": fee,
            "volume": 100000, "yes_token": f"t{i}"}


def market(i, prices, **kw):
    """prices : {heures avant l'échéance: prix Yes}."""
    m = meta(i, **kw)
    limit = min(m["end"], m["closed"])
    points = sorted((m["end"] - h * H - limit, p) for h, p in prices.items())
    return HistoricalMarket(m, points)


def raw(prices='["1", "0"]', status="resolved", volume=60000, outcomes='["Yes", "No"]'):
    return {"id": "1", "outcomes": outcomes, "clobTokenIds": '["a", "b"]', "outcomePrices": prices,
            "closed": True, "umaResolutionStatus": status, "volumeNum": volume,
            "endDate": "2026-09-01T00:00:00Z", "closedTime": "2026-09-01 02:00:00+00",
            "startDate": "2026-08-01T00:00:00Z"}


def test_parse_resolved_keeps_only_clean_binary_resolutions():
    ev = {"id": "e", "tags": [{"slug": "nba"}]}
    assert parse_resolved(raw(), ev, 50000)["winner"] == 0
    assert parse_resolved(raw('["0", "1"]'), ev, 50000)["winner"] == 1
    assert parse_resolved(raw('["0.5", "0.5"]'), ev, 50000) is None
    assert parse_resolved(raw(status="proposed"), ev, 50000) is None
    assert parse_resolved(raw(volume=10), ev, 50000) is None
    assert parse_resolved(raw(outcomes='["A", "B", "C"]'), ev, 50000) is None


def test_categorize_prefers_real_schedule_then_highest_rate():
    assert categorize({"feesEnabled": True, "feeType": "crypto_fees_v2",
                       "feeSchedule": {"rate": 0.07}}, []) == ("crypto", 0.07)
    assert categorize({}, ["geopolitics", "politics"]) == ("politics", 0.04)
    assert categorize({}, ["geopolitics"]) == ("geopolitics", 0.0)
    assert categorize({}, ["inconnu"]) == ("other", 0.05)


def test_price_lookup_never_reads_the_future():
    m = market(1, {10: 0.6, 5: 0.7, 1: 0.99})
    assert m.yes_price_at(END - 9 * H) == 0.6     # le point de 5 h n'existe pas encore
    assert m.yes_price_at(END - 6 * H) is None    # 0,6 date de 4 h : périmé (2 h max)
    assert m.yes_price_at(END - 5 * H) == 0.7
    assert m.yes_price_at(END - 20 * H) is None   # rien avant
    assert m.yes_price_at(END - 2 * H, max_age=3600) is None  # trop vieux


def test_backtest_cannot_use_future_data():
    """Le cas du cahier des charges : une stratégie ne voit jamais un prix postérieur.

    Le prix saute à 0,99 une heure avant l'échéance. À l'horizon 2 h, la stratégie doit
    voir 0,6, jamais 0,99. On vérifie aussi qu'un marché clos avant l'instant de décision
    ne produit aucun échantillon (sinon on « saurait » qu'il s'est résolu tôt).
    """
    samples, _ = build_samples([market(1, {3: 0.6, 1: 0.99})], horizons=(2, 1))
    by_h = {s.horizon_h: s.price_yes for s in samples["1"]}
    assert by_h[2] == 0.6
    early = market(2, {30: 0.5, 25: 0.97}, closed=END - 24 * H)  # résolu un jour avant l'échéance
    samples, _ = build_samples([early], horizons=(24, 12, 1))
    assert "2" not in samples


def test_split_by_event_is_chronological_and_disjoint():
    markets = [market(i, {2: 0.6}, end=END + i * 24 * H, event=f"e{i // 2}") for i in range(20)]
    samples, _ = build_samples(markets, horizons=(2,))
    (train, val, test), _ = split_by_event(samples)
    events = [{s.event_id for rows in part.values() for s in rows} for part in (train, val, test)]
    assert not (events[0] & events[1]) and not (events[1] & events[2]) and not (events[0] & events[2])
    last_train = max(s.ts for rows in train.values() for s in rows)
    first_test = min(s.ts for rows in test.values() for s in rows)
    assert last_train < first_test


def synthetic(n, true_offset, seed=1):
    rng = random.Random(seed)
    markets = []
    for i in range(n):
        price = rng.uniform(0.80, 0.90)
        win = rng.random() < price + true_offset
        markets.append(market(i, {6: price}, winner=0 if win else 1, end=END + i * H))
    return markets


def test_calibration_finds_no_edge_in_calibrated_prices():
    samples, outcomes = build_samples(synthetic(3000, 0.0), horizons=(6,))
    table = calibration.fit(samples, outcomes)
    for cell in table.values():
        assert cell.delta_low <= 0.0 <= cell.delta_high or abs(cell.delta_shrunk) < 0.02


def test_calibration_detects_real_mispricing_and_strategy_profits(limits):
    markets = synthetic(4000, 0.08)
    samples, outcomes = build_samples(markets, horizons=(6,))
    table = calibration.fit(samples, outcomes)
    assert any(c.delta_low > 0.03 for c in table.values())

    def rule(s):
        cell = table.get(calibration.cell_key(s.category, s.horizon_h, s.price_yes))
        if cell is None or cell.delta_low < 0.04:
            return None
        return Decision(0, s.price_yes + cell.delta_low, s.price_yes + cell.delta_shrunk,
                        min(s.price_yes + cell.delta_high, 0.995))
    result = simulate("test", rule, samples, outcomes, limits)
    assert result.metrics()["operations"] > 100
    assert result.final_cash > result.initial
    assert not result.bankrupt


def test_do_nothing_keeps_capital_and_simulation_is_reproducible(limits):
    samples, outcomes = build_samples(synthetic(300, 0.08, seed=5), horizons=(6,))
    nothing = simulate("rien", lambda s: None, samples, outcomes, limits)
    assert nothing.final_cash == nothing.initial == 1000
    rule = lambda s: Decision(0, s.price_yes + 0.05, s.price_yes + 0.06, s.price_yes + 0.07)
    a = simulate("x", rule, samples, outcomes, limits).metrics()
    b = simulate("x", rule, samples, outcomes, limits).metrics()
    assert a == b


def test_simulation_respects_the_safety_controller(limits):
    """Une règle déraisonnable (avantage inventé) est bridée par les mêmes garde-fous qu'en réel."""
    samples, outcomes = build_samples(synthetic(500, -0.3, seed=3), horizons=(6,))
    greedy = lambda s: Decision(0, 0.99, 0.995, 0.999)
    result = simulate("avide", greedy, samples, outcomes, limits)
    assert not result.bankrupt
    assert all(t["cost"] <= 0.05 * 1000 + 1 for t in result.trades)
    assert result.final_cash > 0
