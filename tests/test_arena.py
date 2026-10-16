"""Arène : cliquet des paliers, champion, élimination hebdomadaire."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from conftest import KEY, NOW, buy
from polymarket_agent.arena import Standing, choose_champion, choose_elimination, run_arena
from polymarket_agent.ledger import InvalidEntry, Ledger

D = Decimal


def _rules():
    import yaml
    from conftest import ROOT
    return yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))


RULES = _rules()


def st(name, trades, growth, days=10, eliminated=False):
    return Standing(name, trades, 1000.0, 1000.0, growth, NOW - timedelta(days=days), eliminated)


def test_champion_needs_enough_trades_and_must_beat_doing_nothing():
    assert choose_champion([st("a", 19, 0.5)], "", 20)[0] == ""          # pas assez d'opérations
    assert choose_champion([st("a", 20, -0.1)], "", 20)[0] == ""         # pire que ne rien faire
    assert choose_champion([st("a", 20, 0.1), st("b", 30, 0.3)], "", 20)[0] == "b"


def test_champion_keeps_title_until_beaten_and_new_champion_gets_time():
    standings = [st("a", 40, 0.2), st("b", 40, 0.15)]
    assert choose_champion(standings, "a", 20)[0] == "a"
    assert choose_champion([st("a", 40, 0.2), st("b", 40, 0.25)], "a", 20)[0] == "b"
    assert choose_champion([st("new", 3, -0.05)], "new", 20)[0] == "new"  # pas encore jugé
    assert choose_champion([st("a", 25, -0.01)], "a", 20)[0] == ""        # déchu
    assert choose_champion([st("a", 25, 0.3, eliminated=True)], "a", 20)[0] == ""


def test_weekly_elimination_of_the_worst_never_the_champion():
    standings = [st("champ", 50, -0.5), st("x", 30, 0.1), st("y", 30, -0.2)]
    assert choose_elimination(standings, "champ", None, NOW, 20, 7, 7).name == "y"
    assert choose_elimination(standings, "champ", NOW - timedelta(days=3), NOW, 20, 7, 7) is None
    young = [st("x", 30, 0.1, days=2), st("y", 30, -0.2, days=2)]
    assert choose_elimination(young, "", None, NOW, 20, 7, 7) is None
    assert choose_elimination([st("x", 30, 0.1)], "", None, NOW, 20, 7, 7) is None


def test_run_arena_writes_signed_promotion(ledger, paths, tmp_path):
    shadow = Ledger.create(tmp_path / "s.jsonl", KEY, tmp_path / "s.lock", "1000", now=NOW)
    for i in range(20):
        buy(shadow, f"b{i}", token=f"t{i}", shares="10", price="0.5", event=f"e{i}")
        shadow.record_settlement(op_id=f"s{i}", token_id=f"t{i}", payout_per_share="1",
                                 resolution="Yes", now=NOW)
    assert run_arena(ledger, {"star_v1": shadow}, RULES, NOW)["champion"] == ""  # moins de 24 h d'ancienneté
    summary = run_arena(ledger, {"star_v1": shadow}, RULES, NOW + timedelta(hours=25))
    assert summary["champion"] == "star_v1" and summary["events"]
    assert summary["allocation"] == {"star_v1": 1.0}
    assert Ledger.open(paths[0], KEY, paths[1]).state.champion == "star_v1"


def test_ratchet_milestones_use_realized_capital_only(ledger, paths):
    assert ledger.state.next_target == D("1500")
    buy(ledger, "b1", token="tA", shares="1000", price="0.5")
    # Gain latent énorme : ne compte pas.
    assert ledger.state.total_estimated({"tA": D("0.99")}) > D("1450")
    assert ledger.record_milestones(NOW) == []
    ledger.record_settlement(op_id="s1", token_id="tA", payout_per_share="1", resolution="Yes", now=NOW)
    assert ledger.state.realized_capital() == D("1500")
    reached = ledger.record_milestones(NOW + timedelta(hours=2))
    assert [m["target"] for m in reached] == ["1500.0"] or [D(m["target"]) for m in reached] == [D("1500")]
    assert ledger.state.next_target == D("2250")
    assert Ledger.open(paths[0], KEY, paths[1]).state.next_target == D("2250")


def test_several_milestones_at_once_and_no_fake_milestone(ledger):
    buy(ledger, "b1", token="tA", shares="1990", price="0.5")
    ledger.record_settlement(op_id="s1", token_id="tA", payout_per_share="1", resolution="Yes", now=NOW)
    # 2 000 + 5 = 2 005 de capital réalisé → paliers 1 500 puis… 2 250 non atteint.
    assert [D(m["target"]) for m in ledger.record_milestones(NOW)] == [D("1500")]
    with pytest.raises(InvalidEntry):
        ledger._append("MILESTONE", {"target": "2250"}, NOW)  # pas atteint : refusé


def test_champion_cannot_be_eliminated(ledger):
    ledger.record_promotion("a_v1", "test", now=NOW)
    with pytest.raises(InvalidEntry):
        ledger.record_elimination("a_v1", "test", now=NOW)
    ledger.record_elimination("b_v1", "test", now=NOW)
    with pytest.raises(InvalidEntry):
        ledger.record_promotion("b_v1", "retour interdit", now=NOW)


def test_brief_lists_innovation_obligations(ledger, tmp_path):
    from polymarket_agent.brief import build_brief, render_brief
    cfg = RULES
    brief = build_brief(ledger, {}, ["a_v1"], cfg, now=NOW + timedelta(days=8))
    text = " ".join(brief["obligations"])
    assert "Ajouter 2 nouvelle(s)" in text and "RADICALEMENT" in text
    assert brief["palier_suivant"] == "1500.0" or D(brief["palier_suivant"]) == D("1500")
    assert "Feuille de mission" in render_brief(brief)
    calm = build_brief(ledger, {}, ["a_v1", "b_v1", "c_v1"], cfg, now=NOW + timedelta(days=1))
    assert calm["obligations"] == []


def test_arena_rules_live_in_a_single_file():
    """Règles de l'arène : un seul fichier (libre depuis le 15/10/2026), jamais de copie ailleurs."""
    import yaml
    from conftest import ROOT
    rules = yaml.safe_load((ROOT / "config" / "promotion.yaml").read_text(encoding="utf-8"))
    assert {"min_closed_trades", "elimination_every_days", "min_days_before_elimination",
            "min_strategies_in_test", "radical_idea_after_days_without_record", "promotion_margin",
            "min_age_hours", "min_log_growth", "keep_log_growth"} <= set(rules)
    settings = yaml.safe_load((ROOT / "config" / "settings.yaml").read_text(encoding="utf-8"))
    assert "arena" not in settings


