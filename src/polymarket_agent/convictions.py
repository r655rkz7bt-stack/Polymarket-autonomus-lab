"""Convictions de Claude (labo v2, demande d'Etienne du 07/11/2026 : « beaucoup plus de mainmise de Claude et du chercheur »).

Le chercheur étudie à fond quelques marchés (règles, source de résolution, données, actualité) et écrit sa propre prévision
dans `config/convictions.yaml` : probabilité, borne basse prudente, date limite, mise maximale, raison et sources. Le cycle
achète l'issue quand le vendeur demande moins que la borne basse moins `min_net_edge` (frais compris), avec la mise de Kelly
sur la borne basse, plafonnée par `mise_max`. Si Claude change d'avis (`abandon: true`, ou une probabilité devenue plus basse
que le prix auquel le marché rachète), la position est revendue au meilleur acheteur. Prix et carnets réels : aucune triche
possible, la prévision est écrite AVANT que le marché tranche et l'arène la juge comme toute autre stratégie.

Format d'une conviction (liste `convictions:`) :
  id: identifiant court ; marche: id Gamma du marché ; question: début de la question (contrôle d'identité) ;
  issue: libellé de l'issue achetée (« Yes », « No », un nom…) ; probabilite: 0-1 ; probabilite_basse: 0-1 (≤ probabilite) ;
  expire: AAAA-MM-JJ (plus d'achat après) ; mise_max: part du capital du fantôme (défaut 0,05) ; raison ; sources: [...] ;
  ecrit_le: AAAA-MM-JJ ; abandon: true pour revendre.
"""

from __future__ import annotations

import dataclasses
import logging
from datetime import date, datetime
from decimal import ROUND_DOWN, Decimal
from pathlib import Path

import yaml

from polymarket_agent.ledger import Position
from polymarket_agent.models import MarketInfo, OrderBook
from polymarket_agent.safety_controller import Proposal
from polymarket_agent.strategies_v2 import _Base, _d
from polymarket_agent.strategy_engine import StrategyOutput, make_op_id

log = logging.getLogger(__name__)


def charger(path: Path | None) -> list[dict]:
    """Convictions valides du fichier ; une ligne mal formée est ignorée (et journalisée), jamais fatale au cycle."""
    if path is None or not Path(path).exists():
        return []
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        log.warning("convictions illisibles : %s", exc)
        return []
    out = []
    for c in raw.get("convictions") or []:
        try:
            p, low = float(c["probabilite"]), float(c.get("probabilite_basse", c["probabilite"]))
            if not (0 < low <= p < 1) or not str(c["marche"]) or not str(c["issue"]):
                raise ValueError("probabilités ou identifiants invalides")
            out.append({**c, "marche": str(c["marche"]), "issue": str(c["issue"]), "probabilite": p,
                        "probabilite_basse": low, "mise_max": float(c.get("mise_max", 0.05)),
                        "expire": date.fromisoformat(str(c["expire"])) if c.get("expire") else None})
        except (KeyError, TypeError, ValueError) as exc:
            log.warning("conviction ignorée (%s) : %s", exc, c)
    return out


class ConvictionsClaude(_Base):
    """Prévisions écrites par Claude après recherche (config/convictions.yaml), jouées sur les vrais carnets."""

    strategy_id = "convictions_claude"
    required = ("min_net_edge", "kelly_fraction", "max_proposals_per_cycle")

    def __init__(self, version: str, created_at: str, params: dict[str, Decimal], table: Path | None = None):
        super().__init__(version, created_at, params)
        self.table = table

    def _convictions(self) -> dict[str, dict]:
        return {c["marche"]: c for c in charger(self.table)}

    def candidates(self, markets):
        wanted = self._convictions()
        return [m for m in markets if m.market_id in wanted]

    @staticmethod
    def _side(market: MarketInfo, issue: str) -> int | None:
        names = [str(o).strip().lower() for o in market.outcomes]
        return names.index(issue.strip().lower()) if issue.strip().lower() in names else None

    def propose(self, watchlist, books, state, limits, bucket, marks=None) -> StrategyOutput:
        out, props, wanted = StrategyOutput(), [], self._convictions()
        today = max((b.fetched_at for b in books.values() if b.fetched_at is not None), default=datetime.now()).date()
        for m in watchlist:
            c = wanted.get(m.market_id)
            if c is None:
                continue
            if c.get("abandon"):
                out.abstain("conviction abandonnée")
                continue
            if c["expire"] is not None and today > c["expire"]:
                out.abstain("conviction expirée")
                continue
            if c.get("question") and not (m.question or "").lower().startswith(str(c["question"]).lower()[:40]):
                out.abstain("question différente de la conviction (identifiant à vérifier)")
                continue
            side = self._side(m, c["issue"])
            if side is None:
                out.abstain("issue introuvable dans le marché")
                continue
            if any(t in state.positions for t in m.token_ids):
                out.abstain("déjà en position")
                continue
            book = books.get(m.token_ids[side])
            if book is None or book.best_ask is None:
                out.abstain("carnet indisponible")
                continue
            budget = Decimal(str(c["mise_max"])) * state.total_estimated(marks)
            prop = self._buy(m, books, state, side, c["probabilite_basse"], c["probabilite"],
                             min(0.999, 2 * c["probabilite"] - c["probabilite_basse"]), bucket, marks, out,
                             f"conviction:{c.get('id', m.market_id)}", str(c.get("raison", ""))[:200],
                             "la prévision de Claude était fausse ou dépassée par une nouvelle")
            if prop is not None:
                cap = (min(budget, state.cash) / prop.max_price).quantize(Decimal("0.01"), rounding=ROUND_DOWN)
                if prop.shares > cap:
                    prop = dataclasses.replace(prop, shares=cap) if cap >= m.min_order_size else None
                if prop is not None:
                    props.append(prop)
                else:
                    out.abstain("mise maximale trop faible pour le minimum du marché")
        return self._finish(out, props)

    def exits(self, positions: dict[str, Position], markets: dict[str, MarketInfo],
              books: dict[str, OrderBook], bucket: str, now: datetime) -> list[Proposal]:
        """Revendre quand Claude change d'avis : `abandon: true`, ou probabilité inférieure au prix offert par le marché."""
        wanted, sells = self._convictions(), []
        for token_id, pos in positions.items():
            c, book = wanted.get(pos.market_id), books.get(token_id)
            if c is None or book is None or book.best_bid is None:
                continue
            if not (c.get("abandon") or float(book.best_bid) > c["probabilite"]):
                continue
            mid = _d(c["probabilite"])
            sells.append(Proposal(
                op_id=make_op_id(bucket, self.strategy_id, self.version, token_id, "SELL"), side="SELL",
                market_id=pos.market_id, event_id=pos.event_id, token_id=token_id, outcome=pos.outcome,
                est_probability=mid, prob_low=mid, prob_high=mid, max_price=book.best_bid, shares=pos.shares,
                net_edge=Decimal("0"), sources=("polymarket_clob", f"conviction:{c.get('id', pos.market_id)}"),
                uncertainty="sortie", invalidation="conviction abandonnée" if c.get("abandon")
                else f"le marché paie {float(book.best_bid):.2f}, Claude n'en donne que {c['probabilite']:.2f}",
                horizon_hours=Decimal("0"), strategy_id=self.strategy_id, strategy_version=self.version))
        return sells
