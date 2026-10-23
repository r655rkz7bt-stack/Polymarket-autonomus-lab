"""Vingt nouvelles pistes (20/10/2026), lot A : dix stratégies sur les seules données de Polymarket."""

from __future__ import annotations

import json
from datetime import timedelta
from decimal import Decimal as D

from conftest import KEY, NOW, ROOT, make_book, raw_market
from polymarket_agent.ledger import Ledger
from polymarket_agent.safety_controller import RiskLimits
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import (ApresEcheance, ChocSansNouvelle, CoherenceMatch, DecroissanceTemps,
                                            EchelleDates, ImplicationPolitique, MarcheNeuf, MarchesJumeaux,
                                            OutsidersSurcotes, PaireOuiNon, CpiTranches, JobsFavoriNon)

LIMITS = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
_N = [0]


def _state(tmp_path):
    _N[0] += 1
    return Ledger.create(tmp_path / f"l{_N[0]}.jsonl", KEY, tmp_path / f"l{_N[0]}.lock", "1000", now=NOW).state


def _s(cls, **params):
    return cls("1.0.0", "2026-10-20", {k: D(str(v)) for k, v in params.items()})


def _m(mid, yes="Y", no="N", **kw):
    return parse_market(raw_market(mid, yes_token=f"{mid}{yes}", no_token=f"{mid}{no}", **kw))


def _books(*pairs):
    """pairs : (token, meilleur acheteur, meilleur vendeur)."""
    return {t: make_book(t, bids=((str(b), "1000"),), asks=((str(a), "1000"),)) for t, b, a in pairs}


ARB = {"min_net_edge": 0.005, "stake_fraction": 0.1, "max_proposals_per_cycle": 2}


