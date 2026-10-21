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
    # Une stratégie coupée (reversion, 20/10) et un teneur de marché (horizon = durée de la cote) ne sont pas « oubliés ».
    entries["market_maker_v1.0.0"] = _ledger(_buy(old, "m", 0.5, 10, strategy="market_maker", horizon="2"), born=old)
    assert [f["titre"].split(" :")[0] for f in enquete.positions_oubliees(entries, NOW)] == ["oubli_v1.0.0"]
    assert enquete.positions_oubliees(entries, NOW, active=["autre_v1.0.0"]) == []
    stopped = enquete.cycle_arrete(entries, NOW)
    assert stopped and stopped[0]["gravite"] == enquete.GRAVE


def test_price_outside_the_strategy_range_is_a_lead():
    """20/10 : la fille « prix haut » (0,875-0,95) achetait à 0,79 par un ordre posé."""
    configs = {"haut": {"version": "1.0.0", "params": {"min_ask": {"value": 0.875}, "max_ask": {"value": 0.95}}}}
    rows = _ledger(_buy(NOW - timedelta(hours=1), "a", 0.79, 10, strategy="haut", posted=True),
                   _buy(NOW - timedelta(hours=1), "b", 0.90, 10, strategy="haut"))
    found = enquete.filtre_prix({"haut_v1.0.0": rows}, configs, NOW - timedelta(days=3))
    assert len(found) == 1 and found[0]["exemples"] == [f"{(NOW - timedelta(hours=1)).isoformat()[:16]} « Yes » à 0.790 (ordre posé)"]


def test_daughter_price_filter_is_audited_like_the_strategy_range():
    """21/10 : le contrôle ne lisait que min_ask/max_ask ; la plage `filtres.prix_min/prix_max` des
    filles (ex. nf_sport_patiente_prix_haut : « mellren » à 0,783 pour 0,875-0,95) n'était jamais vérifiée."""
    configs = {"fille": {"version": "1.0.0", "params": {"min_ask": {"value": 0.8}, "max_ask": {"value": 0.95}},
                         "filtres": {"prix_min": 0.875, "prix_max": 0.95}}}
    t = NOW - timedelta(hours=1)
    rows = _ledger(_buy(t, "a", 0.783, 10, strategy="fille", posted=True), _buy(t, "b", 0.90, 10, strategy="fille"))
    found = enquete.filtre_prix({"fille_v1.0.0": rows}, configs, NOW - timedelta(days=3))
    assert len(found) == 1 and "0.875–0.95" in found[0]["titre"] and "0.783" in found[0]["exemples"][0]


def test_time_window_filters_are_audited_for_immediate_buys_only():
    configs = {"tres_court": {"version": "1.0.0", "filtres": {"heures_min": 0, "heures_max": 6, "heure_utc": [4, 12]}},
               "moyen": {"version": "1.0.0", "filtres": {"echeance_min": 72, "echeance_max": 168}}}
    t = datetime(2026, 10, 20, 9, 0, tzinfo=timezone.utc)

    def buy(strategy, token, kickoff=None, horizon="5", posted=False, when=t):
        b = _buy(when, token, 0.9, 10, strategy=strategy, horizon=horizon, posted=posted)
        if kickoff is not None:
            b["data"]["extra"]["depuis_coup_d_envoi_h"] = kickoff
        return b

    entries = {
        "tres_court_v1.0.0": _ledger(buy("tres_court", "ok", kickoff="-2.5"), buy("tres_court", "tard", kickoff="-9.0"),
                                     buy("tres_court", "nuit", kickoff="-1.0", when=t.replace(hour=2)),
                                     buy("tres_court", "pose", kickoff="-9.0", posted=True)),
        "moyen_v1.0.0": _ledger(buy("moyen", "bon", horizon="100"), buy("moyen", "trop_tot", horizon="10")),
    }
    found = {f["titre"].split(" : ")[0]: f for f in enquete.filtre_delai(entries, configs, NOW - timedelta(days=3))}
    assert set(found) == {"tres_court", "moyen"}
    assert len(found["tres_court"]["exemples"]) == 2 and "9.0" in found["tres_court"]["exemples"][0]
    assert len(found["moyen"]["exemples"]) == 1 and "10.0 h" in found["moyen"]["exemples"][0]


def test_run_and_render_put_grave_findings_first():
    t = NOW - timedelta(hours=1)
    entries = {"principal": _ledger(_buy(t, "b", 0.5, 300), _e("HEARTBEAT", NOW, total_estimated="1000")),
               "nf_v1.0.0": _ledger()}
    found = enquete.run(entries, {}, [], NOW)
    assert found and found[0]["gravite"] == enquete.GRAVE
    text = enquete.render(found, NOW)
    assert text.startswith("# Enquête automatique") and "[grave]" in text


