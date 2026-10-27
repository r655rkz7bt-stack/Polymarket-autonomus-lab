"""Outils communs des analyses « audace » (27/10/2026, experiments/audace.md).

Données : journaux publiés des fantômes (`bash scripts/fetch_data.sh` → published_data/ledger/fantome/), lus par
experiments/regle_confiance/rejouer.py (`load`) : une liste d'opérations clôturées par fantôme, avec `open`, `close`,
`cost` (frais compris), `pnl`, `price` (coût par part, frais compris) et `won`.
Attention : plusieurs fantômes font souvent le même pari (filles, variantes) ; les z qui regroupent des stratégies
comptent ces doublons et sont donc trop forts. Le signe et l'ordre de grandeur restent lisibles.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments" / "regle_confiance"))
sys.path.insert(0, str(ROOT / "src"))

import rejouer  # noqa: E402

SANS = ("market_maker", "market_structure")  # tenue de marché et carnet penché : autre mécanisme, très perdants


def charger() -> dict:
    return rejouer.load()


def bilan(paris: list[dict]) -> dict:
    """Gagnés contre attendus (prix payé = chance annoncée), z, rendement moyen à mise plate et en euros."""
    n = len(paris)
    if not n:
        return {"n": 0, "gagnes": 0, "attendus": 0.0, "z": 0.0, "plat": 0.0, "euros": 0.0, "par_euro": 0.0}
    gagnes = sum(p["won"] for p in paris)
    attendus = sum(p["price"] for p in paris)
    var = sum(p["price"] * (1 - p["price"]) for p in paris)
    mise = sum(p["cost"] for p in paris)
    euros = sum(p["pnl"] for p in paris)
    return {"n": n, "gagnes": gagnes, "attendus": attendus, "z": (gagnes - attendus) / math.sqrt(var) if var else 0.0,
            "plat": sum(p["pnl"] / p["cost"] for p in paris) / n, "euros": euros, "par_euro": euros / mise if mise else 0.0}
