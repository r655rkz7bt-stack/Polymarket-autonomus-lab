"""Chargement de la configuration (fichiers YAML de config/)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"


class ConfigError(Exception):
    pass


def load_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ConfigError(f"impossible de lire {path}") from exc


def load_settings(path: Path | None = None) -> dict:
    settings = load_yaml(path or CONFIG_DIR / "settings.yaml")
    if not isinstance(settings, dict):
        raise ConfigError("settings.yaml : dictionnaire attendu")
    return settings


def resolve(root: Path, relative: str) -> Path:
    path = Path(relative)
    return path if path.is_absolute() else root / path
