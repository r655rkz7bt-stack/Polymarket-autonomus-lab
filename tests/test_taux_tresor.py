"""Taux du Trésor : barrière sur clôtures quotidiennes (12/11/2026, experiments/taux_tresor.md, piste n° 43).
Données : CSV réel « Daily Treasury Par Yield Curve Rates » 2026 lu le 12/11/2026 (dernière clôture : 10 ans 4,98 le 10/11)."""
from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path

from conftest import raw_market
from test_fleuves import Http
from test_strategies_v3 import LIMITS, _books, _s, _state

from polymarket_agent import references as refs
from polymarket_agent import taux_tresor as tt
from polymarket_agent.data_collector import collect
from polymarket_agent.persistence import Database
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.strategies_v3 import TauxTresorBarriere

UTC = timezone.utc
NUIT = datetime(2026, 11, 12, 6, 0, tzinfo=UTC)
CSV = (Path(__file__).parent / "data" / "treasury_par_2026-11-12.csv").read_text()
HAUT = ("This market will resolve to \"Yes\" if the Treasury 10-year yield reaches or is higher than the listed value for any date "
        "between November 3, 2026 and November 30, 2026. Otherwise this market will resolve to \"No\".")
BAS = HAUT.replace("reaches or is higher than", "is lower than")


def _market(mid, question, desc):
    return parse_market(raw_market(mid, yes_token=f"{mid}Y", no_token=f"{mid}N", end=datetime(2026, 12, 1, 4, 59, tzinfo=UTC),
                                   question=question, description=desc, events=[{"id": "1310160", "title": "10-year yield November"}]))


def test_csv_questions_and_rule():
    c = tt.parse_csv(CSV)
    assert c[10][-1] == ("2026-11-10", 4.98) and c[2][-1] == ("2026-11-10", 4.73)
    assert tt.question("Will the 10-year Treasury yield hit 5.06% in November?", HAUT) == (10, True, 5.06, date(2026, 11, 3), date(2026, 11, 30))
    assert tt.question("Will the 5-year Treasury yield dip below 4.00% before 2027?", BAS.replace("10-year", "5-year"))[:3] == (5, False, 4.0)
    assert tt.question("Will the 10-year Treasury yield hit 5.06% in November?", "") is None
    # au centième : « hit » = ≥, « dip below » = strictement sous le niveau
    assert tt.touche(5.0551, 5.06, True) and not tt.touche(5.054, 5.06, True)
    assert not tt.touche(4.82, 4.82, False) and tt.touche(4.814, 4.82, False)
    # Thanksgiving et le 11/11 n'ont pas de clôture
    assert len(tt.jours_restants(date(2026, 11, 12), date(2026, 11, 30))) == 12


def test_chance_from_past_closes_only():
    c = [list(x) for x in tt.parse_csv(CSV)[10]]
    p_haut = tt.chance(c, 5.06, True, date(2026, 11, 3), date(2026, 11, 30), NUIT)
    p_loin = tt.chance(c, 5.38, True, date(2026, 11, 3), date(2026, 11, 30), NUIT)
    assert 0.3 < p_haut < 0.8 and p_loin < p_haut and p_loin < 0.15
    # déjà touché dans la fenêtre (4,84 le 05/11 < 4,85) : réglé, rien à calculer
    assert tt.chance(c, 4.85, False, date(2026, 11, 3), date(2026, 11, 30), NUIT) == 1.0
    # une clôture publiée aujourd'hui ou après n'entre pas dans le calcul
    futur = c + [["2026-11-12", 6.0]]
    assert tt.chance(futur, 5.06, True, date(2026, 11, 3), date(2026, 11, 30), NUIT) == p_haut


