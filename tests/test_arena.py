"""Arène : cliquet des paliers, champion, élimination hebdomadaire."""

from __future__ import annotations

import json
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
    keep, margin, n = float(RULES["keep_log_growth"]), RULES["promotion_margin"], int(RULES["min_closed_trades"])
    assert margin is None  # 18/10/2026 : plus de marge, plusieurs championnes
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
    # Ancienne règle (marge +0,01) : il fallait battre le champion de +0,01 pour le détrôner.
    assert choose_champion([st("champ", 40, 0.05, days=5), st("b", 40, 0.055, days=5)], "champ", n, 0.01,
                           keep_growth=keep, **gates)[0] == "champ"
    assert choose_champion([st("champ", 40, 0.05, days=5), st("b", 40, 0.07, days=5)], "champ", n, 0.01,
                           keep_growth=keep, **gates)[0] == "b"
    # Sans marge (18/10/2026) : le titre reste à la doyenne tant qu'elle est qualifiée ; b a sa part quand même.
    both = [st("champ", 40, 0.05, days=5), st("b", 40, 0.07, days=5)]
    assert choose_champion(both, "champ", n, None, keep_growth=keep, **gates)[0] == "champ"
    assert set(allocation(both, n, 5, champion="champ", keep_growth=keep, **gates)) == {"champ", "b"}


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


def test_inactive_strategies_are_retired_without_resetting_the_weekly_elimination(tmp_path):
    """17/10/2026 : ménage des stratégies sans opération ni position après 3 jours ; la tenue de
    marché est épargnée ; l'élimination hebdomadaire garde son propre compteur."""
    from polymarket_agent.arena import last_weekly_elimination, retire_inactive
    main = Ledger.create(tmp_path / "m.jsonl", KEY, tmp_path / "m.lock", "1000", now=NOW)
    ghosts = {n: Ledger.create(tmp_path / f"{n}.jsonl", KEY, tmp_path / f"{n}.lock", "1000", now=NOW)
              for n in ("idle_v1", "market_maker_v1", "young_v1", "busy_v1")}
    ghosts["busy_v1"].record_buy(op_id="b", token_id="t", market_id="m", event_id="e", outcome="Yes", shares="10",
                                 price="0.5", fee="0", strategy_id="busy", strategy_version="1", now=NOW)
    standings = [st("idle_v1", 0, 0.0, days=4), st("market_maker_v1", 0, 0.0, days=4), st("young_v1", 0, 0.0, days=1),
                 st("busy_v1", 0, 0.0, days=4)]
    cfg = dict(RULES, retirer_inactives_apres_jours=3, jamais_retirer=["market_maker"])
    assert retire_inactive(main, ghosts, standings, cfg, NOW) == ["idle_v1"]
    assert "idle_v1" in main.state.eliminated and last_weekly_elimination(main) is None


def test_estimated_rewards_count_for_ranking_but_never_in_ghost_capital(ledger, tmp_path):
    """Option A d'Etienne (17/10/2026) : une tenue de marché à l'équilibre devient championne grâce à
    ses récompenses estimées, mais son capital fantôme ne bouge pas."""
    shadow = Ledger.create(tmp_path / "mm.jsonl", KEY, tmp_path / "mm.lock", "1000", now=NOW)
    for i in range(20):
        buy(shadow, f"b{i}", token=f"t{i}", shares="10", price="0.5", event=f"e{i}")
        shadow.record_settlement(op_id=f"s{i}", token_id=f"t{i}", payout_per_share="0.5",
                                 resolution="50-50", now=NOW)
    later = NOW + timedelta(hours=25)
    name = "market_maker_v1"  # jugée sur ses journées de récompenses (promotion.yaml → juger_sur_recompenses)
    assert run_arena(ledger, {name: shadow}, RULES, later)["champion"] == ""  # croissance nulle
    summary = run_arena(ledger, {name: shadow}, RULES, later, rewards={name: 30.0}, reward_days={name: 3})
    assert summary["champion"] == name and summary["allocation"] == {name: 1.0}
    assert summary["engagement"] == {name: 0.3}  # part plafonnée
    row = summary["classement"][0]
    assert row["rewards"] == 30.0 and row["realized_capital"] == 1000.0
    assert shadow.state.cash == D("1000")


