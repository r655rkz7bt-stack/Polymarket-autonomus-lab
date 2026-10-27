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


def _with_reference(markets, key: str, limit: int) -> list[MarketInfo]:
    """Marchés scannés qui portent la référence `key` (rattachée en amont à tous les marchés,
    21/10/2026), les plus actifs d'abord : la stratégie les demande au scanner (`candidates`)."""
    out = [m for m in markets if (getattr(m, "references", None) or {}).get(key)]
    out.sort(key=lambda m: -float(m.volume_24h or 0))
    return out[:limit]


def _now(books: dict) -> datetime | None:
    return max((b.fetched_at for b in books.values() if b.fetched_at is not None), default=None)


class _Arbitrage(_Base):
    """Deux jambes dont l'une au moins paie toujours 1 : on les achète si elles coûtent moins que
    1 − `min_net_edge`, frais compris (même mécanique que cross_market)."""

    required = ("min_net_edge", "stake_fraction", "max_proposals_per_cycle")

    def _pair(self, legs, books, state, marks, out, bucket, tag: str, used: set) -> list[Proposal]:
        books_ = [books.get(m.token_ids[s]) for m, s in legs]
        # Raisons d'abstention (21/10/2026, « réveiller les muettes ») : sans elles, le tableau de bord
        # ne disait pas pourquoi un arbitrage n'achetait rien (paires absentes ou écart insuffisant).
        if any(b is None or b.best_ask is None or not b.asks for b in books_):
            out.abstain("une jambe sans vendeur")
            return []
        if any(m.token_ids[s] in state.positions or m.market_id in used for m, s in legs):
            out.abstain("position déjà ouverte")
            return []
        try:
            costs = [b.best_ask + taker_fee(ONE, b.best_ask, m.fees) for b, (m, _) in zip(books_, legs)]
        except UnknownFees:
            out.abstain("frais inconnus")
            return []
        edge = ONE - sum(costs)
        if edge < self.params["min_net_edge"]:
            out.abstain("paire cohérente : aucun écart après frais")
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

    def _finish_pairs(self, out: StrategyOutput, props: list[Proposal], pairs_seen: int | None = None) -> StrategyOutput:
        if pairs_seen == 0:
            out.abstain("aucune paire complète parmi les marchés vus")
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
        out, props, used, seen = StrategyOutput(), [], set(), 0
        for event, items in self._group(watchlist).items():
            for i, near in enumerate(items):
                for far in items[i + 1:]:
                    if far.end_date.date() > near.end_date.date():
                        seen += 1
                        props += self._pair(((far, 0), (near, 1)), books, state, marks, out, bucket,
                                            f"{event}:{near.end_date:%m%d}<{far.end_date:%m%d}", used)
        return self._finish_pairs(out, props, seen)


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
        out, props, used, seen = StrategyOutput(), [], set(), 0
        for win_leg, sp_leg, team in self._pairs(watchlist):
            seen += 1
            props += self._pair((win_leg, sp_leg), books, state, marks, out, bucket, f"{team}", used)
        return self._finish_pairs(out, props, seen)


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
        pairs = self._pairs(watchlist)
        for pres, nom, name in pairs:
            props += self._pair(((pres, 1), (nom, 0)), books, state, marks, out, bucket, name, used)
        return self._finish_pairs(out, props, len(pairs))


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
        out, p, props, now = StrategyOutput(), self.params, [], _now(books)
        # 23/10/2026 : « échéance passée » = coup d'envoi pour un match (Gamma ne donne qu'une date placeholder) ; 140 des 173 achats
        # étaient faits 1 à 2 h après le coup d'envoi (-7,8 %), et 8 jambes du même Cavaliers-76ers (-474 €) pendant le match.
        min_hours = float(p.get("heures_apres_coup_d_envoi_min", 0))
        events = {pos.event_id for pos in state.positions.values() if pos.event_id}
        for m in watchlist:
            if not m.ended or "disputed" in m.uma_statuses or any(t in state.positions for t in m.token_ids):
                continue
            if m.game_start is not None and now is not None and (now - m.game_start).total_seconds() < min_hours * 3600:
                out.abstain("match probablement en cours")
                continue
            if m.event_id and m.event_id in events:  # moneyline, écarts et totaux d'un même match : un seul pari
                out.abstain("événement déjà joué")
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
                events.add(m.event_id)
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
        twins = self._twins(watchlist)
        for g in twins:
            for a in g:
                for b in g:
                    if a.market_id != b.market_id:
                        props += self._pair(((a, 0), (b, 1)), books, state, marks, out, bucket,
                                            f"{a.market_id}={b.market_id}", used)
        return self._finish_pairs(out, props, len(twins))


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


# --------------------------------------------------------------------------- vague de volume


class VagueVolume(_Base):
    """Vague de volume (22/10/2026, idée des skills Polymarket de mjunaidca, `momentum_scanner`) : un
    marché qui s'échange au moins `surge_min` fois plus que sa moyenne des 7 derniers jours (Gamma :
    volume du jour contre volume de la semaine / 7), et dont le prix du OUI a bougé d'au moins
    `min_move` en 24 h (marchés d'au moins `min_age_days` jours). `direction` = 1 : on SUIT le mouvement (la foule a une information) ;
    `direction` = -1 : on le CONTRE (la foule s'emballe). Chance estimée = milieu du carnet de l'issue
    achetée + `shift`. Pas testée sur le passé (Gamma ne garde pas le volume de la semaine d'hier) :
    l'arène mesure les deux sens. Pourquoi ça peut rater : une vague de volume suit souvent une
    nouvelle déjà dans le prix."""

    strategy_id = "vague_volume"
    required = ("surge_min", "min_move", "side_min", "side_max", "shift", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    def _surge(self, m: MarketInfo, now: datetime | None) -> float | None:
        """Volume du jour ÷ moyenne des jours PRÉCÉDENTS de la semaine. Un marché de moins de
        `min_age_days` jours n'a pas de référence (créé hier : volume de la semaine = volume du jour,
        fausse vague ×7, vu le 22/10 sur les marchés météo du jour)."""
        if not _yes_no(m) or m.created_at is None or now is None:
            return None
        # Près de l'échéance (Bitcoin du jour, match du soir), le volume monte toujours : pas une information.
        if m.end_date is None or (m.end_date - now).total_seconds() / 3600 < float(self.params.get("min_hours_to_end", 48)):
            return None
        age = (now - m.created_at).total_seconds() / 86400
        if age < float(self.params.get("min_age_days", 3)):
            return None
        days = min(7.0, age)
        before = (float(m.volume_1wk or 0) - float(m.volume_24h or 0)) / max(days - 1, 1)
        # Marché endormi (quelques dollars par jour) : un rapport ×8 000 ne veut rien dire.
        if before < float(self.params.get("min_base_volume", 500)):
            return None
        return float(m.volume_24h or 0) / before

    def candidates(self, markets) -> list[MarketInfo]:
        from datetime import timezone
        p, now = self.params, datetime.now(timezone.utc)
        out = [(r, m) for m in markets for r in [self._surge(m, now)] if r is not None and r >= float(p["surge_min"])
               and m.price_change_1d is not None and abs(m.price_change_1d) >= float(p["min_move"])]
        out.sort(key=lambda x: -x[0])
        return [m for _, m in out[: int(p.get("max_candidates", 30))]]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, props, now = StrategyOutput(), self.params, [], _now(books)
        follow = int(p.get("direction", 1)) >= 0
        for m in watchlist:
            ratio = self._surge(m, now)
            if ratio is None or any(t in state.positions for t in m.token_ids):
                continue
            if ratio < float(p["surge_min"]):
                continue
            move = m.price_change_1d
            if move is None or abs(move) < float(p["min_move"]):
                out.abstain("vague de volume sans mouvement de prix")
                continue
            rose = 0 if move > 0 else 1  # issue dont le prix a monté : OUI si le OUI a monté, sinon NON
            side = rose if follow else 1 - rose
            mid = _book_mid(books, m.token_ids[side])
            if mid is None:
                out.abstain("carnet indisponible")
                continue
            if not float(p["side_min"]) <= mid <= float(p["side_max"]):
                out.abstain("issue hors de la plage de prix")
                continue
            est, unc = mid + float(p["shift"]), float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - unc, est, est + unc, bucket, marks, out,
                             f"vague_volume:{ratio:.1f}x:{move:+.3f}",
                             f"volume ×{ratio:.1f} contre la semaine, prix {move:+.1%} en 24 h",
                             "la vague était déjà dans le prix" if follow else "la foule avait raison")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


