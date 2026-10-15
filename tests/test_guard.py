"""Verrouillage : le contrôle « guard », les workflows GitHub et la réinitialisation manuelle.

« Une modification du code qui supprime une protection est rejetée » (cahier des charges §12) :
toute pull request qui touche un fichier protégé échoue au contrôle `guard`, exigé par le
ruleset de `main` ; elle ne peut donc pas être fusionnée.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys

import pytest
import yaml

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from guard_check import load_patterns, violations  # noqa: E402

PATTERNS = load_patterns((ROOT / "PROTECTED_PATHS.txt").read_text(encoding="utf-8"))
WORKFLOWS = ROOT / ".github" / "workflows"


@pytest.mark.parametrize("path", [
    "src/polymarket_agent/ledger.py", "src/polymarket_agent/safety_controller.py",
    "config/risk_limits.yaml", "config/promotion.yaml", "CLAUDE.md", "PROTECTED_PATHS.txt",
    "tests/test_capital.py", "tests/test_ledger.py", "tests/test_safety_controller.py",
    ".github/workflows/guard.yml", ".github/workflows/nouveau.yml", "scripts/guard_check.py",
    "scripts/reset_capital.py", "tests/test_guard.py",
    # variantes d'écriture qui ne doivent pas contourner le contrôle
    "./CLAUDE.md", "claude.md", "src/polymarket_agent/../polymarket_agent/ledger.py",
    "config\\risk_limits.yaml", ".GITHUB/workflows/x.yml",
])
def test_protected_change_is_blocked(path):
    assert violations(PATTERNS, ["README.md", path]) == [path]


@pytest.mark.parametrize("path", [
    "src/polymarket_agent/strategy_engine.py", "config/strategies.yaml", "config/settings.yaml",
    "README.md", "proposals/idee.md", ".github_notes.md", "src/polymarket_agent/ledger.py.bak/x",
    "tests/test_strategies.py",
])
def test_free_change_passes(path):
    assert violations(PATTERNS, [path]) == []


def test_renaming_a_protected_file_is_blocked():
    """L'API GitHub donne l'ancien nom d'un fichier renommé : le workflow le transmet aussi."""
    assert violations(PATTERNS, ["src/polymarket_agent/ledger_old.py", "src/polymarket_agent/ledger.py"])


def test_empty_rules_are_refused():
    with pytest.raises(ValueError):
        load_patterns("# rien\n\n")


def test_minimum_protected_list_from_claude_md():
    required = {"src/polymarket_agent/safety_controller.py", "src/polymarket_agent/ledger.py",
                "config/risk_limits.yaml", "config/promotion.yaml", "tests/test_capital.py",
                "tests/test_ledger.py", "tests/test_safety_controller.py", ".github/", "CLAUDE.md",
                "PROTECTED_PATHS.txt", "scripts/guard_check.py", "tests/test_guard.py"}
    assert required <= set(PATTERNS)


def test_guard_script_exit_codes(tmp_path):
    rules = tmp_path / "rules.txt"
    rules.write_text("CLAUDE.md\n.github/\n", encoding="utf-8")
    run = lambda stdin: subprocess.run([sys.executable, str(ROOT / "scripts" / "guard_check.py"), str(rules)],
                                       input=stdin, capture_output=True, text=True)
    assert run("README.md\n").returncode == 0
    blocked = run("README.md\n.github/workflows/cycle.yml\n")
    assert blocked.returncode == 1 and "BLOQUÉ" in blocked.stdout


# ----------------------------------------------------------------- workflows

def _workflow(name):
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    return text, yaml.safe_load(text)


def test_guard_workflow_never_runs_pull_request_code():
    text, wf = _workflow("guard.yml")
    on = wf.get("on", wf.get(True))  # PyYAML lit la clé « on » comme le booléen True
    assert "pull_request_target" in on
    assert "pull_request" not in on
    # Le code exécuté est celui de main : jamais de checkout de la tête de la PR.
    assert not re.search(r"pull_request\.head\.(sha|ref)|github\.head_ref", text)
    assert "ref:" not in text
    job = wf["jobs"]["guard"]
    assert job["permissions"] == {"contents": "read", "pull-requests": "read"}


