"""Étape 6 : les cinq familles de stratégies manquantes du cahier des charges (§4.F).

  2. news_momentum           : actualité confirmée + prix qui a commencé à bouger → continuation
  3. information_advantage   : annonce officielle fraîche, prix pas encore réagi (direction via Gemini)
  5. market_structure        : déséquilibre du carnet → hausse à court terme, sortie programmée
  6. social_sentiment        : euphorie sociale unilatérale sans source fiable → pari contraire (Gemini)
  7. cross_market            : incohérence entre marchés liés (échelle de seuils) → arbitrage sans risque

Aucune n'est supposée rentable : ce sont des hypothèses que l'arène juge en conditions réelles.
Les a priori (continuation, impact…) ne sont PAS calibrés ; ils sont des paramètres bornés.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal, ROUND_DOWN

from polymarket_agent.correlation import correlation_group
from polymarket_agent.crypto_model import parse_question
from polymarket_agent.fees import UnknownFees, taker_fee
from polymarket_agent.ledger import LedgerState, Position
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.portfolio_manager import size_buy
from polymarket_agent.safety_controller import Proposal, RiskLimits
from polymarket_agent.strategy_engine import (StrategyConfigError, StrategyOutput, best_limit_price,
                                              make_op_id)

ONE = Decimal("1")


def _d(x: float) -> Decimal:
    return Decimal(str(round(x, 6)))


class _Base:
    strategy_id = "base"
    required: tuple[str, ...] = ()
    needs_price_history = False

    def __init__(self, version: str, created_at: str, params: dict[str, Decimal]):
        missing = [p for p in self.required if p not in params]
        if missing:
            raise StrategyConfigError(f"{self.strategy_id} : paramètres manquants {missing}")
        self.version, self.created_at, self.params = version, created_at, params

    def _buy(self, market: MarketInfo, books: dict[str, OrderBook], state: LedgerState, side: int,
             low: float, est: float, high: float, bucket: str, marks, out: StrategyOutput,
             source: str, uncertainty: str, invalidation: str, shares: Decimal | None = None,
             skip_edge: bool = False) -> Proposal | None:
        """Proposition d'achat de l'issue `side`, prix limite tenant l'avantage net >= min_net_edge."""
        low, est, high = (min(max(v, 0.001), 0.999) for v in (low, est, high))
        if not low <= est <= high:
            low, est, high = sorted((low, est, high))
        book = books.get(market.token_ids[side])
        if book is None:
            out.abstain("carnet indisponible")
            return None
        try:
            if skip_edge:  # jambe d'arbitrage : l'avantage n'existe que pour la paire
                limit = ((book.best_ask, book.best_ask + taker_fee(ONE, book.best_ask, market.fees))
                         if book.best_ask is not None else None)
            else:
                limit = best_limit_price(book, market, _d(low), self.params.get("min_net_edge", Decimal("0")),
                                         int(self.params.get("max_extra_ticks", 2)))
        except UnknownFees:
            out.abstain("frais inconnus")
            return None
        if limit is None:
            out.abstain("avantage net insuffisant")
            return None
        max_price, cost_ps = limit
        if shares is None:
            shares = size_buy(state, prob_low=_d(low), cost_per_share=cost_ps,
                              kelly_fraction=self.params.get("kelly_fraction", Decimal("1")), marks=marks)
        if shares < max(market.min_order_size, book.min_order_size):
            out.abstain("taille autorisée trop faible")
            return None
        token_id = market.token_ids[side]
        hours = (market.end_date - book.fetched_at).total_seconds() / 3600 if market.end_date else 0
        return Proposal(
            op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "BUY"), side="BUY",
            market_id=market.market_id, event_id=market.event_id, token_id=token_id,
            outcome=market.outcomes[side], est_probability=_d(est), prob_low=_d(low), prob_high=_d(high),
            max_price=max_price, shares=shares, net_edge=_d(low) - cost_ps,
            sources=("polymarket_clob", source), uncertainty=uncertainty, invalidation=invalidation,
            horizon_hours=Decimal(str(round(max(hours, 0), 2))),
            strategy_id=self.strategy_id, strategy_version=self.version)

    @staticmethod
    def _mid(books, market) -> float | None:
        book = books.get(market.token_ids[0]) if market.token_ids else None
        return float(book.mid) if book is not None and book.mid is not None else None

    def _finish(self, out: StrategyOutput, candidates: list[Proposal]) -> StrategyOutput:
        candidates.sort(key=lambda p: p.net_edge, reverse=True)
        out.proposals = candidates[: int(self.params.get("max_proposals_per_cycle", 3))]
        return out