def test_time_decay_buys_no_when_yes_has_not_melted(tmp_path):
    s = _s(DecroissanceTemps, yes_min=0.03, yes_max=0.35, min_hours=12, max_hours=720, min_gap=0.01, max_spike=2,
           uncertainty=0.005, min_net_edge=0.003, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    m = _m("d", question="Will X resign by October 21?", end=NOW + timedelta(hours=24), yes_price="0.10")
    m.yes_price_6h_ago = 0.10  # même prix qu'il y a 6 h alors que 20 % du temps restant est passé
    books = _books(("dY", "0.09", "0.10"), ("dN", "0.90", "0.905"))
    out = s.propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert len(out.proposals) == 1 and out.proposals[0].outcome == "No"
    m.yes_price_6h_ago = 0.20  # le OUI a déjà fondu de 0,20 à 0,10 : rien
    assert not s.propose([m], books, _state(tmp_path), LIMITS, "b1").proposals
    other = _m("o", question="Will X resign?", end=NOW + timedelta(hours=24))  # pas d'échéance dans le libellé
    other.yes_price_6h_ago = 0.1
    assert not s.propose([other], _books(("oY", "0.09", "0.10"), ("oN", "0.9", "0.905")), _state(tmp_path), LIMITS, "b1").proposals


def test_date_ladder_coherence_and_twins_are_arbitrages(tmp_path):
    near = _m("n", question="Will X happen by June 30?", end=NOW + timedelta(days=10), event_id="e1")
    far = _m("f", question="Will X happen by December 31?", end=NOW + timedelta(days=100), event_id="e1")
    # OUI(décembre) 0,30 + NON(juin) 0,60 = 0,90 < 1 : la date proche vaut plus que la lointaine.
    books = _books(("fY", "0.29", "0.30"), ("fN", "0.69", "0.70"), ("nY", "0.39", "0.40"), ("nN", "0.59", "0.60"))
    out = _s(EchelleDates, **ARB).propose([near, far], books, _state(tmp_path), LIMITS, "b1")
    assert sorted((p.market_id, p.outcome) for p in out.proposals) == [("f", "Yes"), ("n", "No")]
    fair = _books(("fY", "0.44", "0.45"), ("fN", "0.55", "0.56"), ("nY", "0.29", "0.30"), ("nN", "0.69", "0.70"))
    assert not _s(EchelleDates, **ARB).propose([near, far], fair, _state(tmp_path), LIMITS, "b1").proposals
    # Jumeaux : même question, deux marchés.
    a = _m("a", question="Will X happen by June 30?", end=NOW + timedelta(days=10), event_id="e1")
    b = _m("b", question="Will X happen by June 30?", end=NOW + timedelta(days=10), event_id="e2")
    tw = _books(("aY", "0.29", "0.30"), ("aN", "0.69", "0.70"), ("bY", "0.39", "0.40"), ("bN", "0.59", "0.60"))
    out = _s(MarchesJumeaux, **ARB).propose([a, b], tw, _state(tmp_path), LIMITS, "b1")
    assert sorted((p.market_id, p.outcome) for p in out.proposals) == [("a", "Yes"), ("b", "No")]


def test_spread_implies_winning_and_president_implies_nominee(tmp_path):
    teams = json.dumps(["Titans", "Colts"])
    win = _m("w", question="Titans vs. Colts", outcomes=teams, event_id="g", sportsMarketType="moneyline")
    spread = _m("s", question="Spread: Titans (-3.5)", outcomes=teams, event_id="g", sportsMarketType="spreads")
    # Victoire des Titans 0,55 + Colts au handicap 0,40 = 0,95 < 1.
    books = _books(("wY", "0.54", "0.55"), ("wN", "0.44", "0.45"), ("sY", "0.59", "0.60"), ("sN", "0.39", "0.40"))
    out = _s(CoherenceMatch, **ARB).propose([win, spread], books, _state(tmp_path), LIMITS, "b1")
    assert sorted((p.market_id, p.outcome) for p in out.proposals) == [("s", "Colts"), ("w", "Titans")]
    pres = _m("p", question="Will Gavin Newsom win the 2028 US Presidential Election?", end=NOW + timedelta(days=700))
    nom = _m("q", question="Will Gavin Newsom win the 2028 Democratic presidential nomination?",
             end=NOW + timedelta(days=600))
    books = _books(("pY", "0.29", "0.30"), ("pN", "0.69", "0.70"), ("qY", "0.24", "0.25"), ("qN", "0.74", "0.75"))
    out = _s(ImplicationPolitique, **dict(ARB, min_net_edge=0.01)).propose([pres, nom], books, _state(tmp_path), LIMITS, "b1")
    assert sorted((p.market_id, p.outcome) for p in out.proposals) == [("p", "No"), ("q", "Yes")]


def test_yes_plus_no_below_one_and_overpriced_longshots(tmp_path):
    m = _m("x")
    out = _s(PaireOuiNon, **ARB).propose([m], _books(("xY", "0.47", "0.48"), ("xN", "0.47", "0.48")),
                                         _state(tmp_path), LIMITS, "b1")
    assert sorted(p.outcome for p in out.proposals) == ["No", "Yes"]
    assert not _s(PaireOuiNon, **ARB).propose([m], _books(("xY", "0.49", "0.50"), ("xN", "0.49", "0.51")),
                                              _state(tmp_path), LIMITS, "b1").proposals
    s = _s(OutsidersSurcotes, min_outcomes=5, min_overround=0.03, yes_min=0.02, yes_max=0.15, longshot_factor=0.85,
           uncertainty=0.002, min_net_edge=0.003, max_extra_ticks=1, max_proposals_per_cycle=3, kelly_fraction=0.25)
    mids = [0.40, 0.30, 0.20, 0.12, 0.08]  # somme 1,10
    ms = [_m(f"c{i}", negRisk=True, event_id="champ") for i in range(5)]
    books = {}
    for i, mid in enumerate(mids):
        books.update(_books((f"c{i}Y", f"{mid - 0.005:.3f}", f"{mid + 0.005:.3f}"),
                            (f"c{i}N", f"{1 - mid - 0.005:.3f}", f"{1 - mid + 0.005:.3f}")))
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id for p in out.proposals} == {"c3", "c4"} and all(p.outcome == "No" for p in out.proposals)


