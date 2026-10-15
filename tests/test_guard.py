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
    "src/polymarket_agent/__init__.py", "src/polymarket_agent/execution_simulator.py",
    "src/polymarket_agent/fees.py", "tests/test_execution_simulator.py",
    "config/risk_limits.yaml", "CLAUDE.md", "PROTECTED_PATHS.txt",
    "tests/test_capital.py", "tests/test_ledger.py", "tests/test_safety_controller.py",
    ".github/workflows/guard.yml", ".github/workflows/nouveau.yml", ".github/workflows/cycle.yml",
    ".github/workflows/reset-capital.yml", ".github/dependabot.yml", "scripts/guard_check.py",
    "scripts/reset_capital.py", "requirements-noyau.txt", "tests/test_guard.py",
    "scripts/audit_fills.py", "tests/test_audit_fills.py",
    ".github/workflows/labo-x/../guard.yml", ".github/workflows/labo-x.yaml",
    # variantes d'écriture qui ne doivent pas contourner le contrôle
    "./CLAUDE.md", "claude.md", "src/polymarket_agent/../polymarket_agent/ledger.py",
    "config\\risk_limits.yaml", ".GITHUB/workflows/x.yml",
])
def test_protected_change_is_blocked(path):
    assert violations(PATTERNS, ["README.md", path]) == [path]


@pytest.mark.parametrize("path", [
    "src/polymarket_agent/strategy_engine.py", "config/strategies.yaml", "config/settings.yaml",
    "README.md", "proposals/idee.md", ".github_notes.md", "src/polymarket_agent/ledger.py.bak/x",
    "tests/test_strategies.py", "config/promotion.yaml", "src/polymarket_agent/main.py",
    "scripts/run_simulation.py", "requirements.txt", ".github/workflows/labo-exploration.yml",
    ".GITHUB/workflows/LABO-Exploration.yml",
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
                "src/polymarket_agent/__init__.py", "src/polymarket_agent/execution_simulator.py",
                "src/polymarket_agent/fees.py", "config/risk_limits.yaml", "tests/test_capital.py",
                "tests/test_ledger.py", "tests/test_safety_controller.py", ".github/", "CLAUDE.md",
                "PROTECTED_PATHS.txt", "scripts/guard_check.py", "tests/test_guard.py",
                "scripts/reset_capital.py", "requirements-noyau.txt"}
    assert required <= set(PATTERNS)
    assert [p for p in PATTERNS if p.startswith("!")] == ["!.github/workflows/labo-*.yml"]


def test_reset_only_loads_protected_code():
    """Là où RESET_CODE est présent, aucun fichier libre (modifiable par l'IA) ne s'exécute."""
    import ast
    protected = {"polymarket_agent", "polymarket_agent.ledger", "polymarket_agent.safety_controller"}
    allowed_third_party = {"yaml"}
    stdlib = set(sys.stdlib_module_names)
    for rel in ("scripts/reset_capital.py", "src/polymarket_agent/ledger.py",
                "src/polymarket_agent/safety_controller.py", "src/polymarket_agent/__init__.py"):
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import)
                     else [node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
            for name in names:
                top = name.split(".")[0]
                assert name in protected or top in stdlib or top in allowed_third_party, f"{rel} : {name}"
    noyau = (ROOT / "requirements-noyau.txt").read_text(encoding="utf-8")
    assert [l for l in noyau.splitlines() if l and not l.startswith("#")] == ["PyYAML==6.0.3"]


GOOD_FREE_WORKFLOW = """name: labo-exploration
on:
  workflow_dispatch:
  schedule:
    - cron: "17 3 * * *"
permissions:
  contents: read
jobs:
  explore:
    runs-on: ubuntu-latest
    steps:
      - name: Exploration
        run: echo bonjour
"""


def test_free_workflow_without_secret_or_write_is_accepted():
    from guard_check import workflow_violations
    assert workflow_violations(GOOD_FREE_WORKFLOW) == []


@pytest.mark.parametrize("change", [
    ("        run: echo bonjour", "        run: echo ${{ secrets.LEDGER_KEY }}"),
    ("    runs-on: ubuntu-latest", "    runs-on: ubuntu-latest\n    environment: production"),
    ("  contents: read", "  contents: write"),
    ("permissions:\n  contents: read\n", ""),
    ("  workflow_dispatch:", "  pull_request:"),
    ("  workflow_dispatch:", "  push:"),
    ("  workflow_dispatch:", "  workflow_run:"),
    ("  explore:", "  guard:"),
    ("  explore:", "  tests:"),
    ("      - name: Exploration", "      - name: tests"),
    ("name: labo-exploration", "name: ${{ 'gu' }}ard"),
    ("  contents: read", "  id-token: read"),
])
def test_free_workflow_that_could_reach_secrets_or_imitate_a_check_is_refused(change):
    from guard_check import workflow_violations
    old, new = (c.replace("\\n", "\n") for c in change)
    text = GOOD_FREE_WORKFLOW.replace(old, new)
    assert text != GOOD_FREE_WORKFLOW
    assert workflow_violations(text)


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
    # Le code exécuté est celui de main : jamais de checkout de la tête de la PR. Le sha de la
    # tête ne sert qu'à LIRE le texte des workflows libres via l'API.
    assert not re.search(r"pull_request\.head\.ref|github\.head_ref", text)
    assert "ref:" not in text
    assert text.count("pull_request.head.sha") == 1 and "contents/$f?ref=$HEAD_SHA" in text
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
    # Seul du code protégé s'exécute avec RESET_CODE.
    assert "python -I scripts/reset_capital.py" in text
    assert "requirements-noyau.txt" in text and "-r requirements.txt" not in text


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

    def run(script, *args, isolated=False, **extra):
        flags = ["-I"] if isolated else []
        return subprocess.run([sys.executable, *flags, str(tmp_path / "scripts" / script), *args],
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
        result = run("reset_capital.py", "--reason", "test", isolated=True, **extra)
        assert result.returncode == 3 and "REFUS" in result.stdout
        assert "code-secret-etienne-42" not in result.stdout + result.stderr
    assert (root / "ledger" / "BANKRUPT.lock").exists()


def test_reset_script_restarts_with_the_right_code(sandbox):
    root, run = sandbox
    _bankrupt(root)
    result = run("reset_capital.py", "--reason", "Etienne : nouvelle époque", isolated=True,
                 RESET_INPUT="code-secret-etienne-42")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "code-secret-etienne-42" not in result.stdout + result.stderr
    assert not (root / "ledger" / "BANKRUPT.lock").exists()
    from polymarket_agent.ledger import Ledger
    state = Ledger.open(root / "ledger" / "ledger.jsonl", b"s" * 64, root / "ledger" / "BANKRUPT.lock").state
    assert not state.bankrupt and state.epoch == 1 and str(state.cash) == "1000"
