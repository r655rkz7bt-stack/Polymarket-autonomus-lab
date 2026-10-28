"""Mise en service (étape 9) : workflows du cycle et de l'initialisation."""

from __future__ import annotations

import re

import yaml

from conftest import ROOT

WORKFLOWS = ROOT / ".github" / "workflows"


def _load(name):
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    wf = yaml.safe_load(text)
    return text, wf, wf.get("on", wf.get(True)), next(iter(wf["jobs"].values()))


def test_cycle_cannot_be_triggered_by_a_pull_request():
    """Les secrets ne servent qu'au code de main : aucune PR ne déclenche le cycle."""
    _, _, on, job = _load("cycle.yml")
    assert set(on) == {"workflow_dispatch", "schedule"}
    assert job["if"] == "github.ref == 'refs/heads/main'"
    assert job["environment"] == "production"
    assert job["permissions"] == {"contents": "write"}


def test_one_cycle_at_a_time_shared_with_reset_and_initialize():
    for name in ("cycle.yml", "reset-capital.yml", "initialize.yml"):
        _, wf, _, _ = _load(name)
        assert wf["concurrency"] == {"group": "cycle", "cancel-in-progress": False}, name


def test_cycle_never_sees_the_reset_code_and_never_rewrites_the_journal():
    text, _, _, job = _load("cycle.yml")
    assert "RESET_CODE" not in text
    for step in job["steps"]:
        run = step.get("run", "")
        if "--force" in run:  # seul le tableau de bord (gh-pages) est remplacé
            assert "refs/heads/gh-pages" in run and "data" not in run.split("--force", 1)[1]
    assert "git push -q origin HEAD:data" in text


def test_journal_is_saved_even_after_a_cycle_error_but_not_when_corrupt():
    _, _, _, job = _load("cycle.yml")
    by_name = {s.get("name", ""): s for s in job["steps"]}
    save = by_name["Enregistrement du journal (branche data)"]
    assert save["if"] == "steps.run.outputs.code != '2'"
    assert by_name["Échec signalé par e-mail (GitHub) si le cycle a échoué"]["if"] == "steps.run.outputs.code != '0'"


def test_initialize_refuses_an_existing_journal():
    text, _, on, job = _load("initialize.yml")
    assert set(on) == {"workflow_dispatch"}
    assert job["environment"] == "production"
    assert "git ls-remote --exit-code --heads origin data" in text
    assert '"$CONFIRM" != "INITIALISER"' in text
    assert not re.search(r"\$\{\{[^}]*inputs\.confirm[^}]*\}\}\"?\s*!=", text)  # pas d'interpolation dans le shell


def test_secrets_only_where_needed():
    text, _, _, job = _load("cycle.yml")
    with_secrets = [s.get("name") for s in job["steps"] if "secrets." in str(s.get("env", {}))]
    assert with_secrets == ["Cycle", "Rapports et feuille de mission (si le tableau de bord a été régénéré)"]
