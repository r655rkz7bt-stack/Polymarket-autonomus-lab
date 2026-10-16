"""Tenue de marché : cotation des deux côtés, stock, coupe-perte, récompenses estimées, markout."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal as D

import pytest

from conftest import KEY, NOW, ROOT, make_book, raw_market
from polymarket_agent import liquidity_rewards as lr
from polymarket_agent.ledger import Ledger
from polymarket_agent.safety_controller import RiskLimits
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v2 import MarketMaker

PARAMS = {"min_days_to_end": D("3"), "min_mid": D("0.15"), "max_mid": D("0.85"), "max_move_6h": D("0.03"),
          "min_reward_rate": D("5"), "improve_ticks": D("0"), "min_pair_margin": D("0.02"),
          "market_fraction": D("0.06"), "max_net_quotes": D("2"), "stop_loss": D("0.10"),
          "quote_hours": D("0.2"), "max_markets": D("12"), "max_candidates": D("30")}


def _market(rebate=0.25, bid=0.47, ask=0.50, days=10, rate=50, **kw):
    raw = raw_market("mm", yes_token="Y", no_token="N", yes_price="0.485", best_bid=bid, best_ask=ask,
                     end=NOW + timedelta(days=days),
                     schedule={"exponent": 1, "rate": 0.04, "takerOnly": True, "rebateRate": rebate},
                     rewardsMinSize=20, rewardsMaxSpread=3.5,
                     clobRewards=[{"rewardsDailyRate": rate}], **kw)
    return parse_market(raw)


def _books(ybid="0.47", yask="0.50"):
    nbid, nask = str(D(1) - D(yask)), str(D(1) - D(ybid))  # carnet du NON = miroir du OUI
    return {"Y": make_book("Y", bids=((ybid, "300"),), asks=((yask, "300"),)),
            "N": make_book("N", bids=((nbid, "300"),), asks=((nask, "300"),))}


def _state(tmp_path):
    return Ledger.create(tmp_path / "l.jsonl", KEY, tmp_path / "l.lock", "1000", now=NOW)


def test_gamma_reward_fields_are_parsed():
    m = _market()
    assert (m.rewards_min_size, m.rewards_max_spread, m.rewards_daily_rate, m.fees.rebate_rate) == (
        D("20"), D("3.5"), D("50"), D("0.25"))


def test_quotes_both_sides_on_calm_rewarded_markets_only(tmp_path):
    ledger, mm = _state(tmp_path), MarketMaker("1.0.0", "2026-10-16", dict(PARAMS))
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    out = mm.propose([_market()], _books(), ledger.state, limits, "b1")
    orders = sorted((o.token_id, o.side, o.max_price, o.shares) for o in out.limit_orders)
    # Achat du OUI à 0,47 et du NON à 0,50 : paire payée 0,97 (≤ 1 − 0,02), 20 parts (taille récompensée).
    assert orders == [("N", "BUY", D("0.50"), D("20")), ("Y", "BUY", D("0.47"), D("20"))]
    assert not out.proposals  # jamais d'achat immédiat au vendeur
    assert mm.candidates([_market()]) and not mm.candidates([_market(rebate=0.15)])  # sport exclu
    assert not mm.candidates([_market(rate=0)]) and not mm.candidates([_market(bid=0.89, ask=0.90)])
    near = mm.propose([_market(days=1)], _books(), ledger.state, limits, "b1")
    assert not near.limit_orders  # se tranche bientôt : pas de cote
    tight = mm.propose([_market(bid=0.49, ask=0.50)], _books("0.49", "0.50"), ledger.state, limits, "b1")
    assert not tight.limit_orders  # paire à 0,99 : marge sous 0,02


def test_held_inventory_is_sold_back_and_net_exposure_is_capped(tmp_path):
    ledger, mm = _state(tmp_path), MarketMaker("1.0.0", "2026-10-16", dict(PARAMS))
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    ledger.record_buy(op_id="f1", token_id="Y", market_id="mm", event_id="ev1", outcome="Yes", shares="20",
                      price="0.47", fee="0", strategy_id="market_maker", strategy_version="1.0.0", now=NOW)
    out = mm.propose([_market()], _books(), ledger.state, limits, "b2")
    orders = {(o.token_id, o.side): o for o in out.limit_orders}
    # OUI détenu : revendu au meilleur vendeur (0,50) au lieu d'acheter le NON ; l'achat du OUI continue.
    assert set(orders) == {("Y", "SELL"), ("Y", "BUY")} and orders[("Y", "SELL")].max_price == D("0.50")
    ledger.record_buy(op_id="f2", token_id="Y", market_id="mm", event_id="ev1", outcome="Yes", shares="20",
                      price="0.47", fee="0", strategy_id="market_maker", strategy_version="1.0.0", now=NOW)
    capped = mm.propose([_market()], _books(), ledger.state, limits, "b3")
    assert {(o.token_id, o.side) for o in capped.limit_orders} == {("Y", "SELL")}  # 40 parts nettes = 2 cotes


def test_stop_loss_sells_the_unpaired_inventory_at_the_bid(tmp_path):
    ledger, mm = _state(tmp_path), MarketMaker("1.0.0", "2026-10-16", dict(PARAMS))
    ledger.record_buy(op_id="f1", token_id="Y", market_id="mm", event_id="ev1", outcome="Yes", shares="20",
                      price="0.47", fee="0", strategy_id="market_maker", strategy_version="1.0.0", now=NOW)
    mine = dict(ledger.state.positions)
    calm = mm.exits(mine, {"mm": _market()}, _books(), "b", NOW)
    assert calm == []
    crash = mm.exits(mine, {"mm": _market()}, _books("0.35", "0.38"), "b", NOW)
    assert len(crash) == 1 and crash[0].side == "SELL" and crash[0].max_price == D("0.35")


def test_reward_score_follows_the_official_example():
    # Docs Polymarket : milieu 0,50, v = 3 c : 100 parts à 0,49 → 44,4 ; 200 parts à 0,48 → 22,2.
    assert lr.order_score(0.49, 0.50, 100, 3, 0) == pytest.approx(44.44, abs=0.01)
    assert lr.order_score(0.48, 0.50, 200, 3, 0) == pytest.approx(22.22, abs=0.01)
    assert lr.order_score(0.47, 0.50, 100, 3, 0) == 0  # hors de l'écart récompensé
    assert lr.q_min(30, 0, 0.5) == 10 and lr.q_min(30, 0, 0.95) == 0  # un seul côté : un tiers, ou rien


def test_reward_estimate_counts_competitors_once_from_the_yes_book():
    m = _market()
    book = make_book("Y", bids=(("0.48", "100"),), asks=(("0.50", "100"),))
    quotes = [lr.to_quote(m, "Y", "BUY", 0.48, 100), lr.to_quote(m, "N", "BUY", 0.50, 100)]  # NON à 0,50 = OUI vendu à 0,50
    assert quotes[1] == lr.Quote(2, 0.5, 100)
    est = lr.estimate(m, book, quotes, minutes=5)
    assert est.share == pytest.approx(0.5) and est.amount == pytest.approx(0.5 * 50 * 5 / 1440, rel=1e-3)
    assert lr.estimate(_market(rate=0), book, quotes, 5) is None


def test_markout_compares_filled_and_missed_resting_orders(tmp_path):
    import json
    from polymarket_agent import markout
    from polymarket_agent.persistence import Database
    db = Database(tmp_path / "m.sqlite")
    at = NOW
    later = make_book("Y", bids=(("0.40", "100"),), asks=(("0.42", "100"),), ts=at + timedelta(minutes=6))
    db.save_books("c2", [later])
    entries = [{"type": "BUY", "ts": at.isoformat(), "data": {"token_id": "Y", "price": "0.47", "shares": "20",
                                                           "strategy_id": "market_maker", "extra": {"order_type": "limite"}}},
               {"type": "SETTLE", "ts": (at + timedelta(days=2)).isoformat(),
                "data": {"token_id": "Y", "payout_per_share": "0"}}]
    rep = markout.report(db, {"fantome:market_maker_v1.0.0": entries}, at + timedelta(days=3))
    served = rep["fantome:market_maker_v1.0.0"]["servis"]
    assert served["5 min"]["moyenne"] == pytest.approx(0.41 - 0.47) and served["résolution"]["moyenne"] == -0.47
    assert served["executions"] == 1 and rep["fantome:market_maker_v1.0.0"]["manques"]["ordres"] == 0
    # Un ordre jamais servi (vente posée à 0,50, expirée) : le prix est descendu, il aurait gagné.
    db.conn.execute("INSERT INTO pending_orders VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    ("o1", "fantome:market_maker_v1.0.0", "Y", "SELL", "20", 0, at.isoformat(),
                     (at + timedelta(minutes=12)).isoformat(), "EXPIRE", json.dumps({"max_price": "0.50"}),
                     at.isoformat()))
    rep = markout.report(db, {"fantome:market_maker_v1.0.0": entries}, at + timedelta(days=3))
    assert rep["fantome:market_maker_v1.0.0"]["manques"]["5 min"]["moyenne"] == pytest.approx(0.50 - 0.41)
