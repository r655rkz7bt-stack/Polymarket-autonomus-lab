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
                                "datetime", "pathlib", "polymarket_agent.ledger") for l in imports), imports
