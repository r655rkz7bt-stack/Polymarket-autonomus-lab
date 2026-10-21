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
- Option A d'Etienne (17/10/2026) : les récompenses de liquidité ESTIMÉES d'une stratégie qui pose
  des ordres (journées terminées, × prudence, liquidity_rewards.ranking_bonus) comptent dans son
  CLASSEMENT, jamais dans son capital fantôme. La tenue de marché, payée surtout ainsi, peut donc
  gagner une part du capital principal.
- Preuves avant promotion (AMELIORATION n°1, 17/10/2026) : en plus des seuils, le « score de
  confiance » des rendements par opération (t de Student : moyenne / erreur type ; rendement =
  résultat / mise, pour que la taille des mises ne compte pas) doit atteindre
  `min_t_stat`. meteo_prevision a été promu le 17/10 avec t = 0,61 (du hasard) et a coûté au
  principal. Puis période d'essai : la part d'une stratégie croît avec ses opérations clôturées
  (`essai`), de `part_minimale` jusqu'à la part entière.
- Modes de jugement (AMELIORATION n°3 et 4) : `juger_sur_recompenses` (tenue de marché : jours de
  récompenses au lieu d'opérations clôturées) et `juger_sur_valeur` (politique, réglée en
  semaines : valeur des positions au prix du carnet au lieu du capital réalisé), chacun avec une
  part plafonnée (`part_max`).
- Plusieurs championnes (décision d'Etienne, 18/10/2026) : toute stratégie qualifiée reçoit une
  part, sans avoir à battre les autres (plus de marge de +1 %) ; pas deux places pour les mêmes
  paris (voir « chevauchement » ci-dessous) ; parts = moitié à égalité, moitié selon les gains
  (`repartition.merite`) ; au plus `part_max_par_strategie` du capital par stratégie. Le titre de
  « champion » (journal signé) reste à la doyenne tant qu'elle est qualifiée : pas de va-et-vient.
- Chevauchement mesuré (décision d'Etienne, 18/10/2026, option B) : au lieu d'« une seule place par
  famille », on compare les matchs/événements réellement achetés par deux qualifiées. Si plus de
  `chevauchement_max` des paris de la plus petite ont aussi été faits par l'autre, ce sont des
  doublons : seule la meilleure prend une place (même famille ou pas). Sinon, chacune a la sienne,
  même deux sœurs. Sans mesure possible (aucun achat), on retombe sur la règle de la famille.
- Priorité aux stratégies prouvées sur le passé (option B d'Etienne, 21/10/2026,
  `priorite_validees`) : dès qu'une stratégie de `validated_strategies` est qualifiée en direct,
  les validées passent devant pour les places et se partagent l'essentiel du capital ; les autres
  qualifiées (la championne comprise) gardent ensemble `part_des_autres`.
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
    rewards: float = 0.0  # récompenses estimées comptées pour le classement (hors capital)
    t_stat: float = 0.0  # score de confiance des résultats par opération (moyenne / erreur type)
    reward_days: int = 0  # journées de récompenses versables (≥ 1 $)
    mode: str = ""  # "" (capital réalisé), "recompenses" ou "valeur" (voir mode_for)
    events: frozenset = frozenset()  # événements (matchs…) achetés depuis le début de l'époque
    day_confidence: float | None = None  # confiance par jour, 0 à 1 (voir day_confidence) ; None = inconnue

    def report(self) -> dict:
        """Version lisible (JSON) : sans la liste des événements."""
        return {k: v for k, v in self.__dict__.items() if k != "events"} | {
            "started_at": self.started_at.isoformat() if self.started_at else None}

    def days(self, now: datetime) -> float:
        return (now - self.started_at).total_seconds() / 86400 if self.started_at else 0.0


def t_stat(values: list[float]) -> float:
    """Moyenne / erreur type (t de Student) ; 0 sous 2 valeurs ; grand si toutes égales et positives."""
    n = len(values)
    if n < 2:
        return 0.0
    m = sum(values) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in values) / (n - 1))
    return round(m / (sd / math.sqrt(n)), 3) if sd > 0 else (99.0 if m > 0 else 0.0)


