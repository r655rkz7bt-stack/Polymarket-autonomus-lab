"""Entonnoir 80/20 (demande d'Etienne, 20/10/2026) : le petit morceau des paris qui fait les gains,
et les filles qui l'isolent."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal as D

from conftest import NOW, raw_market
from polymarket_agent import pareto
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategy_engine import Filtered


def _trade(k, price, won, question, hours, domain="", outcome="Player A", resting=False, hour=8):
    ts = (NOW.replace(hour=hour) + timedelta(minutes=k)).isoformat()
    extra = {"horizon_hours": str(hours)} | ({"resting_order": True} if resting else {})
    buy = {"type": "BUY", "ts": ts, "data": {"token_id": f"t{k}", "market_id": f"m{k}", "event_id": f"e{k}",
                                             "outcome": outcome, "shares": "100", "price": str(price), "fee": "0",
                                             "strategy_id": "s", "strategy_version": "1", "extra": extra}}
    settle = {"type": "SETTLE", "ts": ts, "data": {"token_id": f"t{k}", "payout_per_share": "1" if won else "0",
                                                  "resolution": "x"}}
    return [buy, settle], {f"m{k}": {"question": question, "domain": domain}}


def _book(spec):
    entries, markets = [], {}
    for k, row in enumerate(spec):
        e, m = _trade(k, *row)
        entries += e
        markets.update(m)
    return entries, markets


def test_the_small_slice_that_makes_the_gains_is_found_and_becomes_a_daughter():
    tennis = [(0.85, True, "Almaty Open: A vs B", 120, "atptour.com")] * 10
    other = [(0.90, k % 3 != 0, "Cardinals vs. Rams", 2) for k in range(12)]
    entries, markets = _book(tennis + other)
    bets = pareto.bets_of(entries, markets)
    assert len(bets) == 22 and bets[0].traits["discipline"] == "tennis" and bets[0].traits["delai"] == (72, 168)
    d = pareto.dissect(bets)
    assert d["discipline"]["coeur"]["morceaux"] == ["tennis"] and d["discipline"]["coeur"]["part_des_paris"] < 0.5
    found = pareto.proposals("s", bets, d)
    by = {p["morceau"]: p for p in found}
    assert by["discipline tennis"]["filtres"] == {"disciplines": ["tennis"]}
    assert by["délai jusqu'à la fin 72-168 h"]["filtres"] == {"echeance_min": 72, "echeance_max": 168}
    assert not any("autre" in p["morceau"] for p in found)  # « autre » n'isole rien
    assert all(p["rendement"] > pareto._stats(bets)["rendement"] for p in found)


def test_only_growing_strategies_are_dissected_and_existing_daughters_are_not_proposed_twice():
    entries, markets = _book([(0.85, True, "Almaty Open: A vs B", 120, "atptour.com")] * 10
                             + [(0.90, False, "Cardinals vs. Rams", 2)] * 3 + [(0.9, True, "Cardinals vs. Rams", 2)] * 4)
    configs = {"mere_x": {}, "fille_x": {"mere": "mere_x", "filtres": {"disciplines": ["tennis"]}}}
    reports = pareto.analyse({"mere_x_v1": entries, "plate_v1": entries}, {"mere_x_v1": 0.2, "plate_v1": 0.0},
                             {}, markets, configs, min_closed=15)
    assert [r["strategie"] for r in reports] == ["mere_x_v1"]
    tennis = next(p for p in reports[0]["filles"] if p["morceau"] == "discipline tennis")
    assert tennis["existe"]
    todo = pareto.obligations(reports)
    assert todo and all("discipline tennis" not in t for t in todo)
    assert "Entonnoir 80/20" in pareto.render(reports)
    # Une fille qui fait mieux que sa mère est disséquée même avec une croissance modeste.
    both = pareto.analyse({"m_v1": entries, "f_v1": entries}, {"m_v1": -0.1, "f_v1": 0.01}, {"f": "m"}, markets,
                          {}, min_closed=15)
    assert [r["strategie"] for r in both] == ["f_v1"]


def test_discipline_bet_type_and_new_daughter_filters():
    assert pareto.discipline("Mannarino vs Vukic", "https://www.atptour.com/en/scores") == "tennis"
    assert pareto.discipline("Counter-Strike: FURIA vs BetBoom Team - Map 1 Winner") == "counter-strike"
    assert pareto.bet_type("Spread: Titans (-3.5)") == "handicap" and pareto.bet_type("Cardinals vs. Rams") == "vainqueur"
    assert pareto.bet_type("x", "totals") == "total"

    class Inner:
        strategy_id, version = "s", "1"

        def propose(self, watchlist, *a, **k):
            from polymarket_agent.strategy_engine import StrategyOutput
            self.seen = [m.market_id for m in watchlist]
            return StrategyOutput()
    tennis = parse_market(raw_market("t", question="Mannarino vs Vukic", end=NOW + timedelta(hours=120),
                                     resolutionSource="https://www.atptour.com", spread=0.01))
    nfl = parse_market(raw_market("n", question="Spread: Titans (-3.5)", end=NOW + timedelta(hours=2), spread=0.04))
    from conftest import make_book
    books = {"x": make_book("x", ts=NOW)}
    for filt, want in [({"disciplines": ["tennis"]}, ["t"]), ({"types_pari": ["handicap"]}, ["n"]),
                       ({"echeance_min": 72, "echeance_max": 168}, ["t"]), ({"ecart_max": D("0.02")}, ["t"])]:
        inner = Inner()
        Filtered(inner, filt).propose([tennis, nfl], books, None, None, "b1")
        assert inner.seen == want, filt
