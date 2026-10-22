"""Stratégie de référence naïve et chargement des paramètres bornés."""

from __future__ import annotations

from decimal import Decimal

import pytest

from conftest import NOW, ROOT, make_book, raw_market
from polymarket_agent.safety_controller import evaluate
from polymarket_agent.main import market_context
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategy_engine import (NaiveFavorite, StrategyConfigError, load_params,
                                              load_strategies, make_op_id)

D = Decimal


def strategy(**overrides):
    params = {"min_ask": D("0.80"), "max_ask": D("0.95"), "bias": D("0.05"),
              "uncertainty": D("0.015"), "min_net_edge": D("0.02"), "max_extra_ticks": D("2"),
              "max_proposals_per_cycle": D("3")}
    params.update(overrides)
    return NaiveFavorite("1.0.0", "2026-10-14", params)


def test_repository_config_loads():
    loaded = load_strategies(ROOT / "config" / "strategies.yaml")
    assert sorted(s.strategy_id for s in loaded) == sorted([
        "calibration_patiente", "contrer_crypto", "contrer_crypto_patiente", "cross_market",
        "crypto_threshold", "crypto_threshold_patiente",
        "favori_politique", "favori_politique_patiente", "favori_politique_quasi_certain", "favori_politique_nuit", "outsider_sport_apres_midi", "loterie_meteo",
        "market_maker", "market_maker_serre",
        "naive_favorite", "naive_favorite_large", "naive_favorite_sans_fin",
        "nf_sport_prix_haut", "nf_sport_sans_fin",
        "nm_demi_mise", "nf_court", "nf_court_prix_haut", "nf_sport_6_24h", "nf_sport_patiente_6_24h", "nf_sport_patiente_72_168h", "nf_court_football", "nf_tennis_12_18h", "nf_sport_patiente_72_168h_12_18h", "nf_sport_patiente_matin", "crypto_threshold_non", "nf_moyen", "nf_oui", "nf_sport", "nf_sport_patiente", "nf_sport_oui", "nf_sport_non", "nm_court", "nm_crypto", "nm_hors_crypto", "nm_long", "nm_prix_bas",
        "nm_prix_haut", "outsider_sport_patiente", "suivre_politique",
        "parking_politique", "nf_sport_patiente_tennis", "nf_tennis_prix_bas", "nf_tennis_prix_bas_vainqueur", "nf_tennis_prix_bas_800_850", "statu_quo_ia", "nf_tennis_debut_match",
        "crypto_threshold_prix_bas", "crypto_threshold_24_72h", "nf_sport_patiente_prix_850_875",
        # Vingt nouvelles pistes (20/10/2026), lot A.
        "decroissance_temps", "echelle_dates", "coherence_match", "implication_politique", "paire_oui_non",
        "outsiders_surcotes", "marche_neuf", "apres_echeance", "marches_jumeaux",
        # Lot B.
        "kalshi_reference", "predictit_reference", "manifold_reference", "futurs_bookmakers",
        "football_trois_issues", "compteur_tweets", "cotes_tennis",
        # Lot C.
        "mots_prononces", "mots_nouveaux", "fatigue_nhl",
        # Achat échelonné et outsiders (20/10/2026).
        "nf_sport_patiente_sans_itf", "outsider_itf",
            # Filles 80/20 du 21/10/2026.
            "nf_court_soir", "nf_court_football_soir", "nf_sport_18_24h", "nf_sport_925_950", "nf_sport_18_24h_vainqueur", "nf_sport_prix_haut_3_6h", "nf_sport_patiente_12_18h",
            "compteur_tweets_non", "mots_prononces_nfl",
            "mots_prononces_patiente", "compteur_tweets_non_patiente",
            "nf_sport_patiente_tennis_875_900", "nf_sport_patiente_72_168h_850_875", "nf_sport_football", "cpi_tranches", "nf_sport_vainqueur", "nf_sport_patiente_tennis_850_875", "jobs_favori_non", "nf_tennis_vainqueur", "nf_tennis_12_18h_vainqueur"])
    assert all(s.params["kelly_fraction"] == 1 for s in loaded
               if "kelly_fraction" in s.params and not s.strategy_id.startswith(("meteo_prevision", "crypto_threshold_patiente", "naive_favorite_patiente",
                                                                   "favori_politique", "contrer_crypto", "suivre_politique",
                                                                   "loterie_meteo", "naive_favorite_large", "nf_demi_mise",
                                                                   "nf_quart_mise", "nm_demi_mise", "nf_sport_patiente_demi_mise", "cotes_bookmakers",
                                                                   "parking_politique", "statu_quo_ia", "decroissance_temps", "outsiders_surcotes",
                                                                   "marche_neuf", "apres_echeance", "choc_sans_nouvelle", "kalshi_reference",
                                                                   "predictit_reference", "manifold_reference", "futurs_bookmakers",
                                                                   "football_trois_issues", "compteur_tweets", "cotes_tennis",
                                                                   "mots_prononces", "mots_nouveaux", "fatigue_nhl",
                                                                   "outsider_itf", "cpi_tranches", "jobs_favori_non")))


