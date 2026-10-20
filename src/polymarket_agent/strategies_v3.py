"""Vingt nouvelles pistes (demande d'Etienne, 20/10/2026). Lot A : dix stratégies qui n'utilisent
que les données de Polymarket (prix, carnets, échéances, libellés, structure des événements).
Lot B : le prix de la même question ailleurs (Kalshi, PredictIt, Manifold, bookmakers) et le
compteur de tweets XTracker (references.py).

« Fais une recherche pour 20 stratégies différentes de celles qu'on a déjà (explore de nouvelles
pistes), qui auront elles-mêmes des filles petit à petit. » Aucune n'est supposée rentable : ce
sont des hypothèses que l'arène juge, puis l'entonnoir 80/20 (pareto.py) découpe celles qui
grandissent. Recherche et sources : experiments/vingt_pistes.md.

  1. decroissance_temps   : « … d'ici le 31 ? » : la chance du OUI doit fondre avec le temps qui passe
  2. echelle_dates        : « d'ici juin » ne peut pas valoir plus que « d'ici décembre » (arbitrage)
  3. coherence_match      : gagner de 7,5 points implique de gagner (handicap ≤ vainqueur, arbitrage)
  4. implication_politique: être élu président implique d'être le candidat du parti (arbitrage)
  5. paire_oui_non        : OUI + NON coûtent moins de 1 → acheter les deux (arbitrage)
  6. outsiders_surcotes   : événement à plusieurs issues dont la somme dépasse 1 → NON aux outsiders
  7. marche_neuf          : un marché tout neuf est trop prudent → renforcer le favori
  8. apres_echeance       : échéance passée, résultat presque sûr, pas encore réglé → le favori
  9. marches_jumeaux      : la même question dans deux marchés à deux prix → arbitrage
 10. choc_sans_nouvelle   : gros mouvement sans aucune nouvelle → retour partiel (avec sortie)
"""

from __future__ import annotations

import math
import re
from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from polymarket_agent.fees import UnknownFees, taker_fee
from polymarket_agent.ledger import Position
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.safety_controller import Proposal
from polymarket_agent.strategies_v2 import _Base, _d
from polymarket_agent.strategy_engine import StrategyOutput, make_op_id

ONE = Decimal("1")
DEADLINE = re.compile(r"\b(by|before)\b", re.IGNORECASE)


def _yes_no(m: MarketInfo) -> bool:
    return len(m.token_ids) == 2 and [str(o).lower() for o in m.outcomes] == ["yes", "no"]


def _book_mid(books: dict, token: str) -> float | None:
    b = books.get(token)
    return float(b.mid) if b is not None and b.mid is not None else None


def _now(books: dict) -> datetime | None:
    return max((b.fetched_at for b in books.values() if b.fetched_at is not None), default=None)


