"""Garde-fous du capital principal (17/10/2026) : mise par pari et argent engagé par famille plafonnés."""

from __future__ import annotations

from decimal import Decimal as D
from types import SimpleNamespace

from conftest import KEY, NOW, raw_market
from polymarket_agent.ledger import Ledger
from polymarket_agent.main import _cap_main
from polymarket_agent.safety_controller import Proposal
from polymarket_agent.sources.polymarket_gamma import parse_market


def _prop(market_id, token, shares, price="0.50", side="BUY"):
    return Proposal(op_id="o" + token, side=side, market_id=market_id, event_id="e", token_id=token, outcome="No",
                    est_probability=D("0.6"), prob_low=D("0.55"), prob_high=D("0.65"), max_price=D(price),
                    shares=D(shares), net_edge=D("0.05"), sources=("t",), uncertainty="", invalidation="",
                    horizon_hours=D("10"), strategy_id="s", strategy_version="1")


def test_main_portfolio_bets_and_families_are_capped(tmp_path):
    ledger = Ledger.create(tmp_path / "l.jsonl", KEY, tmp_path / "l.lock", "1000", now=NOW)
    weather = [parse_market(raw_market(f"w{i}", yes_token=f"wy{i}", no_token=f"wn{i}", feeType="weather_fees"))
               for i in range(3)]
    sport = parse_market(raw_market("s", yes_token="sy", no_token="sn", feeType="sports_fees_v3"))
    by_market = {m.market_id: m for m in weather + [sport]}
    # Déjà 350 engagés en météo.
    ledger.record_buy(op_id="b0", token_id="wn0", market_id="w0", event_id="e", outcome="No", shares="700",
                      price="0.5", fee="0", strategy_id="s", strategy_version="1", now=NOW)
    deps = SimpleNamespace(settings={"principal": {"max_mise": 0.10, "max_famille": 0.40}})
    portfolio = SimpleNamespace(ledger=ledger, marks={})
    out = _cap_main(deps, portfolio, [_prop("w1", "wn1", "400"), _prop("w2", "wn2", "400"), _prop("s", "sn", "400"),
                                      _prop("w2", "wn2", "50", side="SELL")], by_market)
    shares = {(p.token_id, p.side): p.shares for p in out}
    assert shares[("wn1", "BUY")] == D("100")        # météo : 400 − 350 = 50 de place → 100 parts à 0,50
    assert ("wn2", "BUY") not in shares               # famille pleine : écarté
    assert shares[("sn", "BUY")] == D("200")         # sport : mise ≤ 10 % de 1 000 → 200 parts à 0,50
    assert shares[("wn2", "SELL")] == D("50")        # une vente n'est jamais plafonnée
    assert _cap_main(SimpleNamespace(settings={}), portfolio, [_prop("s", "sn", "400")], by_market)[0].shares == D("400")


def test_shares_are_recomputed_at_most_hourly_but_entries_apply_at_once(tmp_path):
    """18/10/2026 : pas de va-et-vient des parts toutes les 5 minutes ; une entrée ou une sortie
    change la répartition tout de suite."""
    from datetime import timedelta
    from types import SimpleNamespace
    from conftest import NOW
    from polymarket_agent.main import _steady_shares
    from polymarket_agent.persistence import Database
    clock = {"t": NOW}
    deps = SimpleNamespace(settings={"arena": {"repartition": {"recalcul_minutes": 60}}},
                           db=Database(tmp_path / "s.sqlite"), now=lambda: clock["t"])
    assert _steady_shares(deps, {"a": 0.4, "b": 0.2}) == {"a": 0.4, "b": 0.2}
    clock["t"] = NOW + timedelta(minutes=5)
    assert _steady_shares(deps, {"a": 0.41, "b": 0.19}) == {"a": 0.4, "b": 0.2}     # gardées
    assert _steady_shares(deps, {"a": 0.3, "b": 0.2, "c": 0.1}) == {"a": 0.3, "b": 0.2, "c": 0.1}  # entrée
    clock["t"] = NOW + timedelta(minutes=70)
    assert _steady_shares(deps, {"a": 0.25, "b": 0.25, "c": 0.1}) == {"a": 0.25, "b": 0.25, "c": 0.1}  # 1 h passée


def test_a_strategy_never_engages_more_than_its_share_in_total(tmp_path):
    """18/10/2026 : nf_court avait 630 investis sur ≈ 1 000 pour une part d'environ 50 % ; réduire
    chaque mise ne suffisait pas. Positions déjà ouvertes + nouveaux achats ≤ part × capital."""
    import dataclasses
    from decimal import Decimal as D
    from types import SimpleNamespace
    from conftest import KEY, NOW, buy
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.main import Weighted
    ledger = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW)
    for k in range(4):  # 4 × 100 déjà investis par la stratégie
        ledger.record_buy(op_id=f"o{k}", token_id=f"t{k}", market_id=f"m{k}", event_id=f"e{k}", outcome="Yes",
                          shares="200", price="0.5", fee="0", strategy_id="nf_court", strategy_version="1", now=NOW)
    buy(ledger, "x1", token="autre", shares="200", price="0.5")  # une autre stratégie : ne compte pas

    @dataclasses.dataclass
    class Prop:
        side: str
        shares: D
        max_price: D
        op_id: str

    def prop(op, shares, price="0.5"):
        return Prop("BUY", D(shares), D(price), op)

    class Inner:
        strategy_id, version = "nf_court", "1"

        def propose(self, watchlist, books, state, limits, bucket, marks=None):
            return SimpleNamespace(proposals=[prop("a", "300"), prop("b", "300"), prop("c", "300")], limit_orders=[])

    out = Weighted(Inner(), D("0.5")).propose([], {}, ledger.state, None, "b1")
    # Part 0,5 × capital 1 000 = 500 ; 400 déjà investis → 100 de budget, soit 200 parts à 0,5.
    assert [(p.op_id, p.shares) for p in out.proposals] == [("a", D("150")), ("b", D("50"))]
