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
from polymarket_agent.strategy_engine import load_strategies
from polymarket_agent.strategies_v3 import (CompteurTweets, FatigueNhl, FootballTroisIssues, KalshiReference,
                                            MotsNouveaux, MotsPrononces)

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


def test_nhl_rest_flags_the_team_that_played_yesterday(tmp_path):
    """Lot C : le calendrier part d'hier ; une équipe qui y figure est « fatiguée » le lendemain."""
    start = NOW + timedelta(hours=8)

    def team(abbrev, name, place):
        return {"abbrev": abbrev, "commonName": {"default": name}, "placeName": {"default": place}}

    class Http:
        def get_json(self, url, params=None, headers=None):
            assert url.endswith("/schedule/2026-10-13")
            return {"gameWeek": [
                {"date": "2026-10-13", "games": [{"awayTeam": team("NYR", "Rangers", "New York"),
                                                  "homeTeam": team("BOS", "Bruins", "Boston")}]},
                {"date": "2026-10-14", "games": [{"startTimeUTC": start.isoformat(),
                                                  "awayTeam": team("NYR", "Rangers", "New York"),
                                                  "homeTeam": team("PIT", "Penguins", "Pittsburgh")}]}]}
    rows = refs.fetch_nhl_rest(Http(), NOW)
    assert len(rows) == 1 and rows[0]["fatigue_exterieur"] and not rows[0]["fatigue_domicile"]
    db = Database(tmp_path / "db.sqlite")
    refs._save(db, "ref:nhl_repos", rows, NOW)
    m = parse_market(raw_market("h", yes_token="hR", no_token="hP", outcomes=json.dumps(["Rangers", "Penguins"]),
                                gameStartTime=start.strftime("%Y-%m-%d %H:%M:%S+00")))
    assert refs.attach_nhl_rest([m], db) == 1 and m.references["repos_nhl"]["fatigue"] == [True, False]
    db.close()
    books = {"hR": make_book("hR", bids=(("0.54", "1000"),), asks=(("0.55", "1000"),)),
             "hP": make_book("hP", bids=(("0.45", "1000"),), asks=(("0.46", "1000"),))}
    s = _s(FatigueNhl, shift=0.05, margin=0.01, uncertainty=0.005, min_net_edge=0.01, max_age_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    out = s.propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in out.proposals] == ["Penguins"]  # l'équipe reposée
    m.references["repos_nhl"]["fatigue"] = [True, True]
    assert not s.propose([m], books, _state(tmp_path, "b"), LIMITS, "b1").proposals


def test_mention_base_rates_need_precedents_and_skip_cheap_tickets(tmp_path):
    """Lot C : taux de OUI passé du même mot chez le même orateur."""
    def mk(word, yes):
        return {"question": f'Will Trump say "{word}" this week?', "groupItemTitle": word,
                "outcomePrices": json.dumps(["1", "0"] if yes else ["0", "1"])}

    class Http:
        def get_json(self, url, params=None, headers=None):
            if params["offset"]:
                return []
            return [{"markets": [mk("Crypto / Bitcoin", True), mk("Crypto/Bitcoin", True), mk("crypto / bitcoin", True),
                                 mk("Crypto / Bitcoin", False), mk("Tariff", False),
                                 {"question": 'Will "Doom" be said?', "groupItemTitle": "Doom",
                                  "outcomePrices": json.dumps(["1", "0"])}]}]
    rows = {(r["orateur"], r["mot"]): r for r in refs.fetch_mention_history(Http())}
    assert rows[("trump", "crypto/bitcoin")]["oui"] == 3 and rows[("trump", "crypto/bitcoin")]["n"] == 4
    assert rows[("trump", "*")]["n"] == 5 and not any(k[0].startswith('"') for k in rows)
    db = Database(tmp_path / "db.sqlite")
    refs._save(db, "ref:mentions", list(rows.values()), NOW)
    m = parse_market(raw_market("w", yes_token="wY", no_token="wN", question='Will Trump say "crypto" or "Bitcoin" this week?',
                                groupItemTitle="Crypto / Bitcoin"))
    assert refs.attach_mentions([m], db) == 1
    ref = m.references["mentions"]
    assert ref["n"] == 4 and ref["p"] == pytest.approx((3 + 2 * 4 / 7) / 6, abs=1e-4)  # 0,69
    db.close()
    books = {"wY": make_book("wY", bids=(("0.40", "1000"),), asks=(("0.41", "1000"),)),
             "wN": make_book("wN", bids=(("0.59", "1000"),), asks=(("0.60", "1000"),))}
    params = dict(REF, margin=0.05, max_gap=0.6, max_age_hours=26, min_count=3, min_price=0.30)
    out = _s(MotsPrononces, **params).propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in out.proposals] == ["Yes"]
    out = _s(MotsPrononces, **dict(params, min_count=5)).propose([m], books, _state(tmp_path, "b"), LIMITS, "b1")
    assert not out.proposals and "trop peu de précédents" in out.abstentions
    out = _s(MotsPrononces, **dict(params, min_price=0.45)).propose([m], books, _state(tmp_path, "c"), LIMITS, "b1")
    assert not out.proposals and "billet trop bon marché" in out.abstentions