def test_promotion_needs_regular_results_and_starts_with_a_trial_share():
    """AMELIORATION n°1 (17/10/2026) : 20 opérations à +2 % ne suffisent plus si les résultats sont
    du hasard (score de confiance t < min_t_stat) ; une stratégie promue n'engage d'abord qu'une
    partie de sa part (période d'essai)."""
    from polymarket_agent.arena import allocation, exposure, t_stat
    assert RULES["min_t_stat"] >= 1.0
    assert t_stat([10.4, 8.8, 16.6, 5.4, -15.0, 17.7, -1.8, -15.0, 10.2, -2.0]) < 1.0  # meteo_prevision le 17/10
    assert t_stat([5.0, 6.0, 7.0]) > 5 and t_stat([1.0]) == 0.0 and t_stat([2.0, 2.0]) == 99.0
    noisy = Standing("bruit_v1", 20, 1030.0, 1000.0, 0.03, NOW - timedelta(days=2), False, t_stat=0.6)
    steady = Standing("regulier_v1", 20, 1030.0, 1000.0, 0.03, NOW - timedelta(days=2), False, t_stat=2.4)
    gates = {"now": NOW, "min_age_hours": 24.0, "min_growth": 0.02, "min_t": 1.5}
    assert allocation([noisy, steady], 20, 5, **gates) == {"regulier_v1": 1.0}
    assert choose_champion([noisy], "", 20, **gates)[0] == ""
    assert choose_champion([noisy], "bruit_v1", 20, **gates)[0] == "bruit_v1"  # un champion en place reste (maintien)
    trial = {"essai": {"pleine_part_apres_operations": 60, "part_minimale": 0.25}}
    assert exposure([steady], {"regulier_v1": 1.0}, trial) == {"regulier_v1": 0.333333}
    assert exposure([dataclasses_replace(steady, closed_trades=4)], {"regulier_v1": 1.0}, trial) == {"regulier_v1": 0.25}
    assert exposure([dataclasses_replace(steady, closed_trades=90)], {"regulier_v1": 1.0}, trial) == {"regulier_v1": 1.0}


def dataclasses_replace(obj, **kw):
    import dataclasses
    return dataclasses.replace(obj, **kw)


def test_market_maker_is_judged_on_reward_days_and_politics_on_marked_value(ledger, tmp_path):
    """AMELIORATION n°3 et 4 : la tenue de marché entre sur ses journées de récompenses (sans 20
    opérations), le favori politique sur la valeur de ses positions ; chacun avec une part plafonnée."""
    from polymarket_agent.arena import allocation, exposure, mode_for, standing
    cfg = {"juger_sur_recompenses": {"market_maker": {"jours_min": 3, "part_max": 0.3}},
           "juger_sur_valeur": {"favori_politique": {"min_age_hours": 72, "part_max": 0.2}}}
    assert mode_for("market_maker_serre_v1.0.0", cfg)[0] == "recompenses"
    assert mode_for("favori_politique_nuit_v1.0.0", cfg)[0] == "valeur" and mode_for("naive_v1", cfg)[0] == ""
    gates = {"now": NOW, "min_age_hours": 24.0, "min_growth": 0.02, "min_t": 1.5, "modes": cfg}
    mm = Standing("market_maker_v1", 2, 1000.0, 1000.0, 0.03, NOW - timedelta(days=4), False, rewards=30.0,
                  reward_days=3, mode="recompenses")
    young_mm = dataclasses_replace(mm, reward_days=2)
    assert allocation([mm], 20, 5, **gates) == {"market_maker_v1": 1.0}
    assert allocation([young_mm], 20, 5, **gates) == {}
    assert exposure([mm], {"market_maker_v1": 1.0}, cfg) == {"market_maker_v1": 0.3}
    # Politique : le capital réalisé ne bouge pas (rien de réglé), la valeur au prix du carnet si.
    shadow = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW - timedelta(days=4))
    buy(shadow, "b1", token="tP", shares="200", price="0.85", now=NOW - timedelta(days=4))
    shadow.heartbeat("c1", "OK", NOW, total_estimated="1040")
    pol = standing("favori_politique_v1.0.0", shadow, set(), modes=cfg)
    assert pol.mode == "valeur" and pol.realized_capital == 1000.0 and pol.log_growth > 0.03
    assert allocation([pol], 20, 5, **gates) == {"favori_politique_v1.0.0": 1.0}
    assert exposure([pol], {"favori_politique_v1.0.0": 1.0}, cfg) == {"favori_politique_v1.0.0": 0.2}
    assert standing("autre_v1", shadow, set(), modes=cfg).log_growth == 0.0  # mode normal : capital réalisé