def confidence_percent(t: float) -> int:
    """Confiance en pourcentage (affichage, demande d'Etienne du 21/10/2026) : probabilité, d'après le
    score t, que le rendement moyen par pari soit vraiment au-dessus de zéro (loi normale).
    t = 0 → 50 % (pile ou face), 1,5 → 93 %, 2 → 98 %, −1,5 → 7 %. Ne tient pas compte du nombre de
    stratégies essayées : sur 96, une au moins dépasse souvent 93 % par chance."""
    return int(round(100 * 0.5 * (1 + math.erf(float(t) / math.sqrt(2)))))


def day_confidence(trades: list[dict]) -> float:
    """Confiance « par jour » (règle mélange, décision d'Etienne du 21/10/2026), de 0 à 1.

    Pour chaque opération, le prix payé est la chance de gagner annoncée par le marché. On compare,
    jour par jour (jour de clôture), les paris gagnés à ceux attendus ; z = somme des écarts / écart
    type, l'écart type étant le plus grand des deux : celui du hasard (Σ p(1−p)) ou celui mesuré
    entre les journées. Une seule journée exceptionnelle (le 18/10) compte donc moins qu'avec t.
    Championne le 21/10 : 85 % (t : 98 %). Rejeu : experiments/regle_confiance.md."""
    days: dict = {}
    var_model = 0.0
    for t in trades:
        cost, bought = float(t.get("cost") or 0), float(t.get("shares_bought") or 0)
        if cost <= 0 or bought <= 0:
            continue
        p = min(max(cost / bought, 0.01), 0.99)
        day = str(t["closed_at"])[:10]
        days[day] = days.get(day, 0.0) + (float(t["pnl"]) > 0) - p
        var_model += p * (1 - p)
    var = max(var_model, sum(e * e for e in days.values()))
    z = sum(days.values()) / math.sqrt(var) if var > 0 else 0.0
    return round(0.5 * (1 + math.erf(z / math.sqrt(2))), 4)


def bought_events(entries: list[dict]) -> frozenset:
    """Événements achetés depuis la dernière remise à zéro (événement Polymarket, sinon marché)."""
    out: set[str] = set()
    for e in entries:
        if e.get("type") == "RESET":
            out.clear()
        elif e.get("type") == "BUY":
            d = e.get("data") or {}
            key = d.get("event_id") or d.get("market_id")
            if key:
                out.add(str(key))
    return frozenset(out)


def overlap(a: Standing, b: Standing) -> float | None:
    """Part des paris de la plus petite des deux que l'autre a aussi faits (0 à 1) ; None sans achat."""
    if not a.events or not b.events:
        return None
    return len(a.events & b.events) / min(len(a.events), len(b.events))


def trade_returns(trades: list[dict]) -> list[float]:
    """Rendement de chaque opération clôturée (résultat / mise), base du score de confiance.

    Pourquoi le rendement et plus le résultat en euros (AMELIORATION du 18/10/2026) : avec des mises
    très inégales (Kelly), le score sur les euros mesurait surtout la TAILLE des mises gagnantes.
    nf_sport affichait 2,7 avec 24 paris gagnés pour 23,4 attendus d'après ses prix (aucun avantage)
    et nf_court 1,2 en gagnant MOINS souvent que ses prix ; sur le rendement : 0,4 et −0,7. Seule
    nf_sport_patiente (40 gagnés pour 36,2 attendus) passe : 2,75."""
    return [float(t["pnl"]) / float(t["cost"]) for t in trades if float(t.get("cost") or 0) > 0]


def mode_for(name: str, modes: dict | None) -> tuple[str, dict]:
    """Mode de jugement d'une stratégie d'après les préfixes de config/promotion.yaml."""
    for mode, key in (("recompenses", "juger_sur_recompenses"), ("valeur", "juger_sur_valeur")):
        table = (modes or {}).get(key) or {}
        hits = [k for k in table if name.startswith(k)]
        if hits:
            return mode, dict(table[max(hits, key=len)] or {})
    return "", {}