def test_announcers_of_football_and_of_the_rest_have_separate_histories():
    """21/10 (experiments/mentions_annonceurs.md) : aux prix payés, les commentateurs de NFL gagnent et ceux
    de la Coupe du monde perdent : un même mot ne doit pas mélanger leurs deux historiques."""
    nfl = refs.mention_key('Will the announcers say "Flag" 15+ times during the 49ers vs Rams game?', "Flag 15+ times")
    wc = refs.mention_key('Will the announcers say "Flag" 15+ times during Norway vs Senegal World Cup Match?', "Flag 15+ times")
    ufc = refs.mention_key('Will announcers say "Knockout" during McGregor vs Holloway at UFC 329?', "Knockout")
    assert nfl == ("the announcers (game)", "flag 15+ times") and ufc == ("the announcers", "knockout")
    assert wc == ("the announcers (world cup)", "flag 15+ times")
    assert refs.mention_key('Will Trump say "crypto" this week?', "Crypto") == ("trump", "crypto")


def test_question_filters_split_nfl_announcers_from_the_world_cup(tmp_path):
    from polymarket_agent.strategy_engine import Filtered
    cfg = {s.strategy_id: s for s in load_strategies(ROOT / "config" / "strategies.yaml")}["mots_prononces_nfl"]
    assert cfg.filters == {"question_contient": ["game?"], "question_exclut": ["world cup", "ufc"]}
    nfl = parse_market(raw_market("a", question='Will the announcers say "Flag" during the 49ers vs Rams game?'))
    wc = parse_market(raw_market("b", question='Will the announcers say "Goal" during Norway vs Senegal World Cup Match?'))
    ufc = parse_market(raw_market("c", question='Will announcers say "Knockout" during McGregor vs Holloway at UFC 329?'))
    trump = parse_market(raw_market("d", question='Will Trump say "crypto" this week?'))
    window = Filtered(cfg.inner, cfg.filters)
    assert [window._market_ok(m, None) for m in (nfl, wc, ufc, trump)] == [True, False, False, False]