def test_param_outside_bounds_is_refused():
    with pytest.raises(StrategyConfigError):
        load_params({"bias": {"value": 0.5, "min": 0, "max": 0.06}})


def test_proposes_buy_on_favorite_and_controller_accepts(ledger, limits):
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    out = strategy().propose([market], {"tokA": book}, ledger.state, limits, "B1")
    assert len(out.proposals) == 1
    p = out.proposals[0]
    assert p.side == "BUY" and p.token_id == "tokA" and p.outcome == "Yes"
    assert p.prob_low < p.est_probability < p.prob_high
    assert p.net_edge >= D("0.02")  # le min_net_edge de la stratégie
    verdict = evaluate(p, ledger.state, market_context(market, book, "tokA"), limits, NOW)
    assert verdict.accepted, verdict.reasons


def test_picks_no_token_when_no_is_favorite(ledger, limits):
    market = parse_market(raw_market(yes_price="0.1", best_bid=0.09, best_ask=0.10))
    book = make_book("tokB", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    out = strategy().propose([market], {"tokB": book}, ledger.state, limits, "B1")
    assert out.proposals[0].token_id == "tokB" and out.proposals[0].outcome == "No"


def test_abstains_without_data_or_edge(ledger, limits):
    market = parse_market(raw_market())
    s = strategy()
    assert s.propose([market], {}, ledger.state, limits, "B1").abstentions == {"carnet indisponible": 1}
    wide = make_book("tokA", bids=(("0.80", "500"),), asks=(("0.90", "300"),))  # milieu 0,85
    assert s.propose([market], {"tokA": wide}, ledger.state, limits, "B1").abstentions == {
        "avantage net insuffisant": 1}
    cheap = make_book("tokA", bids=(("0.50", "500"),), asks=(("0.51", "300"),))
    assert not s.propose([market], {"tokA": cheap}, ledger.state, limits, "B1").proposals


def test_strategy_is_free_to_lower_its_own_edge_threshold(ledger, limits):
    """Liberté totale : plus de plancher imposé, la stratégie choisit son seuil."""
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    strict = strategy(min_net_edge=D("0.02"), bias=D("0.03"))
    free = strategy(min_net_edge=D("0"), bias=D("0.03"))
    assert not strict.propose([market], {"tokA": book}, ledger.state, limits, "B1").proposals
    assert free.propose([market], {"tokA": book}, ledger.state, limits, "B1").proposals


def test_op_id_is_deterministic():
    assert make_op_id("B1", "s", "1", "t", "BUY") == make_op_id("B1", "s", "1", "t", "BUY")
    assert make_op_id("B1", "s", "1", "t", "BUY") != make_op_id("B2", "s", "1", "t", "BUY")


def test_regression_default_config_can_trade_a_tight_favorite(ledger, limits):
    """Défaut du 14/10/2026 : avec biais 0,04 et incertitude 0,02, la borne basse
    (milieu + 0,02) ne pouvait jamais dépasser prix + frais + 0,02 : aucune position possible."""
    s = strategy()  # paramètres de config/strategies.yaml au 14/10/2026 (biais 0,05, incertitude 0,015)
    market = parse_market(raw_market())
    book = make_book("tokA", bids=(("0.89", "500"),), asks=(("0.90", "300"),))
    assert len(s.propose([market], {"tokA": book}, ledger.state, limits, "B1").proposals) == 1


# --------------------------------------------------------------------------- calibration


def calibrated(tmp_path, delta, n_events=500, key="sports|13-72h|0.85-0.90", **params):
    from polymarket_agent import calibration
    from polymarket_agent.calibration import Cell
    from polymarket_agent.strategy_engine import CalibratedStrategy
    table = {key: Cell(key, 2000, n_events, 0.875, 0.875 + delta, delta, delta - 0.01, delta + 0.01, delta)}
    calibration.save(table, tmp_path / "table.json", {"version": "test"})
    base = {"min_events": D("150"), "min_net_edge": D("0.02"), "max_extra_ticks": D("2"),
            "max_proposals_per_cycle": D("3")}
    base.update(params)
    return CalibratedStrategy("1.0.0", "2026-10-14", base, tmp_path / "table.json")


def sports_market(**kw):
    raw = raw_market(feeType="sports_fees_v3",
                     schedule={"exponent": 1, "rate": 0.05, "takerOnly": True}, **kw)
    return parse_market(raw)


def books_for(yes_bid="0.87", yes_ask="0.88"):
    no_bid, no_ask = str(D(1) - D(yes_ask)), str(D(1) - D(yes_bid))
    return {"tokA": make_book("tokA", bids=((yes_bid, "500"),), asks=((yes_ask, "500"),)),
            "tokB": make_book("tokB", bids=((no_bid, "500"),), asks=((no_ask, "500"),))}


def test_calibrated_buys_underpriced_favorite(tmp_path, ledger, limits):
    s = calibrated(tmp_path, delta=0.06)  # le favori à 0,875 gagne en réalité 93,5 %
    out = s.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert len(out.proposals) == 1
    p = out.proposals[0]
    assert p.token_id == "tokA" and p.outcome == "Yes"
    assert p.prob_low == D("0.925")
    market = sports_market()
    assert evaluate(p, ledger.state, market_context(market, books_for()["tokA"], "tokA"),
                    limits, NOW).accepted


def test_calibrated_buys_underdog_when_favorite_is_overpriced(tmp_path, ledger, limits):
    s = calibrated(tmp_path, delta=-0.07)  # le favori à 0,875 ne gagne que 80,5 %
    out = s.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert out.proposals[0].token_id == "tokB" and out.proposals[0].outcome == "No"


def test_calibrated_abstains_without_measured_edge(tmp_path, ledger, limits):
    assert not calibrated(tmp_path, delta=0.0).propose(
        [sports_market()], books_for(), ledger.state, limits, "B1").proposals
    small = calibrated(tmp_path, delta=0.06, n_events=40)  # trop peu d'événements
    out = small.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert out.abstentions == {"case de calibration absente ou trop petite": 1}
    # Horizon hors table (marché « crypto » : aucune case) → abstention.
    crypto = parse_market(raw_market(feeType="crypto_fees_v2",
                                     schedule={"exponent": 1, "rate": 0.07, "takerOnly": True}))
    assert not calibrated(tmp_path, delta=0.06).propose([crypto], books_for(), ledger.state,
                                                        limits, "B1").proposals


def test_calibrated_respects_dataset_volume_universe(tmp_path, ledger, limits):
    s = calibrated(tmp_path, delta=0.06, min_volume=D("200000"))
    out = s.propose([sports_market()], books_for(), ledger.state, limits, "B1")
    assert out.abstentions == {"volume cumulé sous le seuil de l'historique": 1}


# --------------------------------------------------------------------------- reversion


def reversion(tmp_path, delta_drop=0.15):
    from polymarket_agent import calibration
    from polymarket_agent.calibration import Cell
    from polymarket_agent.strategy_engine import ReversionStrategy
    table = {"baisse": Cell("baisse", 5000, 1800, 0.6, 0.6 + delta_drop, delta_drop,
                            delta_drop - 0.03, delta_drop + 0.01, delta_drop - 0.01),
             "hausse": Cell("hausse", 20000, 4000, 0.84, 0.83, -0.013, -0.018, -0.008, -0.013)}
    calibration.save(table, tmp_path / "rev.json", {"version": "test"})
    params = {"min_move": D("0.10"), "min_changes_24h": D("4"), "min_events": D("150"),
              "min_net_edge": D("0.02"), "max_extra_ticks": D("2"), "max_proposals_per_cycle": D("3")}
    return ReversionStrategy("1.0.0", "2026-10-14", params, tmp_path / "rev.json")


def moved_market(before, changes=10):
    m = sports_market()
    m.yes_price_6h_ago, m.changes_24h = before, changes
    return m


def test_reversion_buys_favorite_after_sharp_drop(tmp_path, ledger, limits):
    out = reversion(tmp_path).propose([moved_market(0.75)], books_for("0.59", "0.60"),
                                      ledger.state, limits, "B1")
    assert len(out.proposals) == 1
    p = out.proposals[0]
    assert p.token_id == "tokA" and p.prob_low == D("0.7150")
    assert "reversion:baisse" in p.sources


def test_reversion_abstains_without_move_history_or_activity(tmp_path, ledger, limits):
    s = reversion(tmp_path)
    books = books_for("0.59", "0.60")
    assert s.propose([moved_market(0.62)], books, ledger.state, limits, "B1").abstentions == {
        "pas de mouvement brusque": 1}
    assert s.propose([moved_market(None)], books, ledger.state, limits, "B1").abstentions == {
        "historique de prix indisponible": 1}
    assert s.propose([moved_market(0.75, changes=2)], books, ledger.state, limits, "B1").abstentions == {
        "marché trop peu actif sur 24 h": 1}


def test_reversion_uses_real_book_not_history(tmp_path, ledger, limits):
    """Le piège du backtest : un prix historique bas sans vendeur réel à ce prix.
    En réel, l'ask du carnet est haut (0,74) : aucun avantage, aucune proposition."""
    out = reversion(tmp_path).propose([moved_market(0.75)], books_for("0.46", "0.74"),
                                      ledger.state, limits, "B1")
    assert not out.proposals


def test_parking_counts_the_holding_reward_only_on_eligible_markets(tmp_path):
    """19/10/2026 : sur un marché à récompense de détention (4 %/an), un favori à 0,97 qui se règle
    dans un an est un bon placement (≈ +4 % de récompense) ; sans la récompense, pas d'avantage ;
    marché non éligible : rien."""
    from datetime import timedelta
    from conftest import KEY, NOW, make_book, raw_market
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.safety_controller import RiskLimits
    from polymarket_agent.sources.polymarket_gamma import parse_market
    limits = RiskLimits.from_file(ROOT / "config" / "risk_limits.yaml")
    state = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW).state
    park = strategy(min_ask=D("0.93"), max_ask=D("0.99"), bias=D("0"), shrink=D("0.5"), uncertainty=D("0.01"),
                    min_net_edge=D("0.01"), max_extra_ticks=D("1"), kelly_fraction=D("0.15"), holding_only=D("1"),
                    holding_rate=D("0.04"), holding_years_max=D("1"))
    books = {"tokA": make_book("tokA", bids=(("0.96", "5000"),), asks=(("0.97", "5000"),)),
             "tokB": make_book("tokB", bids=(("0.03", "5000"),), asks=(("0.04", "5000"),))}
    raw = raw_market(yes_price="0.965", best_bid=0.96, best_ask=0.97, end=NOW + timedelta(days=365),
                     holdingRewardsEnabled=True)
    out = park.propose([parse_market(raw)], books, state, limits, "b1")
    assert len(out.proposals) == 1 and out.proposals[0].prob_low < out.proposals[0].est_probability < 1
    assert out.proposals[0].net_edge > D("0.03")  # la récompense compte dans l'avantage déclaré
    raw["holdingRewardsEnabled"] = False
    out = park.propose([parse_market(raw)], books, state, limits, "b1")
    assert not out.proposals and "pas de récompense de détention" in out.abstentions
    plain = strategy(min_ask=D("0.93"), max_ask=D("0.99"), bias=D("0"), shrink=D("0.5"), uncertainty=D("0.01"),
                     min_net_edge=D("0.01"), max_extra_ticks=D("1"))
    raw["holdingRewardsEnabled"] = True
    assert not plain.propose([parse_market(raw)], books, state, limits, "b1").proposals  # sans la récompense