def test_regression_missing_arena_rule_fails_loudly(ledger):
    """Défaut du 15/10/2026 : la section « arena » avait disparu de settings.yaml sans que rien
    ne le signale (valeurs par défaut silencieuses). Une règle manquante doit faire échouer."""
    incomplete = dict(RULES)
    del incomplete["min_closed_trades"]
    with pytest.raises(KeyError):
        run_arena(ledger, {}, incomplete, NOW)


def test_main_capital_is_shared_among_the_best_strategies():
    """Décision du 15/10/2026 : le capital principal se répartit entre les meilleures
    stratégies éligibles, au prorata de leur croissance (somme des parts = 1)."""
    from polymarket_agent.arena import Standing, allocation
    def s(name, trades, growth, eliminated=False):
        return Standing(name, trades, 1000.0, 1000.0, growth, None, eliminated)
    shares = allocation([s("a", 12, 0.3), s("b", 15, 0.1), s("c", 5, 0.9), s("d", 30, -0.2),
                         s("e", 40, 0.5, eliminated=True)], min_trades=10, max_strategies=5)
    assert set(shares) == {"a", "b"}  # c : trop peu d'opérations ; d : perd ; e : éliminée
    assert abs(shares["a"] - 0.75) < 1e-9 and abs(sum(shares.values()) - 1) < 1e-9
    top = allocation([s(f"x{i}", 20, 0.1 * (i + 1)) for i in range(8)], min_trades=10, max_strategies=3)
    assert set(top) == {"x7", "x6", "x5"}
    assert allocation([s("d", 30, -0.2)], min_trades=10, max_strategies=5) == {}


