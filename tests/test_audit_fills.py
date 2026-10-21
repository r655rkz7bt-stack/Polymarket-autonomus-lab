"""Audit indépendant des exécutions (noyau protégé) : un prix impossible est signalé."""

from __future__ import annotations

import importlib.util
from datetime import timedelta

from conftest import KEY, NOW, ROOT, buy
from polymarket_agent.ledger import Ledger


def _audit_module():
    spec = importlib.util.spec_from_file_location("audit_fills", ROOT / "scripts" / "audit_fills.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _data(tmp_path):
    base = tmp_path / "ledger"
    main = Ledger.create(base / "ledger.jsonl", KEY, base / "BANKRUPT.lock", "1000", now=NOW)
    shadow_path = base / "fantome" / "s_v1.jsonl"
    shadow = Ledger.create(shadow_path, KEY, shadow_path.with_suffix(".BANKRUPT.lock"), "1000", now=NOW)
    return main, shadow


def test_impossible_price_is_an_anomaly_and_plausible_one_is_not(tmp_path):
    audit = _audit_module()
    main, shadow = _data(tmp_path)
    buy(main, "b1", token="tok-ok", shares="10", price="0.50")
    buy(shadow, "b2", token="tok-faux", shares="10", price="0.10")  # le marché n'est jamais passé sous 0,40
    shadow.record_sell(op_id="s2", token_id="tok-faux", shares="10", price="0.95", fee="0", now=NOW)
    prices = {"tok-ok": [0.48, 0.52], "tok-faux": [0.40, 0.45]}
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=1), fetch=lambda t, ts: prices[t])
    assert new == 2 and state["verifiees"] == 1
    details = [a["detail"] for a in state["anomalies"]]
    assert any("achat à 0.1000" in d for d in details) and any("vente à 0.9500" in d for d in details)
    # Deuxième passage : rien de nouveau, rien n'est revérifié.
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=2), fetch=lambda t, ts: prices[t])
    assert new == 0 and state["verifiees"] == 1 and len(state["anomalies"]) == 2


def test_recent_unreachable_or_quiet_markets_are_handled(tmp_path):
    audit = _audit_module()
    main, _ = _data(tmp_path)
    buy(main, "b1", token="calme", shares="10", price="0.5")
    buy(main, "b2", token="recent", shares="10", price="0.5", now=NOW + timedelta(minutes=55))
    # Historique injoignable : on réessaie plus tard, sans rien conclure.
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=1), fetch=lambda t, ts: None)
    assert new == 0 and state["verifiees"] == 0 and state["dernier_seq"]["principal"] == 0
    # Marché sans échange : « non vérifiable » ; exécution trop récente : attend le passage suivant.
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=1), fetch=lambda t, ts: [])
    assert state["non_verifiables"] == 1 and state["dernier_seq"]["principal"] == 1
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=2), fetch=lambda t, ts: [0.5])
    assert state["verifiees"] == 1 and new == 0


def test_tampered_ledger_is_reported(tmp_path):
    audit = _audit_module()
    main, _ = _data(tmp_path)
    buy(main, "b1", shares="10", price="0.5")
    path = tmp_path / "ledger" / "ledger.jsonl"
    path.write_text(path.read_text().replace('"0.5', '"0.1'), encoding="utf-8")
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=1), fetch=lambda t, ts: [0.5])
    assert new == 1 and "journal illisible" in state["anomalies"][0]["detail"]


def test_audit_script_only_imports_protected_code():
    """Lancé avec python -I -S sur une machine où aucun code libre n'a tourné : il ne doit
    importer que ledger.py et la bibliothèque standard."""
    text = (ROOT / "scripts" / "audit_fills.py").read_text(encoding="utf-8")
    imports = [l for l in text.splitlines() if l.startswith(("import ", "from "))]
    assert all(l.split()[1] in ("__future__", "argparse", "json", "sys", "urllib.parse", "urllib.request",
                                "datetime", "decimal", "pathlib", "polymarket_agent.ledger") for l in imports), imports


def _market(token, prices, closed=True, status="resolved", other="tok-autre"):
    import json
    return {"closed": closed, "umaResolutionStatus": status, "clobTokenIds": json.dumps([token, other]),
            "outcomePrices": json.dumps(prices)}


