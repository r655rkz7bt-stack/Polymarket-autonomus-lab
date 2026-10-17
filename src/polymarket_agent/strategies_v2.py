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

    def _model(self, m: MarketInfo, book: OrderBook, out: StrategyOutput | None = None) -> dict | None:
        """Probabilité du OUI selon les prévisions (et ce qu'il faut pour l'expliquer), ou None."""
        from datetime import timedelta, timezone
        from polymarket_agent import weather_model as wm
        p = self.params
        abstain = out.abstain if out is not None else (lambda reason: None)
        q = wm.parse_question(m.question)
        if q is None:
            return None
        w = m.weather or {}
        fc = w.get("prevision")
        if not fc:
            abstain("prévision météo indisponible")
            return None
        year = book.fetched_at.year
        date = f"{year}-{q.month:02d}-{q.day:02d}"
        day = (fc.get("jours") or {}).get(date)
        if not day:
            abstain("jour hors prévision")
            return None
        offset = timedelta(seconds=int(fc.get("utc_offset") or 0))
        start = datetime.fromisoformat(date).replace(tzinfo=timezone.utc) - offset  # minuit local
        lead = (start - book.fetched_at).total_seconds() / 3600
        observed = None
        if w.get("jour_local") == date:
            observed = w.get("max_jour_c")  # le maximum relevé ne peut que monter
        sigma, bias = ((p["sigma_max"], p["bias_max"]) if q.kind == "max" else (p["sigma_min"], p["bias_min"]))
        used = 0
        if p.get("station_calibration", Decimal("0")) > 0:
            # Biais et flou propres à la station (erreurs des jours précédents), tirés vers le réglage global.
            from polymarket_agent.weather_calibration import station_params
            past = ((fc.get("erreurs") or {}).get(q.kind) or [])[: int(p.get("calibration_days", 7))]
            sigma, bias, used = station_params(past, float(sigma), float(bias),
                                               int(p.get("calibration_min_days", 3)),
                                               float(p.get("calibration_shrink", 3)),
                                               float(p.get("sigma_floor", Decimal("0.8"))))
        members = day["max" if q.kind == "max" else "min"]
        est_yes = wm.probability(q, members, float(sigma), float(bias), observed if q.kind == "max" else None)
        if est_yes is None:
            return None
        return {"yes": est_yes, "q": q, "date": date, "lead": lead, "sigma": sigma, "bias": bias, "used": used,
                "members": members}

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            if len(m.token_ids) != 2 or any(t in state.positions for t in m.token_ids):
                continue
            book = books.get(m.token_ids[1])
            if book is None:
                out.abstain("carnet indisponible")
                continue
            model = self._model(m, book, out)
            if model is None:
                continue
            if not -float(p["min_lead_hours"]) <= model["lead"] <= float(p["max_lead_hours"]):
                out.abstain("hors de la fenêtre testée")
                continue
            est_yes, q, date, sigma, bias, used, members = (model[k] for k in
                                                            ("yes", "q", "date", "sigma", "bias", "used", "members"))
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
                             f"σ {float(sigma):.1f} °C, biais {float(bias):+.1f} °C"
                             + (f" (station, {used} j)" if used >= int(p.get("calibration_min_days", 3)) else "")
                             + f", modèles {', '.join(f'{x:.1f}' for x in members)} °C",
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

    def exits(self, positions: dict[str, Position], markets: dict[str, MarketInfo],
              books: dict[str, OrderBook], bucket: str, now: datetime) -> list[Proposal]:
        """Sortie quand l'avantage s'est retourné (AMELIORATION n°7, 17/10/2026) : le marché RACHÈTE
        le NON plus cher que ce que le modèle lui donne (meilleur acheteur ≥ probabilité du modèle
        + `exit_margin`). Vendre est alors gagnant d'après le modèle lui-même ; sinon on garde
        jusqu'au règlement. Sans prévision à jour pour ce marché : on garde."""
        margin = float(self.params.get("exit_margin", Decimal("0.03")))
        sells = []
        for token_id, pos in positions.items():
            market, book = markets.get(pos.market_id), books.get(token_id)
            if market is None or book is None or book.best_bid is None or len(market.token_ids) != 2:
                continue
            if token_id != market.token_ids[1]:
                continue  # seuls les paris NON sont pris par cette stratégie
            model = self._model(market, book)
            if model is None:
                continue
            est_no = 1 - model["yes"]
            if float(book.best_bid) < est_no + margin:
                continue
            mid = _d(est_no)
            sells.append(Proposal(
                op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "SELL"), side="SELL",
                market_id=pos.market_id, event_id=pos.event_id, token_id=token_id, outcome=pos.outcome,
                est_probability=mid, prob_low=mid, prob_high=mid, max_price=book.best_bid,
                shares=pos.shares, net_edge=Decimal("0"), sources=("open_meteo", "polymarket_clob"),
                uncertainty="sortie", invalidation=f"le marché paie {float(book.best_bid):.2f}, le modèle n'en donne que {est_no:.2f}",
                horizon_hours=Decimal("0"), strategy_id=self.strategy_id, strategy_version=self.version))
        return sells


