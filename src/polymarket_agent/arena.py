"""Arène : compétition darwinienne entre stratégies (décision d'Etienne, 15/10/2026).

- Chaque stratégie active trade dans son propre journal fantôme (1 000 virtuels, vrais
  carnets). Le classement se fait sur la croissance logarithmique du capital RÉALISÉ.
- Le meilleur en direct devient automatiquement le « champion » : le capital principal
  suit ses décisions, dès qu'il a au moins N opérations clôturées et qu'il bat à la fois
  « ne rien faire » (croissance > 0) et le champion en titre.
- Chaque semaine, la pire stratégie éligible est éliminée (jamais le champion) : sa place
  revient à une nouvelle idée (`scripts/research_brief.py` le signale au chercheur).

Promotions et éliminations sont inscrites dans le journal signé du capital principal.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from polymarket_agent.ledger import Ledger, parse_ts
from polymarket_agent.reporting import closed_trades, read_entries


@dataclass(frozen=True)
class Standing:
    name: str  # « reversion_v1.0.0 »
    closed_trades: int
    realized_capital: float
    initial_capital: float
    log_growth: float
    started_at: datetime | None
    eliminated: bool

    def days(self, now: datetime) -> float:
        return (now - self.started_at).total_seconds() / 86400 if self.started_at else 0.0


def standing(name: str, ledger: Ledger, eliminated: set[str]) -> Standing:
    state = ledger.state
    realized = float(state.realized_capital())
    initial = float(state.initial_capital)
    growth = math.log(realized / initial) if realized > 0 and initial > 0 else float("-inf")
    return Standing(name, len(closed_trades(read_entries(ledger))), realized, initial, growth,
                    state.epoch_started_at, name in eliminated)


def ranking(standings: list[Standing]) -> list[Standing]:
    return sorted(standings, key=lambda s: (s.eliminated, -s.log_growth, -s.closed_trades))


def choose_champion(standings: list[Standing], current: str, min_trades: int,
                    margin: float = 0.0) -> tuple[str, str]:
    """(nouveau champion, raison). "" = ne rien faire."""
    by_name = {s.name: s for s in standings}
    eligible = [s for s in standings
                if not s.eliminated and s.closed_trades >= min_trades and s.log_growth > 0]
    best = max(eligible, key=lambda s: s.log_growth, default=None)
    incumbent = by_name.get(current)
    # Un champion n'est jugé qu'à partir de `min_trades` opérations clôturées.
    incumbent_ok = (incumbent is not None and not incumbent.eliminated
                    and (incumbent.closed_trades < min_trades or incumbent.log_growth > 0))
    if current and not incumbent_ok:
        if best is None:
            return "", "le champion ne bat plus « ne rien faire » (ou a disparu)"
        return best.name, (f"{best.name} remplace un champion déchu : croissance "
                           f"{best.log_growth:+.4f} sur {best.closed_trades} opérations")
    if best is None:
        return current, "aucun challenger éligible"
    if incumbent_ok and best.name != current and best.log_growth <= incumbent.log_growth + margin:
        return current, "le champion reste devant"
    if best.name == current:
        return current, "le champion reste devant"
    return best.name, (f"{best.name} : croissance {best.log_growth:+.4f} sur "
                       f"{best.closed_trades} opérations clôturées")


def choose_elimination(standings: list[Standing], champion: str, last_elimination: datetime | None,
                       now: datetime, min_trades: int, every_days: float,
                       min_days: float) -> Standing | None:
    """La pire stratégie éligible, au plus une fois tous les `every_days` jours."""
    if last_elimination is not None and now - last_elimination < timedelta(days=every_days):
        return None
    pool = [s for s in standings if not s.eliminated and s.name != champion
            and s.closed_trades >= min_trades and s.days(now) >= min_days]
    if len(pool) < 2:  # on garde toujours au moins un concurrent jugé
        return None
    return min(pool, key=lambda s: s.log_growth)


def run_arena(main: Ledger, competitors: dict[str, Ledger], cfg: dict,
              now: datetime | None = None) -> dict:
    """Met à jour champion et éliminations dans le journal principal. Retourne un résumé."""
    now = now or datetime.now(timezone.utc)
    # Attention : chaque écriture remplace main.state par une nouvelle copie ; on relit
    # donc toujours main.state (jamais une référence gardée d'avant l'écriture).
    standings = [standing(name, ledger, main.state.eliminated) for name, ledger in competitors.items()]
    min_trades = int(cfg.get("min_closed_trades", 20))
    events = []
    previous = main.state.champion
    champion, reason = choose_champion(standings, previous, min_trades,
                                       float(cfg.get("promotion_margin", 0.0)))
    if champion != previous:
        main.record_promotion(champion, reason, {"from": previous}, now)
        events.append(f"promotion : {champion or 'ne rien faire'} ({reason})")
    loser = choose_elimination(standings, main.state.champion, main.state.last_elimination_at, now,
                               min_trades, float(cfg.get("elimination_every_days", 7)),
                               float(cfg.get("min_days_before_elimination", 7)))
    if loser is not None:
        main.record_elimination(loser.name, "pire croissance de l'arène",
                                {"log_growth": loser.log_growth, "trades": loser.closed_trades}, now)
        events.append(f"élimination : {loser.name}")
    final = ranking([standing(n, l, main.state.eliminated) for n, l in competitors.items()])
    return {"champion": main.state.champion, "events": events,
            "classement": [s.__dict__ | {"started_at": s.started_at.isoformat() if s.started_at else None}
                           for s in final]}


def days_since_record(ledger: Ledger, now: datetime) -> float:
    """Jours depuis le dernier palier (ou depuis le début de l'époque)."""
    state = ledger.state
    last = parse_ts(state.milestones[-1]["reached_at"]) if state.milestones else state.epoch_started_at
    return (now - last).total_seconds() / 86400 if last else 0.0