def test_settlements_are_checked_against_the_official_resolution(tmp_path):
    audit = _audit_module()
    main, shadow = _data(tmp_path)
    buy(main, "b1", token="gagne", shares="10", price="0.5")
    main.record_settlement(op_id="s1", token_id="gagne", payout_per_share="1", resolution="Yes", now=NOW)
    buy(shadow, "b2", token="perdu", shares="10", price="0.5")
    # Faux règlement : le marché a été perdu (prix final 0) mais le journal inscrit 1 par part.
    shadow.record_settlement(op_id="s2", token_id="perdu", payout_per_share="1", resolution="Yes", now=NOW)
    markets = {"m-gagne": _market("gagne", ["1", "0"]), "m-perdu": _market("perdu", ["0", "1"])}
    asked = []

    def fetch_market(mid):
        asked.append(mid)
        return markets[mid]
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=1), fetch=lambda t, ts: [0.5],
                             fetch_market=fetch_market)
    assert new == 1 and state["reglements_verifies"] == 1 and sorted(asked) == ["m-gagne", "m-perdu"]
    assert state["anomalies"][-1]["type"] == "SETTLE"
    assert "payé 1 par part, résultat officiel 0" in state["anomalies"][-1]["detail"]
    # Deuxième passage : rien n'est revérifié.
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(hours=2), fetch=lambda t, ts: [0.5],
                             fetch_market=fetch_market)
    assert new == 0 and len(asked) == 2


def test_settlement_of_an_open_market_is_an_anomaly_and_a_pending_one_waits(tmp_path):
    audit = _audit_module()
    main, _ = _data(tmp_path)
    buy(main, "b1", token="tA", shares="10", price="0.5")
    main.record_settlement(op_id="s1", token_id="tA", payout_per_share="1", resolution="Yes", now=NOW)
    later = NOW + timedelta(hours=1)
    # API injoignable, puis litige en cours : on attend, sans rien conclure.
    state, new = audit.audit(tmp_path, KEY, later, fetch=lambda t, ts: [0.5], fetch_market=lambda m: None)
    assert new == 0 and state["dernier_seq_reglements"]["principal"] < 2
    disputed = _market("tA", ["0.6", "0.4"], status="disputed")
    state, new = audit.audit(tmp_path, KEY, later, fetch=lambda t, ts: [0.5], fetch_market=lambda m: disputed)
    assert new == 0 and state["reglements_verifies"] == 0
    # Toujours pas définitif après 3 jours : anomalie.
    state, new = audit.audit(tmp_path, KEY, NOW + timedelta(days=4), fetch=lambda t, ts: [0.5],
                             fetch_market=lambda m: disputed)
    assert new == 1 and "pas définitive" in state["anomalies"][-1]["detail"]


def test_settlement_checks_cover_every_rule():
    audit = _audit_module()
    entry = {"data": {"token_id": "t", "payout_per_share": "0.5"}}
    assert audit.check_settlement(entry, "m", _market("t", ["0.5", "0.5"]), 0)[0] == "ok"
    assert audit.check_settlement(entry, None, None, 0)[0] == "anomalie"
    assert "n'est pas clos" in audit.check_settlement(entry, "m", _market("t", ["0.5", "0.5"], closed=False), 0)[1]
    assert "ne fait pas partie" in audit.check_settlement(entry, "m", _market("x", ["0.5", "0.5"], other="y"), 0)[1]
    bad = {"data": {"token_id": "t", "payout_per_share": "abc"}}
    assert audit.check_settlement(bad, "m", _market("t", ["1", "0"]), 0)[0] == "anomalie"



def test_rewards_are_checked_only_the_principal_may_receive_them(tmp_path):
    """21/10/2026 : une récompense dans un fantôme est une anomalie ; dans le principal, son montant
    ne dépasse ni la somme de ses détails ni, marché par marché, la cagnotte du jour."""
    audit = _audit_module()
    main, shadow = _data(tmp_path)
    later = NOW + timedelta(days=1)
    day = NOW.date().isoformat()
    main.record_reward(day=day, amount="2", source="liquidite",
                       details=[{"market_id": "m1", "montant": 3.0, "cagnotte": 10.0}], now=later)
    main.record_reward(day=day, amount="5", source="detention", details=[{"market_id": "m2", "montant": 4.0}],
                       now=later)
    shadow.record_reward(day=day, amount="1", source="liquidite",
                         details=[{"market_id": "m1", "montant": 2.0, "cagnotte": 10.0}], now=later)
    state, new = audit.audit(tmp_path, KEY, later + timedelta(hours=1), fetch=lambda t, ts: [])
    assert state["recompenses_verifiees"] == 1 and new == 2
    details = sorted(a["detail"] for a in state["anomalies"])
    assert any("fantôme" in d for d in details) and any("supérieure à la somme" in d for d in details)
    assert audit.check_reward("principal", {"data": {"amount": "1", "details": [
        {"market_id": "m", "montant": 12.0, "cagnotte": 10.0}]}})[0] == "anomalie"
    assert audit.check_reward("principal", {"data": {"amount": "1"}})[0] == "anomalie"