def standing(name: str, ledger: Ledger, eliminated: set[str], rewards: float = 0.0, reward_days: int = 0,
             modes: dict | None = None) -> Standing:
    """`rewards` : récompenses estimées (option A), ajoutées au capital réalisé pour la croissance
    seulement ; `realized_capital` reste le vrai capital du fantôme. Mode « valeur » : la croissance
    jugée part du capital total estimé du dernier battement (positions au prix du carnet)."""
    state = ledger.state
    entries = read_entries(ledger)
    trades = closed_trades(entries)
    realized = float(state.realized_capital())
    initial = float(state.initial_capital)
    mode, _ = mode_for(name, modes)
    base = realized
    if mode == "valeur":
        beats = [e for e in entries if e.get("type") == "HEARTBEAT" and (e.get("data") or {}).get("total_estimated")]
        if beats:
            base = float(beats[-1]["data"]["total_estimated"])
    judged = base + max(0.0, rewards)
    growth = math.log(judged / initial) if judged > 0 and initial > 0 else float("-inf")
    return Standing(name, len(trades), realized, initial, growth, state.epoch_started_at, name in eliminated,
                    round(max(0.0, rewards), 4), t_stat(trade_returns(trades)), int(reward_days), mode,
                    bought_events(entries), day_confidence(trades))


def ranking(standings: list[Standing]) -> list[Standing]:
    return sorted(standings, key=lambda s: (s.eliminated, -s.log_growth, -s.closed_trades))


def _old_enough(s: Standing, now: datetime | None, min_age_hours: float) -> bool:
    return min_age_hours <= 0 or (now is not None and s.days(now) * 24 >= min_age_hours)


def validated_gates(name: str, validated: dict | None) -> dict | None:
    """Seuils d'entrée allégés d'une stratégie VALIDÉE sur le passé (config/promotion.yaml,
    `validated_strategies` : préfixe du nom → seuils), ou None. Le plus long préfixe gagne ; une
    valeur vide (`null`) exclut une fille d'une mère validée (21/10/2026)."""
    hits = [k for k in (validated or {}) if name.startswith(k)]
    own = validated[max(hits, key=len)] if hits else None
    return dict(own) if own else None


def _enters(s: Standing, min_trades: int, now: datetime | None, min_age_hours: float,
            min_growth: float, validated: dict | None = None, min_t: float | None = None,
            modes: dict | None = None) -> bool:
    """Seuil d'ENTRÉE (devenir champion ou recevoir une part) : assez d'opérations, assez
    d'ancienneté, une croissance qui bat « ne rien faire » d'au moins `min_growth`, et des résultats
    assez réguliers (score de confiance ≥ `min_t`). Une stratégie validée sur le passé a ses propres
    seuils, plus bas ; elle doit quand même battre « ne rien faire » en direct (croissance > 0).
    Modes : « recompenses » (jours de récompenses au lieu d'opérations, sans score de confiance),
    « valeur » (ancienneté plus longue, croissance au prix du carnet, sans opérations exigées)."""
    own = validated_gates(s.name, validated)
    if own:
        min_trades = int(own.get("min_closed_trades", min_trades))
        min_age_hours = float(own.get("min_age_hours", min_age_hours))
        min_growth = float(own.get("min_log_growth", min_growth))
        min_t = own.get("min_t_stat", min_t)
    if s.eliminated or not (s.log_growth > 0 and s.log_growth >= min_growth):
        return False
    mode, mp = mode_for(s.name, modes)
    if mode == "recompenses":
        return s.reward_days >= int(mp.get("jours_min", 3)) and _old_enough(s, now, min_age_hours)
    if mode == "valeur":
        return _old_enough(s, now, float(mp.get("min_age_hours", 72)))
    return (s.closed_trades >= min_trades and _old_enough(s, now, min_age_hours)
            and (min_t is None or s.t_stat >= float(min_t)))


def mother_map(path=None) -> dict[str, str]:
    """{stratégie: sa mère directe (champ `mere`), "" sans mère} d'après config/strategies.yaml."""
    import yaml
    from pathlib import Path
    path = Path(path) if path else Path(__file__).resolve().parents[2] / "config" / "strategies.yaml"
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    return {sid: str(spec.get("mere") or "") for sid, spec in raw.items() if isinstance(spec, dict)}