# =========================================================================== lot B : autres sources


class _Reference(_Base):
    """Le prix de la MÊME question sur une autre plateforme (ou chez les bookmakers) sert
    d'estimation (references.py) : on achète le côté que Polymarket vend nettement moins cher,
    marge `margin` retirée. Garde-fous : référence de moins de `max_age_hours` ; écart avec
    Polymarket au plus `max_gap` (au-delà, c'est presque toujours un mauvais rattachement)."""

    ref_key = ""
    required = ("margin", "max_gap", "max_age_hours", "uncertainty", "min_net_edge", "max_proposals_per_cycle")

    def candidates(self, markets) -> list[MarketInfo]:
        return _with_reference(markets, self.ref_key, int(self.params.get("max_candidates", 25)))

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
            if not self._usable(ref, out):
                continue
            margin, unc, best = float(p["margin"]), float(p["uncertainty"]), None
            for side in (0, 1):
                q = prob if side == 0 else 1 - prob
                book = books.get(m.token_ids[side])
                if book is not None and book.best_ask is not None and float(book.best_ask) < float(p.get("min_price", 0)):
                    out.abstain("billet trop bon marché")
                    continue
                prop = self._buy(m, books, state, side, q - margin - unc, q - margin, q - margin + unc, bucket, marks,
                                 out, f"{self.strategy_id}:{prob:.3f}", f"{ref.get('titre', '')[:80]} : {prob:.1%}",
                                 "les deux plateformes ne tranchent pas la même question")
                if prop is not None and (best is None or prop.net_edge > best.net_edge):
                    best = prop
            if best is not None:
                props.append(best)
        return self._finish(out, props)

    def _usable(self, ref: dict, out: StrategyOutput) -> bool:
        return True


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

    def candidates(self, markets) -> list[MarketInfo]:
        """Les cotes à 3 issues sont rattachées plus tard (marchés surveillés) : on demande les marchés
        « Will X win on AAAA-MM-JJ? » et « Will A vs. B end in a draw? » d'après leur libellé."""
        from polymarket_agent.references import DRAW, WIN_ON
        out = [m for m in markets if _yes_no(m) and (WIN_ON.match((m.question or "").strip())
                                                       or DRAW.match((m.question or "").strip()))]
        out.sort(key=lambda m: -float(m.volume_24h or 0))
        return out[: int(self.params.get("max_candidates", 30))]


