"""Outils communs de la piste « initiés » (27/10/2026, experiments/inities.md).

Données publiques, sans clé : Gamma (`/public-search`, `/events/<id>`), data-api (`/trades`, `/activity`, `/traded`).
Les téléchargements vont dans experiments/inities/donnees/ (ignoré par Git).
"""

from __future__ import annotations

import gzip
import json
import re
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from polymarket_agent.http_client import HttpClient, SourceUnavailable  # noqa: E402

DONNEES = ROOT / "experiments" / "inities" / "donnees"
DONNEES.mkdir(parents=True, exist_ok=True)
GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
NOM_PAR_DEFAUT = re.compile(r"^0x[0-9a-fA-F]{40}-(\d{12,14})$")  # profil jamais renommé : « adresse-création en ms »
_local = threading.local()


def http() -> HttpClient:
    """Un client par fil (requests.Session n'est pas partagée entre fils)."""
    if not hasattr(_local, "client"):
        _local.client = HttpClient(timeout=30, max_retries=3)
    return _local.client


def lire_gz(path: Path):
    return json.loads(gzip.decompress(path.read_bytes())) if path.exists() else None


def ecrire_gz(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(data).encode()))


__all__ = ["ROOT", "DONNEES", "GAMMA", "DATA", "NOM_PAR_DEFAUT", "http", "lire_gz", "ecrire_gz", "SourceUnavailable"]