def family_map(path=None) -> dict[str, str]:
    """{stratégie: sa famille} d'après config/strategies.yaml : la famille d'une fille est celle de
    sa mère (champ `mere`, en remontant) ; une stratégie sans mère est sa propre famille."""
    mother = mother_map(path)

    def root(sid: str) -> str:
        seen = set()
        while mother.get(sid) and sid not in seen:
            seen.add(sid)
            sid = mother[sid]
        return sid
    return {sid: root(sid) for sid in mother}


def _family(name: str, families: dict | None) -> str:
    base = name.rsplit("_v", 1)[0]
    return (families or {}).get(base, base)


def _twins(a: Standing, b: Standing, families: dict | None, max_overlap: float | None) -> bool:
    """Deux stratégies qui font les mêmes paris (une seule place pour les deux)."""
    shared = overlap(a, b) if max_overlap is not None else None
    if shared is None:  # pas de mesure : une mère et ses filles sont présumées jumelles
        return _family(a.name, families) == _family(b.name, families)
    return shared > max_overlap


def _stays(s: Standing, min_trades: int, keep_growth: float, keep_t: float | None) -> bool:
    """Seuil de MAINTIEN du champion (plus bas que l'entrée : pas de va-et-vient). Un champion
    n'est jugé qu'à partir de `min_trades` opérations clôturées (sauf modes de jugement)."""
    if s.eliminated:
        return False
    if s.closed_trades < min_trades and not s.mode:
        return True
    return s.log_growth > keep_growth and (keep_t is None or bool(s.mode) or s.t_stat >= keep_t)


def choose_champion(standings: list[Standing], current: str, min_trades: int,
                    margin: float | None = 0.0, *, now: datetime | None = None, min_age_hours: float = 0.0,
                    min_growth: float = 0.0, keep_growth: float = 0.0,
                    validated: dict | None = None, min_t: float | None = None,
                    modes: dict | None = None, keep_t: float | None = None) -> tuple[str, str]:
    """(nouveau champion, raison). "" = ne rien faire.

    Hystérésis : on entre à `min_growth`, on reste tant que la croissance dépasse `keep_growth`
    (plus bas) ; sinon un champion promu sur du bruit tombe au cycle suivant (15/10/2026). Depuis le
    18/10 au soir, il faut aussi garder un score de confiance d'au moins `keep_t` (plus bas que
    l'entrée) : un champion qui gagne de l'argent en pariant MOINS bien que ses prix ne reste pas."""
    by_name = {s.name: s for s in standings}
    eligible = [s for s in standings if _enters(s, min_trades, now, min_age_hours, min_growth, validated, min_t, modes)]
    best = max(eligible, key=lambda s: s.log_growth, default=None)
    incumbent = by_name.get(current)
    # Un champion n'est jugé qu'à partir de `min_trades` opérations clôturées.
    incumbent_ok = incumbent is not None and _stays(incumbent, min_trades, keep_growth, keep_t)
    if current and not incumbent_ok:
        if best is None:
            return "", "le champion ne bat plus « ne rien faire » (ou a disparu)"
        return best.name, (f"{best.name} remplace un champion déchu : croissance "
                           f"{best.log_growth:+.4f} sur {best.closed_trades} opérations")
    if best is None:
        return current, "aucun challenger éligible"
    if incumbent_ok and best.name != current and (margin is None or best.log_growth <= incumbent.log_growth + margin):
        # Sans marge (18/10/2026) : le titre reste à la doyenne tant qu'elle est qualifiée ; les
        # autres qualifiées reçoivent quand même leur part du capital (allocation).
        return current, "le champion reste devant" if margin is not None else "le champion reste qualifié"
    if best.name == current:
        return current, "le champion reste devant"
    return best.name, (f"{best.name} : croissance {best.log_growth:+.4f} sur "
                       f"{best.closed_trades} opérations clôturées, confiance t = {best.t_stat:.2f}"
                       + (f", jugée sur {'ses récompenses' if best.mode == 'recompenses' else 'la valeur de ses positions'}"
                          if best.mode else ""))


