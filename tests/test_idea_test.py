"""Outil générique de test sur le passé (idea_test.py)."""

from __future__ import annotations

import json

import pytest

from polymarket_agent import idea_test as it


def _event(slug="highest-temperature-in-paris-on-october-10-2026", prices=("1", "0"), status="resolved"):
    return {"id": "e1", "slug": slug, "endDate": "2026-10-10T12:00:00Z", "markets": [
        {"id": "m1", "question": "Will the highest temperature in Paris be 16°C on October 10?",
         "outcomePrices": json.dumps(list(prices)), "clobTokenIds": json.dumps(["Y", "N"]),
         "umaResolutionStatus": status, "endDate": "2026-10-10T12:00:00Z", "feesEnabled": True,
         "feeSchedule": {"rate": 0.05}, "resolutionSource": "https://www.weather.gov/wrh/timeseries?site=lfpb"}]}


class FakeHttp:
    def __init__(self, routes):
        self.routes, self.calls = routes, []

    def get_json(self, url, params=None, headers=None):
        self.calls.append((url, params))
        for prefix, payload in self.routes.items():
            if url.startswith(prefix):
                return payload(params) if callable(payload) else payload
        raise it.SourceUnavailable(url)


def test_resolved_markets_are_parsed_filtered_and_cached(tmp_path):
    http = FakeHttp({it.GAMMA + "/events": [_event(), _event(slug="autre-chose"), _event(prices=("0.5", "0.5")),
                                            _event(status="disputed")]})
    rows = it.fetch_resolved(http, tmp_path, "2026-10-01", "2026-10-15", tag_id=84, slug_pattern=r"temperature")
    assert len(rows) == 1 and rows[0].won == 1 and rows[0].fee_rate == 0.05 and "lfpb" in rows[0].resolution_source
    assert http.calls[0][1]["tag_id"] == 84
    again = it.fetch_resolved(FakeHttp({}), tmp_path, "2026-10-01", "2026-10-15", tag_id=84, slug_pattern=r"temperature")
    assert [r.market_id for r in again] == ["m1"]  # lu dans le cache, aucun appel


def test_price_never_reads_after_the_decision_and_is_cached(tmp_path):
    http = FakeHttp({it.CLOB: {"history": [{"t": 100, "p": 0.4}, {"t": 200, "p": 0.6}, {"t": 300, "p": 0.9}]}})
    cache = it.PriceCache(tmp_path / "prix.sqlite", http)
    assert cache.price_at("Y", 250) == 0.6 and cache.price_at("Y", 250) == 0.6 and len(http.calls) == 1
    empty = it.PriceCache(tmp_path / "p2.sqlite", FakeHttp({it.CLOB: {"history": []}}))
    assert empty.price_at("Y", 250) is None


def test_evaluation_is_out_of_sample_with_real_fees():
    def case(day, price, won, group="a"):
        r = it.Resolved("m" + day + str(price), "e", "s", "q", "Y", won, 0, fee_rate=0.05)
        return it.Case(r, price, group, day)
    cases = [case(f"2026-10-0{d}", 0.6, 0) for d in range(1, 9)] + [case(f"2026-10-0{d}", 0.1, 0) for d in range(1, 9)]
    model = lambda c: 0.2   # le modèle juge les deux types de marché à 20 %
    train, test = it.split_by_day(cases)
    assert {c.day for c in train}.isdisjoint({c.day for c in test}) and len(test) == 8
    sim = it.simulate(test, model, edge=0.05, spread=0.01)
    # 0,6 → NON acheté 0,41 (+ frais), gagne ; 0,1 → OUI ? 0,2 − 0,11 − frais > 0,05 → OUI acheté, perd.
    assert sim["par_type"]["NON 0,2-0,8"]["paris"] == 4 and sim["par_type"]["OUI <0,2"]["paris"] == 4
    assert sim["par_type"]["NON 0,2-0,8"]["resultat"] > 0 > sim["par_type"]["OUI <0,2"]["resultat"]
    only_no = it.simulate(test, model, sides=("NON",))
    assert set(only_no["par_type"]) == {"NON 0,2-0,8"}
    rep = it.evaluate(cases, model)
    assert rep["test"] == 8 and "seuil 0.05 / écart 0.01" in rep["simulations"]
    assert "| Brier" in it.markdown("essai", rep)


def test_taker_cost_reads_real_trades_and_never_looks_ahead(tmp_path):
    from test_sources import FakeHttp
    from polymarket_agent import idea_test as it
    raw = [{"timestamp": 1000, "asset": "NO", "side": "BUY", "price": 0.40, "size": 10},
           {"timestamp": 1500, "asset": "YES", "side": "SELL", "price": 0.55, "size": 5},   # NON à 0,45
           {"timestamp": 1600, "asset": "NO", "side": "SELL", "price": 0.30, "size": 5},   # vente du NON : ignorée
           {"timestamp": 2500, "asset": "NO", "side": "BUY", "price": 0.50, "size": 5}]
    http = FakeHttp({it.TRADES: raw})
    trades = it.fetch_event_trades(http, tmp_path, "e1")
    assert it.fetch_event_trades(FakeHttp({}), tmp_path, "e1") == trades  # cache
    assert it.taker_cost(trades, "NO", "YES", 2000) == pytest.approx(0.45)  # jamais l'échange de 2500
    assert it.taker_cost(trades, "NO", "YES", 2000, after=True) == 0.50
    assert it.taker_cost(trades, "NO", "YES", 1200, window=100) is None