# --------------------------------------------------------------------------- 7. cross-market


class CrossMarketLadder(_Base):
    """Échelles de seuils (« BTC au-dessus de 80 k le 15 », « … de 82 k le 15 ») : P(> K bas) >= P(> K haut).

    Si « Oui au-dessus de K bas » + « Non au-dessus de K haut » coûtent moins de 1 (frais compris),
    on achète les deux : au moins l'un des deux paie toujours 1 (S > K bas, ou S <= K haut),
    les deux si K bas < S <= K haut. Gain garanti, sauf risque d'exécution d'une seule jambe.
    """

    strategy_id = "cross_market"
    required = ("min_net_edge", "stake_fraction", "max_proposals_per_cycle")

    @staticmethod
    def _key(market: MarketInfo):
        q = parse_question(market.question)
        if q is None or q.kind not in ("above", "below") or market.end_date is None:
            return None
        return (correlation_group(market), q.kind, market.end_date.isoformat()), q.threshold

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        groups = defaultdict(list)
        for m in markets:
            k = self._key(m)
            if k:
                groups[k[0]].append(m)
        return [m for g in groups.values() if len(g) >= 2 for m in g]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        groups = defaultdict(list)
        for m in watchlist:
            k = self._key(m)
            if k and len(m.token_ids) == 2:
                groups[k[0]].append((k[1], m))
        candidates = []
        used: set[str] = set()
        total = state.total_estimated(marks)
        for (group, kind, _), items in groups.items():
            items.sort(key=lambda t: t[0])
            for i, (k_low, low_m) in enumerate(items):
                for k_high, high_m in items[i + 1:]:
                    # « above » : Oui(K bas) + Non(K haut) ; « below » : Non(K bas) + Oui(K haut).
                    legs = ((low_m, 0), (high_m, 1)) if kind == "above" else ((low_m, 1), (high_m, 0))
                    books_ = [books.get(m.token_ids[s]) for m, s in legs]
                    if any(b is None or b.best_ask is None for b in books_):
                        continue
                    if any(m.token_ids[s] in state.positions or m.market_id in used for m, s in legs):
                        continue
                    try:
                        costs = [b.best_ask + taker_fee(ONE, b.best_ask, m.fees) for b, (m, _) in zip(books_, legs)]
                    except UnknownFees:
                        continue
                    edge = ONE - sum(costs)
                    if edge < p["min_net_edge"]:
                        continue
                    depth = min(b.asks[0].size for b in books_)
                    budget = min(p["stake_fraction"] * total, state.cash)
                    shares = min(depth, budget / sum(costs)).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                    for (m, s), b, c in zip(legs, books_, costs):
                        # Probabilités d'une jambe seule (le gain garanti vient de la paire).
                        mid = float(b.mid or b.best_ask)
                        prop = self._buy(m, books, state, s, mid, mid, mid, bucket, marks, out,
                                         f"cross_market:{group}:{k_low}<{k_high}",
                                         f"arbitrage d'échelle, marge {edge:.4f} par paire",
                                         "une seule jambe exécutée (risque directionnel)", shares=shares,
                                         skip_edge=True)
                        if prop is not None:
                            candidates.append(prop)
                            used.add(m.market_id)
        if not groups:
            out.abstain("aucune échelle de seuils")
        out.proposals = candidates[: 2 * int(p["max_proposals_per_cycle"])]  # par paires
        return out


# --------------------------------------------------------------------------- 5. market structure