def test_a_word_never_offered_for_a_regular_speaker_is_marked_new(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    refs._save(db, "ref:mentions", [{"orateur": "trump", "mot": "*", "oui": 6, "n": 12},
                                    {"orateur": "trump", "mot": "tariff", "oui": 6, "n": 12},
                                    {"orateur": "vance", "mot": "*", "oui": 1, "n": 4}], NOW)
    new = parse_market(raw_market("n", yes_token="nY", no_token="nN", question='Will Trump say "Hormuz" this week?',
                                  groupItemTitle="Hormuz"))
    rare = parse_market(raw_market("r", question='Will Vance say "Hormuz" today?', groupItemTitle="Hormuz"))
    assert refs.attach_mentions([new, rare], db) == 1 and "mot_nouveau" in new.references and not rare.references
    db.close()
    books = {"nY": make_book("nY", bids=(("0.49", "1000"),), asks=(("0.50", "1000"),)),
             "nN": make_book("nN", bids=(("0.50", "1000"),), asks=(("0.51", "1000"),))}
    s = _s(MotsNouveaux, shift=0.10, margin=0.02, uncertainty=0.005, min_yes=0.30, max_yes=0.85, min_net_edge=0.01,
           max_age_hours=26, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    assert [p.outcome for p in s.propose([new], books, _state(tmp_path), LIMITS, "b1").proposals] == ["No"]
    books["nY"] = make_book("nY", bids=(("0.19", "1000"),), asks=(("0.20", "1000"),))
    assert not s.propose([new], books, _state(tmp_path, "b"), LIMITS, "b1").proposals  # OUI déjà bon marché
    books["nY"] = make_book("nY", bids=(("0.16", "1000"),), asks=(("0.85", "1000"),))
    s.params["max_spread"] = D("0.10")
    assert "carnet trop écarté" in s.propose([new], books, _state(tmp_path, "c"), LIMITS, "b1").abstentions


def test_tweet_strategy_only_no_and_skip_nyc(tmp_path):
    m = parse_market(raw_market("t", yes_token="tY", no_token="tN", groupItemTitle="200-219",
                                end=NOW + timedelta(hours=24)))
    m.tweets = {"compte": "NYCMayor", "fin": (NOW + timedelta(hours=24)).isoformat(), "total": 180,
                "heures": [1] * 72, "vu_le": NOW.isoformat()}
    # le calcul donne ~0,6 pour la tranche : OUI à 0,21 est une affaire, NON à 0,80 n'en est pas une
    books = {"tY": make_book("tY", bids=(("0.20", "1000"),), asks=(("0.21", "1000"),)),
             "tN": make_book("tN", bids=(("0.79", "1000"),), asks=(("0.80", "1000"),))}
    base = dict(dispersion=1000, recent_hours=72, max_stale_hours=6, margin=0.03, uncertainty=0.005,
                min_net_edge=0.01, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    assert [p.outcome for p in _s(CompteurTweets, **base).propose([m], books, _state(tmp_path), LIMITS, "b1").proposals] == ["Yes"]
    # NON seulement : le OUI n'est plus envisagé, donc rien à acheter ici
    assert _s(CompteurTweets, only_no=1, **base).propose([m], books, _state(tmp_path, "b"), LIMITS, "b1").proposals == []
    # NYC Mayor écarté : abstention nommée, même avec l'affaire du OUI
    out = _s(CompteurTweets, skip_nyc=1, **base).propose([m], books, _state(tmp_path, "c"), LIMITS, "b1")
    assert out.proposals == [] and any("NYC Mayor" in a for a in out.abstentions)
    m.tweets["compte"] = "tedcruz"  # un autre compte reste joué
    assert [p.outcome for p in _s(CompteurTweets, skip_nyc=1, **base).propose([m], books, _state(tmp_path, "d"), LIMITS, "b1").proposals] == ["Yes"]


def test_reference_history_keeps_hourly_price_pairs(tmp_path):
    """21/10/2026 : photo horaire des références rattachées avec le prix Polymarket du même instant,
    pour tester plus tard « Polymarket contre Kalshi / Pinnacle » sans clé d'API."""
    from datetime import datetime, timedelta, timezone
    from types import SimpleNamespace
    from decimal import Decimal
    from polymarket_agent import references
    from polymarket_agent.persistence import Database
    db = Database(tmp_path / "x.sqlite")
    now = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
    m = SimpleNamespace(market_id="m1", outcome_prices=[Decimal("0.42"), Decimal("0.58")], best_bid=Decimal("0.41"),
                        best_ask=Decimal("0.43"), references={"kalshi": {"p": 0.47, "titre": "x"}}, tweets={"compte": "a"})
    bare = SimpleNamespace(market_id="m2", outcome_prices=[], best_bid=None, best_ask=None, references={}, tweets=None)
    assert references.record_history([m, bare], db, now, 60) == 2
    assert references.record_history([m], db, now + timedelta(minutes=30), 60) == 0  # trop tôt
    assert references.record_history([m], db, now + timedelta(hours=1), 60, keep_days=0.01) == 2
    rows = db.conn.execute("SELECT source, p_ref, prix_oui, achat, vente FROM historique_references ORDER BY source").fetchall()
    assert [tuple(r) for r in rows] == [("kalshi", 0.47, 0.42, 0.41, 0.43), ("tweets", None, 0.42, 0.41, 0.43)]
    db.close()


def test_tweet_strategy_min_period_days_skips_two_day_markets(tmp_path):
    """23/10/2026 : 19 achats sur 81 portaient sur des marchés de 2 jours, jamais testés sur le passé."""
    m = parse_market(raw_market("t", yes_token="tY", no_token="tN", groupItemTitle="200-219",
                                end=NOW + timedelta(hours=24)))
    m.tweets = {"compte": "tedcruz", "debut": (NOW - timedelta(hours=24)).isoformat(), "fin": (NOW + timedelta(hours=24)).isoformat(),
                "total": 180, "heures": [1] * 72, "vu_le": NOW.isoformat()}
    books = {"tY": make_book("tY", bids=(("0.20", "1000"),), asks=(("0.21", "1000"),)),
             "tN": make_book("tN", bids=(("0.79", "1000"),), asks=(("0.80", "1000"),))}
    base = dict(dispersion=1000, recent_hours=72, max_stale_hours=6, margin=0.03, uncertainty=0.005,
                min_net_edge=0.01, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    out = _s(CompteurTweets, min_period_days=5, **base).propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert out.proposals == [] and "période plus courte que celles du test sur le passé" in out.abstentions
    assert _s(CompteurTweets, **base).propose([m], books, _state(tmp_path, "b"), LIMITS, "b1").proposals  # sans le réglage : joué
    m.tweets["debut"] = (NOW - timedelta(days=6)).isoformat()  # marché d'une semaine : joué
    assert _s(CompteurTweets, min_period_days=5, **base).propose([m], books, _state(tmp_path, "c"), LIMITS, "b1").proposals