def test_collect_attach_at_night_and_buy(tmp_path):
    db = Database(tmp_path / "db.sqlite")
    url = tt.CSV.format(y=2026)
    result = collect({"sources": {"taux_tresor": {"enabled": True, "every_minutes": 60}}}, Http({url: CSV}), db, [], NUIT)
    assert result.status["taux_tresor"].startswith("ok (1")
    near = _market("1", "Will the 10-year Treasury yield hit 5.06% in November?", HAUT)
    far = _market("2", "Will the 10-year Treasury yield hit 5.38% in November?", HAUT)
    autre = _market("3", "Will the 10-year Treasury yield hit 5.06% in November?", "")
    assert refs.attach_all([near, far, autre], db, NUIT)["taux_tresor"] == 2
    # en séance américaine (15 h UTC), pas de chance donnée : le marché voit le cours du jour
    assert refs.attach_all([_market("4", near.question, HAUT)], db, datetime(2026, 11, 12, 15, 0, tzinfo=UTC))["taux_tresor"] == 0
    s = _s(TauxTresorBarriere, min_net_edge=0.08, uncertainty=0.04, min_price=0.05, max_price=0.90, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=3, max_per_event=2, kelly_fraction=1.0, max_candidates=120)
    p_far, p_near = far.references["taux_tresor"]["p"], near.references["taux_tresor"]["p"]
    y_near = round(p_near, 2)   # 5,06 cotée à sa chance : rien

    def books(y_far):
        b = _books(("1Y", str(round(y_near - 0.01, 2)), str(y_near)), ("1N", str(round(1 - y_near, 2)), str(round(1.01 - y_near, 2))), ("2Y", str(round(y_far - 0.01, 2)), str(y_far)),
                   ("2N", str(round(1 - y_far, 2)), str(round(1.01 - y_far, 2))))
        for x in b.values():
            x.fetched_at = NUIT
        return b
    # 5,38 cotée au-dessus de sa chance : achat du NON
    out = s.propose([near, far], books(round(p_far + 0.25, 2)), _state(tmp_path), LIMITS, "b1")
    assert [p.token_id for p in out.proposals] == ["2N"]


def test_max_per_event_counts_positions_already_held(tmp_path):
    """13/11/2026 (00 h 05 → 00 h 16 UTC) : `max_per_event` 2 ne comptait que les achats du cycle ; d'un cycle à l'autre, le fantôme a
    acheté 3 seuils du même événement « 10-year yield November » (6656076, 6656075, 6656072 : une seule trajectoire), et de même
    pour les 5 et 30 ans (enquetes/2026-11-13_nuit_max_par_evenement_entre_cycles.md)."""
    from decimal import Decimal
    from polymarket_agent.ledger import Position
    db = Database(tmp_path / "db.sqlite")
    collect({"sources": {"taux_tresor": {"enabled": True, "every_minutes": 60}}}, Http({tt.CSV.format(y=2026): CSV}), db, [], NUIT)
    far = _market("2", "Will the 10-year Treasury yield hit 5.38% in November?", HAUT)
    refs.attach_all([far], db, NUIT)
    p_far = far.references["taux_tresor"]["p"]
    b = _books(("2Y", str(round(p_far + 0.24, 2)), str(round(p_far + 0.25, 2))), ("2N", str(round(0.75 - p_far, 2)), str(round(0.76 - p_far, 2))))
    for x in b.values():
        x.fetched_at = NUIT
    s = _s(TauxTresorBarriere, min_net_edge=0.08, uncertainty=0.04, min_price=0.05, max_price=0.90, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=3, max_per_event=2, kelly_fraction=1.0, max_candidates=120)
    st = _state(tmp_path)
    assert [p.token_id for p in s.propose([far], b, st, LIMITS, "b1").proposals] == ["2N"]   # événement vide : achat
    for tok, mid in (("6656076Y", "6656076"), ("6656075Y", "6656075")):   # deux seuils déjà tenus, achetés aux cycles d'avant
        st.positions[tok] = Position(tok, mid, "1310160", "Yes", Decimal("10"), Decimal("1"), NUIT.isoformat(), "taux_tresor_barriere", "2.0.0")
    out = s.propose([far], b, st, LIMITS, "b1")
    assert out.proposals == [] and out.abstentions.get("déjà deux tranches de cet événement") == 1