def test_holding_reward_estimate_is_kept_outside_capital(tmp_path):
    from datetime import timedelta
    from types import SimpleNamespace
    from conftest import NOW
    from polymarket_agent import holding_rewards
    from polymarket_agent.persistence import Database
    db = Database(tmp_path / "db.sqlite")
    pos = {"t1": SimpleNamespace(market_id="m1", shares=D("1000")), "t2": SimpleNamespace(market_id="m2", shares=D("10"))}
    markets = {"m1": SimpleNamespace(holding_rewards=True), "m2": SimpleNamespace(holding_rewards=False)}
    amounts = holding_rewards.accrue(pos, {"t1": D("0.97"), "t2": D("0.5")}, markets, 0.04, 60 * 24 * 365)
    assert list(amounts) == ["m1"] and abs(amounts["m1"][1] - 970 * 0.04) < 1e-9  # un an à 4 % sur 970
    assert holding_rewards.accrue(pos, {}, markets, 0.04, 5) == {}  # sans prix de revente : rien
    holding_rewards.record(db, "c1", NOW, "fantome:parking_v1", {"m1": (970.0, 0.5)})
    assert holding_rewards.ranking_bonus(db, {"parking_v1": NOW - timedelta(days=1)}, 0.5) == {"parking_v1": 0.25}
    assert holding_rewards.ranking_bonus(db, {"parking_v1": NOW + timedelta(days=1)}, 0.5) == {}
    db.close()