def test_tests_workflow_has_no_secret():
    text, wf = _workflow("tests.yml")
    assert "secrets." not in text and "environment" not in wf["jobs"]["tests"]
    assert wf["jobs"]["tests"]["permissions"] == {"contents": "read"}


def test_reset_workflow_keeps_the_code_out_of_logs():
    text, wf = _workflow("reset-capital.yml")
    job = wf["jobs"]["reset"]
    assert job["environment"] == "production"
    assert set((wf.get("on", wf.get(True)))) == {"workflow_dispatch"}
    # Le code saisi n'est jamais interpolé par GitHub (ni dans une commande, ni dans une variable
    # d'environnement affichée en tête d'étape) : il est lu dans le fichier de l'événement et masqué.
    assert not re.search(r"\$\{\{[^}]*inputs\.code", text)
    assert "::add-mask::" in text and "GITHUB_EVENT_PATH" in text
    assert "secrets.RESET_CODE" in text


def test_actions_are_pinned_to_a_commit():
    for path in WORKFLOWS.glob("*.yml"):
        for ref in re.findall(r"uses:\s*(\S+)", path.read_text(encoding="utf-8")):
            assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", ref), f"{path.name} : {ref}"


# ----------------------------------------------------------------- réinitialisation

@pytest.fixture
def sandbox(tmp_path):
    """Copie minimale du dépôt : les scripts écrivent dans tmp_path, jamais dans le vrai journal."""
    for folder in ("config", "scripts"):
        shutil.copytree(ROOT / folder, tmp_path / folder, ignore=shutil.ignore_patterns("__pycache__"))
    (tmp_path / "src").symlink_to(ROOT / "src")
    env = dict(os.environ, LEDGER_KEY="s" * 64, RESET_CODE="code-secret-etienne-42")
    env.pop("RESET_INPUT", None)

    def run(script, *args, **extra):
        return subprocess.run([sys.executable, str(tmp_path / "scripts" / script), *args],
                              env=dict(env, **extra), capture_output=True, text=True, cwd=tmp_path)
    assert run("initialize.py").returncode == 0
    return tmp_path, run


def _bankrupt(root):
    sys.path.insert(0, str(ROOT / "src"))
    from polymarket_agent.ledger import Ledger
    ledger = Ledger.open(root / "ledger" / "ledger.jsonl", b"s" * 64, root / "ledger" / "BANKRUPT.lock")
    ledger.record_buy(op_id="all-in", token_id="t", market_id="m", event_id="e", outcome="Yes",
                      shares="2000", price="0.5", fee="0", strategy_id="x", strategy_version="0")
    assert ledger.state.bankrupt  # solde disponible à 0 : faillite


def test_reset_script_refuses_a_wrong_or_missing_code(sandbox):
    root, run = sandbox
    _bankrupt(root)
    for extra in ({}, {"RESET_INPUT": "mauvais-code"}):
        result = run("reset_capital.py", "--reason", "test", **extra)
        assert result.returncode == 3 and "REFUS" in result.stdout
        assert "code-secret-etienne-42" not in result.stdout + result.stderr
    assert (root / "ledger" / "BANKRUPT.lock").exists()


def test_reset_script_restarts_with_the_right_code(sandbox):
    root, run = sandbox
    _bankrupt(root)
    result = run("reset_capital.py", "--reason", "Etienne : nouvelle époque",
                 RESET_INPUT="code-secret-etienne-42")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "code-secret-etienne-42" not in result.stdout + result.stderr
    assert not (root / "ledger" / "BANKRUPT.lock").exists()
    from polymarket_agent.ledger import Ledger
    state = Ledger.open(root / "ledger" / "ledger.jsonl", b"s" * 64, root / "ledger" / "BANKRUPT.lock").state
    assert not state.bankrupt and state.epoch == 1 and str(state.cash) == "1000"