def test_real_case_of_16_november_evening_says_why_it_waits(tmp_path):
    """16/11/2026 20 h 51 : « aucun marché vu n'a la référence ou la forme demandée (raison non notée) » ×294 (constat
    `acheteuses_arretees`, dernier achat le 13/11). La chance n'est donnée que de 00 à 12 h UTC : le soir, la stratégie doit voir ses
    marchés et dire pourquoi elle attend, sans rien acheter ; un marché étranger reste invisible."""
    db = Database(tmp_path / "db.sqlite")
    soir = datetime(2026, 11, 16, 20, 51, tzinfo=UTC)
    collect({"sources": {"taux_tresor": {"enabled": True, "every_minutes": 60}}}, Http({tt.CSV.format(y=2026): CSV}), db, [], soir)
    m = _market("6656077", "Will the 10-year Treasury yield hit 5.38% in November?", HAUT)
    autre = _market("9", "Will it rain?", "")
    assert refs.attach_all([m, autre], db, soir)["taux_tresor"] == 0
    s = _s(TauxTresorBarriere, min_net_edge=0.08, uncertainty=0.04, min_price=0.05, max_price=0.90, max_stale_hours=3,
           max_extra_ticks=1, max_proposals_per_cycle=3, max_per_event=2, kelly_fraction=1.0, max_candidates=120)
    assert [x.market_id for x in s.candidates([m, autre])] == ["6656077"]
    out = s.propose([m], {}, _state(tmp_path), LIMITS, "b1")
    assert not out.proposals and any("00 à 12 h UTC" in r for r in out.abstentions)


def test_real_case_of_16_november_k_1_3_overstated_the_hits():
    """16/11/2026 (experiments/enquetes/2026-11-16_soir_taux_tresor_k_trop_haut.md) : sur 36 ans de clôtures, la marche × 1,3 prévoyait
    0,34 pour une barrière à 1 σ60 × √10 en 10 jours, observé 0,24. La production lit maintenant la loi empirique des excursions :
    même calcul, chance plus basse que K 1,3 et proche de K 1,0 au cœur, plus haute dans les queues (z ≥ 2 : queues épaisses)."""
    # table : 10 jours, excursion ≥ 1 σ60 ≈ 0,61 (gaussienne discrète 0,617) ; monotone en z et en n
    assert 0.55 < tt.survie(1.0, 10) < 0.66
    assert tt.survie(2.0, 10) < tt.survie(1.0, 10) and tt.survie(2.0, 30) > tt.survie(2.0, 10)
    # hors de la table (n > 90 ou z > 8) : mise à l'échelle, continue et monotone
    assert abs(tt.survie(7.99, 90) - tt.survie(8.01, 90)) < 0.02 and tt.survie(12.0, 120) < tt.survie(8.0, 120)
    c = [list(x) for x in tt.parse_csv(CSV)[10]]
    p_emp = tt.chance(c, 5.38, True, date(2026, 11, 3), date(2026, 11, 30), NUIT)
    p_13 = tt.chance(c, 5.38, True, date(2026, 11, 3), date(2026, 11, 30), NUIT, k=1.3)
    p_10 = tt.chance(c, 5.38, True, date(2026, 11, 3), date(2026, 11, 30), NUIT, k=1.0)
    assert p_emp < p_13 and abs(p_emp - p_10) < 0.06
    # « dip below » strictement sous le niveau, déjà touché = 1
    assert tt.p_barriere_empirique(4.84, 0.05, 4.85, False, 5) == 1.0
    assert tt.p_barriere_empirique(4.86, 0.05, 4.85, False, 5) < tt.p_barriere_empirique(4.86, 0.05, 4.85, True, 5) == 1.0