# --------------------------------------------------------------------------- 8. température (chantier n°0)


class TemperatureFloor(_Base):
    """Marchés « température maximale du jour » : le maximum ne peut que monter. Tranche déjà
    dépassée de `margin_c` / `margin_f` degrés par le maximum METAR du jour → « Non » quasi certain ;
    tranche « X ou plus » déjà atteinte → « Oui » quasi certain. Le risque restant (erreur de jour
    local, de conversion, de source) est le paramètre `certainty`, borne basse de la probabilité."""

    strategy_id = "temperature_floor"
    required = ("margin_c", "margin_f", "certainty", "min_net_edge", "max_extra_ticks",
                "max_proposals_per_cycle")

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.weather_model import certain_side, parse_bucket
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            w = getattr(m, "weather", None)
            b = parse_bucket(m.question)
            if w is None or b is None or w.get("max_jour_c") is None or len(m.token_ids) != 2:
                continue
            if str(w.get("jour_local", ""))[5:] != f"{b.month:02d}-{b.day:02d}":
                out.abstain("jour de l'observation différent du jour du marché")
                continue
            if any(t in state.positions for t in m.token_ids):
                continue
            side = certain_side(b, float(w["max_jour_c"]), float(p["margin_c"]), float(p["margin_f"]))
            if side is None:
                continue
            c = float(p["certainty"])
            prop = self._buy(m, books, state, side, c, min(c + 0.02, 0.995), 0.999, bucket, marks, out,
                             f"meteo_metar:{w.get('station')}:max={w['max_jour_c']}°C",
                             "erreur de jour local, de conversion °F ou de source de résolution",
                             "relevé METAR corrigé / source de résolution différente")
            if prop:
                candidates.append(prop)
        return self._finish(out, candidates)



# --------------------------------------------------------------------------- 9. tenue de marché


