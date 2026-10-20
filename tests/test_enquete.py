"""Enquête automatique (20/10/2026) : chaque contrôle retrouve le défaut réel qui l'a fait naître."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from polymarket_agent import enquete

NOW = datetime(2026, 10, 20, 14, 0, tzinfo=timezone.utc)


def _e(kind: str, when: datetime, **data) -> dict:
    return {"type": kind, "ts": when.isoformat(), "data": data}


def _buy(when, token, price, shares, strategy="nf", version="1.0.0", cycle="c1", est=None, posted=False,
         status="FILLED", horizon="5"):
    extra = {"cycle_id": cycle, "fill_status": status, "horizon_hours": horizon}
    if est is not None:
        extra["est_probability"] = str(est)
    if posted:
        extra["order_type"] = "limite"
    return _e("BUY", when, token_id=token, market_id="m" + token, event_id="e", outcome="Yes", price=str(price),
              shares=str(shares), fee="0", strategy_id=strategy, strategy_version=version, extra=extra)


def _settle(when, token, payout):
    return _e("SETTLE", when, token_id=token, payout_per_share=str(payout), resolution="résolu")


def _ledger(*rows, capital=1000, born=NOW - timedelta(days=5)):
    return [_e("GENESIS", born, initial_capital=str(capital)), _e("HEARTBEAT", born, total_estimated=str(capital))] + list(rows)


def test_principal_buy_without_ghost_twin_is_grave():
    """18/10 (PR #76) : le principal relançait la stratégie avec son argent au lieu de copier ses paris."""
    t = NOW - timedelta(hours=3)
    ghost = _ledger(_buy(t, "a", 0.9, 100, cycle="c1"))
    principal = _ledger(_buy(t, "a", 0.9, 35, cycle="c1"), _buy(t, "b", 0.5, 300, cycle="c1"))
    found = enquete.copie_fidele({"principal": principal, "nf_v1.0.0": ghost}, NOW - timedelta(days=3))
    assert found[0]["gravite"] == enquete.GRAVE and "1 achat" in found[0]["titre"]
    assert enquete.obligations(found) and "copie_fidele" in enquete.obligations(found)[0]


def test_principal_stake_above_its_cap_is_grave_ghost_stake_is_a_lead():
    t = NOW - timedelta(hours=2)
    principal = _ledger(_buy(t, "a", 0.8, 200))  # 160 € sur 1000
    ghost = _ledger(_buy(t, "b", 0.9, 400))  # 360 € sur 1000
    found = enquete.mises({"principal": principal, "nf_v1.0.0": ghost}, 0.10, 0.25, NOW - timedelta(days=3))
    assert [f["gravite"] for f in found] == [enquete.GRAVE, enquete.A_REGARDER]


def test_estimate_far_above_the_usual_gap_is_flagged():
    """20/10 : Moyuka Uchijima estimé 0,98 sur le carnet du début de cycle, payé 0,817."""
    t = NOW - timedelta(hours=5)
    rows = [_buy(t + timedelta(minutes=i), f"t{i}", 0.85, 10, est=0.90) for i in range(6)]
    rows.append(_buy(t + timedelta(hours=1), "crash", 0.817, 278, est=0.9785))
    rows.append(_buy(t + timedelta(hours=2), "posted", 0.70, 10, est=0.90, posted=True))  # ordre posé : ignoré
    found = enquete.estimation_perimee({"nf_v1.0.0": _ledger(*rows)}, NOW - timedelta(days=3))
    assert len(found) == 1 and "1 achat" in found[0]["titre"] and "0.817" in found[0]["exemples"][0]


def test_a_gain_made_in_one_day_is_grave_when_the_principal_copies_it():
    """20/10 : 95 % du gain de la championne vient du 18/10."""
    rows = []
    start = NOW - timedelta(days=4)
    for day in range(4):
        for i in range(6):
            when = start + timedelta(days=day, minutes=i)
            token = f"d{day}-{i}"
            rows.append(_buy(when, token, 0.5 if day == 0 else 0.9, 100))
            rows.append(_settle(when + timedelta(minutes=30), token, 1 if (day == 0 or i % 6) else 0))
    ghost = _ledger(*rows)
    found = enquete.chance({"nf_v1.0.0": ghost}, copied={"nf_v1.0.0"})
    days = [f for f in found if "fait" in f["titre"] and "du gain" in f["titre"] and "le " in f["titre"]]
    assert days and days[0]["gravite"] == enquete.GRAVE
    assert all(f["gravite"] == enquete.A_REGARDER for f in enquete.chance({"nf_v1.0.0": ghost}, copied=set()))


def test_daughter_is_compared_with_her_mother_on_the_same_period():
    born = NOW - timedelta(days=2)
    old = [r for i in range(10) for r in (_buy(born - timedelta(days=1, minutes=i), f"o{i}", 0.5, 10),
                                          _settle(born - timedelta(days=1), f"o{i}", 1))]
    new_mother = [r for i in range(10) for r in (_buy(born + timedelta(minutes=i), f"n{i}", 0.9, 10),
                                                 _settle(born + timedelta(hours=1), f"n{i}", 0 if i < 3 else 1))]
    child = [r for i in range(10) for r in (_buy(born + timedelta(minutes=i), f"c{i}", 0.9, 10),
                                            _settle(born + timedelta(hours=1), f"c{i}", 0 if i < 2 else 1))]
    configs = {"mere": {"version": "1.0.0"}, "fille": {"version": "1.0.0", "mere": "mere"}}
    entries = {"mere_v1.0.0": _ledger(*old, *new_mother), "fille_v1.0.0": _ledger(*child, born=born)}
    found = enquete.filles_periode(entries, configs)
    assert found and "depuis le" in found[0]["exemples"][0]
    # Sur la même période, la mère perd (−22 %) ; la fille perd moins (−11 %).
    assert "-11.1%" in found[0]["exemples"][0] and "-22.2%" in found[0]["exemples"][0]


def test_silent_strategies_forgotten_positions_and_stopped_cycle():
    old = NOW - timedelta(days=4)
    entries = {"principal": _ledger(born=old), "muette_v1.0.0": _ledger(born=old),
               "oubli_v1.0.0": _ledger(_buy(old, "x", 0.9, 10, horizon="2"), born=old)}
    assert enquete.muettes(entries, ["muette_v1.0.0", "oubli_v1.0.0"], NOW)[0]["exemples"] == ["muette_v1.0.0 (née le 2026-10-16)"]
    assert "oubli_v1.0.0" in enquete.positions_oubliees(entries, NOW)[0]["titre"]
    stopped = enquete.cycle_arrete(entries, NOW)
    assert stopped and stopped[0]["gravite"] == enquete.GRAVE


def test_price_outside_the_strategy_range_is_a_lead():
    """20/10 : la fille « prix haut » (0,875-0,95) achetait à 0,79 par un ordre posé."""
    configs = {"haut": {"version": "1.0.0", "params": {"min_ask": {"value": 0.875}, "max_ask": {"value": 0.95}}}}
    rows = _ledger(_buy(NOW - timedelta(hours=1), "a", 0.79, 10, strategy="haut", posted=True),
                   _buy(NOW - timedelta(hours=1), "b", 0.90, 10, strategy="haut"))
    found = enquete.filtre_prix({"haut_v1.0.0": rows}, configs, NOW - timedelta(days=3))
    assert len(found) == 1 and found[0]["exemples"] == [f"{(NOW - timedelta(hours=1)).isoformat()[:16]} « Yes » à 0.790 (ordre posé)"]


def test_run_and_render_put_grave_findings_first():
    t = NOW - timedelta(hours=1)
    entries = {"principal": _ledger(_buy(t, "b", 0.5, 300), _e("HEARTBEAT", NOW, total_estimated="1000")),
               "nf_v1.0.0": _ledger()}
    found = enquete.run(entries, {}, [], NOW)
    assert found and found[0]["gravite"] == enquete.GRAVE
    text = enquete.render(found, NOW)
    assert text.startswith("# Enquête automatique") and "[grave]" in text