class MarketStructure(_Base):
    """Déséquilibre du carnet près du milieu : plus d'acheteurs que de vendeurs → hausse probable
    à court terme. Mise fixe (`stake_fraction`), sortie : objectif atteint, stop, ou durée maximale."""

    strategy_id = "market_structure"
    required = ("min_imbalance", "max_spread", "depth_window", "stake_fraction", "take_profit",
                "stop_loss", "max_hold_hours", "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        candidates = []
        total = state.total_estimated(marks)
        for m in watchlist:
            if len(m.token_ids) != 2 or any(t in state.positions for t in m.token_ids):
                continue
            for side in (0, 1):
                book = books.get(m.token_ids[side])
                if book is None or book.mid is None or book.best_ask is None:
                    continue
                spread = book.best_ask - book.best_bid
                if spread > p["max_spread"] or not (Decimal("0.10") <= book.mid <= Decimal("0.90")):
                    continue
                window = p["depth_window"]
                bids = sum(l.size for l in book.bids if l.price >= book.mid - window)
                asks = sum(l.size for l in book.asks if l.price <= book.mid + window)
                if bids + asks <= 0:
                    continue
                imbalance = (bids - asks) / (bids + asks)
                if imbalance < p["min_imbalance"]:
                    continue
                stake = min(p["stake_fraction"] * total, state.cash)
                shares = (stake / book.best_ask).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                mid = float(book.mid)
                prop = self._buy(m, books, state, side, mid, mid, mid, bucket, marks, out,
                                 f"market_structure:imbalance={imbalance:.2f}",
                                 "court terme : le déséquilibre peut s'inverser",
                                 "objectif, stop ou durée maximale atteints", shares=shares,
                                 skip_edge=True)  # avantage à court terme, géré par les sorties
                if prop is not None:
                    candidates.append(prop)
                    break
        return self._finish(out, candidates)

    def exits(self, positions: dict[str, Position], markets: dict[str, MarketInfo],
              books: dict[str, OrderBook], bucket: str, now: datetime) -> list[Proposal]:
        p = self.params
        sells = []
        for token_id, pos in positions.items():
            book, market = books.get(token_id), markets.get(pos.market_id)
            if book is None or book.best_bid is None or market is None:
                continue
            held_h = (now - datetime.fromisoformat(pos.opened_at)).total_seconds() / 3600
            gain = book.best_bid - pos.avg_cost
            reason = ("objectif atteint" if gain >= p["take_profit"] else
                      "stop" if gain <= -p["stop_loss"] else
                      "durée maximale" if held_h >= float(p["max_hold_hours"]) else None)
            if reason is None:
                continue
            mid = _d(float(book.mid or book.best_bid))
            sells.append(Proposal(
                op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "SELL"), side="SELL",
                market_id=pos.market_id, event_id=pos.event_id, token_id=token_id, outcome=pos.outcome,
                est_probability=mid, prob_low=mid, prob_high=mid, max_price=book.best_bid,
                shares=pos.shares, net_edge=Decimal("0"), sources=("polymarket_clob",),
                uncertainty="sortie", invalidation=reason, horizon_hours=Decimal("0"),
                strategy_id=self.strategy_id, strategy_version=self.version))
        return sells


# --------------------------------------------------------------------------- 2. news momentum


class NewsMomentum(_Base):
    """Actualité confirmée (signal : >= 2 sources indépendantes) avec pic de mentions, et prix qui a
    bougé d'au moins `min_move` en 6 h : on parie que le mouvement continue (sous-réaction).
    Si Gemini donne une direction contraire au mouvement : abstention."""

    strategy_id = "news_momentum"
    needs_price_history = True
    required = ("min_spike", "min_move", "continuation", "uncertainty", "min_net_edge", "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            intel = m.intel
            if intel is None or not intel.signal:
                out.abstain("pas d'actualité confirmée")
                continue
            if intel.spike < float(p["min_spike"]):
                out.abstain("pas de pic de mentions")
                continue
            mid = self._mid(books, m)
            if mid is None or m.yes_price_6h_ago is None or any(t in state.positions for t in m.token_ids):
                out.abstain("prix ou historique indisponible")
                continue
            move = mid - m.yes_price_6h_ago
            if abs(move) < float(p["min_move"]):
                out.abstain("le prix n'a pas encore réagi")
                continue
            if intel.stance and (intel.stance > 0) != (move > 0):
                out.abstain("direction de l'IA contraire au mouvement")
                continue
            side = 0 if move > 0 else 1
            side_mid = mid if side == 0 else 1 - mid
            est = side_mid + float(p["continuation"])
            u = float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - u, est, est + u, bucket, marks, out,
                             f"news_momentum:{intel.independent_sources} sources, pic ×{intel.spike}",
                             f"a priori de continuation non calibré ± {u}",
                             "démenti, ou mouvement inversé")
            if prop:
                candidates.append(prop)
        return self._finish(out, candidates)