def allocation(standings: list[Standing], min_trades: int, max_strategies: int, *,
               now: datetime | None = None, min_age_hours: float = 0.0, min_growth: float = 0.0,
               champion: str = "", keep_growth: float = 0.0,
               validated: dict | None = None, min_t: float | None = None,
               modes: dict | None = None, merit: float = 1.0, families: dict | None = None,
               max_overlap: float | None = None, twins: dict | None = None,
               keep_t: float | None = None, others_share: float | None = None) -> dict[str, float]:
    """{stratégie: part du capital principal}. Vide = ne rien faire (aucune stratégie ne passe
    le seuil d'entrée). Le champion garde sa place tant qu'il reste au-dessus de `keep_growth`.
    `twins` (facultatif) reçoit les qualifiées écartées comme doublons : {nom: {comme, chevauchement}}.
    `others_share` (option B d'Etienne, 21/10/2026) : dès qu'une stratégie VALIDÉE sur le passé est
    qualifiée, les validées passent d'abord (places, doublons) et les autres se partagent au plus
    `others_share` du capital ; sans validée qualifiée, rien ne change."""
    def kept(s: Standing) -> bool:
        return (s.name == champion and (s.closed_trades >= min_trades or bool(s.mode))
                and _stays(s, min_trades, max(keep_growth, 0.0), keep_t))

    def proven(s: Standing) -> bool:
        return others_share is not None and validated_gates(s.name, validated) is not None
    ranked = sorted((s for s in standings
                     if _enters(s, min_trades, now, min_age_hours, min_growth, validated, min_t, modes) or kept(s)),
                    key=lambda s: (proven(s), s.log_growth), reverse=True)
    eligible = []
    for s in ranked:  # pas deux places pour les mêmes paris : la meilleure des deux la garde
        twin = next((e for e in eligible if _twins(s, e, families, max_overlap)), None)
        if twin is None:
            eligible.append(s)
        elif twins is not None:
            shared = overlap(s, twin)
            twins[s.name] = {"comme": twin.name, "chevauchement": None if shared is None else round(shared, 3)}
    eligible = eligible[:max(0, max_strategies)]
    first = [s for s in eligible if proven(s)]
    if not first or len(first) == len(eligible):
        return _split(eligible, merit)
    rest = min(1.0, max(0.0, float(others_share)))
    out = {n: w * (1 - rest) for n, w in _split(first, merit).items()}
    out.update({n: w * rest for n, w in _split([s for s in eligible if not proven(s)], merit).items()})
    return out


def _split(group: list[Standing], merit: float) -> dict[str, float]:
    """Moitié à égalité, moitié au mérite (merit = 1 : proportionnel pur à la croissance)."""
    total = sum(s.log_growth for s in group)
    if total <= 0:
        return {}
    k = len(group)
    return {s.name: (1 - merit) / k + merit * s.log_growth / total for s in group}


def exposure(standings: list[Standing], shares: dict[str, float], cfg: dict) -> dict[str, float]:
    """Part RÉELLEMENT engagée de chaque stratégie (≤ sa part) : période d'essai (la part croît avec
    les opérations clôturées, de `part_minimale` à 1 après `pleine_part_apres_operations`) et
    plafond `part_max` des modes « recompenses » et « valeur ». Garde-fou par jour (`garde_fou_jour`,
    21/10/2026) : part multipliée par `reduction` si la confiance par jour est sous `confiance_min`.
    Le reste du capital attend."""
    by = {s.name: s for s in standings}
    guard = cfg.get("garde_fou_jour") or {}
    trial = cfg.get("essai") or {}
    full, floor = float(trial.get("pleine_part_apres_operations", 0)), float(trial.get("part_minimale", 1.0))
    cap = float(cfg.get("part_max_par_strategie") or 1.0)  # plafond commun (18/10/2026)
    out = {}
    for name, w in shares.items():
        s = by.get(name)
        mode, mp = mode_for(name, cfg)
        if mode:
            out[name] = min(w, float(mp.get("part_max", 1.0)))
        elif s is not None and full > 0:
            out[name] = w * min(1.0, max(floor, s.closed_trades / full))
        else:
            out[name] = w
        if (guard and not mode and s is not None and s.day_confidence is not None
                and s.day_confidence < float(guard.get("confiance_min", 0.0))):
            out[name] *= float(guard.get("reduction", 1.0))
    return {n: round(min(v, cap), 6) for n, v in out.items()}


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
HOPELESS = "perdante"  # début du motif d'un retrait pour résultats clairement mauvais (idem)
SURPLUS = "fille en trop"  # retrait d'une fille au-delà de `filles.max_par_mere` (idem, 21/10/2026)
DUPLICATE = "doublon"  # retrait d'une fille qui refait les paris de sa mère ou d'une sœur, sans mieux (idem)