class MarketMaker(_Base):
    """Tenue de marché (« market making », 16/10/2026, experiments/veille_bots/) : ce que font les
    bots qui gagnent durablement. On ne prédit rien : on pose à chaque cycle un ordre d'ACHAT du OUI
    au meilleur acheteur et un ordre d'ACHAT du NON au meilleur acheteur du NON (= vente du OUI au
    meilleur vendeur). Si les deux sont servis, on détient une paire OUI + NON qui vaut 1 à coup
    sûr, payée 1 − écart : c'est l'écart capturé. On gagne aussi (estimé à part, hors capital) les
    récompenses de liquidité de Polymarket et, sur le vrai marché, une remise sur les frais.

    Risques gérés :
    - stock : ce qui est détenu est REVENDU au meilleur vendeur (libère le capital et capture
      l'écart) au lieu d'acheter l'autre côté ; au-delà de `max_net_quotes` cotes nettes d'un côté,
      on ne cote plus que le côté qui rééquilibre ; perte coupée par `stop_loss` (vente immédiate) ;
    - sélection adverse (on est servi quand on a tort) : marchés CALMES seulement (prix stable sur
      6 h, milieu 0,15-0,85, échéance lointaine), ni sport ni crypto (flux rapides), cotes jamais
      plus serrées que `min_pair_margin` (paire achetée au plus 1 − marge) ;
    - ordres de courte durée (`quote_hours`) : une cote non renouvelée disparaît d'elle-même.
    Marchés choisis : cagnotte de récompense par dollar de liquidité déjà présente la plus haute.
    """

    strategy_id = "market_maker"
    forecasting = False  # ne prédit rien : pas de « mise prudente » sur des prévisions (main._apply_health)
    required = ("min_days_to_end", "min_mid", "max_mid", "max_move_6h", "min_reward_rate",
                "improve_ticks", "min_pair_margin", "market_fraction", "max_net_quotes", "stop_loss",
                "quote_hours", "max_markets", "max_candidates")
    needs_price_history = True

    def _calm(self, m: MarketInfo, now: datetime | None = None) -> bool:
        p = self.params
        if len(m.token_ids) != 2 or m.best_bid is None or m.best_ask is None:
            return False
        if m.fees.rebate_rate is not None and m.fees.rebate_rate < Decimal("0.25"):
            return False  # sport (0,15) et crypto (0,20) : flux rapides, sélection adverse forte
        mid = (m.best_bid + m.best_ask) / 2
        if not (p["min_mid"] <= mid <= p["max_mid"]):
            return False
        if m.end_date is not None and now is not None and \
                (m.end_date - now).total_seconds() < float(p["min_days_to_end"]) * 86400:
            return False
        if m.yes_price_6h_ago is not None and abs(float(mid) - m.yes_price_6h_ago) > float(p["max_move_6h"]):
            return False
        return m.rewards_daily_rate >= p["min_reward_rate"]

    @staticmethod
    def _attractiveness(m: MarketInfo) -> float:
        return float(m.rewards_daily_rate) / (float(m.liquidity) + 1000)

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        out = [m for m in markets if self._calm(m)]  # échéance vérifiée dans propose (heure du carnet)
        out.sort(key=self._attractiveness, reverse=True)
        return out[: int(self.params["max_candidates"])]

    def _order(self, m: MarketInfo, side: int, order_side: str, price: Decimal, shares: Decimal, mid: float,
               bucket: str, why: str) -> Proposal:
        token = m.token_ids[side]
        est = mid if side == 0 else 1 - mid
        est = min(0.98, max(0.02, est))
        return Proposal(
            op_id=make_op_id(bucket, self.strategy_id, self.version, token, order_side), side=order_side,
            market_id=m.market_id, event_id=m.event_id, token_id=token, outcome=m.outcomes[side],
            est_probability=_d(est), prob_low=_d(est - 0.01), prob_high=_d(est + 0.01), max_price=price,
            shares=shares, net_edge=_d(est - float(price)), sources=("polymarket_clob", "tenue_de_marche"),
            uncertainty=why, invalidation="nouvelle qui fait bouger le prix (sélection adverse)",
            horizon_hours=Decimal(str(self.params["quote_hours"])), strategy_id=self.strategy_id,
            strategy_version=self.version)

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        p, out, now = self.params, StrategyOutput(), None
        mine = {t: pos for t, pos in state.positions.items() if pos.strategy_id == self.strategy_id}
        total = state.total_estimated(marks)
        quoted = 0
        markets = sorted((m for m in watchlist if len(m.token_ids) == 2), key=self._attractiveness, reverse=True)
        for m in markets:
            yb, nb = books.get(m.token_ids[0]), books.get(m.token_ids[1])
            held_y, held_n = mine.get(m.token_ids[0]), mine.get(m.token_ids[1])
            if not (held_y or held_n):
                if quoted >= int(p["max_markets"]):
                    break
                now = now or (yb.fetched_at if yb is not None else None)
                if not self._calm(m, now):
                    continue
            if yb is None or nb is None or None in (yb.best_bid, yb.best_ask, nb.best_bid, nb.best_ask):
                out.abstain("carnet incomplet")
                continue
            tick = yb.tick_size
            qy = min(yb.best_bid + tick * int(p["improve_ticks"]), yb.best_ask - tick)
            qn = min(nb.best_bid + tick * int(p["improve_ticks"]), nb.best_ask - tick)
            if qy <= 0 or qn <= 0 or qy + qn > ONE - p["min_pair_margin"]:
                out.abstain("écart trop serré pour coter")
                continue
            mid = float(yb.best_bid + yb.best_ask) / 2
            budget = p["market_fraction"] * total
            size = max(m.rewards_min_size or m.min_order_size, m.min_order_size)
            ny = held_y.shares if held_y else Decimal("0")
            nn = held_n.shares if held_n else Decimal("0")
            net = ny - nn  # parts nettes de OUI (une paire OUI + NON est sans risque)
            max_net = p["max_net_quotes"] * size
            invested = (held_y.cost_basis if held_y else 0) + (held_n.cost_basis if held_n else 0)
            room = budget - invested
            orders = []
            q2 = lambda x: x.quantize(Decimal("0.01"), rounding=ROUND_DOWN)  # noqa: E731
            # Côté « acheteur du OUI » : revendre le NON détenu (libère du capital), sinon acheter le OUI.
            if net < max_net:
                if nn > 0:
                    ask_n = max(nb.best_ask - tick * int(p["improve_ticks"]), nb.best_bid + tick)
                    orders.append(self._order(m, 1, "SELL", ask_n, q2(min(nn, size)), mid, bucket,
                                              "revente du NON détenu"))
                elif room > 0:
                    shares = min(size, q2(room / qy))
                    if shares >= m.min_order_size:
                        orders.append(self._order(m, 0, "BUY", qy, shares, mid, bucket, "cote d'achat du OUI"))
            # Côté « vendeur du OUI » : revendre le OUI détenu, sinon acheter le NON.
            if -net < max_net:
                if ny > 0:
                    ask_y = max(yb.best_ask - tick * int(p["improve_ticks"]), yb.best_bid + tick)
                    orders.append(self._order(m, 0, "SELL", ask_y, q2(min(ny, size)), mid, bucket,
                                              "revente du OUI détenu"))
                elif room > 0:
                    shares = min(size, q2(room / qn))
                    if shares >= m.min_order_size:
                        orders.append(self._order(m, 1, "BUY", qn, shares, mid, bucket, "cote d'achat du NON"))
            orders = [o for o in orders if o.shares > 0]
            if orders:
                out.limit_orders += orders
                quoted += 1
        return out

    def exits(self, positions: dict[str, Position], markets: dict[str, MarketInfo], books, bucket, now):
        """Coupe la perte : la partie NON appariée d'un stock dont le prix a chuté de `stop_loss`
        sous son coût est vendue au meilleur acheteur (preneur)."""
        out = []
        by_market: dict[str, list[Position]] = defaultdict(list)
        for pos in positions.values():
            by_market[pos.market_id].append(pos)
        for market_id, held in by_market.items():
            m = markets.get(market_id)
            if m is None or len(m.token_ids) != 2:
                continue
            shares = {pos.token_id: pos.shares for pos in held}
            for pos in held:
                other = m.token_ids[1] if pos.token_id == m.token_ids[0] else m.token_ids[0]
                excess = pos.shares - shares.get(other, Decimal("0"))
                book = books.get(pos.token_id)
                if excess <= 0 or book is None or book.best_bid is None:
                    continue
                if book.best_bid <= pos.avg_cost - self.params["stop_loss"]:
                    side = m.token_ids.index(pos.token_id)
                    mid = float(book.best_bid)
                    out.append(self._order(m, side, "SELL", book.best_bid,
                                           excess.quantize(Decimal("0.01"), rounding=ROUND_DOWN),
                                           mid if side == 0 else 1 - mid, bucket,
                                           f"coupe-perte : {book.best_bid} contre un coût de {pos.avg_cost:.3f}"))
        return [o for o in out if o.shares > 0]