# --------------------------------------------------------------------------- 3. information advantage


class InformationAdvantage(_Base):
    """Annonce officielle récente rattachée au marché, direction donnée par Gemini (stance), prix
    pas encore bougé (< `max_reaction` en 1 h) : on prend la position avant que le marché réagisse.
    Sans Gemini, la direction est inconnue : abstention systématique (documentée)."""

    strategy_id = "information_advantage"
    needs_price_history = True
    required = ("max_age_minutes", "min_stance", "impact", "uncertainty", "max_reaction",
                "min_net_edge", "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            intel = m.intel
            if intel is None or intel.official_minutes is None or intel.official_minutes > float(p["max_age_minutes"]):
                out.abstain("pas d'annonce officielle récente")
                continue
            if abs(intel.official_stance) < float(p["min_stance"]):
                out.abstain("direction de l'annonce inconnue (Gemini inactif ou neutre)")
                continue
            mid = self._mid(books, m)
            if mid is None or m.yes_price_1h_ago is None or any(t in state.positions for t in m.token_ids):
                out.abstain("prix ou historique indisponible")
                continue
            if abs(mid - m.yes_price_1h_ago) > float(p["max_reaction"]):
                out.abstain("le marché a déjà réagi")
                continue
            side = 0 if intel.official_stance > 0 else 1
            side_mid = mid if side == 0 else 1 - mid
            est = side_mid + float(p["impact"]) * abs(intel.official_stance)
            u = float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - u, est, est + u, bucket, marks, out,
                             "information_advantage:annonce officielle",
                             f"impact a priori non calibré ± {u}", "annonce mal interprétée")
            if prop:
                candidates.append(prop)
        return self._finish(out, candidates)


# --------------------------------------------------------------------------- 6. social sentiment