def last_weekly_elimination(main: Ledger) -> datetime | None:
    """Dernière élimination HEBDOMADAIRE (les retraits pour inactivité ne remettent pas le compteur à zéro)."""
    last = None
    for e in read_entries(main):
        if e.get("type") == "ELIMINATION" and not str(e.get("data", {}).get("reason", "")).startswith(
                (INACTIVE, HOPELESS, SURPLUS, DUPLICATE)):
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


def retire_hopeless(main: Ledger, standings: list[Standing], cfg: dict, now: datetime) -> list[str]:
    """Ménage (AMELIORATION du 19/10/2026) : une stratégie qui parie clairement MOINS bien que le
    hasard (score de confiance ≤ `confiance_max` après `min_operations` opérations) est retirée tout
    de suite, sans attendre l'élimination hebdomadaire (une par semaine : news_momentum_patiente
    perdait encore à t = −1,6 après 128 opérations). Depuis le 21/10/2026 (AMELIORATION n°5) : aussi
    quand le capital réalisé est sous `capital_min` après `min_operations` opérations (cotes_bookmakers
    à 625 €, −37 %, gardait t = −0,8). Jamais le champion, ni les modes de jugement (tenue de marché,
    politique), ni `jamais_retirer`."""
    rule = cfg.get("retirer_perdantes") or {}
    if not rule:
        return []
    keep = tuple(str(k) for k in cfg.get("jamais_retirer") or ())
    n_min, t_max = int(rule.get("min_operations", 20)), float(rule.get("confiance_max", -1.5))
    floor = rule.get("capital_min")  # AMELIORATION n°5 du 21/10/2026 : capital réalisé sous ce seuil
    out = []
    for s in standings:
        if (s.eliminated or s.mode or s.name == main.state.champion or s.closed_trades < n_min
                or (keep and s.name.startswith(keep))):
            continue
        if s.t_stat <= t_max:
            reason = f"{HOPELESS} : confiance {s.t_stat:.2f} après {s.closed_trades} opérations"
        elif floor is not None and s.realized_capital < float(floor):
            reason = (f"{HOPELESS} : capital {s.realized_capital:.0f} sous {float(floor):.0f} après "
                      f"{s.closed_trades} opérations")
        else:
            continue
        main.record_elimination(s.name, reason, {"confiance": s.t_stat, "trades": s.closed_trades,
                                                 "capital": round(s.realized_capital, 2)}, now)
        out.append(s.name)
    return out


def _mean_return_since(trades: list[dict], since: datetime | None) -> tuple[float, int]:
    """(rendement moyen par opération, nombre) des opérations clôturées ouvertes depuis `since`."""
    values = trade_returns([t for t in trades if since is None or (parse_ts(t["opened_at"]) or since) >= since])
    return (sum(values) / len(values) if values else 0.0), len(values)


