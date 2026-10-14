"""Table de calibration : le marché sous-estime-t-il ou surestime-t-il ses favoris ?

Pour chaque case (groupe de catégories × tranche d'horizon × tranche de prix du
favori), on mesure sur l'historique l'écart moyen δ = (le favori a gagné) − (prix
du favori). Si les prix étaient parfaitement calibrés, δ vaudrait 0 partout.

Prudence statistique :
  - intervalle de confiance par bootstrap sur les ÉVÉNEMENTS (les marchés d'un même
    événement sont liés, ils ne comptent pas comme des observations indépendantes) ;
  - rétrécissement vers 0 (δ × n / (n + k)) : peu de données → estimation proche
    du prix du marché, donc pas d'avantage inventé ;
  - une case n'est utilisable que si elle contient assez d'événements.

La probabilité estimée d'un favori au prix f vaut alors f + δ, avec l'intervalle
[f + δ_bas, f + δ_haut]. Pour l'outsider (prix 1 − f), c'est 1 − (f + δ).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from polymarket_agent.backtest import Outcome, Sample, cluster_mean_ci

PRICE_EDGES = (0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00)
HORIZON_BANDS = ((1, 3), (4, 12), (13, 72))  # heures avant la limite de décision


def category_group(category: str) -> str:
    return category if category in ("sports", "crypto") else "autres"


def horizon_band(hours: float) -> str | None:
    for low, high in HORIZON_BANDS:
        if low <= hours <= high:
            return f"{low}-{high}h"
    return None


def price_band(fav_price: float) -> str | None:
    for low, high in zip(PRICE_EDGES, PRICE_EDGES[1:]):
        if low <= fav_price < high:
            return f"{low:.2f}-{high:.2f}"
    return None


def cell_key(category: str, hours: float, fav_price: float) -> str | None:
    hb, pb = horizon_band(hours), price_band(fav_price)
    if hb is None or pb is None:
        return None
    return f"{category_group(category)}|{hb}|{pb}"


@dataclass(frozen=True)
class Cell:
    key: str
    n_samples: int
    n_events: int
    mean_price: float
    win_rate: float
    delta: float  # δ brut
    delta_low: float  # borne basse de l'intervalle à 90 %, après rétrécissement
    delta_high: float
    delta_shrunk: float


def fit(samples: dict[str, list[Sample]], outcomes: dict[str, Outcome], shrink_k: float = 200,
        n_boot: int = 500, seed: int = 11) -> dict[str, Cell]:
    """Ajuste la table sur un ensemble d'échantillons (en pratique : la période d'entraînement)."""
    by_cell: dict[str, dict[str, list[float]]] = {}
    prices: dict[str, list[float]] = {}
    wins: dict[str, list[int]] = {}
    for market_id, rows in samples.items():
        winner = outcomes[market_id].winner
        for s in rows:
            fav_side = 0 if s.price_yes >= 0.5 else 1
            fav_price = s.price_yes if fav_side == 0 else 1 - s.price_yes
            key = cell_key(s.category, s.horizon_h, fav_price)
            if key is None:
                continue
            won = 1 if winner == fav_side else 0
            by_cell.setdefault(key, {}).setdefault(s.event_id, []).append(won - fav_price)
            prices.setdefault(key, []).append(fav_price)
            wins.setdefault(key, []).append(won)
    table = {}
    for key, clusters in by_cell.items():
        mean, lo, hi, n_events = cluster_mean_ci(clusters, n_boot=n_boot, seed=seed)
        factor = n_events / (n_events + shrink_k)
        n = len(prices[key])
        table[key] = Cell(key, n, n_events, sum(prices[key]) / n, sum(wins[key]) / n, mean,
                          lo * factor, hi * factor, mean * factor)
    return table


def save(table: dict[str, Cell], path: Path, metadata: dict) -> None:
    payload = {"metadata": metadata, "cells": {k: c.__dict__ for k, c in sorted(table.items())}}
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")


def load(path: Path) -> tuple[dict[str, Cell], dict]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: Cell(**v) for k, v in payload["cells"].items()}, payload["metadata"]
