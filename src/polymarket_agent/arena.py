"""Arène : compétition darwinienne entre stratégies (décision d'Etienne, 15/10/2026).

- Chaque stratégie active trade dans son propre journal fantôme (1 000 virtuels, vrais
  carnets). Le classement se fait sur la croissance logarithmique du capital RÉALISÉ.
- Le meilleur en direct devient automatiquement le « champion » dès qu'il passe le seuil
  d'ENTRÉE (config/promotion.yaml : opérations clôturées, ancienneté, croissance minimale) et
  bat le champion en titre d'une marge ; il le reste tant que sa croissance dépasse le seuil
  de MAINTIEN, plus bas (hystérésis : pas de va-et-vient sur du bruit).
- Le capital principal se répartit entre les meilleures stratégies éligibles (au plus
  `max_strategies_in_main`), chacune avec une part proportionnelle à sa croissance : la
  somme des parts vaut 1, l'exposition totale reste celle d'une seule stratégie
  (décision d'Etienne, 15/10/2026).
- Une stratégie VALIDÉE sur le passé (test hors échantillon documenté, `validated_strategies`)
  a des seuils d'entrée plus bas : elle reçoit sa part plus tôt (16/10/2026).
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


def _old_enough(s: Standing, now: datetime | None, min_age_hours: float) -> bool:
    return min_age_hours <= 0 or (now is not None and s.days(now) * 24 >= min_age_hours)


def validated_gates(name: str, validated: dict | None) -> dict | None:
    """Seuils d'entrée allégés d'une stratégie VALIDÉE sur le passé (config/promotion.yaml,
    `validated_strategies` : préfixe du nom → seuils), ou None. Le plus long préfixe gagne."""
    hits = [k for k in (validated or {}) if name.startswith(k)]
    return dict(validated[max(hits, key=len)]) if hits else None


def _enters(s: Standing, min_trades: int, now: datetime | None, min_age_hours: float,
            min_growth: float, validated: dict | None = None) -> bool:
    """Seuil d'ENTRÉE (devenir champion ou recevoir une part) : assez d'opérations, assez
    d'ancienneté, et une croissance qui bat « ne rien faire » d'au moins `min_growth`.
    Une stratégie validée sur le passé a ses propres seuils, plus bas ; elle doit quand même
    battre « ne rien faire » en direct (croissance > 0)."""
    own = validated_gates(s.name, validated)
    if own:
        min_trades = int(own.get("min_closed_trades", min_trades))
        min_age_hours = float(own.get("min_age_hours", min_age_hours))
        min_growth = float(own.get("min_log_growth", min_growth))
    return (not s.eliminated and s.closed_trades >= min_trades and s.log_growth > 0
            and s.log_growth >= min_growth and _old_enough(s, now, min_age_hours))


def choose_champion(standings: list[Standing], current: str, min_trades: int,
                    margin: float = 0.0, *, now: datetime | None = None, min_age_hours: float = 0.0,
                    min_growth: float = 0.0, keep_growth: float = 0.0,
                    validated: dict | None = None) -> tuple[str, str]:
    """(nouveau champion, raison). "" = ne rien faire.

    Hystérésis : on entre à `min_growth`, on reste tant que la croissance dépasse `keep_growth`
    (plus bas) ; sinon un champion promu sur du bruit tombe au cycle suivant (15/10/2026)."""
    by_name = {s.name: s for s in standings}
    eligible = [s for s in standings if _enters(s, min_trades, now, min_age_hours, min_growth, validated)]
    best = max(eligible, key=lambda s: s.log_growth, default=None)
    incumbent = by_name.get(current)
    # Un champion n'est jugé qu'à partir de `min_trades` opérations clôturées.
    incumbent_ok = (incumbent is not None and not incumbent.eliminated
                    and (incumbent.closed_trades < min_trades or incumbent.log_growth > keep_growth))
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


def allocation(standings: list[Standing], min_trades: int, max_strategies: int, *,
               now: datetime | None = None, min_age_hours: float = 0.0, min_growth: float = 0.0,
               champion: str = "", keep_growth: float = 0.0,
               validated: dict | None = None) -> dict[str, float]:
    """{stratégie: part du capital principal}. Vide = ne rien faire (aucune stratégie ne passe
    le seuil d'entrée). Le champion garde sa place tant qu'il reste au-dessus de `keep_growth`."""
    def kept(s: Standing) -> bool:
        return (s.name == champion and not s.eliminated and s.closed_trades >= min_trades
                and s.log_growth > max(keep_growth, 0.0))
    eligible = sorted((s for s in standings
                       if _enters(s, min_trades, now, min_age_hours, min_growth, validated) or kept(s)),
                      key=lambda s: s.log_growth, reverse=True)[:max(0, max_strategies)]
    total = sum(s.log_growth for s in eligible)
    return {s.name: s.log_growth / total for s in eligible} if total > 0 else {}


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


INACTIVE = "inactive"  # début du motif d'un retrait pour inactivité (≠ élimination hebdomadaire)


def last_weekly_elimination(main: Ledger) -> datetime | None:
    """Dernière élimination HEBDOMADAIRE (les retraits pour inactivité ne remettent pas le compteur à zéro)."""
    last = None
    for e in read_entries(main):
        if e.get("type") == "ELIMINATION" and not str(e.get("data", {}).get("reason", "")).startswith(INACTIVE):
            last = parse_ts(e["ts"])
    return last


def retire_inactive(main: Ledger, competitors: dict[str, Ledger], standings: list[Standing], cfg: dict,
                    now: datetime) -> list[str]:
    """Ménage (17/10/2026, AMELIORATION n°9) : une stratégie sans aucune opération clôturée ni position
    après `retirer_inactives_apres_jours` jours est retirée (journal signé, comme une élimination).
    Jamais le champion, ni les stratégies listées dans `jamais_retirer` (préfixes)."""
    days = cfg.get("retirer_inactives_apres_jours")
    if not days:
        return []
    keep = tuple(str(k) for k in cfg.get("jamais_retirer") or ())
    out = []
    for s in standings:
        ledger = competitors.get(s.name)
        if (ledger is None or s.eliminated or s.name == main.state.champion or s.closed_trades > 0
                or ledger.state.positions or s.days(now) < float(days) or (keep and s.name.startswith(keep))):
            continue
        main.record_elimination(s.name, f"{INACTIVE} : aucune opération ni position en {float(days):g} jours",
                                {"jours": round(s.days(now), 2)}, now)
        out.append(s.name)
    return out


def run_arena(main: Ledger, competitors: dict[str, Ledger], cfg: dict,
              now: datetime | None = None) -> dict:
    """Met à jour champion et éliminations dans le journal principal. Retourne un résumé."""
    now = now or datetime.now(timezone.utc)
    # Attention : chaque écriture remplace main.state par une nouvelle copie ; on relit
    # donc toujours main.state (jamais une référence gardée d'avant l'écriture).
    standings = [standing(name, ledger, main.state.eliminated) for name, ledger in competitors.items()]
    # Règles obligatoires (config/promotion.yaml) : pas de valeur par défaut silencieuse.
    min_trades = int(cfg["min_closed_trades"])
    gates = {"now": now, "min_age_hours": float(cfg["min_age_hours"]),
             "min_growth": float(cfg["min_log_growth"]), "validated": cfg.get("validated_strategies") or {}}
    keep = float(cfg["keep_log_growth"])
    events = []
    previous = main.state.champion
    champion, reason = choose_champion(standings, previous, min_trades,
                                       float(cfg["promotion_margin"]), keep_growth=keep, **gates)
    if champion != previous:
        main.record_promotion(champion, reason, {"from": previous}, now)
        events.append(f"promotion : {champion or 'ne rien faire'} ({reason})")
    loser = choose_elimination(standings, main.state.champion, last_weekly_elimination(main), now,
                               min_trades, float(cfg["elimination_every_days"]),
                               float(cfg["min_days_before_elimination"]))
    if loser is not None:
        main.record_elimination(loser.name, "pire croissance de l'arène",
                                {"log_growth": loser.log_growth, "trades": loser.closed_trades}, now)
        events.append(f"élimination : {loser.name}")
    events += [f"retrait (inactive) : {n}" for n in retire_inactive(main, competitors, standings, cfg, now)]
    final = ranking([standing(n, l, main.state.eliminated) for n, l in competitors.items()])
    shares = allocation(final, min_trades, int(cfg["max_strategies_in_main"]),
                        champion=main.state.champion, keep_growth=keep, **gates)
    return {"champion": main.state.champion, "events": events, "allocation": shares,
            "classement": [s.__dict__ | {"started_at": s.started_at.isoformat() if s.started_at else None}
                           for s in final]}


def days_since_record(ledger: Ledger, now: datetime) -> float:
    """Jours depuis le dernier palier (ou depuis le début de l'époque)."""
    state = ledger.state
    last = parse_ts(state.milestones[-1]["reached_at"]) if state.milestones else state.epoch_started_at
    return (now - last).total_seconds() / 86400 if last else 0.0
