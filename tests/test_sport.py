"""Sport : marché « A vs. B » relié à son match et à ses cotes ; fin de match et cotes des
bookmakers (AMELIORATION n°2 et 5, 17/10/2026)."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal as D

from conftest import KEY, NOW, ROOT, make_book, raw_market
from polymarket_agent import sports_link
from polymarket_agent.ledger import Ledger
from polymarket_agent.observations import Observation
from polymarket_agent.safety_controller import RiskLimits
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v2 import CotesBookmakers, FinDeMatch


def _market(start, question="Dodgers vs. Brewers", outcomes=("Dodgers", "Brewers")):
    return parse_market(raw_market("g1", yes_token="T0", no_token="T1", question=question,
                                   outcomes=json.dumps(list(outcomes)), feeType="sports_fees_v3",
                                   gameStartTime=start.strftime("%Y-%m-%d %H:%M:%S+00")))


def _game(state, home="Milwaukee Brewers", away="Los Angeles Dodgers", hs=2, as_=5, start=NOW, seen=NOW):
    return Observation(source="mlb_stats", external_id=f"mlb_stats-1-{state}-{as_}-{hs}", published_at=start,
                       collected_at=seen, url="https://www.mlb.com/gameday/1", title="", text="",
                       data={"ligue": "MLB", "domicile": home, "exterieur": away, "score_domicile": hs,
                             "score_exterieur": as_, "etat": state, "debut": start.isoformat()})


def _odds(p_home, p_away, start, seen=NOW, home="Milwaukee Brewers", away="Los Angeles Dodgers"):
    return Observation(source="odds_api", external_id="odds-1", published_at=seen, collected_at=seen,
                       url="https://the-odds-api.com", title="", text="",
                       data={"domicile": home, "exterieur": away, "probabilites": {home: p_home, away: p_away},
                             "debut": start.isoformat()})


def test_markets_are_linked_to_their_game_only_when_both_teams_match():
    m = _market(NOW - timedelta(hours=3))
    info = sports_link.link(m, [_game("en cours", seen=NOW - timedelta(hours=1)), _game("terminé")])
    assert info["etat"] == "terminé" and info["score"] == [5, 2] and info["gagnant"] == 0  # Dodgers (issue 0)
    assert sports_link.link(m, [_game("terminé", home="Milwaukee Brewers", away="New York Mets")]) is None
    assert sports_link.link(m, [_game("terminé", start=NOW + timedelta(days=2))]) is None  # autre match
    yes_no = _market(NOW, question="Will the Dodgers win?", outcomes=("Yes", "No"))
    assert sports_link.link(yes_no, [_game("terminé")]) is None
    assert sports_link.same_team("Dodgers", "Los Angeles Dodgers") and not sports_link.same_team("Mets", "Dodgers")
    tie = sports_link.link(m, [_game("terminé", hs=3, as_=3)])
    assert tie["gagnant"] is None
    odds = sports_link.link(m, [_odds(0.42, 0.58, NOW)])
    assert odds["cotes"] == [0.58, 0.42] and odds["etat"] is None


_N = [0]


def _state(tmp_path):
    _N[0] += 1
    return Ledger.create(tmp_path / f"l{_N[0]}.jsonl", KEY, tmp_path / f"l{_N[0]}.lock", "1000", now=NOW).state


def _strategy(cls, **params):
    return cls("1.0.0", "2026-10-17", {k: D(str(v)) for k, v in params.items()})


def test_fin_de_match_buys_the_official_winner_below_one(tmp_path):
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    s = _strategy(FinDeMatch, certainty=0.995, max_price=0.99, min_net_edge=0.004, stake_fraction=0.1,
                  max_proposals_per_cycle=5, max_extra_ticks=2)
    m = _market(NOW - timedelta(hours=3))
    m.sport = sports_link.link(m, [_game("terminé")])
    books = {"T0": make_book("T0", bids=(("0.96", "500"),), asks=(("0.97", "500"),)),
             "T1": make_book("T1", bids=(("0.02", "500"),), asks=(("0.03", "500"),))}
    out = s.propose([m], books, _state(tmp_path), limits, "b1")
    assert len(out.proposals) == 1 and out.proposals[0].token_id == "T0" and out.proposals[0].outcome == "Dodgers"
    # Déjà au prix plein : rien. Match en cours : rien.
    books["T0"] = make_book("T0", bids=(("0.99", "500"),), asks=(("0.995", "500"),))
    assert not s.propose([m], books, _state(tmp_path), limits, "b1").proposals
    m.sport = sports_link.link(m, [_game("en cours")])
    books["T0"] = make_book("T0", bids=(("0.96", "500"),), asks=(("0.97", "500"),))
    assert not s.propose([m], books, _state(tmp_path), limits, "b1").proposals


def test_cotes_bookmakers_buys_what_polymarket_sells_too_cheap_before_kickoff(tmp_path):
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    s = _strategy(CotesBookmakers, margin=0.02, min_net_edge=0.03, max_odds_age_hours=13, kelly_fraction=0.25,
                  max_proposals_per_cycle=4, max_extra_ticks=1)
    start = NOW + timedelta(hours=6)
    m = _market(start)
    m.sport = sports_link.link(m, [_odds(0.40, 0.60, start, seen=NOW - timedelta(hours=2))])
    # Bookmakers : Dodgers 60 % ; Polymarket les vend 0,50 → avantage ≈ 0,58 − 0,50 − frais.
    books = {"T0": make_book("T0", bids=(("0.49", "500"),), asks=(("0.50", "500"),)),
             "T1": make_book("T1", bids=(("0.50", "500"),), asks=(("0.51", "500"),))}
    out = s.propose([m], books, _state(tmp_path), limits, "b1")
    assert len(out.proposals) == 1 and out.proposals[0].outcome == "Dodgers"
    # Prix juste (0,59) : rien. Cotes trop vieilles : rien.
    books["T0"] = make_book("T0", bids=(("0.58", "500"),), asks=(("0.59", "500"),))
    assert not s.propose([m], books, _state(tmp_path), limits, "b1").proposals
    m.sport = sports_link.link(m, [_odds(0.40, 0.60, start, seen=NOW - timedelta(hours=20))])
    books["T0"] = make_book("T0", bids=(("0.49", "500"),), asks=(("0.50", "500"),))
    assert not s.propose([m], books, _state(tmp_path), limits, "b1").proposals


def test_only_the_match_winner_market_is_linked_to_scores_and_odds(tmp_path):
    """19/10/2026 : cotes_bookmakers appliquait les cotes du vainqueur aux handicaps et aux totaux du
    même match (Patriots estimés à 75 % vendus 28 %, −287 sur 14 paris)."""
    start = NOW + timedelta(hours=6)
    odds = [_odds(0.40, 0.60, start)]
    assert sports_link.link(_market(start), odds)["cotes"] == [0.6, 0.4]
    assert sports_link.link(_market(start, question="Spread: Dodgers (-1.5)"), odds) is None
    assert sports_link.link(_market(start, question="Dodgers vs. Brewers: O/U 8.5"), odds) is None
    typed = _market(start)
    typed.sports_market_type = "spreads"  # Gamma le dit : jamais rattaché
    assert sports_link.link(typed, odds) is None
    typed.sports_market_type = "moneyline"
    assert sports_link.link(typed, odds) is not None
    raw = raw_market("g2", sportsMarketType="totals", holdingRewardsEnabled=True)
    assert parse_market(raw).sports_market_type == "totals" and parse_market(raw).holding_rewards
    # Garde-fou : plus de 25 points d'écart avec les bookmakers = rattachement douteux, rien n'est acheté.
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    s = _strategy(CotesBookmakers, margin=0.02, min_net_edge=0.03, max_odds_age_hours=13, kelly_fraction=0.25,
                  max_proposals_per_cycle=4, max_extra_ticks=1, max_gap=0.25)
    m = _market(start)
    m.sport = sports_link.link(m, [_odds(0.25, 0.75, start, seen=NOW - timedelta(hours=2))])
    m.outcome_prices = [D("0.28"), D("0.72")]
    books = {"T0": make_book("T0", bids=(("0.27", "500"),), asks=(("0.28", "500"),)),
             "T1": make_book("T1", bids=(("0.71", "500"),), asks=(("0.72", "500"),))}
    out = s.propose([m], books, _state(tmp_path), limits, "b1")
    assert not out.proposals and "écart trop grand avec les bookmakers (rattachement douteux)" in out.abstentions