def test_several_champions_half_equal_half_merit_one_per_family_and_capped():
    """Décision d'Etienne (18/10/2026) : toutes les qualifiées reçoivent une part, moitié à égalité
    moitié selon les gains ; une seule place par famille ; au plus 50 % par stratégie."""
    from polymarket_agent.arena import allocation, exposure, family_map
    gates = {"now": NOW, "min_age_hours": 24.0, "min_growth": 0.02}
    a, b = st("a_v1", 40, 0.15, days=5), st("b_v1", 40, 0.03, days=5)
    shares = allocation([a, b], 20, 5, merit=0.5, **gates)
    assert shares["a_v1"] == pytest.approx(0.25 + 0.5 * 0.15 / 0.18) and sum(shares.values()) == pytest.approx(1)
    assert round(shares["a_v1"], 2) == 0.67 and round(shares["b_v1"], 2) == 0.33
    # Une mère et sa fille : seule la meilleure des deux prend une place.
    mom, kid = st("naive_favorite_v1.0.0", 40, 0.09, days=5), st("nf_sport_v1.0.0", 40, 0.12, days=5)
    fams = {"naive_favorite": "naive_favorite", "nf_sport": "naive_favorite"}
    assert set(allocation([mom, kid, b], 20, 5, merit=0.5, families=fams, **gates)) == {"nf_sport_v1.0.0", "b_v1"}
    # Le dépôt : les filles remontent bien à leur mère.
    real = family_map()
    assert real["nf_sport"] == "naive_favorite" and real["naive_favorite"] == "naive_favorite"
    # Seule qualifiée : au plus 50 % du capital principal.
    assert exposure([a], {"a_v1": 1.0}, {"part_max_par_strategie": 0.5}) == {"a_v1": 0.5}
    assert RULES["part_max_par_strategie"] == 0.5 and RULES["repartition"]["merite"] == 0.5


