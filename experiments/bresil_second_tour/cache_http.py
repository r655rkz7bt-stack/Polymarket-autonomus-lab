"""Téléchargements mis en cache pour l'étude du 2e tour au Brésil (données publiques seulement).

Les fichiers bruts vont dans `donnees/` (ignoré par git). Rien n'est envoyé : lectures GET.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from polymarket_agent.http_client import HttpClient, SourceUnavailable  # noqa: E402

DONNEES = Path(__file__).resolve().parent / "donnees"
DONNEES.mkdir(exist_ok=True)
HTTP = HttpClient(timeout=40, min_interval=0.15, max_retries=2)


def cached_json(url: str, params: dict | None = None, name: str | None = None, refresh: bool = False):
    """GET JSON mis en cache sous donnees/<name ou hash>.json. `refresh` force le téléchargement."""
    key = name or hashlib.sha1((url + json.dumps(params or {}, sort_keys=True)).encode()).hexdigest()[:16]
    path = DONNEES / f"{key}.json"
    if path.exists() and not refresh:
        return json.loads(path.read_text())
    data = HTTP.get_json(url, params=params)
    path.write_text(json.dumps(data))
    return data


__all__ = ["cached_json", "HTTP", "DONNEES", "SourceUnavailable"]
