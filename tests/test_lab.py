"""Laboratoire : modification bornée des paramètres dans strategies.yaml."""

from __future__ import annotations

import sys

import pytest
import yaml

from conftest import ROOT

sys.path.insert(0, str(ROOT / "scripts"))
from lab import in_bounds, set_param  # noqa: E402


def test_set_param_changes_only_the_target_and_keeps_comments():
    text = (ROOT / "config" / "strategies.yaml").read_text(encoding="utf-8")
    new = set_param(text, "reversion", "min_net_edge", 0.05)
    cfg_old, cfg_new = yaml.safe_load(text), yaml.safe_load(new)
    assert cfg_new["reversion"]["params"]["min_net_edge"]["value"] == 0.05
    assert cfg_new["calibration"]["params"]["min_net_edge"] == cfg_old["calibration"]["params"]["min_net_edge"]
    cfg_old["reversion"]["params"]["min_net_edge"]["value"] = 0.05
    assert cfg_new == cfg_old
    assert new.count("#") == text.count("#")
    with pytest.raises(KeyError):
        set_param(text, "inexistante", "min_net_edge", 0.1)


def test_grid_respects_bounds():
    cfg = yaml.safe_load((ROOT / "config" / "strategies.yaml").read_text(encoding="utf-8"))
    assert in_bounds(cfg, "reversion", "kelly_fraction", 1.0)
    assert not in_bounds(cfg, "reversion", "kelly_fraction", 9.0)
    assert not in_bounds(cfg, "reversion", "inconnu", 1.0)
