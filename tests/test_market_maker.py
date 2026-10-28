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
    # Le tableau de bord nomme le fantôme sans « fantome: » (nom du fichier du journal) : même résultat.
    rep2 = markout.report(db, {"market_maker_v1.0.0": entries}, at + timedelta(days=3))
    assert rep2["market_maker_v1.0.0"]["manques"]["ordres"] == 1


def test_ranking_bonus_counts_finished_paid_days_capped_by_the_pool(tmp_path):
    from polymarket_agent.persistence import Database
    db = Database(tmp_path / "r.sqlite")
    day1, today = NOW - timedelta(days=1), NOW

    def put(cycle, when, portfolio, market, amount, pool):
        lr.record(db, cycle, when, portfolio, market, lr.Estimate(0.5, 1.0, 1.0, amount, True), D(str(pool)))

    put("c1", day1, "fantome:mm_v1", "m1", 3.0, 2.0)      # plafonné à la cagnotte : 2 $
    put("c2", day1, "fantome:mm_v1", "m2", 1.5, 50.0)
    put("c3", day1, "fantome:petit_v1", "m1", 0.4, 50.0)  # moins de 1 $ : pas versé par Polymarket
    put("c4", today, "fantome:mm_v1", "m1", 9.0, 50.0)    # journée pas terminée
    put("c5", day1, "principal", "m1", 5.0, 50.0)
    days = lr.payable_days(db, (day1 - timedelta(days=1)).isoformat(), today.date())
    assert sum(m["montant"] for m in days["fantome:mm_v1"][day1.date().isoformat()]) == pytest.approx(3.5)
    assert not days.get("fantome:petit_v1")
    starts = {"mm_v1": day1 - timedelta(hours=1), "petit_v1": day1, "neuf_v1": today}
    # Le principal n'est jamais un concurrent de l'arène ; prudence 0,5.
    assert lr.ranking_bonus(db, starts, 0.5, today) == {"mm_v1": pytest.approx(1.75)}