class _Arbitrage(_Base):
    """Deux jambes dont l'une au moins paie toujours 1 : on les achète si elles coûtent moins que
    1 − `min_net_edge`, frais compris (même mécanique que cross_market)."""

    required = ("min_net_edge", "stake_fraction", "max_proposals_per_cycle")

    def _pair(self, legs, books, state, marks, out, bucket, tag: str, used: set) -> list[Proposal]:
        books_ = [books.get(m.token_ids[s]) for m, s in legs]
        if any(b is None or b.best_ask is None or not b.asks for b in books_):
            return []
        if any(m.token_ids[s] in state.positions or m.market_id in used for m, s in legs):
            return []
        try:
            costs = [b.best_ask + taker_fee(ONE, b.best_ask, m.fees) for b, (m, _) in zip(books_, legs)]
        except UnknownFees:
            return []
        edge = ONE - sum(costs)
        if edge < self.params["min_net_edge"]:
            return []
        depth = min(b.asks[0].size for b in books_)
        budget = min(self.params["stake_fraction"] * state.total_estimated(marks), state.cash)
        shares = min(depth, budget / sum(costs)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
        props = []
        for (m, s), b in zip(legs, books_):
            mid = float(b.mid or b.best_ask)
            prop = self._buy(m, books, state, s, mid, mid, mid, bucket, marks, out, f"{self.strategy_id}:{tag}",
                             f"arbitrage, marge {edge:.4f} par paire", "une seule jambe exécutée (risque directionnel)",
                             shares=shares, skip_edge=True)
            if prop is None:
                return []
            props.append(prop)
        used.update(m.market_id for m, _ in legs)
        return props

    def _finish_pairs(self, out: StrategyOutput, props: list[Proposal]) -> StrategyOutput:
        out.proposals = props[: 2 * int(self.params["max_proposals_per_cycle"])]
        return out


# --------------------------------------------------------------------------- 1. décroissance du temps


class DecroissanceTemps(_Base):
    """« Est-ce que X arrivera d'ici le 31 ? » : si rien ne se passe, la chance du OUI doit FONDRE à
    mesure que l'échéance approche. Avec un risque constant par heure, la chance d'il y a 6 h
    (prix p6, T6 heures restantes) donne le risque horaire, d'où le prix juste aujourd'hui :
    1 − (1 − p6)^(T / T6). Si le OUI n'a pas baissé autant (« prime d'espoir »), on achète le NON.
    Pas en pleine actualité (pic de mentions au-delà de `max_spike`). Pourquoi ça peut rater : les
    événements se décident souvent juste avant l'échéance (annonces, votes)."""

    strategy_id = "decroissance_temps"
    needs_price_history = True
    required = ("yes_min", "yes_max", "min_hours", "max_hours", "min_gap", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    def _ok(self, m: MarketInfo, now: datetime | None) -> bool:
        if not _yes_no(m) or not DEADLINE.search(m.question or "") or m.end_date is None or now is None:
            return False
        hours = (m.end_date - now).total_seconds() / 3600
        return float(self.params["min_hours"]) <= hours <= float(self.params["max_hours"])

    def candidates(self, markets):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        p = self.params
        out = [m for m in markets if self._ok(m, now) and m.outcome_prices
               and float(p["yes_min"]) <= float(m.outcome_prices[0]) <= float(p["yes_max"])]
        out.sort(key=lambda m: -float(m.volume_24h))
        return out[: int(p.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            if not self._ok(m, now) or any(t in state.positions for t in m.token_ids):
                continue
            mid, p6 = _book_mid(books, m.token_ids[0]), m.yes_price_6h_ago
            if mid is None or p6 is None or not (float(p["yes_min"]) <= mid <= float(p["yes_max"])) or p6 <= 0:
                out.abstain("prix ou historique indisponible")
                continue
            intel = getattr(m, "intel", None)
            if intel is not None and intel.spike > float(p.get("max_spike", 2)):
                out.abstain("actualité en cours")
                continue
            hours = (m.end_date - now).total_seconds() / 3600
            fair = 1 - (1 - min(p6, 0.99)) ** (hours / (hours + 6))
            if mid - fair < float(p["min_gap"]):
                out.abstain("le OUI a déjà fondu")
                continue
            unc = float(p["uncertainty"])
            prop = self._buy(m, books, state, 1, 1 - fair - unc, 1 - fair, 1 - fair + unc, bucket, marks, out,
                             f"decroissance_temps:{fair:.3f}", f"OUI juste {fair:.1%} (risque constant), payé {mid:.1%}",
                             "l'événement se décide juste avant l'échéance")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


# --------------------------------------------------------------------------- 2. échelle de dates


class EchelleDates(_Arbitrage):
    """Même événement, plusieurs échéances (« d'ici juin », « d'ici décembre ») : la plus proche ne
    peut pas valoir plus que la plus lointaine. OUI(lointaine) + NON(proche) paie toujours au
    moins 1 (l'événement arrive avant la date proche, entre les deux, ou jamais)."""

    strategy_id = "echelle_dates"

    @staticmethod
    def _group(markets) -> dict:
        groups = defaultdict(list)
        for m in markets:
            if _yes_no(m) and DEADLINE.search(m.question or "") and m.end_date is not None and m.event_id:
                groups[m.event_id].append(m)
        return {k: sorted(v, key=lambda m: m.end_date) for k, v in groups.items()
                if len({m.end_date.date() for m in v}) >= 2}

    def candidates(self, markets):
        return [m for g in self._group(markets).values() for m in g]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, props, used = StrategyOutput(), [], set()
        for event, items in self._group(watchlist).items():
            for i, near in enumerate(items):
                for far in items[i + 1:]:
                    if far.end_date.date() > near.end_date.date():
                        props += self._pair(((far, 0), (near, 1)), books, state, marks, out, bucket,
                                            f"{event}:{near.end_date:%m%d}<{far.end_date:%m%d}", used)
        return self._finish_pairs(out, props)


# --------------------------------------------------------------------------- 3. cohérence d'un match


SPREAD = re.compile(r"^spread:\s*(.+?)\s*\(-\s*\d", re.IGNORECASE)


class CoherenceMatch(_Arbitrage):
    """Dans un même match : « Spread: Titans (-3.5) » (gagner de plus de 3,5 points) implique « les
    Titans gagnent ». Acheter les Titans au marché « vainqueur » + l'AUTRE équipe au handicap paie
    toujours au moins 1 (grosse victoire, petite victoire : les deux, défaite)."""

    strategy_id = "coherence_match"

    @staticmethod
    def _two_teams(m: MarketInfo) -> bool:
        return len(m.token_ids) == 2 and {str(o).lower() for o in m.outcomes} != {"yes", "no"}

    def _pairs(self, markets):
        from polymarket_agent.pareto import bet_type
        from polymarket_agent.sports_link import same_team
        by_event = defaultdict(list)
        for m in markets:
            if self._two_teams(m) and m.event_id:
                by_event[m.event_id].append(m)
        for items in by_event.values():
            winners = [m for m in items if bet_type(m.question, m.sports_market_type) == "vainqueur"]
            for sp in items:
                hit = SPREAD.match(sp.question or "")
                if not hit or not winners:
                    continue
                team = hit.group(1)
                side_sp = next((i for i, o in enumerate(sp.outcomes) if not same_team(str(o), team)), None)
                for w in winners:
                    side_w = next((i for i, o in enumerate(w.outcomes) if same_team(str(o), team)), None)
                    if side_sp is not None and side_w is not None:
                        yield (w, side_w), (sp, side_sp), team

    def candidates(self, markets):
        return list({id(m): m for a, b, _ in self._pairs(markets) for m in (a[0], b[0])}.values())

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, props, used = StrategyOutput(), [], set()
        for win_leg, sp_leg, team in self._pairs(watchlist):
            props += self._pair((win_leg, sp_leg), books, state, marks, out, bucket, f"{team}", used)
        return self._finish_pairs(out, props)


# --------------------------------------------------------------------------- 4. implication politique


PRESIDENT = re.compile(r"^will (.+?) win the (20\d\d) (?:us |u\.s\. )?presidential election", re.IGNORECASE)
NOMINEE = re.compile(r"^will (.+?) win the (20\d\d) (republican|democratic) presidential nomination", re.IGNORECASE)


class ImplicationPolitique(_Arbitrage):
    """Pour être élu président, il faut (presque toujours) être le candidat de son parti : la chance
    d'être président ne peut pas dépasser celle d'être candidat. NON(président) + OUI(candidat) paie
    toujours au moins 1 (sauf victoire d'un candidat indépendant, risque restant)."""

    strategy_id = "implication_politique"

    @staticmethod
    def _pairs(markets):
        pres, nom = {}, {}
        for m in markets:
            if not _yes_no(m):
                continue
            a, b = PRESIDENT.match(m.question or ""), NOMINEE.match(m.question or "")
            if a:
                pres[(a.group(1).lower(), a.group(2))] = m
            elif b:
                nom[(b.group(1).lower(), b.group(2))] = m
        return [(pres[k], nom[k], k[0]) for k in pres.keys() & nom.keys()]

    def candidates(self, markets):
        return [m for a, b, _ in self._pairs(markets) for m in (a, b)]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, props, used = StrategyOutput(), [], set()
        for pres, nom, name in self._pairs(watchlist):
            props += self._pair(((pres, 1), (nom, 0)), books, state, marks, out, bucket, name, used)
        return self._finish_pairs(out, props)


# --------------------------------------------------------------------------- 5. OUI + NON < 1


class PaireOuiNon(_Arbitrage):
    """Dans un même marché, l'une des deux issues paie 1 : si OUI + NON coûtent moins de 1 (frais
    compris), on achète les deux. Les robots le font en quelques secondes ; on mesure si un cycle
    de 5 minutes en attrape encore."""

    strategy_id = "paire_oui_non"

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, props, used = StrategyOutput(), [], set()
        for m in watchlist:
            if len(m.token_ids) == 2:
                props += self._pair(((m, 0), (m, 1)), books, state, marks, out, bucket, m.market_id, used)
        return self._finish_pairs(out, props)


# --------------------------------------------------------------------------- 6. outsiders surcotés


class OutsidersSurcotes(_Base):
    """Événement à plusieurs issues (« qui sera champion ? ») dont les OUI additionnés dépassent 1 :
    l'excès est surtout payé par les outsiders (biais pour les longs tirs, connu depuis les courses
    de chevaux). Prix juste d'un outsider = son prix ÷ la somme × `longshot_factor` ; on achète son
    NON s'il coûte assez moins que 1 − ce prix juste."""

    strategy_id = "outsiders_surcotes"
    required = ("min_outcomes", "min_overround", "yes_min", "yes_max", "longshot_factor", "uncertainty",
                "min_net_edge", "max_proposals_per_cycle")

    def _events(self, markets, books=None) -> dict:
        groups = defaultdict(list)
        for m in markets:
            if _yes_no(m) and m.neg_risk and m.event_id and not m.neg_risk_other:
                groups[m.event_id].append(m)
        return {k: v for k, v in groups.items() if len(v) >= int(self.params["min_outcomes"])}

    def candidates(self, markets):
        return [m for g in self._events(markets).values() for m in g][: int(self.params.get("max_candidates", 120))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, props = StrategyOutput(), self.params, []
        for event, items in self._events(watchlist).items():
            mids = {m.market_id: _book_mid(books, m.token_ids[0]) for m in items}
            if any(v is None for v in mids.values()):
                continue
            total = sum(mids.values())
            if total < 1 + float(p["min_overround"]):
                out.abstain("pas d'excès dans la somme des OUI")
                continue
            for m in items:
                yes = mids[m.market_id]
                if not (float(p["yes_min"]) <= yes <= float(p["yes_max"])) or any(t in state.positions for t in m.token_ids):
                    continue
                fair = yes / total * float(p["longshot_factor"])
                unc = float(p["uncertainty"])
                prop = self._buy(m, books, state, 1, 1 - fair - unc, 1 - fair, 1 - fair + unc, bucket, marks, out,
                                 f"outsiders_surcotes:{total:.3f}", f"somme des OUI {total:.3f}, outsider juste {fair:.1%}",
                                 "l'outsider gagne vraiment")
                if prop is not None:
                    props.append(prop)
        return self._finish(out, props)


# --------------------------------------------------------------------------- 7. marché tout neuf


class MarcheNeuf(_Base):
    """Les marchés tout neufs (créés il y a moins de `max_age_hours`) ont peu d'échanges : leur prix
    reste souvent trop près de 50/50. Une thèse de Princeton sur Polymarket mesure des prix trop
    prudents en général (pente de recalibrage 1,11). On renforce le favori : chance estimée =
    logistique(`extremize` × logit(prix))."""

    strategy_id = "marche_neuf"
    required = ("max_age_hours", "fav_min", "fav_max", "extremize", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    def _young(self, m: MarketInfo, now: datetime | None) -> bool:
        return (m.created_at is not None and now is not None and len(m.token_ids) == 2
                and (now - m.created_at).total_seconds() / 3600 <= float(self.params["max_age_hours"]))

    def candidates(self, markets):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        out = [m for m in markets if self._young(m, now)]
        out.sort(key=lambda m: m.created_at, reverse=True)
        return out[: int(self.params.get("max_candidates", 30))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            if not self._young(m, now) or any(t in state.positions for t in m.token_ids):
                continue
            mids = [_book_mid(books, t) for t in m.token_ids]
            if None in mids:
                continue
            side = 0 if mids[0] >= mids[1] else 1
            fav = mids[side]
            if not (float(p["fav_min"]) <= fav <= float(p["fav_max"])):
                out.abstain("favori hors de la plage")
                continue
            est = 1 / (1 + math.exp(-float(p["extremize"]) * math.log(fav / (1 - fav))))
            unc = float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - unc, est, est + unc, bucket, marks, out,
                             f"marche_neuf:{est:.3f}", f"marché de moins de {p['max_age_hours']} h, favori renforcé {est:.1%}",
                             "le marché neuf avait raison d'hésiter")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


# --------------------------------------------------------------------------- 8. après l'échéance


class ApresEcheance(_Base):
    """L'échéance est passée, le résultat est presque connu (favori à 0,90-0,985), mais Polymarket
    n'a pas encore réglé le marché (résolution UMA). Le favori finit presque toujours à 1 : on
    l'achète, sauf résolution contestée. Pourquoi ça peut rater : si le prix reste sous 0,99 après
    l'échéance, c'est parfois qu'un doute réel existe (règles ambiguës)."""

    strategy_id = "apres_echeance"
    wants_ended = True  # voit les marchés échus du scanner (ended_pages)
    required = ("fav_min", "fav_max", "est", "uncertainty", "min_net_edge", "max_proposals_per_cycle")

    def candidates(self, markets):
        out = [m for m in markets if m.ended and len(m.token_ids) == 2 and "disputed" not in m.uma_statuses]
        out.sort(key=lambda m: -float(m.volume_24h))
        return out[: int(self.params.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, props = StrategyOutput(), self.params, []
        for m in watchlist:
            if not m.ended or "disputed" in m.uma_statuses or any(t in state.positions for t in m.token_ids):
                continue
            mids = [_book_mid(books, t) for t in m.token_ids]
            if None in mids:
                continue
            side = 0 if mids[0] >= mids[1] else 1
            if not (float(p["fav_min"]) <= mids[side] <= float(p["fav_max"])):
                continue
            est, unc = float(p["est"]), float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - unc, est, min(est + unc, 0.999), bucket, marks, out,
                             "apres_echeance", "échéance passée, favori pas encore réglé",
                             "résolution contestée ou règle ambiguë")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


# --------------------------------------------------------------------------- 9. marchés jumeaux


def _normalized(question: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", (question or "").lower())).strip()


class MarchesJumeaux(_Arbitrage):
    """La même question posée dans deux marchés différents (doublons d'événements) : s'ils n'ont pas
    le même prix, OUI(le moins cher) + NON(l'autre) paie toujours 1. Prudence (vu en direct le
    20/10 : « Will there be no Hormuz agreement? » à 0,931 et 0,871 dans deux événements combinés) :
    même libellé, même description complète et même échéance à la minute, sinon ce ne sont pas
    des jumeaux."""

    strategy_id = "marches_jumeaux"

    @staticmethod
    def _twins(markets):
        groups = defaultdict(list)
        for m in markets:
            if _yes_no(m) and m.end_date is not None:
                groups[(_normalized(m.question), _normalized(m.description), m.end_date)].append(m)
        return [g for g in groups.values() if len({m.market_id for m in g}) >= 2]

    def candidates(self, markets):
        return [m for g in self._twins(markets) for m in g]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, props, used = StrategyOutput(), [], set()
        for g in self._twins(watchlist):
            for a in g:
                for b in g:
                    if a.market_id != b.market_id:
                        props += self._pair(((a, 0), (b, 1)), books, state, marks, out, bucket,
                                            f"{a.market_id}={b.market_id}", used)
        return self._finish_pairs(out, props)


# --------------------------------------------------------------------------- 10. choc sans nouvelle


class ChocSansNouvelle(_Base):
    """Le prix a bougé d'au moins `min_move` en une heure alors qu'AUCUNE nouvelle n'en parle
    (pas de pic de mentions, peu d'articles) : souvent un gros ordre isolé, pas une information.
    On parie sur un retour partiel (`reversion` du mouvement) et on revend : objectif atteint,
    stop ou durée maximale. Différent de price_move (contrer) : ici seulement sans nouvelle."""

    strategy_id = "choc_sans_nouvelle"
    needs_price_history = True
    required = ("min_move", "reversion", "max_mentions", "uncertainty", "min_net_edge", "take_profit",
                "stop_loss", "max_hold_hours", "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, props = StrategyOutput(), self.params, []
        for m in watchlist:
            if not _yes_no(m) or m.yes_price_1h_ago is None or any(t in state.positions for t in m.token_ids):
                continue
            mid = _book_mid(books, m.token_ids[0])
            if mid is None:
                continue
            move = mid - m.yes_price_1h_ago
            if abs(move) < float(p["min_move"]):
                continue
            intel = getattr(m, "intel", None)
            if intel is not None and (intel.spike > 1.5 or intel.mentions_24h > int(p["max_mentions"])):
                out.abstain("le mouvement a une nouvelle")
                continue
            target = mid - float(p["reversion"]) * move  # chance estimée du OUI après le retour
            side = 1 if move > 0 else 0
            est = 1 - target if side == 1 else target
            unc = float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - unc, est, est + unc, bucket, marks, out,
                             f"choc_sans_nouvelle:{move:+.3f}", f"mouvement {move:+.1%} en 1 h sans nouvelle",
                             "une vraie information pas encore publiée")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)

    def exits(self, positions: dict[str, Position], markets: dict[str, MarketInfo],
              books: dict[str, OrderBook], bucket: str, now: datetime) -> list[Proposal]:
        p, sells = self.params, []
        for token_id, pos in positions.items():
            book = books.get(token_id)
            if book is None or book.best_bid is None:
                continue
            held_h = (now - datetime.fromisoformat(pos.opened_at)).total_seconds() / 3600
            gain = book.best_bid - pos.avg_cost
            reason = ("objectif atteint" if gain >= p["take_profit"] else "stop" if gain <= -p["stop_loss"] else
                      "durée maximale" if held_h >= float(p["max_hold_hours"]) else None)
            if reason is None:
                continue
            mid = _d(float(book.mid or book.best_bid))
            sells.append(Proposal(
                op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "SELL"), side="SELL",
                market_id=pos.market_id, event_id=pos.event_id, token_id=token_id, outcome=pos.outcome,
                est_probability=mid, prob_low=mid, prob_high=mid, max_price=book.best_bid, shares=pos.shares,
                net_edge=Decimal("0"), sources=("polymarket_clob",), uncertainty="sortie", invalidation=reason,
                horizon_hours=Decimal("0"), strategy_id=self.strategy_id, strategy_version=self.version))
        return sells


# =========================================================================== lot B : autres sources


class _Reference(_Base):
    """Le prix de la MÊME question sur une autre plateforme (ou chez les bookmakers) sert
    d'estimation (references.py) : on achète le côté que Polymarket vend nettement moins cher,
    marge `margin` retirée. Garde-fous : référence de moins de `max_age_hours` ; écart avec
    Polymarket au plus `max_gap` (au-delà, c'est presque toujours un mauvais rattachement)."""

    ref_key = ""
    required = ("margin", "max_gap", "max_age_hours", "uncertainty", "min_net_edge", "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get(self.ref_key)
            if not ref or not _yes_no(m) or any(t in state.positions for t in m.token_ids):
                continue
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or now is None or (now - seen).total_seconds() > float(p["max_age_hours"]) * 3600:
                out.abstain("référence trop vieille")
                continue
            mid = _book_mid(books, m.token_ids[0])
            prob = float(ref["p"])
            if mid is None or abs(prob - mid) > float(p["max_gap"]):
                out.abstain("écart trop grand (rattachement douteux)")
                continue
            margin, unc, best = float(p["margin"]), float(p["uncertainty"]), None
            for side in (0, 1):
                q = prob if side == 0 else 1 - prob
                prop = self._buy(m, books, state, side, q - margin - unc, q - margin, q - margin + unc, bucket, marks,
                                 out, f"{self.strategy_id}:{prob:.3f}", f"{ref.get('titre', '')[:80]} : {prob:.1%}",
                                 "les deux plateformes ne tranchent pas la même question")
                if prop is not None and (best is None or prop.net_edge > best.net_edge):
                    best = prop
            if best is not None:
                props.append(best)
        return self._finish(out, props)


class KalshiReference(_Reference):
    """Kalshi (plateforme américaine réglementée) : hors sport, sur l'économie, la politique, la
    météo. L'étude de la Fed trouve Kalshi meilleur que le consensus sur l'inflation."""
    strategy_id = "kalshi_reference"
    ref_key = "kalshi"


class PredictItReference(_Reference):
    """PredictIt (politique américaine) : d'autres parieurs, d'autres biais (frais de 10 % sur les
    gains, plafond de 850 $ par contrat)."""
    strategy_id = "predictit_reference"
    ref_key = "predictit"


class ManifoldReference(_Reference):
    """Manifold : monnaie fictive, mais beaucoup de prévisionnistes attentifs sur les questions
    longues ; souvent cité comme bien calibré."""
    strategy_id = "manifold_reference"
    ref_key = "manifold"


class FutursBookmakers(_Reference):
    """Champion de la saison (NBA, NFL, MLB, NHL) : la cote de Pinnacle, marge retirée, contre le
    marché « Will the X win the 2027 NBA Finals? »."""
    strategy_id = "futurs_bookmakers"
    ref_key = "outright"


class FootballTroisIssues(_Reference):
    """Football : victoire, nul ou victoire, chacun dans son marché OUI/NON sur Polymarket ; les
    bookmakers cotent les trois issues ensemble (cotes_bookmakers ne voyait que deux équipes)."""
    strategy_id = "football_trois_issues"
    ref_key = "bookmakers_3"


class CompteurTweets(_Base):
    """« Combien de messages Elon Musk publiera-t-il cette semaine ? » : une tranche par marché
    (« 200-219 »). XTracker (le compteur qui tranche) donne le total déjà compté et le rythme heure
    par heure ; total final ≈ déjà compté + rythme (mélange des `recent_hours` et `long_hours`
    dernières heures) × heures restantes, loi binomiale négative (les rafales de messages sont
    fréquentes, `dispersion`). On achète la tranche (ou son NON) que le marché vend nettement moins
    cher que ce calcul, jamais un billet sous `min_price`. Réglages choisis sur le passé
    (experiments/vingt_pistes.md : 177 périodes de juillet à octobre 2026, +12 % par achat)."""

    strategy_id = "compteur_tweets"
    required = ("dispersion", "recent_hours", "max_stale_hours", "margin", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.references import bucket_of, tweet_bucket_probability
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            tr = getattr(m, "tweets", None)
            if not tr or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            rng = bucket_of(m.group_title)
            last = parse_date(tr.get("vu_le") or "")
            if rng is None:
                out.abstain("tranche illisible")
                continue
            if last is None or (now - last).total_seconds() > float(p["max_stale_hours"]) * 3600:
                out.abstain("compteur pas à jour")
                continue
            prob = tweet_bucket_probability(tr, rng, now, float(p["dispersion"]), int(p["recent_hours"]),
                                            int(p.get("long_hours", 336)), float(p.get("recent_weight", 0.5)))
            if prob is None:
                continue
            margin, unc, best = float(p["margin"]), float(p["uncertainty"]), None
            for side in (0, 1):
                q = prob if side == 0 else 1 - prob
                ask = books.get(m.token_ids[side]).best_ask if books.get(m.token_ids[side]) else None
                if ask is not None and float(ask) < float(p.get("min_price", 0)):
                    out.abstain("billet trop bon marché")  # sur le passé : < 0,10 perdant (-34 %)
                    continue
                prop = self._buy(m, books, state, side, q - margin - unc, q - margin, q - margin + unc, bucket, marks,
                                 out, f"compteur_tweets:{prob:.3f}",
                                 f"{tr.get('compte')} : {tr.get('total')} déjà, tranche {m.group_title} à {prob:.1%}",
                                 "rafale ou silence inhabituel, ou règle de comptage différente")
                if prop is not None and (best is None or prop.net_edge > best.net_edge):
                    best = prop
            if best is not None:
                props.append(best)
        return self._finish(out, props)


CLASSES = {c.strategy_id: c for c in (DecroissanceTemps, EchelleDates, CoherenceMatch, ImplicationPolitique,
                                      PaireOuiNon, OutsidersSurcotes, MarcheNeuf, ApresEcheance, MarchesJumeaux,
                                      ChocSansNouvelle, KalshiReference, PredictItReference, ManifoldReference,
                                      FutursBookmakers, FootballTroisIssues, CompteurTweets)}