class SocialSentiment(_Base):
    """Foule unilatérale (direction sociale forte d'après Gemini) SANS confirmation par des sources
    fiables (pas de signal) : on parie contre l'emballement. Sans Gemini : abstention."""

    strategy_id = "social_sentiment"
    required = ("min_stance", "min_mentions", "fade", "uncertainty", "min_net_edge", "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            intel = m.intel
            if intel is None or intel.mentions_24h < int(p["min_mentions"]):
                out.abstain("trop peu de discussions")
                continue
            if abs(intel.stance) < float(p["min_stance"]):
                out.abstain("pas d'emballement directionnel (ou Gemini inactif)")
                continue
            if intel.signal:
                out.abstain("emballement confirmé par des sources fiables : pas de pari contraire")
                continue
            mid = self._mid(books, m)
            if mid is None or any(t in state.positions for t in m.token_ids):
                out.abstain("prix indisponible")
                continue
            side = 1 if intel.stance > 0 else 0  # contre la foule
            side_mid = mid if side == 0 else 1 - mid
            est = side_mid + float(p["fade"])
            u = float(p["uncertainty"])
            prop = self._buy(m, books, state, side, est - u, est, est + u, bucket, marks, out,
                             f"social_sentiment:stance={intel.stance}", f"a priori contrarian ± {u}",
                             "information fiable qui confirme la foule")
            if prop:
                candidates.append(prop)
        return self._finish(out, candidates)


# --------------------------------------------------------------------------- météo


class MeteoForecast(_Base):
    """Marchés « température maximale / minimale à <ville> le <jour> » (≈ 400 par jour, réglés en
    1 à 2 jours). Probabilité de chaque tranche tirée des prévisions GFS et ECMWF (Open-Meteo)
    floutées de `sigma` et décalées de `bias` (weather_model.py), corrigée par ce que la station a
    déjà relevé.

    Test sur les marchés résolus du 1er au 15/10/2026, hors échantillon (experiments/meteo_backtest.md) :
    le marché surestime la tranche favorite. Parier NON sur une tranche cotée 0,2 à 0,8 quand le
    modèle la juge nettement moins probable a gagné tous les jours testés (≈ +20 % des mises après
    frais et écart achat-vente), alors que les paris OUI sur les tranches bon marché perdaient.
    D'où : NON seulement (`allow_yes` = 0), dans la fenêtre testée (de `max_lead_hours` avant le
    début du jour local à `min_lead_hours` après). Prix réels, carnets réels : l'arène tranche.
    """

    strategy_id = "meteo_prevision"
    required = ("min_net_edge", "margin", "sigma_max", "bias_max", "sigma_min", "bias_min",
                "max_lead_hours", "min_lead_hours", "min_no_price", "max_no_price", "max_proposals_per_cycle")

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        from polymarket_agent import weather_model as wm
        from polymarket_agent.sources.weather import station_of
        out = []
        for m in markets:
            if station_of(m.resolution_source, m.description) and wm.parse_question(m.question):
                if m.best_bid is not None and Decimal("0.15") <= m.best_bid <= Decimal("0.85"):
                    out.append(m)
        out.sort(key=lambda m: -float(m.liquidity))
        return out[: int(self.params.get("max_candidates", 100))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from datetime import timedelta, timezone
        from polymarket_agent import weather_model as wm
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            q = wm.parse_question(m.question)
            if q is None or len(m.token_ids) != 2 or any(t in state.positions for t in m.token_ids):
                continue
            w = m.weather or {}
            fc = w.get("prevision")
            if not fc:
                out.abstain("prévision météo indisponible")
                continue
            book = books.get(m.token_ids[1])
            if book is None:
                out.abstain("carnet indisponible")
                continue
            year = book.fetched_at.year
            date = f"{year}-{q.month:02d}-{q.day:02d}"
            day = (fc.get("jours") or {}).get(date)
            if not day:
                out.abstain("jour hors prévision")
                continue
            offset = timedelta(seconds=int(fc.get("utc_offset") or 0))
            start = datetime.fromisoformat(date).replace(tzinfo=timezone.utc) - offset  # minuit local
            lead = (start - book.fetched_at).total_seconds() / 3600
            if not -float(p["min_lead_hours"]) <= lead <= float(p["max_lead_hours"]):
                out.abstain("hors de la fenêtre testée")
                continue
            observed = None
            rel = w.get("releve") or {}
            if rel.get("jour_local") == date:
                observed = rel.get("max_jour_c")  # le maximum relevé ne peut que monter
            sigma, bias = ((p["sigma_max"], p["bias_max"]) if q.kind == "max" else (p["sigma_min"], p["bias_min"]))
            members = day["max" if q.kind == "max" else "min"]
            est_yes = wm.probability(q, members, float(sigma), float(bias), observed if q.kind == "max" else None)
            if est_yes is None:
                continue
            no_ask = book.best_ask
            if no_ask is None or not (p["min_no_price"] <= no_ask <= p["max_no_price"]):
                out.abstain("prix du NON hors de la zone testée")
                continue
            est_no = 1 - est_yes
            margin = float(p["margin"])
            # Beaucoup de petits paris (le test a gagné en moyenne sur des centaines) : Kelly réduit,
            # plafonné à `stake_fraction` du capital par pari.
            low_no = _d(est_no - margin)
            cost_ps = no_ask + taker_fee(ONE, no_ask, m.fees)
            kelly = size_buy(state, prob_low=low_no, cost_per_share=cost_ps,
                             kelly_fraction=p.get("kelly_fraction", Decimal("0.25")), marks=marks)
            cap = (p.get("stake_fraction", Decimal("0.03")) * state.total_estimated(marks) / cost_ps
                   ).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            prop = self._buy(m, books, state, 1, est_no - margin, est_no, min(0.999, est_no + margin), bucket, marks,
                             out, f"meteo_prevision:gfs+ecmwf {date} {q.kind}",
                             f"σ {float(sigma):.1f} °C, biais {float(bias):+.1f} °C, modèles {', '.join(f'{x:.1f}' for x in members)} °C",
                             "prévision ratée, station ou jour mal compris, arrondi de la source",
                             shares=min(kelly, cap))
            if prop is not None:
                candidates.append(prop)
            if p.get("allow_yes", Decimal("0")) > 0 and est_yes - margin > float(m.best_ask or 1):
                prop = self._buy(m, books, state, 0, est_yes - margin, est_yes, min(0.999, est_yes + margin),
                                 bucket, marks, out, f"meteo_prevision:{date}", "OUI : non validé par le test",
                                 "prévision ratée")
                if prop is not None:
                    candidates.append(prop)
        return self._finish(out, candidates)


CLASSES = {c.strategy_id: c for c in (CrossMarketLadder, MarketStructure, NewsMomentum,
                                      InformationAdvantage, SocialSentiment, MeteoForecast)}