def test_weighted_strategy_scales_buys_but_never_sells():
    from dataclasses import dataclass
    from decimal import Decimal
    from types import SimpleNamespace
    from polymarket_agent.main import Weighted

    @dataclass
    class P:
        side: str
        shares: Decimal

    class Fake:
        strategy_id, version = "fake", "1"

        def propose(self, *args):
            return SimpleNamespace(proposals=[P("BUY", Decimal("100")), P("SELL", Decimal("40")),
                                              P("BUY", Decimal("0.01"))])
    out = Weighted(Fake(), Decimal("0.25")).propose()
    assert [(p.side, p.shares) for p in out.proposals] == [("BUY", Decimal("25.00")), ("SELL", Decimal("40"))]


def test_regression_noise_is_not_promoted():
    """15/10/2026 : market_structure promue sur +0,02 % après 27 opérations en 3 h, destituée 10 min
    après. Seuil d'entrée (repository) : 20 opérations, 24 h, +2 % ; maintien au-dessus de 0."""
    gates = {"now": NOW, "min_age_hours": float(RULES["min_age_hours"]),
             "min_growth": float(RULES["min_log_growth"])}
    keep, margin, n = float(RULES["keep_log_growth"]), float(RULES["promotion_margin"]), int(RULES["min_closed_trades"])
    noise = st("market_structure", 27, 0.0002, days=3 / 24)
    assert choose_champion([noise], "", n, margin, keep_growth=keep, **gates)[0] == ""
    young_star = st("star", 27, 0.10, days=0.5)  # belle croissance mais moins de 24 h
    assert choose_champion([young_star], "", n, margin, keep_growth=keep, **gates)[0] == ""
    assert choose_champion([st("star", 27, 0.10, days=2)], "", n, margin, keep_growth=keep, **gates)[0] == "star"
    # Hystérésis : un champion à +1 % (sous le seuil d'entrée) reste, et garde sa part du capital.
    from polymarket_agent.arena import allocation
    champ = st("champ", 40, 0.01, days=5)
    assert choose_champion([champ], "champ", n, margin, keep_growth=keep, **gates)[0] == "champ"
    assert allocation([champ], n, 5, champion="champ", keep_growth=keep, **gates) == {"champ": 1.0}
    assert allocation([champ], n, 5, champion="", keep_growth=keep, **gates) == {}
    # Marge : il faut battre le champion de +0,01 pour le détrôner.
    assert choose_champion([st("champ", 40, 0.05, days=5), st("b", 40, 0.055, days=5)], "champ", n, margin,
                           keep_growth=keep, **gates)[0] == "champ"
    assert choose_champion([st("champ", 40, 0.05, days=5), st("b", 40, 0.07, days=5)], "champ", n, margin,
                           keep_growth=keep, **gates)[0] == "b"


def test_backtest_validated_strategies_enter_earlier_but_must_still_win():
    """16/10/2026 : une stratégie validée hors échantillon (validated_strategies) reçoit sa part
    plus tôt ; elle doit quand même battre « ne rien faire » en direct."""
    from polymarket_agent.arena import allocation, validated_gates
    assert RULES["validated_strategies"] == {}  # 16/10/2026 : météo retirée (aucun gain aux prix réels)
    validated = {"meteo_prevision": {"min_closed_trades": 8, "min_age_hours": 8, "min_log_growth": 0.005}}
    gates = {"now": NOW, "min_age_hours": float(RULES["min_age_hours"]),
             "min_growth": float(RULES["min_log_growth"])}
    n = int(RULES["min_closed_trades"])
    assert validated_gates("meteo_prevision_patiente_v1.0.0", validated)["min_closed_trades"] < n
    assert validated_gates("news_momentum_v1.0.0", validated) is None
    meteo = st("meteo_prevision_v1.0.0", 10, 0.01, days=0.5)   # 10 opérations, 12 h, +1 %
    other = st("news_momentum_v1.0.0", 10, 0.01, days=0.5)
    assert allocation([meteo, other], n, 5, **gates) == {}                       # sans la règle
    assert allocation([meteo, other], n, 5, validated=validated, **gates) == {"meteo_prevision_v1.0.0": 1.0}
    losing = st("meteo_prevision_v1.0.0", 10, -0.01, days=0.5)
    assert allocation([losing], n, 5, validated=validated, **gates) == {}
    assert choose_champion([meteo, other], "", n, 0.01, validated=validated, **gates)[0] == "meteo_prevision_v1.0.0"