def test_measured_overlap_decides_who_shares_a_place():
    """Option B d'Etienne (18/10/2026) : deux qualifiées n'ont qu'une place si elles font surtout les
    mêmes paris (mesurés), même famille ou pas ; deux sœurs qui jouent des matchs différents ont
    chacune la sienne ; sans achat à comparer, une mère et ses filles restent jumelles."""
    from dataclasses import replace

    from polymarket_agent.arena import allocation, bought_events, overlap
    gates = {"now": NOW, "min_age_hours": 24.0, "min_growth": 0.02}
    fams = {"nf_court": "naive_favorite", "nf_sport": "naive_favorite", "nf_sport_patiente": "naive_favorite"}
    court = replace(st("nf_court_v1.0.0", 50, 0.15, days=5), events=frozenset(f"e{i}" for i in range(40)))
    # 8 matchs sur 10 déjà joués par nf_court : doublon, la meilleure des deux garde la place.
    sport = replace(st("nf_sport_v1.0.0", 40, 0.14, days=5), events=frozenset(["e1", "e2", "e3", "e4", "e5", "e6",
                                                                               "e7", "e8", "x1", "x2"]))
    assert overlap(court, sport) == pytest.approx(0.8)
    twins = {}
    assert set(allocation([court, sport], 20, 5, merit=0.5, families=fams, max_overlap=0.5, twins=twins,
                          **gates)) == {"nf_court_v1.0.0"}
    assert twins == {"nf_sport_v1.0.0": {"comme": "nf_court_v1.0.0", "chevauchement": 0.8}}
    # 2 sur 10 : des paris différents, chacune sa place malgré la même mère.
    other = replace(sport, events=frozenset(["e1", "e2"] + [f"y{i}" for i in range(8)]))
    assert set(allocation([court, other], 20, 5, merit=0.5, families=fams, max_overlap=0.5, **gates)) == {
        "nf_court_v1.0.0", "nf_sport_v1.0.0"}
    # Familles différentes mais mêmes paris : doublon aussi.
    clone = replace(sport, name="cotes_v1.0.0")
    assert set(allocation([court, clone], 20, 5, merit=0.5, families=fams, max_overlap=0.5, **gates)) == {
        "nf_court_v1.0.0"}
    # Rien à comparer (aucun achat enregistré) : règle de la famille ; sans seuil : règle de la famille.
    blind = replace(other, events=frozenset())
    assert set(allocation([court, blind], 20, 5, merit=0.5, families=fams, max_overlap=0.5, **gates)) == {
        "nf_court_v1.0.0"}
    assert set(allocation([court, other], 20, 5, merit=0.5, families=fams, **gates)) == {"nf_court_v1.0.0"}
    # Événements comptés depuis la dernière remise à zéro (événement, sinon marché).
    entries = [{"type": "BUY", "data": {"event_id": "old", "market_id": "m0"}}, {"type": "RESET", "data": {}},
               {"type": "BUY", "data": {"event_id": "e1", "market_id": "m1"}},
               {"type": "BUY", "data": {"event_id": "", "market_id": "m2"}}, {"type": "SELL", "data": {"event_id": "e9"}}]
    assert bought_events(entries) == frozenset({"e1", "m2"})
    assert RULES["chevauchement_max"] == 0.5


def test_run_arena_reports_twins_and_keeps_its_ranking_readable(ledger, tmp_path):
    from polymarket_agent.arena import standing
    shadow = Ledger.create(tmp_path / "s.jsonl", KEY, tmp_path / "s.lock", "1000", now=NOW - timedelta(days=2))
    buy(shadow, "o1", "t1", shares="2")
    assert standing("s_v1", shadow, set()).events
    out = run_arena(ledger, {"s_v1": shadow}, RULES, NOW)
    assert out["doublons"] == {} and "events" not in out["classement"][0]
    json.dumps(out)  # tout le résumé reste lisible en JSON


def test_confidence_is_measured_on_returns_not_on_stake_sizes(tmp_path):
    """AMELIORATION du 18/10/2026 au soir : le score de confiance porte sur le rendement de chaque
    opération (résultat / mise). Sur les euros, deux gros paris gagnés suffisaient à faire croire à
    un avantage (nf_sport : 2,7 avec 24 gagnés pour 23,4 attendus d'après ses prix)."""
    from polymarket_agent.arena import standing, t_stat, trade_returns
    trades = [{"pnl": D("10"), "cost": D("100")}, {"pnl": D("1"), "cost": D("10")}, {"pnl": D("2"), "cost": D("0")}]
    assert trade_returns(trades) == [0.1, 0.1]  # mise nulle ignorée
    shadow = Ledger.create(tmp_path / "s.jsonl", KEY, tmp_path / "s.lock", "1000", now=NOW)
    for k, (shares, payout) in enumerate([("400", "1"), ("300", "1"), ("10", "0"), ("20", "1")]):
        buy(shadow, f"b{k}", token=f"t{k}", shares=shares, price="0.9", event=f"e{k}")
        shadow.record_settlement(op_id=f"s{k}", token_id=f"t{k}", payout_per_share=payout,
                                 resolution="Yes" if payout == "1" else "No", now=NOW)
    s = standing("s_v1", shadow, set())
    returns = [1 / 9, 1 / 9, -1.0, 1 / 9]  # trois gains de 11 % et une perte totale (sur une petite mise)
    assert s.t_stat == t_stat(returns) and s.t_stat < 1.0
    assert t_stat([40.0, 30.0, -9.0, 2.0]) > s.t_stat  # sur les euros, la perte « disparaissait »