# --------------------------------------------------------------------------- 10. mouvement de prix


class PriceMove(_Base):
    """Mouvement récent du prix (16/10/2026, experiments/favori.md §6) : selon la famille, un prix
    qui vient de bouger continue (politique : l'information s'y diffuse lentement, SUIVRE +3 à +7 %
    sur les deux moitiés de la période) ou revient en arrière (crypto à seuil : les mouvements y
    sont exagérés, CONTRER +12 à +17 %). `direction` = 1 suivre, −1 contrer ; mouvement = milieu
    actuel − prix d'il y a 6 h (historique du CLOB) ; estimation = prix de l'issue achetée +
    `edge_prior` (a priori tiré du test, NON garanti). Familles : YAML `familles`."""

    strategy_id = "price_move"
    required = ("direction", "min_move", "min_price", "max_price", "edge_prior", "uncertainty",
                "min_net_edge", "max_proposals_per_cycle")
    needs_price_history = True
    families: tuple[str, ...] = ()
    exclude_words: tuple[str, ...] = ()

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        from polymarket_agent.strategy_engine import excluded, market_family
        if not self.families or self.params.get("max_candidates", Decimal("0")) <= 0:
            return []
        out = [m for m in markets if len(m.token_ids) == 2 and market_family(m) in self.families
               and not excluded(m, self.exclude_words) and m.best_bid is not None and m.best_ask is not None]
        out.sort(key=lambda m: -m.volume_24h)
        return out[: int(self.params["max_candidates"])]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.strategy_engine import excluded, market_family
        p, out, candidates = self.params, StrategyOutput(), []
        for m in watchlist:
            if len(m.token_ids) != 2 or any(t in state.positions for t in m.token_ids):
                continue
            if (self.families and market_family(m) not in self.families) or excluded(m, self.exclude_words):
                continue
            if m.yes_price_6h_ago is None:
                out.abstain("historique de prix indisponible")
                continue
            mid = self._mid(books, m)
            book = books.get(m.token_ids[0])
            if mid is None or book is None:
                out.abstain("carnet indisponible")
                continue
            ref = m.game_start or m.end_date
            if ref is not None and ("min_hours" in p or "max_hours" in p):
                hours = Decimal(str((ref - book.fetched_at).total_seconds() / 3600))
                if not p.get("min_hours", Decimal("-1e9")) <= hours <= p.get("max_hours", Decimal("1e9")):
                    out.abstain("hors de la fenêtre de temps")
                    continue
            move = mid - m.yes_price_6h_ago
            if abs(move) < float(p["min_move"]):
                out.abstain("pas de mouvement suffisant")
                continue
            up = move > 0
            side = (0 if up else 1) if p["direction"] > 0 else (1 if up else 0)
            price = mid if side == 0 else 1 - mid
            if not float(p["min_price"]) <= price <= float(p["max_price"]):
                out.abstain("issue hors de la plage de prix")
                continue
            est = price + float(p["edge_prior"])
            u = float(p["uncertainty"])
            verb = "suivre" if p["direction"] > 0 else "contrer"
            prop = self._buy(m, books, state, side, est - u, est, min(0.999, est + u), bucket, marks, out,
                             f"mouvement_6h:{move:+.3f}", f"{verb} un mouvement de {move:+.2f} en 6 h (a priori ± {u})",
                             "le mouvement était une vraie information (ou un vrai excès) : l'inverse de la règle")
            if prop is not None:
                candidates.append(prop)
        return self._finish(out, candidates)