def _fav_ledger(wins, losses, strategy="champ", price=0.9, **kw):
    """`wins` favoris gagnés, `losses` perdus, tous payés `price`."""
    rows = []
    for i in range(wins + losses):
        t = NOW - timedelta(hours=40 - i)
        rows += [_buy(t, f"{strategy}{i}", price, 10, strategy=strategy, **kw), _settle(t + timedelta(hours=1), f"{strategy}{i}", 1 if i < wins else 0)]
    return _ledger(*rows)


def test_best_of_many_with_a_small_lead_is_not_proof():
    """20/10 : la championne (86 gagnés pour 79,8 attendus, z = 1,86) est la meilleure de ~35 stratégies :
    le hasard seul donne ce z au meilleur de 35."""
    entries = {"champ_v1.0.0": _fav_ledger(44, 6)}  # 44 gagnés pour 45 attendus : pas d'avance du tout
    entries |= {f"autre{i}_v1.0.0": _fav_ledger(45, 5, strategy=f"autre{i}") for i in range(30)}
    entries["chanceuse_v1.0.0"] = _fav_ledger(49, 1, strategy="chanceuse")  # z ≈ +1,9, mais 1 sur 32
    found = enquete.selection_multiple(entries, {"chanceuse_v1.0.0", "champ_v1.0.0"})
    assert [f["titre"].split(" :")[0] for f in found] == ["champ_v1.0.0", "chanceuse_v1.0.0"]
    assert all(f["gravite"] == enquete.A_REGARDER and "choisie parmi 32" in f["titre"] for f in found)
    # Seule, la même stratégie chanceuse (z ≈ 1,9, p = 0,03) serait un signal.
    alone = enquete.selection_multiple({"chanceuse_v1.0.0": _fav_ledger(49, 1, strategy="chanceuse")}, {"chanceuse_v1.0.0"})
    assert alone == []


def test_both_sides_of_one_match_are_reported():
    """17/10 : Team Falcons (0,918, −223 €) puis BetBoom (0,871) sur le même match ; 20/10 : Safiullin puis Shimabukuro."""
    t = NOW - timedelta(hours=5)
    first = _buy(t, "falcons", 0.918, 200, strategy="champ")
    second = _buy(t + timedelta(hours=2), "betboom", 0.871, 25, strategy="champ")
    first["data"]["market_id"] = second["data"]["market_id"] = "5787759"
    one_side = _buy(t, "autre", 0.9, 10, strategy="champ")
    found = enquete.deux_camps({"champ_v1.0.0": _ledger(first, second, one_side)}, NOW - timedelta(days=3))
    assert len(found) == 1 and "1 marché(s)" in found[0]["titre"] and "↔" in found[0]["exemples"][0]
    assert enquete.deux_camps({"champ_v1.0.0": _ledger(first, one_side)}) == []


def test_live_buys_are_counted_from_the_kickoff_field():
    """20/10 : 84 % des achats de la championne ont lieu après le coup d'envoi, malgré un « horizon » de 165 h."""
    rows = []
    for i in range(12):
        row = _buy(NOW - timedelta(hours=20 - i), f"x{i}", 0.9, 10, strategy="champ", horizon="165")
        row["data"]["extra"]["depuis_coup_d_envoi_h"] = "1.50" if i < 9 else "-3.00"
        rows.append(row)
    found = enquete.achats_en_jeu({"champ_v1.0.0": _ledger(*rows)}, {"champ_v1.0.0"})
    assert len(found) == 1 and "9 achats sur 12" in found[0]["titre"]
    # Anciens journaux sans le champ : rien à dire, pas d'erreur.
    old = [_buy(NOW - timedelta(hours=20 - i), f"y{i}", 0.9, 10, strategy="champ") for i in range(12)]
    assert enquete.achats_en_jeu({"champ_v1.0.0": _ledger(*old)}, {"champ_v1.0.0"}) == []


def test_kickoff_hours_are_logged_with_the_buy():
    from polymarket_agent import main
    from types import SimpleNamespace
    start = NOW - timedelta(hours=1.5)
    assert main._depuis_coup_d_envoi(SimpleNamespace(game_start=start), NOW) == {"depuis_coup_d_envoi_h": "1.50"}
    assert main._depuis_coup_d_envoi(SimpleNamespace(game_start=None), NOW) == {}
