"""Vingt nouvelles pistes, lot B (20/10/2026) : le prix de la même question ailleurs (Kalshi,
PredictIt, Manifold, bookmakers) et le compteur de tweets XTracker."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal as D

import pytest

from conftest import KEY, NOW, ROOT, make_book, raw_market
from polymarket_agent import references as refs
from polymarket_agent.ledger import Ledger
from polymarket_agent.observations import Observation
from polymarket_agent.persistence import Database
from polymarket_agent.safety_controller import RiskLimits
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import CompteurTweets, FootballTroisIssues, KalshiReference

LIMITS = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
REF = {"margin": 0.03, "max_gap": 0.2, "max_age_hours": 2, "uncertainty": 0.005, "min_net_edge": 0.01,
       "max_extra_ticks": 1, "max_proposals_per_cycle": 2, "kelly_fraction": 0.25}


def _s(cls, **params):
    return cls("1.0.0", "2026-10-20", {k: D(str(v)) for k, v in params.items()})


def _state(tmp_path, name="l"):
    return Ledger.create(tmp_path / f"{name}.jsonl", KEY, tmp_path / f"{name}.lock", "1000", now=NOW).state


def test_kalshi_and_predictit_matches_need_same_words_and_numbers(tmp_path):
    fed = parse_market(raw_market("f", question="Will the Fed cut rates by 50 bps in December?",
                                  end=NOW + timedelta(days=50)))
    rows = [{"titre": "Will the Fed cut rates by 50 bps at the December meeting?", "p": 0.31,
             "fin": (NOW + timedelta(days=52)).isoformat()},
            {"titre": "Will the Fed cut rates by 25 bps at the December meeting?", "p": 0.6,
             "fin": (NOW + timedelta(days=52)).isoformat()}]
    hit = refs.match_kalshi(fed, rows)
    assert hit["p"] == 0.31 and hit["similarite"] >= 0.55  # 25 bps : autres nombres, écarté
    assert refs.match_kalshi(fed, [dict(rows[0], fin=(NOW + timedelta(days=200)).isoformat())]) is None
    nom = parse_market(raw_market("n", question="Will Gavin Newsom win the 2028 Democratic presidential nomination?"))
    pi = [{"marche": "Who will win the 2028 Democratic presidential nomination?", "contrat": "Gavin Newsom", "p": 0.27},
          {"marche": "Who will win the 2028 Democratic presidential nomination?", "contrat": "Kamala Harris", "p": 0.1}]
    assert refs.match_predictit(nom, pi)["p"] == 0.27
    db = Database(tmp_path / "db.sqlite")
    refs._save(db, "ref:kalshi", rows, NOW)
    refs._save(db, "ref:predictit", pi, NOW)
    counts = refs.attach([fed, nom], db, NOW)
    assert counts["kalshi"] == 1 and counts["predictit"] == 1 and fed.references["kalshi"]["p"] == 0.31
    db.close()


def test_reference_strategy_buys_the_cheap_side_and_refuses_doubtful_matches(tmp_path):
    m = parse_market(raw_market("k", yes_token="kY", no_token="kN"))
    m.references = {"kalshi": {"p": 0.62, "vu_le": NOW.isoformat(), "titre": "même question"}}
    books = {"kY": make_book("kY", bids=(("0.53", "1000"),), asks=(("0.54", "1000"),)),
             "kN": make_book("kN", bids=(("0.46", "1000"),), asks=(("0.47", "1000"),))}
    s = _s(KalshiReference, **REF)
    out = s.propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in out.proposals] == ["Yes"]  # Kalshi 62 %, Polymarket 54 % : le OUI
    m.references["kalshi"]["p"] = 0.95  # 41 points d'écart : rattachement douteux
    assert not s.propose([m], books, _state(tmp_path, "b"), LIMITS, "b1").proposals
    m.references["kalshi"].update(p=0.62, vu_le=(NOW - timedelta(hours=5)).isoformat())
    assert "référence trop vieille" in s.propose([m], books, _state(tmp_path, "c"), LIMITS, "b1").abstentions


def test_tweet_buckets_from_the_pace_and_a_negative_binomial():
    assert refs.bucket_of("200-219") == (200, 219) and refs.bucket_of("<100") == (0, 99)
    assert refs.bucket_of("400+") == (400, 10 ** 9) and refs.bucket_of("Other") is None
    total = sum(refs.negbin_interval(k, k + 9, 50, 4) for k in range(0, 1000, 10))
    assert total == pytest.approx(1, abs=1e-6)
    assert refs.negbin_interval(0, 10 ** 9, 30, 2) == pytest.approx(1, abs=1e-6)
    tr = {"fin": (NOW + timedelta(hours=24)).isoformat(), "total": 180, "heures": [1] * 72}  # 1 par heure
    inside = refs.tweet_bucket_probability(tr, (200, 209), NOW, dispersion=1000)  # 180 + ~24
    assert inside > refs.tweet_bucket_probability(tr, (240, 249), NOW, dispersion=1000)
    assert refs.tweet_bucket_probability(tr, (100, 179), NOW, dispersion=4) == 0.0  # déjà dépassé


def test_tweet_strategy_uses_xtracker_and_refuses_a_stale_counter(tmp_path):
    m = parse_market(raw_market("t", yes_token="tY", no_token="tN", groupItemTitle="200-219",
                                end=NOW + timedelta(hours=24)))
    m.tweets = {"compte": "elonmusk", "fin": (NOW + timedelta(hours=24)).isoformat(), "total": 180,
                "heures": [1] * 72, "vu_le": NOW.isoformat()}
    books = {"tY": make_book("tY", bids=(("0.20", "1000"),), asks=(("0.21", "1000"),)),
             "tN": make_book("tN", bids=(("0.79", "1000"),), asks=(("0.80", "1000"),))}
    s = _s(CompteurTweets, dispersion=1000, recent_hours=72, max_stale_hours=6, margin=0.03, uncertainty=0.005,
           min_net_edge=0.01, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    out = s.propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in out.proposals] == ["Yes"]  # ~204 attendus : la tranche 200-219 vaut bien plus que 0,21
    m.tweets["vu_le"] = (NOW - timedelta(hours=12)).isoformat()
    assert "compteur pas à jour" in s.propose([m], books, _state(tmp_path, "b"), LIMITS, "b1").abstentions


def test_xtracker_counts_the_period_and_keeps_fourteen_days_hour_by_hour():
    start = NOW - timedelta(hours=30)

    class Http:
        def get_json(self, url, params=None, headers=None):
            if url.endswith("/api/users"):
                return {"data": [{"handle": "elonmusk", "trackings": [
                    {"isActive": True, "title": "Elon", "startDate": start.isoformat(),
                     "endDate": (start + timedelta(days=7)).isoformat(), "marketLink": "https://polymarket.com/event/elon-x"},
                    {"isActive": False, "title": "ancienne", "startDate": start.isoformat()}]}]}
            assert url.endswith("/api/users/elonmusk/posts") and params["startDate"] <= start.isoformat()
            hours = (1.5, 2.5, 2.7, 40, 50)  # il y a 1h30, 2h30, 2h42, 40 h (avant la période), 50 h
            return {"data": [{"createdAt": (NOW - timedelta(hours=h)).isoformat()} for h in hours]}
    rows = refs.fetch_tweet_trackings(Http(), now=NOW)
    assert len(rows) == 1 and rows[0]["slug"] == "elon-x" and rows[0]["total"] == 3
    hourly = rows[0]["heures"]
    assert len(hourly) == 336 and sum(hourly) == 5 and hourly[-2] == 1 and hourly[-3] == 2


def test_football_three_ways_and_champions_are_linked_to_bookmakers(tmp_path):
    start = NOW + timedelta(hours=5)
    obs = Observation(source="odds_api", external_id="o1", published_at=NOW, collected_at=NOW, url="", title="Cotes EPL",
                      text="", data={"domicile": "Arsenal", "exterieur": "Fulham", "debut": start.isoformat(),
                                     "probabilites": {"Arsenal": 0.6, "Fulham": 0.15, "Draw": 0.25},
                                     "reference": {"Arsenal": 0.62, "Fulham": 0.14, "Draw": 0.24}})
    win = parse_market(raw_market("w", question=f"Will Arsenal FC win on {start:%Y-%m-%d}?"))
    draw = parse_market(raw_market("d", question="Will Arsenal FC vs. Fulham FC end in a draw?", end=start))
    assert refs.attach_football([win, draw], [obs]) == 2
    assert win.references["bookmakers_3"]["p"] == 0.62 and draw.references["bookmakers_3"]["p"] == 0.24
    assert FootballTroisIssues.ref_key == "bookmakers_3"
    db = Database(tmp_path / "db.sqlite")
    refs._save(db, "ref:outrights", [{"sport": "basketball_nba_championship_winner", "titre": "NBA",
                                     "equipe": "Oklahoma City Thunder", "p": 0.31, "reference": "pinnacle",
                                     "vu_le": NOW.isoformat()}], NOW)
    champ = parse_market(raw_market("c", question="Will the Oklahoma City Thunder win the 2027 NBA Finals?"))
    assert refs.attach_outrights([champ], db) == 1 and champ.references["outright"]["p"] == 0.31
    db.close()


def test_outright_odds_share_the_daily_credit_budget(tmp_path, monkeypatch):
    from polymarket_agent.sources.odds_api import OutrightsSource
    monkeypatch.setenv("ODDS_API_KEY", "cle-test")
    db = Database(tmp_path / "db.sqlite")
    db.set_value(f"odds_api:credits:{NOW:%Y-%m-%d}", "15")  # déjà 15 crédits dépensés pour les matchs

    class Http:
        calls = 0

        def get_json(self, url, params=None, headers=None):
            Http.calls += 1
            outcomes = [{"name": n, "price": p} for n, p in (("A", 3.0), ("B", 4.0), ("C", 5.0))]
            return [{"sport_title": "NBA", "bookmakers": [{"key": "pinnacle", "markets": [
                {"key": "outrights", "outcomes": outcomes}]}]}]
    rows = OutrightsSource(Http(), ["nba", "nfl"], db, daily_budget=16).fetch(NOW)
    assert Http.calls == 1 and len(rows) == 3 and sum(r["p"] for r in rows) == pytest.approx(1, abs=1e-3)
    assert db.get_value(f"odds_api:credits:{NOW:%Y-%m-%d}") == "16"
    db.close()


def test_collector_keeps_reference_snapshots_without_observations(tmp_path):
    from polymarket_agent.data_collector import collect
    db = Database(tmp_path / "db.sqlite")
    settings = {"sources": {"kalshi": {"enabled": True}, "predictit": {"enabled": True}, "xtracker": {"enabled": True}}}
    factories = {"kalshi": lambda c: [{"titre": "x", "p": 0.4, "fin": None}], "predictit": lambda c: [],
                 "xtracker": lambda c: [{"slug": "s", "total": 3}]}
    res = collect(settings, None, db, [], NOW, factories)
    assert res.status["kalshi"] == "ok (1 prix relevés)" and res.status["xtracker"] == "ok (1 prix relevés)"
    assert json.loads(db.get_value("ref:kalshi"))["rows"][0]["p"] == 0.4 and not res.observations
    db.close()