class CompteurTweets(_Base):
    """« Combien de messages Elon Musk publiera-t-il cette semaine ? » : une tranche par marché
    (« 200-219 »). XTracker (le compteur qui tranche) donne le total déjà compté et le rythme heure
    par heure ; total final ≈ déjà compté + rythme (mélange des `recent_hours` et `long_hours`
    dernières heures) × heures restantes, loi binomiale négative (les rafales de messages sont
    fréquentes, `dispersion`). On achète la tranche (ou son NON) que le marché vend nettement moins
    cher que ce calcul, jamais un billet sous `min_price`. Réglages choisis sur le passé
    (experiments/vingt_pistes.md : 177 périodes de juillet à octobre 2026, +12 % par achat).
    Réglages optionnels (fille « NON sans NYC Mayor », 21/10/2026, experiments/tweets_filles.md) :
    `only_no` = 1 n'achète que le NON ; `skip_nyc` = 1 ignore le compte NYC Mayor ; `skip_elon_trump` = 1 ignore Elon Musk et Trump ;
    `only_trump` = 1 ne joue que les posts Truth Social de Trump (compte `realDonaldTrump` de XTracker, 25/10/2026, experiments/truth_social.md)."""

    strategy_id = "compteur_tweets"
    required = ("dispersion", "recent_hours", "max_stale_hours", "margin", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    def candidates(self, markets) -> list[MarketInfo]:
        out = [m for m in markets if getattr(m, "tweets", None)]
        out.sort(key=lambda m: -float(m.volume_24h or 0))
        return out[: int(self.params.get("max_candidates", 60))]

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
            if float(p.get("skip_nyc", 0)) and str(tr.get("compte", "")).lower() == "nycmayor":
                out.abstain("compte écarté (NYC Mayor : perdant à tous les réglages sur le passé)")
                continue
            if float(p.get("skip_elon_trump", 0)) and str(tr.get("compte", "")).lower() in ("elonmusk", "realdonaldtrump"):
                out.abstain("compte écarté (Elon Musk et Trump : ≈ 0 % sur le passé, les plus suivis par les gros acheteurs)")
                continue
            if float(p.get("only_trump", 0)) and str(tr.get("compte", "")).lower() != "realdonaldtrump":
                out.abstain("compte écarté (seulement les posts Truth Social de Trump)")
                continue
            prob = tweet_bucket_probability(tr, rng, now, float(p["dispersion"]), int(p["recent_hours"]),
                                            int(p.get("long_hours", 336)), float(p.get("recent_weight", 0.5)))
            if prob is None:
                continue
            margin, unc, best = float(p["margin"]), float(p["uncertainty"]), None
            for side in ((1,) if float(p.get("only_no", 0)) else (0, 1)):
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


class MotsPrononces(_Reference):
    """« Trump dira-t-il "crypto" cette semaine ? » : le taux de OUI passé du même mot chez le même
    orateur (marchés « mentions » réglés de Polymarket, rapproché de son taux tous mots confondus).
    Sur le passé (experiments/vingt_pistes.md, 794 marchés, prix réels deux heures après
    l'ouverture) : le marché est mieux calibré en moyenne, mais acheter quand le taux historique
    s'écarte de 5 points ET que le billet coûte au moins 0,30 gagnait (+17 % à +27 % par achat
    selon les réglages) ; sous 0,30, rien. Il faut au moins `min_count` précédents."""
    strategy_id = "mots_prononces"
    ref_key = "mentions"
    required = _Reference.required + ("min_count", "min_price")

    def _usable(self, ref: dict, out: StrategyOutput) -> bool:
        if int(ref.get("n") or 0) < int(self.params["min_count"]):
            out.abstain("trop peu de précédents")
            return False
        return True


class MotsNouveaux(_Base):
    """« Dira-t-il ce mot ? » quand le mot n'a JAMAIS été proposé pour cet orateur (qui a pourtant au
    moins 10 marchés passés) : mot à la mode, le OUI est trop cher. Sur le passé
    (experiments/vingt_pistes.md, septembre-octobre 2026 seulement) : OUI à 0,30-0,85, réalisé
    nettement en dessous ; acheter le NON gagnait +16 % (2 h après l'ouverture, 228 achats,
    t +1,8), +20 % (12 h), +9 % (24 h). Indice encore court : fantôme. NON estimé à son prix +
    `shift`."""
    strategy_id = "mots_nouveaux"
    required = ("shift", "margin", "uncertainty", "min_yes", "max_yes", "min_net_edge", "max_age_hours",
                "max_proposals_per_cycle")

    def candidates(self, markets) -> list[MarketInfo]:
        return _with_reference(markets, "mot_nouveau", int(self.params.get("max_candidates", 25)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("mot_nouveau")
            if not ref or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_age_hours"]) * 3600:
                out.abstain("historique trop vieux")
                continue
            mid, book = _book_mid(books, m.token_ids[0]), books.get(m.token_ids[0])
            if mid is None or not float(p["min_yes"]) <= mid <= float(p["max_yes"]):
                continue
            if book.best_bid is None or book.best_ask is None or float(book.best_ask - book.best_bid) > float(p.get("max_spread", 1)):
                out.abstain("carnet trop écarté")  # milieu sans valeur (souvent 0,16 / 0,85 le 20/10)
                continue
            est, unc = 1 - mid + float(p["shift"]) - float(p["margin"]), float(p["uncertainty"])
            prop = self._buy(m, books, state, 1, est - unc, est, est + unc, bucket, marks, out,
                             f"mots_nouveaux:{mid:.3f}", ref.get("titre", ""), "le mot est vraiment dans l'actualité")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


class FatigueNhl(_Base):
    """NHL : l'équipe qui a joué la veille, contre un adversaire reposé, gagne moins souvent que son
    prix. Sur le passé (experiments/vingt_pistes.md, saisons 2024-25 et 2025-26, prix Polymarket une
    heure avant le match) : 299 matchs « fatiguée à l'extérieur », 37,8 % gagnés pour 43,2 % de prix
    (−5,4 points), même sens les deux saisons ; à domicile −3,3 points (99 matchs). Encore faible
    statistiquement (t +1,2) : l'arène tranchera. On achète l'équipe reposée, estimée à son prix +
    `shift`."""
    strategy_id = "fatigue_nhl"
    required = ("shift", "margin", "uncertainty", "min_net_edge", "max_age_hours", "max_proposals_per_cycle")

    def candidates(self, markets) -> list[MarketInfo]:
        """Seulement les matchs où une seule équipe a joué la veille."""
        out = [m for m in _with_reference(markets, "repos_nhl", 200)
               if sorted(m.references["repos_nhl"].get("fatigue") or []) == [False, True]]
        return out[: int(self.params.get("max_candidates", 20))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from datetime import timedelta
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("repos_nhl")
            if not ref or now is None or any(t in state.positions for t in m.token_ids):
                continue
            tired = ref.get("fatigue") or []
            if sorted(tired) != [False, True]:
                continue  # aucune ou les deux fatiguées
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_age_hours"]) * 3600:
                out.abstain("calendrier trop vieux")
                continue
            if m.game_start is None or m.game_start <= now + timedelta(minutes=10):
                out.abstain("match commencé")
                continue
            if int(p.get("seulement_exterieur", 0)) and (ref.get("domicile") or [False, False])[tired.index(True)]:
                continue
            side = tired.index(False)
            mid = _book_mid(books, m.token_ids[side])
            if mid is None:
                continue
            est, unc = mid + float(p["shift"]) - float(p["margin"]), float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - unc, est, est + unc, bucket, marks, out,
                             f"fatigue_nhl:{mid:.3f}", f"{ref.get('titre', '')} : {m.outcomes[1 - side]} a joué la veille",
                             "l'effet de la fatigue est déjà dans le prix")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


# --------------------------------------------------------------------------- 8. tranches improbables du CPI américain

_CPI_EVENT = re.compile(r"^(?:[A-Z][a-z]+ Inflation(?: US)? - (?:Annual|Monthly)|Core CPI (?:YoY|MoM) - .*)$")


class CpiTranches(_Base):
    """Événement CPI américain découpé en tranches (« inflation mensuelle : 0,2 % / 0,3 % / 0,4 %… ») : les tranches
    à 5-30 % gagnent environ moitié moins que leur prix (long tir). On achète leur NON, de 1 à 7 jours avant la publication.
    Test sur le passé (48 événements, 2024-12 → 2026-10) : experiments/cpi_nowcast.md, verdict « indice »."""

    strategy_id = "cpi_tranches"
    required = ("yes_min", "yes_max", "yes_factor", "hours_min", "hours_max", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    @staticmethod
    def _is_cpi(m: MarketInfo) -> bool:
        return _yes_no(m) and bool(_CPI_EVENT.match(m.event_title or ""))

    def candidates(self, markets):
        return [m for m in markets if self._is_cpi(m)][: int(self.params.get("max_candidates", 80))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, props = StrategyOutput(), self.params, []
        for m in watchlist:
            if not self._is_cpi(m) or m.end_date is None or any(t in state.positions for t in m.token_ids):
                continue
            now = _now(books)
            if now is None:
                continue
            hours = (m.end_date - now).total_seconds() / 3600
            if not float(p["hours_min"]) <= hours <= float(p["hours_max"]):
                out.abstain("hors de la fenêtre avant la publication")
                continue
            yes = _book_mid(books, m.token_ids[0])
            if yes is None or not float(p["yes_min"]) <= yes <= float(p["yes_max"]):
                continue
            fair = yes * float(p["yes_factor"])
            unc = float(p["uncertainty"])
            prop = self._buy(m, books, state, 1, 1 - fair - unc, 1 - fair, 1 - fair + unc, bucket, marks, out,
                             f"cpi_tranches:{yes:.3f}", f"tranche CPI à {yes:.1%}, juste {fair:.1%}", "le CPI tombe dans cette tranche")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


_JOBS_EVENT = re.compile(r"^How many [Jj]obs added in [A-Z][a-z]+\?$")


class JobsFavoriNon(_Base):
    """« Combien d'emplois créés en <mois> ? » (rapport américain, tranches de 25-50 k) : la tranche favorite du marché, à 25-70 %,
    gagne environ moitié moins souvent que son prix (même un bon pronostic ne tombe que rarement dans 50 k quand la surprise
    typique fait 75 k). On achète son NON de 4 à 72 heures avant la publication.
    Test sur le passé (29 événements, 2024-03 → 2026-10) : experiments/emploi_nfp.md, verdict « indice » (5 victoires pour 11 attendues)."""

    strategy_id = "jobs_favori_non"
    required = ("yes_min", "yes_max", "yes_factor", "hours_min", "hours_max", "min_buckets", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")

    @staticmethod
    def _is_jobs(m: MarketInfo) -> bool:
        return _yes_no(m) and bool(_JOBS_EVENT.match(m.event_title or ""))

    def candidates(self, markets):
        return [m for m in markets if self._is_jobs(m)][: int(self.params.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, props = StrategyOutput(), self.params, []
        now = _now(books)
        if now is None:
            return self._finish(out, props)
        events: dict[str, list[tuple[float, MarketInfo]]] = {}
        for m in watchlist:
            if not self._is_jobs(m) or m.end_date is None:
                continue
            yes = _book_mid(books, m.token_ids[0])
            if yes is not None:
                events.setdefault(m.event_id, []).append((yes, m))
        for tranches in events.values():
            if len(tranches) < int(p["min_buckets"]):
                out.abstain("trop peu de tranches suivies pour désigner le favori")
                continue
            yes, m = max(tranches, key=lambda x: x[0])
            hours = (m.end_date - now).total_seconds() / 3600
            if not float(p["hours_min"]) <= hours <= float(p["hours_max"]):
                out.abstain("hors de la fenêtre avant la publication")
                continue
            if any(t in state.positions for t in m.token_ids) or not float(p["yes_min"]) <= yes <= float(p["yes_max"]):
                continue
            fair = yes * float(p["yes_factor"])
            unc = float(p["uncertainty"])
            prop = self._buy(m, books, state, 1, 1 - fair - unc, 1 - fair, 1 - fair + unc, bucket, marks, out,
                             f"jobs_favori_non:{yes:.3f}", f"tranche favorite des emplois à {yes:.1%}, juste {fair:.1%}",
                             "le nombre d'emplois tombe dans cette tranche")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)



# --------------------------------------------------------------------------- pistes du 23/10/2026

class MoinsDeCartes(_Base):
    """E-sport en 2 ou 3 manches gagnantes (BO3, BO5) : le marché « Games Total » (nombre de cartes
    jouées) semble calculé comme si chaque carte était un tirage indépendant ; en vrai, l'équipe la
    plus forte du jour gagne souvent 2-0. On achète « Under » entre 6 h et 1 h avant le match.
    Sur le passé, aux prix payés : +13,5 % par pari, 457 paris, 412 matchs, t +2,75, 10 mois sur 12
    (experiments/pistes_sport_coherence.md ; trouvé parmi ~90 essais : fantôme, l'arène tranche).
    Pourquoi ça peut rater : sélection parmi beaucoup d'essais ; marchés minces."""

    strategy_id = "moins_de_cartes"
    required = ("min_hours", "max_hours", "price_min", "price_max", "shift", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")
    WORDS = ("(BO3)", "(BO5)")

    def _ok(self, m: MarketInfo, now: datetime | None) -> bool:
        if (m.sports_market_type != "totals" or not (m.question or "").startswith("Games Total")
                or [str(o).lower() for o in m.outcomes] != ["over", "under"] or len(m.token_ids) != 2
                or not any(w in (m.event_title or "") for w in self.WORDS) or m.game_start is None or now is None):
            return False
        hours = (m.game_start - now).total_seconds() / 3600
        return float(self.params["min_hours"]) <= hours <= float(self.params["max_hours"])

    def candidates(self, markets):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        out = [m for m in markets if self._ok(m, now)]
        out.sort(key=lambda m: m.game_start)
        return out[: int(self.params.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            if not self._ok(m, now):
                continue
            if any(t in state.positions for t in m.token_ids):
                out.abstain("position déjà ouverte")
                continue
            book = books.get(m.token_ids[1])
            if book is None or book.best_ask is None or book.mid is None:
                out.abstain("carnet indisponible")
                continue
            if not float(p["price_min"]) <= float(book.best_ask) <= float(p["price_max"]):
                out.abstain("« Under » hors de la plage de prix")
                continue
            est = float(book.mid) + float(p["shift"])
            prop = self._buy(m, books, state, 1, est - float(p["uncertainty"]), est, est + float(p["uncertainty"]),
                             bucket, marks, out, f"moins_de_cartes:{m.question[-7:].strip()}",
                             "écart mesuré sur le passé (+13,5 % par pari), trouvé parmi ~90 essais",
                             "le match va au bout des cartes")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


class MoinsDeKills(_Base):
    """E-sport, totaux de kills d'une partie (« Total Kills Over/Under 30.5 in Game 1? », LoL) : le « Over » est trop cher, le « Under » un peu trop bon marché.
    Chaque partie a 3 à 6 lignes qui se gagnent ou se perdent ensemble : on n'achète « Under » qu'UNE fois par partie, sur la ligne dont le prix est le plus
    proche de 0,5, entre 12 h et 2 h avant le coup d'envoi. Sur le passé (27/10/2026, 4 jeux, vrais échanges, frais payés, un pari par partie, payé 0,35-0,65, 3 h avant) :
    « Under » +9,5 % (588 paris, 330 gagnés pour 297,3, t par événement 2,75, 8 mois sur 9), « Over » −10,5 % (675 paris, t −3,6) (experiments/lol_kills.md).
    Pourquoi ça peut rater : le gain s'efface quand on exige beaucoup de parts (≥ 400 parts : +4 %), et l'indice vient d'un seul jeu (LoL)."""

    strategy_id = "moins_de_kills"
    required = ("min_hours", "max_hours", "price_min", "price_max", "shift", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")
    GAME = re.compile(r"in Game (\d)")

    def _ok(self, m: MarketInfo, now: datetime | None) -> bool:
        if (m.sports_market_type != "kill_over_under_game" or [str(o).lower() for o in m.outcomes] != ["over", "under"]
                or len(m.token_ids) != 2 or m.game_start is None or now is None):
            return False
        hours = (m.game_start - now).total_seconds() / 3600
        return float(self.params["min_hours"]) <= hours <= float(self.params["max_hours"])

    def candidates(self, markets):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        out = [m for m in markets if self._ok(m, now)]
        out.sort(key=lambda m: m.game_start)
        return out[: int(self.params.get("max_candidates", 60))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        games: dict[tuple, list[tuple[float, MarketInfo]]] = {}
        for m in watchlist:
            if not self._ok(m, now):
                continue
            g = self.GAME.search(m.question or "")
            book = books.get(m.token_ids[1])
            if g is None or book is None or book.best_ask is None or book.mid is None:
                out.abstain("carnet indisponible")
                continue
            if not float(p["price_min"]) <= float(book.best_ask) <= float(p["price_max"]):
                out.abstain("« Under » hors de la plage de prix")
                continue
            games.setdefault((m.event_id, g.group(1)), []).append((abs(float(book.best_ask) - 0.5), m))
        for lines in games.values():
            if any(t in state.positions for _d, m in lines for t in m.token_ids):
                out.abstain("partie déjà jouée")  # une seule ligne par partie : elles se gagnent ou se perdent ensemble
                continue
            m = min(lines, key=lambda x: x[0])[1]
            est = float(books[m.token_ids[1]].mid) + float(p["shift"])
            prop = self._buy(m, books, state, 1, est - float(p["uncertainty"]), est, est + float(p["uncertainty"]),
                             bucket, marks, out, f"moins_de_kills:{m.question[-12:].strip()}",
                             "« Over » trop cher sur le passé (−10,5 %), « Under » +9,5 % (t 2,75), un pari par partie",
                             "la partie compte beaucoup de kills")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


DRAME = re.compile(
    r"\b(invade|invades|invasion|war\b|wars\b|military action|military clash|strikes? on|attacks?\b|airstrikes?|"
    r"missiles?|nuclear|bomb|troops|blockade|annex|annexes|annexation|ceasefire|cease-fire|truce|clash|"
    r"declares? war|hostilities|drone strike|conflict|"
    r"out as|out by|out in|ousted|resigns?|resignation|step down|steps down|leaves? office|removed|impeach|"
    r"impeached|impeachment|coup\b|assassinat\w*|dies?\b|death|dead\b|jail|prison|arrest(ed)?|indicted|"
    r"convicted|extradited|detained|captured|25th amendment|deported|expelled|"
    r"bankrupt\w*|default|recession|collapse|crash|insolven\w*|bank run|hyperinflation|depeg|de-peg|"
    r"delisted|shutdown|nationaliz\w*|"
    r"aliens?|ufo|uap|extraterrestrial|non-human|jesus|rapture|asteroid|apocalypse|martial law|secede|"
    r"secession|civil war|pandemic|outbreak|lockdown|state of emergency|meteor)", re.I)
STATU_QUO = re.compile(r"\b(remain|remains|still|survive|survives|stay|stays|keep|keeps|alive|retain|hold on)\b"
                       r"|sentenced to between", re.I)


class NonAuxDrames(_Base):
    """« Est-ce que <drame> arrivera avant <date> ? » (invasion, chef d'État renversé, faillite,
    extraterrestres…) à 2-15 % plus d'un mois avant l'échéance : la foule paie trop cher le frisson.
    On achète le NON, au plus 2 % du capital par événement. Sur le passé (2024-2026, prix payés) :
    149 paris, +4,6 % par pari, 2 drames arrivés pour 9,3 attendus, t par événement 2,81 ; les marchés
    longs qui ne sont pas des drames : +0,9 % seulement (experiments/pistes_crypto_elections_drames.md).
    Pourquoi ça peut rater : 2 pertes seulement dans l'échantillon ; une guerre fait tout perdre d'un coup."""

    strategy_id = "non_aux_drames"
    required = ("min_days", "max_days", "yes_min", "yes_max", "min_volume", "yes_factor", "uncertainty",
                "stake_fraction", "min_net_edge", "max_proposals_per_cycle")

    def _ok(self, m: MarketInfo, now: datetime | None) -> bool:
        q = m.question or ""
        if not _yes_no(m) or m.end_date is None or now is None or not DRAME.search(q) or STATU_QUO.search(q):
            return False
        days = (m.end_date - now).total_seconds() / 86400
        return (float(self.params["min_days"]) <= days <= float(self.params["max_days"])
                and float(m.volume_total or 0) >= float(self.params["min_volume"]))

    def candidates(self, markets):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        p = self.params
        out = [m for m in markets if self._ok(m, now) and m.outcome_prices
               and float(p["yes_min"]) <= float(m.outcome_prices[0]) <= float(p["yes_max"])]
        out.sort(key=lambda m: -float(m.volume_total or 0))
        return out[: int(p.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        events = {pos.event_id for pos in state.positions.values()}
        for m in watchlist:
            if not self._ok(m, now):
                continue
            if m.event_id in events or any(t in state.positions for t in m.token_ids):
                out.abstain("événement déjà joué")
                continue
            yes, book = _book_mid(books, m.token_ids[0]), books.get(m.token_ids[1])
            if yes is None or book is None or book.best_ask is None:
                out.abstain("carnet indisponible")
                continue
            if not float(p["yes_min"]) <= yes <= float(p["yes_max"]):
                out.abstain("OUI hors de la plage de prix")
                continue
            est = 1 - yes * float(p["yes_factor"])
            budget = p["stake_fraction"] * state.total_estimated(marks)
            shares = min(budget, state.cash) / book.best_ask
            prop = self._buy(m, books, state, 1, est - float(p["uncertainty"]), est,
                             min(est + float(p["uncertainty"]), 0.999), bucket, marks, out,
                             f"non_aux_drames:oui={yes:.3f}", "drames arrivés 2 fois pour 9,3 attendus sur le passé",
                             "le drame arrive", shares=shares.quantize(Decimal("0.01"), rounding=ROUND_DOWN))
            if prop is not None:
                props.append(prop)
                events.add(m.event_id)
        return self._finish(out, props)


class DetroitsTranches(_Base):
    """« Avg. # of ships transiting Bab el-Mandeb Strait / Strait of Hormuz end of <mois> ? » : tranches de la moyenne sur 7 jours
    publiée par IMF PortWatch (avec ≈ 5 jours de retard). On prolonge la série du FMI (references.attach_detroits : moyenne sur
    7 jours d'aujourd'hui mélangée au niveau des 45 derniers jours, écart-type tiré des erreurs passées) et on achète le côté que
    le marché vend nettement moins cher que cette loi. Le 23/10/2026 la tranche 25-29 de Bab el-Mandeb était à 0,81 pour 0,45-0,51
    d'après 2 ans d'historique ; AUCUN prix passé de ce type de marché n'existe (deux événements seulement) : verdict « indice »,
    fantôme en quart de Kelly (experiments/detroits.md)."""

    strategy_id = "detroits_tranches"
    required = ("min_gap", "uncertainty", "max_stale_hours", "min_net_edge", "max_proposals_per_cycle")

    def candidates(self, markets):
        return _with_reference(markets, "detroit", int(self.params.get("max_candidates", 40)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("detroit")
            if not ref or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_stale_hours"]) * 3600:
                out.abstain("relevé PortWatch pas à jour")
                continue
            yes = _book_mid(books, m.token_ids[0])
            if yes is None:
                out.abstain("carnet indisponible")
                continue
            fair, unc, gap = float(ref["p"]), float(p["uncertainty"]), float(p["min_gap"])
            if fair - yes >= gap:
                side, est = 0, fair
            elif yes - fair >= gap:
                side, est = 1, 1 - fair
            else:
                out.abstain("prix proche de la loi calculée")
                continue
            prop = self._buy(m, books, state, side, est - unc, est, min(est + unc, 0.999), bucket, marks, out,
                             f"detroits:{ref['titre']}", f"loi calculée {fair:.3f} contre prix {yes:.3f}",
                             "la moyenne sur 7 jours de PortWatch sort de la loi calculée (changement de régime)")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


class DetroitsMarcheLog(_Base):
    """Tranches hebdomadaires (« How many ships transit … week of … ») et mensuelles (« Avg. # of ships transiting … ») d'Ormuz et
    de Bab el-Mandeb, réglées sur IMF PortWatch. Loi de la somme des 7 jours à la date cible : celle d'aujourd'hui × chaque
    variation relative déjà vue à ce même horizon depuis 2019 (references.attach_detroits_log). On achète le côté (OUI ou NON)
    dont la chance calculée dépasse le prix demandé + frais d'au moins `min_net_edge`, entre `min_price` et `max_price`.
    Test sur le passé (experiments/detroits.md, 23/10/2026) : 40 événements réglés de juin à octobre, 150 paris aux prix payés,
    +24 % par pari, t par événement 2,1, z des prix 2,8, 5 mois sur 5 ; les billets sous 0,10 perdaient tous (3 sur 3)."""

    strategy_id = "detroits_marche_log"
    required = ("min_net_edge", "min_price", "max_price", "max_stale_hours", "max_proposals_per_cycle")

    def candidates(self, markets):
        return _with_reference(markets, "detroit_log", int(self.params.get("max_candidates", 60)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("detroit_log")
            if not ref or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_stale_hours"]) * 3600:
                out.abstain("relevé PortWatch pas à jour")
                continue
            fair, unc = float(ref["p"]), float(p.get("uncertainty", 0))
            best = None
            for side, est in ((0, fair), (1, 1 - fair)):
                book = books.get(m.token_ids[side])
                ask = float(book.best_ask) if book is not None and book.best_ask is not None else None
                if ask is None or not float(p["min_price"]) <= ask <= float(p["max_price"]):
                    continue
                if best is None or est - ask > best[2]:
                    best = (side, est, est - ask)
            if best is None:
                out.abstain("issue hors de la plage de prix ou carnet vide")
                continue
            side, est, _ = best
            prop = self._buy(m, books, state, side, est - unc, est, min(est + unc, 0.999), bucket, marks, out,
                             f"detroits_log:{ref['titre']}", f"loi calculée {est:.3f} pour l'issue achetée",
                             "PortWatch change de rythme ou de chiffres (révision), ou le trafic change de régime")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


class SeismesMarche(_Base):
    """Marchés « plus gros séisme du jour » (6 tranches) et « combien de séismes >= 5,5 / 6,5 cette semaine », réglés sur le catalogue USGS
    que l'on lit en direct (sources/usgs.py). Chance calculée par seismes.py : maximum déjà vu et heures restantes (jour), compte déjà vu et
    binomiale négative des 156 dernières semaines (semaine). On achète le côté (OUI ou NON) dont la chance calculée dépasse le prix demandé
    + frais d'au moins `min_net_edge`, entre `min_price` et `max_price`.
    Test sur le passé (experiments/seismes.md, 24/10/2026) : jour, 27 jours réglés : 27 paris aux prix payés +69 % (t par jour 1,15) ;
    semaine, 55 événements, séismes >= 5,5 +24 % après frais (t par événement 2,05), >= 6,5 rien (+7 %, t 0,6) ; mais le modèle n'est pas démontré
    meilleur que le marché en perte log (test apparié par événement, t -1,3 au mieux) : indice faible, fantôme."""

    strategy_id = "seismes_marche"
    required = ("min_net_edge", "min_price", "max_price", "max_stale_hours", "max_proposals_per_cycle")

    def candidates(self, markets):
        return _with_reference(markets, "seismes", int(self.params.get("max_candidates", 60)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        scored = []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("seismes")
            if not ref or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_stale_hours"]) * 3600:
                out.abstain("catalogue USGS pas à jour")
                continue
            # Doublon entre réseaux (24/10/2026 : 6,6 « pt » et 6,3 « us » du même séisme) : si le compte sans doublon change la chance de plus de
            # `max_ecart_doublon`, on ne sait pas ce que le règlement comptera : pas d'achat.
            if abs(float(ref.get("p_dedup", ref["p"])) - float(ref["p"])) > float(p.get("max_ecart_doublon", 0.15)):
                out.abstain("doublon possible entre réseaux USGS (compte incertain)")
                continue
            # Jamais de certitude : le catalogue du règlement peut différer du flux (révision, séisme encore absent), 1 fois sur 27 côté jour et 10 sur 57 côté semaine >= 5,5.
            fair = min(max(float(ref["p"]), 0.03), 0.97)
            best = None
            for side, est in ((0, fair), (1, 1 - fair)):
                book = books.get(m.token_ids[side])
                ask = float(book.best_ask) if book is not None and book.best_ask is not None else None
                if ask is None or not float(p["min_price"]) <= ask <= float(p["max_price"]):
                    continue
                if best is None or est - ask > best[2]:
                    best = (side, est, est - ask)
            if best is None:
                out.abstain("issue hors de la plage de prix ou carnet vide")
                continue
            scored.append((best[2], m, best[0], best[1], ref))
        # Les tranches d'un même événement gagnent ou perdent ensemble (même compte, même maximum) : au plus `max_per_event`, les meilleures d'abord.
        per_event: dict = {}
        unc = float(p.get("uncertainty", 0))
        for _, m, side, est, ref in sorted(scored, key=lambda x: -x[0]):
            if per_event.get(m.event_id, 0) >= int(p.get("max_per_event", 2)):
                out.abstain("déjà deux tranches de cet événement")
                continue
            prop = self._buy(m, books, state, side, est - unc, est, min(est + unc, 0.999), bucket, marks, out,
                             f"seismes:{ref['titre']}", f"loi calculée {est:.3f} pour l'issue achetée",
                             "une réplique ou un séisme fort de dernière minute, ou une révision de magnitude par l'USGS")
            if prop is not None:
                per_event[m.event_id] = per_event.get(m.event_id, 0) + 1
                props.append(prop)
        return self._finish(out, props)


class ToucherMetaux(_Base):
    """Marchés « What will Gold (XAUUSD) / Silver (XAGUSD) hit Week of … » (échelle de barres HIGH et LOW, réglée sur les bougies d'1 minute de Pyth). Chance de
    toucher la barre d'ici la fin de la semaine : barrière d'un mouvement brownien sans dérive, volatilité fixe, maximum et minimum déjà relevés depuis la création
    du marché (matieres.py ; journal des prix tenu par le cycle, sources/goldapi.py). On achète le côté (OUI ou NON) dont la chance calculée dépasse le prix
    demandé + frais d'au moins `min_net_edge`.
    Test sur le passé (experiments/commodites_toucher.md, 24/10/2026, avril → octobre) : 4 matières (pétrole, gaz, or, argent), 112 semaines, prix des vrais
    échanges : 328 paris sur 98 événements, +33 % (seuil 0,05), confiance par événement 2,35, z des prix 1,96, 5 mois sur 7 gagnants, +19 % sans les 3 meilleurs ;
    gain seulement sur les barres cotées 0,10-0,45 (le marché sous-cote les touches ; prix demandé plafonné à `max_price`, choix après coup) ; avril-juillet +58 % puis août-octobre +8 % (t 0,4) : INDICE FAIBLE, fantôme (or et argent seuls :
    le cycle n'a pas de prix pour le pétrole et le gaz). Pourquoi ça peut rater : volatilité fixe, bougies d'1 minute de Pyth plus extrêmes que nos relevés,
    marché qui apprend (mois récents)."""

    strategy_id = "toucher_metaux"
    required = ("min_net_edge", "min_price", "max_price", "max_stale_hours", "max_proposals_per_cycle")

    def candidates(self, markets):
        return _with_reference(markets, "matieres", int(self.params.get("max_candidates", 60)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, scored, rattaches = StrategyOutput(), self.params, _now(books), [], 0
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("matieres")
            if not ref or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            rattaches += 1
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_stale_hours"]) * 3600:
                out.abstain("journal des prix pas à jour")
                continue
            fair = min(max(float(ref["p"]), 0.05), 0.95)      # jamais de certitude (bougies de Pyth ≠ nos relevés)
            best = None
            for side, est in ((0, fair), (1, 1 - fair)):
                book = books.get(m.token_ids[side])
                ask = float(book.best_ask) if book is not None and book.best_ask is not None else None
                if ask is None or not float(p["min_price"]) <= ask <= float(p["max_price"]):
                    continue
                if best is None or est - ask > best[2]:
                    best = (side, est, est - ask)
            if best is None:
                out.abstain("issue hors de la plage de prix ou carnet vide")
                continue
            scored.append((best[2], m, best[0], best[1], ref))
        if not rattaches:  # 27/10/2026 : « aucune raison notée » pendant 3 jours, alors qu'elle attendait une semaine née après le premier relevé
            out.abstain("aucune barre d'or ou d'argent avec un prix rattaché (semaine née avant le journal des prix, ou barre à l'arrêt)")
        per_event: dict = {}
        props = []
        unc = float(p.get("uncertainty", 0))
        for _, m, side, est, ref in sorted(scored, key=lambda x: -x[0]):
            if per_event.get(m.event_id, 0) >= int(p.get("max_per_event", 3)):
                out.abstain("déjà le maximum de barres de cet événement")
                continue
            prop = self._buy(m, books, state, side, est - unc, est, min(est + unc, 0.999), bucket, marks, out,
                             f"matieres:{ref['titre']}", f"chance calculée {est:.3f} pour l'issue achetée",
                             "volatilité plus forte ou plus faible que la médiane d'un an, ou bougie de Pyth plus extrême que nos relevés")
            if prop is not None:
                per_event[m.event_id] = per_event.get(m.event_id, 0) + 1
                props.append(prop)
        return self._finish(out, props)


class SpaceXCumul(_Base):
    """Marchés « How many SpaceX launches in <mois / année> ? » (tranches de nombre de lancements), réglés sur spacex.com/launches. Le compte ne fait que
    monter et se lit en direct (Launch Library 2, sources/ll2.py) : compte déjà fait + cadence des 120 derniers jours sous trois lois (spacex.py). On achète
    seulement le côté (OUI ou NON) que les cinq lois (spacex.py) jugent probable (prix demandé entre `min_price` et `max_price`) quand la chance la PLUS PRUDENTE des
    trois dépasse le prix + frais d'au moins `min_net_edge`.
    Test sur le passé (experiments/spacex_cadence.md, 24/10/2026) : règlement relu 9 fois sur 9 (compte LL2 dans la tranche gagnante) mais 9 événements
    seulement (1 466 à 6 886 échanges) : les paris à chance modeste (0,1 à 0,5) perdent (20 paris, −19 %), les quasi-certains gagnent (7 paris sur 7, +10 %,
    3 événements) : INDICE FAIBLE, sans preuve statistique, fantôme. Pourquoi ça peut rater : spacex.com ne compte pas comme LL2 (essai, charge utile),
    ou une pause de plusieurs semaines de la flotte."""

    strategy_id = "spacex_cumul"
    required = ("min_net_edge", "min_price", "max_price", "max_stale_hours", "max_proposals_per_cycle")

    def candidates(self, markets):
        return _with_reference(markets, "spacex", int(self.params.get("max_candidates", 40)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sources._util import parse_date
        out, p, now, scored = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (getattr(m, "references", None) or {}).get("spacex")
            if not ref or not _yes_no(m) or now is None or any(t in state.positions for t in m.token_ids):
                continue
            seen = parse_date(ref.get("vu_le") or "")
            if seen is None or (now - seen).total_seconds() > float(p["max_stale_hours"]) * 3600:
                out.abstain("relevé des lancements pas à jour")
                continue
            # Jamais de certitude : spacex.com peut compter autrement que Launch Library 2.
            yes_fair = min(max(float(ref["p_min"]), 0.03), 0.97)
            no_fair = min(max(1 - float(ref["p_max"]), 0.03), 0.97)
            best = None
            for side, est in ((0, yes_fair), (1, no_fair)):
                book = books.get(m.token_ids[side])
                ask = float(book.best_ask) if book is not None and book.best_ask is not None else None
                if ask is None or not float(p["min_price"]) <= ask <= float(p["max_price"]):
                    continue
                if best is None or est - ask > best[2]:
                    best = (side, est, est - ask)
            if best is None:
                out.abstain("issue hors de la plage de prix ou carnet vide")
                continue
            scored.append((best[2], m, best[0], best[1], ref))
        per_event: dict = {}
        props = []
        unc = float(p.get("uncertainty", 0))
        for _, m, side, est, ref in sorted(scored, key=lambda x: -x[0]):
            if per_event.get(m.event_id, 0) >= int(p.get("max_per_event", 2)):
                out.abstain("déjà deux tranches de cet événement")
                continue
            prop = self._buy(m, books, state, side, est - unc, est, min(est + unc, 0.999), bucket, marks, out,
                             f"spacex:{ref['titre']}", f"chance prudente {est:.3f} pour l'issue achetée",
                             "pause de la flotte de plusieurs semaines, ou spacex.com compte autrement que Launch Library 2")
            if prop is not None:
                per_event[m.event_id] = per_event.get(m.event_id, 0) + 1
                props.append(prop)
        return self._finish(out, props)


class BoxOfficeFavori(_Base):
    """« Box-office du premier week-end » (5 tranches de recettes par film) : on achète le OUI de la tranche
    favorite, entre `min_hours` et `max_hours` avant la fin du marché (vendredi et samedi déjà connus du public).
    Sur le passé (experiments/box_office.md, 24/10/2026), aux prix du dernier achat réel et frais 5 % : à 24 h de la fin,
    110 films, la favorite gagne 100 fois pour 93,6 attendues, +7,5 % par pari (t par film 1,96) ; ancrée sur le week-end
    (dimanche 0 h → 16 h UTC) +6,6 % (142 films, t 1,56) mais −2 % si l'on commence dès le samedi 18 h : ~40 réglages
    regardés, découpe par jour de fin instable, trois familles témoins (Netflix, vues, Rotten Tomatoes) sans effet : indice faible, fantôme.
    Pourquoi ça peut rater : sélection parmi beaucoup d'essais ; la fin du marché varie (dimanche midi ou lundi midi)."""

    strategy_id = "box_office_favori"
    required = ("min_hours", "max_hours", "price_min", "price_max", "shift", "uncertainty", "min_net_edge",
                "max_proposals_per_cycle")
    FILM = re.compile(r"[\"“'](.+?)[\"”']\s+Opening Weekend Box Office", re.I)

    def _film(self, m: MarketInfo) -> str | None:
        t = m.event_title or m.question or ""
        if "opening weekend box office" not in t.lower() or not _yes_no(m):
            return None
        found = self.FILM.search(t)
        return (found.group(1) if found else t).strip().lower() + "|" + (m.end_date.date().isoformat() if m.end_date else "")

    def candidates(self, markets):
        out = [m for m in markets if self._film(m)]
        out.sort(key=lambda m: m.end_date.timestamp() if m.end_date else 0)
        return out[: int(self.params.get("max_candidates", 80))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        groups: dict = defaultdict(list)
        for m in watchlist:
            key = self._film(m)
            if key and m.end_date is not None:
                groups[key].append(m)
        for key, ms in groups.items():
            if now is None or len(ms) < 2:
                out.abstain("moins de deux tranches visibles")
                continue
            hours = (ms[0].end_date - now).total_seconds() / 3600
            if not float(p["min_hours"]) <= hours <= float(p["max_hours"]):
                out.abstain("hors de la fenêtre avant la fin")
                continue
            wd = int(p.get("weekday", -1))  # fenêtre ancrée sur le week-end (la fin du marché varie : dimanche midi ou lundi midi)
            if wd >= 0 and not (now.weekday() == wd and float(p.get("hour_from", 0)) <= now.hour + now.minute / 60 < float(p.get("hour_to", 24))):
                out.abstain("hors de la fenêtre du week-end")
                continue
            asks = []
            for m in ms:
                book = books.get(m.token_ids[0])
                asks.append((float(book.best_ask) if book is not None and book.best_ask is not None else None, m))
            if any(a is None for a, _ in asks):
                out.abstain("carnet indisponible")
                continue
            ask, fav = max(asks, key=lambda x: x[0])
            # Le scanner écarte les tranches trop chères ou sans carnet : la favorite n'est sûre que si les tranches
            # cachées (au plus 1 − somme des prix visibles) pèsent moins que la tranche choisie.
            mids = [_book_mid(books, m.token_ids[0]) for m in ms]
            if any(v is None for v in mids) or max(mids) < max(0.0, 1 - sum(mids)) + float(p.get("hidden_margin", 0.02)):
                out.abstain("une tranche cachée pourrait être la favorite")
                continue
            if any(t in state.positions for mm in ms for t in mm.token_ids):
                out.abstain("position déjà ouverte")
                continue
            if not float(p["price_min"]) <= ask <= float(p["price_max"]):
                out.abstain("favorite hors de la plage de prix")
                continue
            est = min(ask + float(p["shift"]), 0.99)
            prop = self._buy(fav, books, state, 0, est - float(p["uncertainty"]), est, min(est + float(p["uncertainty"]), 0.999),
                             bucket, marks, out, f"box_office:{key.split('|')[0]}",
                             "écart mesuré sur le passé (+7 % par pari, 110 films), trouvé parmi ~24 réglages",
                             "une tranche voisine l'emporte (recettes du samedi et du dimanche)")
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


class SuivreInities(_Base):
    """Suivre les comptes suspects quand on en parle (27/10/2026, demande d'Etienne après l'affaire du Ballon d'Or) : la
    presse, les réseaux ou les commentaires Polymarket parlent de paris suspects sur un événement « à initiés » encore ouvert
    (prix, classements d'entreprise, émissions enregistrées, choix d'une petite équipe), ET de l'argent NEUF et CONCENTRÉ
    (comptes à première activité récente, peu de marchés : référence `inities`, polymarket_agent/inities.py) achète un même
    jeton ; on achète avec eux tant que le prix n'a pas rattrapé leur prix moyen. Ballon d'Or 2026 : article d'Upside le 23/10,
    bons résultats encore à 0,69-0,72, réponse le 26/10. Sur le passé (experiments/inities.md, 48 réglages) : l'argent neuf
    SEUL ne bat pas ses prix (des joueurs qui débutent, pas des initiés) ; la presse avant le résultat est trop rare pour un
    test : expérience. Pourquoi ça peut rater : de faux initiés qui se trompent ensemble, une rumeur fausse, une réponse déjà
    dans le prix."""

    strategy_id = "suivre_inities"
    required = ("presse_requise", "min_comptes", "min_dollars", "prix_min", "max_age_hours", "max_price", "max_rattrapage",
                "edge_prior", "uncertainty", "stake_fraction", "min_net_edge", "max_proposals_per_cycle")

    def candidates(self, markets):
        return _with_reference(markets, "inities", int(self.params.get("max_candidates", 40)))

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, p, now, props = StrategyOutput(), self.params, _now(books), []
        for m in watchlist:
            ref = (m.references or {}).get("inities")
            if not ref:
                continue
            side = int(ref.get("issue", 0))
            if side >= len(m.token_ids) or any(t in state.positions for t in m.token_ids):
                out.abstain("déjà en position")
                continue
            presse = bool(ref.get("presse") or ref.get("commentaires"))
            if int(p["presse_requise"]) and not presse:
                out.abstain("personne ne parle de paris suspects sur cet événement")
                continue
            comptes, dollars, moyen = int(ref.get("comptes") or 0), float(ref.get("dollars") or 0), float(ref.get("prix_moyen") or 0)
            if comptes < int(p["min_comptes"]) or dollars < float(p["min_dollars"]):
                out.abstain("grappe trop petite")
                continue
            if moyen < float(p["prix_min"]):
                out.abstain("comptes suspects sur un outsider (joueurs, pas initiés)")
                continue
            if now is not None and ref.get("dernier") and now.timestamp() - float(ref["dernier"]) > float(p["max_age_hours"]) * 3600:
                out.abstain("grappe trop ancienne")
                continue
            book = books.get(m.token_ids[side])
            if book is None or book.best_ask is None:
                out.abstain("carnet indisponible")
                continue
            ask = float(book.best_ask)
            if ask > min(float(p["max_price"]), moyen + float(p["max_rattrapage"])):
                out.abstain("le prix a déjà rattrapé les comptes suspects")
                continue
            est = min(0.99, ask + float(p["edge_prior"]))
            u = float(p["uncertainty"])
            budget = p["stake_fraction"] * state.total_estimated(marks)
            shares = (min(budget, state.cash) / book.best_ask).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            prop = self._buy(m, books, state, side, est - u, est, min(est + u, 0.999), bucket, marks, out,
                             f"inities:{comptes}c:{dollars:.0f}$:{moyen:.2f}",
                             f"{comptes} compte(s) neuf(s) et concentré(s), {dollars:.0f} $ à {moyen:.2f} en moyenne ; "
                             + ("la presse, les réseaux ou les commentaires parlent de paris suspects" if presse else "sans soupçon public"),
                             "les comptes se trompaient ensemble, ou la réponse était déjà dans le prix", shares=shares)
            if prop is not None:
                props.append(prop)
        return self._finish(out, props)


CLASSES = {c.strategy_id: c for c in (SuivreInities, MoinsDeCartes, MoinsDeKills, NonAuxDrames, DecroissanceTemps, EchelleDates, CoherenceMatch, ImplicationPolitique,
                                      PaireOuiNon, OutsidersSurcotes, MarcheNeuf, ApresEcheance, MarchesJumeaux,
                                      ChocSansNouvelle, KalshiReference, PredictItReference, ManifoldReference,
                                      FutursBookmakers, FootballTroisIssues, CompteurTweets, MotsPrononces,
                                      MotsNouveaux, FatigueNhl, CpiTranches, JobsFavoriNon, VagueVolume,
                                      DetroitsTranches, DetroitsMarcheLog, SeismesMarche, BoxOfficeFavori, SpaceXCumul, ToucherMetaux)}