# --------------------------------------------------------------------------- 11. sport : scores et cotes


def _two_teams(m: MarketInfo) -> bool:
    return len(m.token_ids) == 2 and len(m.outcomes) == 2 and {o.lower() for o in m.outcomes} != {"yes", "no"}


class FinDeMatch(_Base):
    """« Le match est fini, le marché n'est pas encore réglé » (AMELIORATION n°2, 17/10/2026).

    Le score FINAL officiel de la ligue (mlb.com, nhl.com, football-data.org) désigne le gagnant ;
    tant que Polymarket n'a pas réglé le marché, son jeton se vend parfois encore sous 0,99 : on
    l'achète (frais déduits, avantage ≥ `min_net_edge`). Risque restant (`certainty`) : mauvais
    rattachement d'équipe (prudent, sports_link.py), score corrigé, litige de résolution.
    Test sur le passé : experiments/fin_de_match/."""

    strategy_id = "fin_de_match"
    required = ("certainty", "max_price", "min_net_edge", "stake_fraction", "max_proposals_per_cycle")

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc)
        hours = float(self.params.get("window_hours", 8))
        out = [m for m in markets if _two_teams(m) and m.game_start is not None
               and now - timedelta(hours=hours) <= m.game_start <= now - timedelta(minutes=60)]
        out.sort(key=lambda m: -float(m.volume_24h))
        return out[: int(self.params.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out = StrategyOutput()
        p = self.params
        candidates = []
        total = state.total_estimated(marks)
        for m in watchlist:
            sp = getattr(m, "sport", None)
            if not sp or sp.get("gagnant") is None or not _two_teams(m):
                continue
            side = int(sp["gagnant"])
            if any(t in state.positions for t in m.token_ids):
                continue
            book = books.get(m.token_ids[side])
            if book is None or book.best_ask is None:
                out.abstain("carnet indisponible")
                continue
            if book.best_ask > p["max_price"]:
                out.abstain("gagnant déjà au prix plein")
                continue
            cost = book.best_ask + taker_fee(ONE, book.best_ask, m.fees)
            shares = (min(p["stake_fraction"] * total, state.cash) / cost).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
            sure = float(p["certainty"])
            prop = self._buy(m, books, state, side, sure, sure, 0.999, bucket, marks, out,
                             f"fin_de_match:{sp.get('ligue')} {sp.get('score')}",
                             f"score final officiel ({sp.get('ligue')}), marché pas encore réglé",
                             "mauvais rattachement d'équipe, score corrigé, litige de résolution", shares=shares)
            if prop is not None:
                candidates.append(prop)
        return self._finish(out, candidates)


class CotesBookmakers(_Base):
    """Polymarket contre les bookmakers (AMELIORATION n°5, 17/10/2026) : avant le match, probabilité
    implicite moyenne des bookmakers (The Odds API, marge retirée) ; on achète l'issue que Polymarket
    vend nettement moins cher (avantage ≥ `min_net_edge` après frais, sur la borne basse
    probabilité − `margin`). Cotes relevées toutes les 12 h (offre gratuite) : trop vieilles au-delà
    de `max_odds_age_hours`, on s'abstient. La comparaison avec Kalshi n'avait rien donné
    (experiments/sport_kalshi.md) ; l'arène juge celle-ci."""

    strategy_id = "cotes_bookmakers"
    required = ("margin", "min_net_edge", "max_odds_age_hours", "max_proposals_per_cycle")

    def candidates(self, markets: list[MarketInfo]) -> list[MarketInfo]:
        from datetime import timedelta, timezone
        now = datetime.now(timezone.utc)
        out = [m for m in markets if _two_teams(m) and m.game_start is not None
               and now + timedelta(minutes=30) <= m.game_start <= now + timedelta(hours=float(self.params.get("horizon_hours", 36)))]
        out.sort(key=lambda m: -float(m.volume_24h))
        return out[: int(self.params.get("max_candidates", 40))]

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        from polymarket_agent.sports_link import age_minutes
        out = StrategyOutput()
        p = self.params
        candidates = []
        for m in watchlist:
            sp = getattr(m, "sport", None)
            if not sp or not sp.get("cotes") or not _two_teams(m) or any(t in state.positions for t in m.token_ids):
                continue
            book0 = books.get(m.token_ids[0])
            if book0 is None:
                continue
            age = age_minutes(sp.get("cotes_le"), book0.fetched_at)
            if age is None or age > float(p["max_odds_age_hours"]) * 60:
                out.abstain("cotes trop vieilles")
                continue
            if sp.get("etat") in ("en cours", "terminé") or (m.game_start and m.game_start <= book0.fetched_at):
                out.abstain("match commencé")
                continue
            margin = float(p["margin"])
            best = None
            for side in (0, 1):
                prob = float(sp["cotes"][side])
                prop = self._buy(m, books, state, side, prob - margin, prob, min(0.999, prob + margin), bucket, marks,
                                 out, f"cotes_bookmakers:{prob:.3f}", f"moyenne des bookmakers {prob:.0%}, marge {margin:.0%}",
                                 "cotes en retard sur l'actualité (blessure, composition)")
                if prop is not None and (best is None or prop.net_edge > best.net_edge):
                    best = prop
            if best is not None:
                candidates.append(best)
        return self._finish(out, candidates)


CLASSES = {c.strategy_id: c for c in (CrossMarketLadder, MarketStructure, NewsMomentum,
                                      InformationAdvantage, SocialSentiment, MeteoForecast,
                                      TemperatureFloor, MarketMaker, PriceMove, FinDeMatch, CotesBookmakers)}