def test_young_markets_ended_markets_and_shocks_without_news(tmp_path):
    young = _m("y", createdAt=(NOW - timedelta(hours=3)).isoformat())
    old = _m("o", createdAt=(NOW - timedelta(days=10)).isoformat())
    s = _s(MarcheNeuf, max_age_hours=24, fav_min=0.6, fav_max=0.88, extremize=1.3, uncertainty=0.005, min_net_edge=0.01,
           max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    books = _books(("yY", "0.69", "0.70"), ("yN", "0.30", "0.31"), ("oY", "0.69", "0.70"), ("oN", "0.30", "0.31"))
    out = s.propose([young, old], books, _state(tmp_path), LIMITS, "b1")
    assert [(p.market_id, p.outcome) for p in out.proposals] == [("y", "Yes")]
    ended = _m("e", end=NOW - timedelta(hours=3))
    ended.ended = True
    a = _s(ApresEcheance, fav_min=0.94, fav_max=0.985, est=0.99, uncertainty=0.003, min_net_edge=0.002,
           max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    assert a.wants_ended
    eb = _books(("eY", "0.955", "0.96"), ("eN", "0.04", "0.045"))
    assert [p.outcome for p in a.propose([ended], eb, _state(tmp_path), LIMITS, "b1").proposals] == ["Yes"]
    ended.uma_statuses = ("disputed",)
    assert not a.propose([ended], eb, _state(tmp_path), LIMITS, "b1").proposals
    c = _s(ChocSansNouvelle, min_move=0.08, reversion=0.5, max_mentions=3, uncertainty=0.005, min_net_edge=0.01,
           take_profit=0.03, stop_loss=0.05, max_hold_hours=24, max_extra_ticks=1, max_proposals_per_cycle=2,
           kelly_fraction=0.25)
    jump = _m("j")
    jump.yes_price_1h_ago = 0.40  # bond à 0,55 sans nouvelle → retour partiel vers 0,475 : le NON
    jb = _books(("jY", "0.545", "0.555"), ("jN", "0.445", "0.455"))
    assert [p.outcome for p in c.propose([jump], jb, _state(tmp_path), LIMITS, "b1").proposals] == ["No"]
    from polymarket_agent.social_intelligence import MarketIntel
    jump.intel = MarketIntel("j", mentions_24h=12, spike=3.0, independent_sources=4, stance=0.5)
    assert not c.propose([jump], jb, _state(tmp_path), LIMITS, "b1").proposals  # le mouvement a une nouvelle


def test_new_gamma_fields_and_ended_markets_stay_away_from_other_strategies():
    m = parse_market(raw_market("g", groupItemTitle="200-219", createdAt="2026-10-14T10:00:00Z", negRiskOther=True,
                                umaResolutionStatuses='["proposed"]', events=[{"id": "e", "slug": "elon-tweets"}]))
    assert m.group_title == "200-219" and m.created_at.year == 2026 and m.neg_risk_other
    assert m.uma_statuses == ("proposed",) and m.event_slug == "elon-tweets" and not m.ended
    from polymarket_agent.market_scanner import scan

    class Gamma:
        def __init__(self):
            self.calls = 0

        def list_markets(self, **kw):
            self.calls += 1
            return [raw_market("vivant")] if self.calls == 1 else [raw_market("echu", end=NOW - timedelta(hours=5))]
    cfg = {"page_size": 100, "max_pages": 1, "min_horizon_minutes": 30, "max_horizon_hours": 72, "min_liquidity": 1000,
           "min_volume_24h": 1000, "max_spread": 0.05, "watchlist_size": 30, "ended_pages": 1, "ended_min_hours": 1,
           "ended_max_hours": 72}
    r = scan(Gamma(), NOW, cfg)
    ended = next(x for x in r.markets if x.market_id == "echu")
    assert ended.ended and ended.eligible and [x.market_id for x in r.watchlist] == ["vivant"]


def test_all_twenty_strategies_lot_a_load_from_the_repository_config():
    from polymarket_agent.strategy_engine import load_strategies
    ids = {s.strategy_id for s in load_strategies(ROOT / "config" / "strategies.yaml")}
    assert {"decroissance_temps", "echelle_dates", "coherence_match", "implication_politique", "paire_oui_non",
            "outsiders_surcotes", "marche_neuf", "marches_jumeaux"} <= ids
    assert "choc_sans_nouvelle" not in ids  # éliminée par l'arène, coupée le 20/10/2026 (enabled: false)


def test_cpi_tranches_buys_no_on_unlikely_buckets_only_for_us_cpi_in_window(tmp_path):
    s = _s(CpiTranches, yes_min=0.05, yes_max=0.30, yes_factor=0.6, hours_min=20, hours_max=170, uncertainty=0.02,
           min_net_edge=0.005, max_extra_ticks=1, max_proposals_per_cycle=5, kelly_fraction=0.25)
    cpi = lambda mid, **kw: _m(mid, events=[{"id": "cpi", "title": "September Inflation US - Monthly"}], **kw)
    ms = [cpi("a"), cpi("b"), cpi("far", end=NOW + timedelta(hours=300)),
          _m("arg", events=[{"id": "ar", "title": "Argentina Monthly Inflation - September"}]),
          _m("core", events=[{"id": "co", "title": "Core CPI MoM - September 2026"}])]
    books = {}
    for mid, yes in (("a", 0.15), ("b", 0.55), ("far", 0.15), ("arg", 0.15), ("core", 0.10)):
        books.update(_books((f"{mid}Y", f"{yes - 0.005:.3f}", f"{yes + 0.005:.3f}"),
                            (f"{mid}N", f"{1 - yes - 0.005:.3f}", f"{1 - yes + 0.005:.3f}")))
    assert {m.market_id for m in s.candidates(ms)} == {"a", "b", "far", "core"}
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert {p.market_id for p in out.proposals} == {"a", "core"} and all(p.outcome == "No" for p in out.proposals)


def test_jobs_favori_non_buys_no_on_the_favorite_bucket_only_inside_window_and_price_band(tmp_path):
    s = _s(JobsFavoriNon, yes_min=0.25, yes_max=0.70, yes_factor=0.6, hours_min=4, hours_max=72, min_buckets=4, uncertainty=0.03,
           min_net_edge=0.005, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    ev = [{"id": "jobs", "title": "How many jobs added in October?"}]
    ms = [_m(f"j{i}", events=ev, end=NOW + timedelta(hours=30)) for i in range(5)]
    ms += [_m(f"o{i}", events=[{"id": "other", "title": "How many jobs added in September?"}], end=NOW + timedelta(hours=30)) for i in range(5)]
    ms += [_m("u", events=[{"id": "u", "title": "October Unemployment Rate"}], end=NOW + timedelta(hours=30))]
    books = {}
    for i, yes in enumerate((0.05, 0.15, 0.40, 0.25, 0.15)):  # favorite : j2 à 0,40
        books.update(_books((f"j{i}Y", f"{yes - 0.005:.3f}", f"{yes + 0.005:.3f}"), (f"j{i}N", f"{1 - yes - 0.005:.3f}", f"{1 - yes + 0.005:.3f}")))
    for i, yes in enumerate((0.02, 0.10, 0.15, 0.12, 0.08)):  # favorite à 0,15 : sous la bande, rien
        books.update(_books((f"o{i}Y", f"{yes - 0.005:.3f}", f"{yes + 0.005:.3f}"), (f"o{i}N", f"{1 - yes - 0.005:.3f}", f"{1 - yes + 0.005:.3f}")))
    books.update(_books(("uY", "0.395", "0.405"), ("uN", "0.595", "0.605")))
    assert {m.market_id for m in s.candidates(ms)} == {f"j{i}" for i in range(5)} | {f"o{i}" for i in range(5)}
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert [(p.market_id, p.outcome) for p in out.proposals] == [("j2", "No")]
    late = _s(JobsFavoriNon, yes_min=0.25, yes_max=0.70, yes_factor=0.6, hours_min=40, hours_max=72, min_buckets=4, uncertainty=0.03,
              min_net_edge=0.005, max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    assert not late.propose(ms, books, _state(tmp_path), LIMITS, "b1").proposals  # à 30 h : hors de la fenêtre 40-72 h
    few = [m for m in ms if m.market_id in ("j0", "j2")]
    assert not s.propose(few, books, _state(tmp_path), LIMITS, "b1").proposals  # 2 tranches suivies : pas de favori fiable


def test_arbitrages_say_why_they_stay_silent(tmp_path):
    """« Réveiller les muettes » (21/10/2026) : un arbitrage qui n'achète rien dit pourquoi (aucune
    paire parmi les marchés vus, ou paire cohérente sans écart après frais)."""
    near = _m("n", question="Will X happen by June 30?", end=NOW + timedelta(days=10), event_id="e1")
    far = _m("f", question="Will X happen by December 31?", end=NOW + timedelta(days=100), event_id="e1")
    alone = _s(EchelleDates, **ARB).propose([near], _books(("nY", "0.39", "0.40"), ("nN", "0.59", "0.60")),
                                           _state(tmp_path), LIMITS, "b1")
    assert alone.abstentions == {"aucune paire complète parmi les marchés vus": 1}
    fair = _books(("fY", "0.44", "0.45"), ("fN", "0.55", "0.56"), ("nY", "0.29", "0.30"), ("nN", "0.69", "0.70"))
    out = _s(EchelleDates, **ARB).propose([near, far], fair, _state(tmp_path), LIMITS, "b1")
    assert not out.proposals and out.abstentions == {"paire cohérente : aucun écart après frais": 1}
    empty = _s(MarchesJumeaux, **ARB).propose([near, far], fair, _state(tmp_path), LIMITS, "b1")
    assert empty.abstentions == {"aucune paire complète parmi les marchés vus": 1}
    no_ask = _s(EchelleDates, **ARB).propose([near, far], _books(("fY", "0.44", "0.45")),  # NON(juin) sans carnet
                                            _state(tmp_path), LIMITS, "b1")
    assert no_ask.abstentions == {"une jambe sans vendeur": 1}


def test_volume_surge_follows_or_fades_the_move(tmp_path):
    """Vague de volume (22/10/2026, idée des skills Polymarket de mjunaidca) : volume du jour ≥ 3 fois la
    moyenne de la semaine et prix du OUI +5 points en 24 h → `suivre` achète le OUI, `contrer` le NON."""
    from polymarket_agent.strategies_v3 import VagueVolume
    common = dict(surge_min=3, min_move=0.03, shift=0.03, uncertainty=0.01, min_net_edge=0.005,
                  max_extra_ticks=1, max_proposals_per_cycle=2, kelly_fraction=0.25)
    follow = _s(VagueVolume, direction=1, side_min=0.55, side_max=0.90, **common)
    fade = _s(VagueVolume, direction=-1, side_min=0.10, side_max=0.45, **common)
    old = (NOW - timedelta(days=20)).strftime("%Y-%m-%dT%H:%M:%SZ")
    far = NOW + timedelta(days=30)
    m = _m("v", volume24hr=30000, volume1wk=72000, oneDayPriceChange=0.05, createdAt=old, end=far)  # 30 000 contre 7 000 par jour avant
    assert m.volume_1wk == D("72000") and m.price_change_1d == 0.05
    books = _books(("vY", "0.69", "0.70"), ("vN", "0.30", "0.31"))
    up = follow.propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in up.proposals] == ["Yes"]
    down = fade.propose([m], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in down.proposals] == ["No"]
    calm = _m("c", volume24hr=8000, volume1wk=50000, oneDayPriceChange=0.05, createdAt=old, end=far)  # pas de vague
    still = _m("s", volume24hr=30000, volume1wk=72000, oneDayPriceChange=0.01, createdAt=old, end=far)  # vague sans mouvement
    new = _m("n", volume24hr=30000, volume1wk=30000, oneDayPriceChange=0.05, end=far,  # créé hier : pas de référence
             createdAt=(NOW - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
    soon = _m("t", volume24hr=30000, volume1wk=72000, oneDayPriceChange=0.05, createdAt=old)  # se termine demain
    assert follow.candidates([soon]) == []
    out = follow.propose([new], _books(("nY", "0.69", "0.70"), ("nN", "0.30", "0.31")), _state(tmp_path), LIMITS, "b1")
    assert not out.proposals
    out = follow.propose([calm, still], _books(("cY", "0.69", "0.70"), ("cN", "0.30", "0.31"),
                                               ("sY", "0.69", "0.70"), ("sN", "0.30", "0.31")), _state(tmp_path), LIMITS, "b1")
    assert not out.proposals and out.abstentions == {"vague de volume sans mouvement de prix": 1}


def _esport(mid, start_h, title="Dota 2: 1win vs OG (BO3) - PARI Universe Group A", **kw):
    return _m(mid, yes="O", no="U", question="Games Total: O/U 2.5", outcomes=json.dumps(["Over", "Under"]),
              sportsMarketType="totals", gameStartTime=(NOW + timedelta(hours=start_h)).strftime("%Y-%m-%d %H:%M:%S+00"),
              events=[{"id": f"e{mid}", "title": title}], **kw)


def test_fewer_maps_buys_under_a_few_hours_before_an_esport_series(tmp_path):
    from polymarket_agent.strategies_v3 import MoinsDeCartes
    s = _s(MoinsDeCartes, min_hours=1, max_hours=6, price_min=0.30, price_max=0.70, shift=0.05, uncertainty=0.01,
           min_net_edge=0.01, max_extra_ticks=1, max_proposals_per_cycle=3, kelly_fraction=0.25)
    ok = _esport("a", 3)
    books = _books(("aO", "0.49", "0.50"), ("aU", "0.50", "0.51"))
    out = s.propose([ok], books, _state(tmp_path), LIMITS, "b1")
    assert [p.outcome for p in out.proposals] == ["Under"]
    # Trop tôt (10 h avant), déjà commencé, un BO1, un total de NBA, « Under » hors plage : rien.
    late, started = _esport("b", 10), _esport("c", -0.5)
    bo1 = _esport("d", 3, title="LoL: A vs B (BO1) - Nexus League")
    nba = _m("e", yes="O", no="U", question="Nuggets vs. Thunder: O/U 236.5", outcomes=json.dumps(["Over", "Under"]),
             sportsMarketType="totals", gameStartTime=(NOW + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S+00"))
    dear = _esport("f", 3)
    books.update(_books(*[(f"{x}{y}", "0.49", "0.50") for x in "bcde" for y in "OU"], ("fO", "0.19", "0.20"), ("fU", "0.80", "0.81")))
    out = s.propose([late, started, bo1, nba, dear], books, _state(tmp_path), LIMITS, "b1")
    assert not out.proposals and out.abstentions == {"« Under » hors de la plage de prix": 1}


def test_no_to_far_dramas_buys_no_with_a_small_stake_once_per_event(tmp_path):
    from polymarket_agent.strategies_v3 import NonAuxDrames
    s = _s(NonAuxDrames, min_days=30, max_days=120, yes_min=0.02, yes_max=0.15, min_volume=5000, yes_factor=0.5,
           uncertainty=0.01, stake_fraction=0.02, min_net_edge=0.005, max_extra_ticks=1, max_proposals_per_cycle=2)
    far = NOW + timedelta(days=60)
    war = _m("w", question="Will China invade Taiwan before 2027?", end=far, yes_price="0.08", event_id="ev")
    twin = _m("t", question="Will China blockade Taiwan before 2027?", end=far, yes_price="0.08", event_id="ev")
    books = _books(("wY", "0.07", "0.08"), ("wN", "0.92", "0.93"), ("tY", "0.07", "0.08"), ("tN", "0.92", "0.93"))
    state = _state(tmp_path)
    out = s.propose([war, twin], books, state, LIMITS, "b1")
    assert [p.outcome for p in out.proposals] == ["No"]  # un seul pari par événement
    assert out.proposals[0].shares * out.proposals[0].max_price <= D("20.5")  # 2 % de 1 000
    # Statu quo, échéance trop proche, pas un drame : rien.
    stay = _m("s", question="Will Maduro remain president through 2026?", end=far, yes_price="0.08", event_id="e2")
    soon = _m("o", question="Will Russia invade Finland by November 10?", end=NOW + timedelta(days=10), yes_price="0.08",
              event_id="e3")
    calm = _m("c", question="Will Bitcoin reach $200k before 2027?", end=far, yes_price="0.08", event_id="e4")
    books.update(_books(*[(f"{x}{y}", "0.07", "0.08") for x in "soc" for y in "Y"], *[(f"{x}N", "0.92", "0.93") for x in "soc"]))
    assert not s.propose([stay, soon, calm], books, _state(tmp_path), LIMITS, "b1").proposals


def test_after_deadline_waits_for_the_match_to_end_and_plays_one_leg_per_event(tmp_path):
    """23/10/2026 : Cavaliers-76ers, coup d'envoi 23:00, huit jambes (vainqueur, écarts, total) achetées entre 1 h et 1 h 52 après le début,
    toutes perdues (-474 € sur le fantôme). `endDate` d'un match = le coup d'envoi : « échéance passée » ne veut pas dire « match fini »."""
    a = _s(ApresEcheance, fav_min=0.94, fav_max=0.985, est=0.99, uncertainty=0.003, min_net_edge=0.002, heures_apres_coup_d_envoi_min=3,
           max_extra_ticks=1, max_proposals_per_cycle=3, kelly_fraction=0.25)
    ms = []
    for i in range(3):
        m = _m(f"g{i}", end=NOW - timedelta(hours=1), event_id="nba1", gameStartTime=(NOW - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"))
        m.ended = True
        ms.append(m)
    books = _books(*[(f"g{i}{t}", b, k) for i in range(3) for t, b, k in (("Y", "0.955", "0.96"), ("N", "0.04", "0.045"))])
    assert not a.propose(ms, books, _state(tmp_path), LIMITS, "b1").proposals  # le match est en cours
    for m in ms:
        m.game_start = NOW - timedelta(hours=4)  # fini depuis longtemps
    out = a.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    assert len(out.proposals) == 1  # trois jambes du même match : une seule


def test_detroits_tranches_sells_the_overpriced_bucket_and_buys_the_cheap_one(tmp_path):
    from polymarket_agent.strategies_v3 import DetroitsTranches
    s = _s(DetroitsTranches, min_gap=0.12, uncertainty=0.12, max_stale_hours=12, min_net_edge=0.02, max_extra_ticks=1,
           max_proposals_per_cycle=3, kelly_fraction=0.25)
    fresh = NOW.isoformat()

    def tr(mid, p, yes_mid, vu=fresh):
        m = _m(mid, events=[{"id": "ev9", "title": "Avg. # of ships transiting Bab el-Mandeb Strait end of October?"}])
        m.references = {"detroit": {"p": p, "mu": 26.7, "sd": 3.6, "dernier_jour": "2026-10-18", "vu_le": vu, "titre": "Bab el-Mandeb : test"}}
        return m, _books((f"{mid}Y", f"{yes_mid - 0.01:.3f}", f"{yes_mid + 0.01:.3f}"), (f"{mid}N", f"{1 - yes_mid - 0.01:.3f}", f"{1 - yes_mid + 0.01:.3f}"))
    cases = [tr("c", 0.48, 0.81), tr("b", 0.28, 0.07), tr("d", 0.17, 0.105), tr("old", 0.48, 0.81, vu=(NOW - timedelta(hours=40)).isoformat())]
    ms, books = [c[0] for c in cases], {}
    for _, b in cases:
        books.update(b)
    out = s.propose(ms, books, _state(tmp_path), LIMITS, "b1")
    got = {p.market_id: p.outcome for p in out.proposals}
    assert got == {"c": "No", "b": "Yes"}  # d : écart de 0,065 < 0,12 ; old : relevé périmé
    assert out.abstentions
    assert {m.market_id for m in s.candidates(ms)} == {"c", "b", "d", "old"}