def retire_daughters(main: Ledger, competitors: dict[str, Ledger], standings: list[Standing], cfg: dict,
                     now: datetime, mothers: dict[str, str] | None, qualified=lambda s: False) -> list[str]:
    """Moins de filles (AMELIORATION n°5 du 21/10/2026, `filles` de config/promotion.yaml). Plus on
    teste de variantes, plus l'une gagne par chance (la championne était la meilleure de 43 par
    chance), et plus le cycle ralentit ; naive_favorite et nf_sport_patiente avaient 21 filles chacune.
    Une fille (stratégie qui a une `mere`) est retirée, dans l'ordre :
    1. muette : aucune opération ni position après `inactives_apres_jours` jours ;
    2. doublon : ses paris recoupent ceux de sa mère ou d'une sœur à `doublon_chevauchement` au moins,
       et sur la période commune (au moins `doublon_min_operations` opérations chacune) son rendement
       moyen par opération ne fait pas mieux : son filtre n'apporte rien ;
    3. en trop : au-delà de `max_par_mere` filles vivantes pour une même mère, les plus faibles
       (croissance) parmi celles qui ont au moins `age_min_jours` jours et une croissance sous
       `garder_croissance` (une fille qui gagne vraiment n'est pas retirée pour faire de la place à
       des filles trop jeunes pour être jugées).
    Jamais le champion, une qualifiée (qui a ou peut avoir une part du principal), un mode de
    jugement ni `jamais_retirer`. Comme les autres retraits, ne compte pas pour l'élimination
    hebdomadaire."""
    rule = cfg.get("filles") or {}
    if not rule or not mothers:
        return []
    keep = tuple(str(k) for k in cfg.get("jamais_retirer") or ())
    base = {s.name: s.name.rsplit("_v", 1)[0] for s in standings}
    out: list[str] = []

    def alive(s: Standing) -> bool:
        return s.name not in main.state.eliminated

    def safe(s: Standing) -> bool:
        return (s.name == main.state.champion or bool(s.mode) or (keep and s.name.startswith(keep))
                or bool(qualified(s)))

    def retire(s: Standing, reason: str, data: dict) -> None:
        main.record_elimination(s.name, reason, data, now)
        out.append(s.name)
    kids = [s for s in standings if mothers.get(base[s.name]) and alive(s)]
    days = rule.get("inactives_apres_jours")
    for s in kids:
        ledger = competitors.get(s.name)
        if (days and ledger is not None and not safe(s) and s.closed_trades == 0 and not ledger.state.positions
                and s.days(now) >= float(days)):
            retire(s, f"{INACTIVE} : fille sans opération ni position en {float(days):g} jours",
                   {"jours": round(s.days(now), 2)})
    by_base = {base[s.name]: s for s in standings}
    lim, n_min = rule.get("doublon_chevauchement"), int(rule.get("doublon_min_operations", 20))
    trades: dict[str, list[dict]] = {}  # opérations clôturées, lues une fois par stratégie
    for s in kids:
        if lim is None or not alive(s) or safe(s) or s.closed_trades < n_min:
            continue
        mother = by_base.get(mothers[base[s.name]])
        rivals = ([mother] if mother is not None else []) + [
            k for k in kids if k is not s and mothers[base[k.name]] == mothers[base[s.name]]]
        for r in rivals:
            shared = overlap(s, r)
            if not alive(r) or r.closed_trades < n_min or shared is None or shared < float(lim):
                continue
            starts = [t for t in (s.started_at, r.started_at) if t is not None]
            since = max(starts) if starts else None
            for name in (s.name, r.name):
                if name not in trades:
                    trades[name] = closed_trades(read_entries(competitors[name]))
            (mine, n_mine), (theirs, n_theirs) = (_mean_return_since(trades[s.name], since),
                                                  _mean_return_since(trades[r.name], since))
            if n_mine >= n_min and n_theirs >= n_min and mine <= theirs:
                retire(s, f"{DUPLICATE} de {r.name} : {shared:.0%} de paris communs, rendement {mine:+.1%} "
                          f"contre {theirs:+.1%} par opération", {"comme": r.name, "chevauchement": round(shared, 3)})
                break
    cap, age = rule.get("max_par_mere"), float(rule.get("age_min_jours", 2))
    good = float(rule.get("garder_croissance", float("inf")))
    if cap is not None:
        groups: dict[str, list[Standing]] = {}
        for s in kids:
            if alive(s):
                groups.setdefault(mothers[base[s.name]], []).append(s)
        for mother, group in sorted(groups.items()):
            extra = len(group) - int(cap)
            pool = sorted((s for s in group if not safe(s) and s.days(now) >= age and s.log_growth < good),
                          key=lambda s: (s.log_growth, s.closed_trades))
            for s in pool[:max(0, extra)]:
                retire(s, f"{SURPLUS} : {mother} a {len(group)} filles vivantes (au plus {int(cap)}), "
                          f"croissance {s.log_growth:+.3f}", {"mere": mother, "filles": len(group)})
    return out