def test_champion_betting_worse_than_its_prices_loses_its_place():
    """18/10/2026 au soir : rester champion demande aussi un score de confiance ≥ `keep_t_stat`
    (nf_court gagnait de l'argent avec un score de −0,7 sur le rendement)."""
    from dataclasses import replace

    from polymarket_agent.arena import allocation
    gates = {"now": NOW, "min_age_hours": 24.0, "min_growth": 0.02, "min_t": 1.5}
    court = Standing("nf_court_v1", 65, 1116.0, 1000.0, 0.11, NOW - timedelta(days=2), False, t_stat=-0.7)
    patient = Standing("nf_sport_patiente_v1", 42, 1144.0, 1000.0, 0.13, NOW - timedelta(days=2), False, t_stat=2.75)
    assert RULES["keep_t_stat"] == 0.0
    assert choose_champion([court, patient], "nf_court_v1", 20, None, keep_t=0.0, **gates)[0] == "nf_sport_patiente_v1"
    assert choose_champion([court], "nf_court_v1", 20, None, keep_t=0.0, **gates)[0] == ""
    assert set(allocation([court, patient], 20, 5, champion="nf_court_v1", keep_t=0.0, **gates)) == {
        "nf_sport_patiente_v1"}
    # Sans seuil de maintien (ancienne règle), le champion gardait sa place.
    assert choose_champion([court], "nf_court_v1", 20, None, **gates)[0] == "nf_court_v1"
    assert "nf_court_v1" in allocation([court, patient], 20, 5, champion="nf_court_v1", **gates)
    assert choose_champion([replace(court, t_stat=0.3)], "nf_court_v1", 20, None, keep_t=0.0, **gates)[0] == "nf_court_v1"


def test_clearly_losing_strategies_are_retired_at_once(tmp_path):
    """19/10/2026 : confiance ≤ −1,5 après 20 opérations → retrait immédiat (journal signé), sans
    toucher au compteur hebdomadaire ; jamais le champion, ni les modes de jugement, ni trop tôt."""
    from dataclasses import replace

    from polymarket_agent.arena import last_weekly_elimination, retire_hopeless
    main = Ledger.create(tmp_path / "m.jsonl", KEY, tmp_path / "m.lock", "1000", now=NOW)
    main.record_promotion("champ_v1", "test", now=NOW)
    bad = replace(st("news_momentum_v1", 128, -0.1), t_stat=-1.6)
    standings = [bad, replace(st("champ_v1", 50, -0.1), t_stat=-2.0), replace(st("jeune_v1", 12, -0.1), t_stat=-3.0),
                 replace(st("market_maker_v1", 30, -0.1), t_stat=-2.0, mode="recompenses"),
                 replace(st("moyenne_v1", 40, 0.0), t_stat=-1.0)]
    assert retire_hopeless(main, standings, RULES, NOW) == ["news_momentum_v1"]
    assert "news_momentum_v1" in main.state.eliminated and last_weekly_elimination(main) is None
    assert RULES["retirer_perdantes"] == {"min_operations": 20, "confiance_max": -1.5}
    assert retire_hopeless(main, standings, {}, NOW) == []
