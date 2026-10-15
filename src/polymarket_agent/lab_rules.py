"""Règles de décision rejouables sur l'historique (backtests, recherche, laboratoire).

Déplacées depuis scripts/research_calibration.py (comportement identique) pour que la
recherche protocolaire et le laboratoire utilisent exactement le même code.
"""

from __future__ import annotations

from polymarket_agent import calibration
from polymarket_agent.backtest import Decision, cluster_mean_ci, fee_per_share

HALF_SPREAD = 0.01
MIN_EVENTS = 150
FLOOR = 0.02
MIN_CHANGES = 4  # protocole v2 : prix changé >= 4 fois sur les 24 h précédentes (connu à T)


def naive_v1(sample):
    """Référence naïve v1 (biais a priori non calibré : milieu + 0,05 ± 0,015)."""
    if sample.changes_24h < MIN_CHANGES:
        return None
    fav = 0 if sample.price_yes >= 0.5 else 1
    f = sample.price_yes if fav == 0 else 1 - sample.price_yes
    if not 0.80 <= f + HALF_SPREAD <= 0.95:
        return None
    est = min(f + 0.05, 0.99)
    return Decision(fav, est - 0.015, est, min(est + 0.015, 0.995))


def make_calibrated(table, half_spread=HALF_SPREAD, min_events=MIN_EVENTS, floor=FLOOR):
    def rule(sample):
        if sample.changes_24h < MIN_CHANGES:
            return None
        fav = 0 if sample.price_yes >= 0.5 else 1
        f = sample.price_yes if fav == 0 else 1 - sample.price_yes
        key = calibration.cell_key(sample.category, sample.horizon_h, f)
        cell = table.get(key) if key else None
        if cell is None or cell.n_events < min_events:
            return None
        ask_fav = f + half_spread
        low = f + cell.delta_low
        if ask_fav < 1 and low - ask_fav - fee_per_share(ask_fav, sample.fee_rate) >= floor:
            est = f + cell.delta_shrunk
            return Decision(fav, low, est, min(f + cell.delta_high, 0.995))
        dog = 1 - f
        ask_dog = dog + half_spread
        low_dog = 1 - (f + cell.delta_high)
        if low_dog - ask_dog - fee_per_share(ask_dog, sample.fee_rate) >= floor:
            est = 1 - (f + cell.delta_shrunk)
            return Decision(1 - fav, low_dog, est, min(1 - (f + cell.delta_low), 0.995))
        return None
    return rule


def fit_reversion(samples, outcomes, shrink_k=200):
    """δ des favoris après un mouvement brusque (hausse / baisse >= 0,10 en 6 h)."""
    from polymarket_agent.calibration import Cell
    groups = {"hausse": {}, "baisse": {}}
    prices = {"hausse": [], "baisse": []}
    for market_id, rows in samples.items():
        winner = outcomes[market_id].winner
        for s in rows:
            if s.changes_24h < MIN_CHANGES:
                continue
            move = reversion_move(s)
            if move is None:
                continue
            fav, f, direction = move
            groups[direction].setdefault(s.event_id, []).append((1 if winner == fav else 0) - f)
            prices[direction].append(f)
    table = {}
    for direction, clusters in groups.items():
        mean, lo, hi, n_events = cluster_mean_ci(clusters, n_boot=500, seed=11)
        if not n_events:
            continue
        k = n_events / (n_events + shrink_k)
        n = len(prices[direction])
        table[direction] = Cell(direction, n, n_events, sum(prices[direction]) / n,
                                sum(prices[direction]) / n + mean, mean, lo * k, hi * k, mean * k)
    return table


def reversion_move(sample):
    if sample.price_yes_6h_ago is None:
        return None
    fav = 0 if sample.price_yes >= 0.5 else 1
    f = sample.price_yes if fav == 0 else 1 - sample.price_yes
    before = sample.price_yes_6h_ago if fav == 0 else 1 - sample.price_yes_6h_ago
    if abs(f - before) < 0.10:
        return None
    return fav, f, "hausse" if f > before else "baisse"


def make_reversion(table, half_spread=HALF_SPREAD, min_events=MIN_EVENTS, floor=FLOOR):
    def rule(sample):
        if sample.changes_24h < MIN_CHANGES:
            return None
        move = reversion_move(sample)
        if move is None:
            return None
        fav, f, direction = move
        cell = table.get(direction)
        if cell is None or cell.n_events < min_events:
            return None
        ask_fav = f + half_spread
        low = f + cell.delta_low
        if ask_fav < 1 and low - ask_fav - fee_per_share(ask_fav, sample.fee_rate) >= floor:
            return Decision(fav, low, f + cell.delta_shrunk, min(f + cell.delta_high, 0.995))
        dog = 1 - f
        ask_dog = dog + half_spread
        low_dog = 1 - (f + cell.delta_high)
        if low_dog - ask_dog - fee_per_share(ask_dog, sample.fee_rate) >= floor:
            return Decision(1 - fav, low_dog, 1 - (f + cell.delta_shrunk),
                            min(1 - (f + cell.delta_low), 0.995))
        return None
    return rule