def run_arena(main: Ledger, competitors: dict[str, Ledger], cfg: dict,
              now: datetime | None = None, rewards: dict[str, float] | None = None,
              reward_days: dict[str, int] | None = None, families: dict[str, str] | None = None,
              mothers: dict[str, str] | None = None) -> dict:
    """Met à jour champion et éliminations dans le journal principal. Retourne un résumé.
    `rewards` : {nom: récompenses estimées comptées pour le classement} (option A) ;
    `reward_days` : {nom: journées de récompenses versables} (mode « recompenses »)."""
    rewards, reward_days = rewards or {}, reward_days or {}
    now = now or datetime.now(timezone.utc)
    # Attention : chaque écriture remplace main.state par une nouvelle copie ; on relit
    # donc toujours main.state (jamais une référence gardée d'avant l'écriture).
    standings = [standing(name, ledger, main.state.eliminated, rewards.get(name, 0.0), reward_days.get(name, 0), cfg)
                 for name, ledger in competitors.items()]
    # Règles obligatoires (config/promotion.yaml) : pas de valeur par défaut silencieuse.
    min_trades = int(cfg["min_closed_trades"])
    gates = {"now": now, "min_age_hours": float(cfg["min_age_hours"]),
             "min_growth": float(cfg["min_log_growth"]), "validated": cfg.get("validated_strategies") or {},
             "min_t": float(cfg["min_t_stat"]) if cfg.get("min_t_stat") is not None else None, "modes": cfg}
    keep = float(cfg["keep_log_growth"])
    keep_t = None if cfg.get("keep_t_stat") is None else float(cfg["keep_t_stat"])
    events = []
    previous = main.state.champion
    margin = cfg.get("promotion_margin")
    champion, reason = choose_champion(standings, previous, min_trades,
                                       None if margin is None else float(margin), keep_growth=keep, keep_t=keep_t,
                                       **gates)
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
    events += [f"retrait (perdante) : {n}" for n in retire_hopeless(main, standings, cfg, now)]
    events += [f"retrait (fille) : {n}" for n in retire_daughters(
        main, competitors, standings, cfg, now, mothers,
        qualified=lambda s: _enters(s, min_trades, gates["now"], gates["min_age_hours"], gates["min_growth"],
                                    gates["validated"], gates["min_t"], gates["modes"]))]
    final = ranking([standing(n, l, main.state.eliminated, rewards.get(n, 0.0), reward_days.get(n, 0), cfg)
                     for n, l in competitors.items()])
    twins: dict = {}
    max_overlap = cfg.get("chevauchement_max")
    shares = allocation(final, min_trades, int(cfg["max_strategies_in_main"]),
                        champion=main.state.champion, keep_growth=keep,
                        merit=float((cfg.get("repartition") or {}).get("merite", 1.0)), families=families,
                        max_overlap=None if max_overlap is None else float(max_overlap), twins=twins,
                        keep_t=keep_t, others_share=_others_share(cfg), **gates)
    engaged = exposure(final, shares, cfg)
    if not shares and main.state.champion:
        engaged = exposure(final, {main.state.champion: 1.0}, cfg)
    return {"champion": main.state.champion, "events": events, "allocation": shares, "engagement": engaged,
            "doublons": twins, "classement": [s.report() for s in final]}


def _others_share(cfg: dict) -> float | None:
    """`priorite_validees.part_des_autres` (option B, 21/10/2026), ou None (règle désactivée)."""
    rule = cfg.get("priorite_validees") or {}
    value = rule.get("part_des_autres") if isinstance(rule, dict) else None
    return None if value is None else float(value)


def days_since_record(ledger: Ledger, now: datetime) -> float:
    """Jours depuis le dernier palier (ou depuis le début de l'époque)."""
    state = ledger.state
    last = parse_ts(state.milestones[-1]["reached_at"]) if state.milestones else state.epoch_started_at
    return (now - last).total_seconds() / 86400 if last else 0.0
