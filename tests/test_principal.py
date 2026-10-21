"""Garde-fous du capital principal (17/10/2026) : mise par pari et argent engagé par famille plafonnés."""

from __future__ import annotations

from decimal import Decimal as D
from types import SimpleNamespace

from conftest import KEY, NOW, raw_market
from polymarket_agent.ledger import Ledger
from polymarket_agent.main import _cap_main
from polymarket_agent.safety_controller import Proposal
from polymarket_agent.sources.polymarket_gamma import parse_market


def _prop(market_id, token, shares, price="0.50", side="BUY"):
    return Proposal(op_id="o" + token, side=side, market_id=market_id, event_id="e", token_id=token, outcome="No",
                    est_probability=D("0.6"), prob_low=D("0.55"), prob_high=D("0.65"), max_price=D(price),
                    shares=D(shares), net_edge=D("0.05"), sources=("t",), uncertainty="", invalidation="",
                    horizon_hours=D("10"), strategy_id="s", strategy_version="1")


def test_main_portfolio_bets_and_families_are_capped(tmp_path):
    ledger = Ledger.create(tmp_path / "l.jsonl", KEY, tmp_path / "l.lock", "1000", now=NOW)
    weather = [parse_market(raw_market(f"w{i}", yes_token=f"wy{i}", no_token=f"wn{i}", feeType="weather_fees"))
               for i in range(3)]
    sport = parse_market(raw_market("s", yes_token="sy", no_token="sn", feeType="sports_fees_v3"))
    by_market = {m.market_id: m for m in weather + [sport]}
    # Déjà 350 engagés en météo.
    ledger.record_buy(op_id="b0", token_id="wn0", market_id="w0", event_id="e", outcome="No", shares="700",
                      price="0.5", fee="0", strategy_id="s", strategy_version="1", now=NOW)
    deps = SimpleNamespace(settings={"principal": {"max_mise": 0.10, "max_famille": 0.40}})
    portfolio = SimpleNamespace(ledger=ledger, marks={})
    out = _cap_main(deps, portfolio, [_prop("w1", "wn1", "400"), _prop("w2", "wn2", "400"), _prop("s", "sn", "400"),
                                      _prop("w2", "wn2", "50", side="SELL")], by_market)
    shares = {(p.token_id, p.side): p.shares for p in out}
    assert shares[("wn1", "BUY")] == D("100")        # météo : 400 − 350 = 50 de place → 100 parts à 0,50
    assert ("wn2", "BUY") not in shares               # famille pleine : écarté
    assert shares[("sn", "BUY")] == D("200")         # sport : mise ≤ 10 % de 1 000 → 200 parts à 0,50
    assert shares[("wn2", "SELL")] == D("50")        # une vente n'est jamais plafonnée
    assert _cap_main(SimpleNamespace(settings={}), portfolio, [_prop("s", "sn", "400")], by_market)[0].shares == D("400")


def test_shares_are_recomputed_at_most_hourly_but_entries_apply_at_once(tmp_path):
    """18/10/2026 : pas de va-et-vient des parts toutes les 5 minutes ; une entrée ou une sortie
    change la répartition tout de suite."""
    from datetime import timedelta
    from types import SimpleNamespace
    from conftest import NOW
    from polymarket_agent.main import _steady_shares
    from polymarket_agent.persistence import Database
    clock = {"t": NOW}
    deps = SimpleNamespace(settings={"arena": {"repartition": {"recalcul_minutes": 60}}},
                           db=Database(tmp_path / "s.sqlite"), now=lambda: clock["t"])
    assert _steady_shares(deps, {"a": 0.4, "b": 0.2}) == {"a": 0.4, "b": 0.2}
    clock["t"] = NOW + timedelta(minutes=5)
    assert _steady_shares(deps, {"a": 0.41, "b": 0.19}) == {"a": 0.4, "b": 0.2}     # gardées
    assert _steady_shares(deps, {"a": 0.3, "b": 0.2, "c": 0.1}) == {"a": 0.3, "b": 0.2, "c": 0.1}  # entrée
    clock["t"] = NOW + timedelta(minutes=70)
    assert _steady_shares(deps, {"a": 0.25, "b": 0.25, "c": 0.1}) == {"a": 0.25, "b": 0.25, "c": 0.1}  # 1 h passée


def test_a_strategy_never_engages_more_than_its_share_in_total(tmp_path):
    """18/10/2026 : nf_court avait 630 investis sur ≈ 1 000 pour une part d'environ 50 % ; réduire
    chaque mise ne suffisait pas. Positions déjà ouvertes + nouveaux achats ≤ part × capital."""
    import dataclasses
    from decimal import Decimal as D
    from types import SimpleNamespace
    from conftest import KEY, NOW, buy
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.main import Weighted
    ledger = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW)
    for k in range(4):  # 4 × 100 déjà investis par la stratégie
        ledger.record_buy(op_id=f"o{k}", token_id=f"t{k}", market_id=f"m{k}", event_id=f"e{k}", outcome="Yes",
                          shares="200", price="0.5", fee="0", strategy_id="nf_court", strategy_version="1", now=NOW)
    buy(ledger, "x1", token="autre", shares="200", price="0.5")  # une autre stratégie : ne compte pas

    @dataclasses.dataclass
    class Prop:
        side: str
        shares: D
        max_price: D
        op_id: str

    def prop(op, shares, price="0.5"):
        return Prop("BUY", D(shares), D(price), op)

    class Inner:
        strategy_id, version = "nf_court", "1"

        def propose(self, watchlist, books, state, limits, bucket, marks=None):
            return SimpleNamespace(proposals=[prop("a", "300"), prop("b", "300"), prop("c", "300")], limit_orders=[])

    out = Weighted(Inner(), D("0.5")).propose([], {}, ledger.state, None, "b1")
    # Part 0,5 × capital 1 000 = 500 ; 400 déjà investis → 100 de budget, soit 200 parts à 0,5.
    assert [(p.op_id, p.shares) for p in out.proposals] == [("a", D("150")), ("b", D("50"))]


def test_principal_copies_the_ghost_bets_at_its_own_scale(tmp_path):
    """Copie fidèle (18/10/2026) : le principal refait les paris que le fantôme vient de faire, mêmes
    marchés, mise à l'échelle (part × capital du principal / capital du fantôme) ; il ne rachète pas
    les positions que le fantôme tenait déjà, et ne parie pas quand le fantôme ne parie pas."""
    import dataclasses
    from decimal import Decimal as D
    from conftest import KEY, NOW
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.main import Portfolio, Weighted

    @dataclasses.dataclass
    class Prop:
        side: str
        token_id: str
        shares: D
        max_price: D
        op_id: str

    class Inner:
        strategy_id, version = "nf_sport", "1"

        def propose(self, *args, **kwargs):
            raise AssertionError("en copie fidèle, la stratégie n'est pas relancée sur le principal")

    main = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW)
    main.record_buy(op_id="old", token_id="deja", market_id="m0", event_id="e0", outcome="Yes", shares="10",
                    price="0.5", fee="0", strategy_id="nf_sport", strategy_version="1", now=NOW)
    ghost = Portfolio("fantome:nf_sport_v1", None, [])
    ghost.copied = {"nf_sport": {"total": D("2000"), "buys": [(Prop("BUY", "t1", D("90"), D("0.9"), "a"), D("80")),
                                                              (Prop("BUY", "deja", D("50"), D("0.5"), "b"), D("50"))],
                                 "orders": [Prop("BUY", "t2", D("40"), D("0.8"), "c"),
                                            Prop("SELL", "deja", D("100"), D("0.6"), "d"),
                                            Prop("SELL", "absent", D("100"), D("0.6"), "e")]}}
    out = Weighted(Inner(), D("0.5"), source=ghost).propose([], {}, main.state, None, "b1")
    # Échelle : 0,5 × 1 000 / 2 000 = 0,25 → 80 parts exécutées par le fantôme deviennent 20.
    assert [(p.op_id, p.shares) for p in out.proposals] == [("a", D("20"))]  # « deja » : déjà détenu
    # Ordres posés : l'achat à l'échelle ; la revente seulement du stock détenu (10 parts au plus).
    assert [(p.op_id, p.side, p.shares) for p in out.limit_orders] == [("c", "BUY", D("10")), ("d", "SELL", D("10"))]
    ghost.copied = {"nf_sport": {"total": D("2000"), "buys": [], "orders": []}}
    assert Weighted(Inner(), D("0.5"), source=ghost).propose([], {}, main.state, None, "b1").proposals == []
    # Le fantôme n'a rien enregistré (suspendu, autre stratégie) : rien à copier.
    ghost.copied = {}
    out = Weighted(Inner(), D("0.5"), source=ghost).propose([], {}, main.state, None, "b1")
    assert out.proposals == [] and out.limit_orders == []


def test_principal_copies_at_base_stake_whatever_the_ghost_prudence(tmp_path):
    """« Grossir les gagnantes » (21/10/2026) : la prudence du fantôme (½, entière, ¼, renfort) sert à
    l'arène ; le principal copie toujours à la mise de base simulée avec Etienne (son propre renfort
    passe par l'arène, une seule fois)."""
    import dataclasses
    from decimal import Decimal as D
    from conftest import KEY, NOW
    from polymarket_agent.ledger import Ledger
    from polymarket_agent.main import Portfolio, Weighted

    @dataclasses.dataclass
    class Prop:
        side: str
        token_id: str
        shares: D
        max_price: D
        op_id: str

    class Inner:
        strategy_id, version = "nf_sport", "1"

    main = Ledger.create(tmp_path / "p.jsonl", KEY, tmp_path / "p.lock", "1000", now=NOW)
    ghost = Portfolio("fantome:nf_sport_v1", None, [])
    ghost.copied = {"nf_sport": {"total": D("1000"), "buys": [(Prop("BUY", "t1", D("80"), D("0.9"), "a"), D("80"))],
                                 "orders": []}}
    for prudence, want in [(D("0.5"), D("40")), (D("1"), D("20")), (D("2"), D("10")), (D("0.25"), D("80"))]:
        out = Weighted(Weighted(Inner(), prudence), D("0.5"), source=ghost, base=D("0.5")).propose([], {}, main.state, None, "b1")
        # 80 parts du fantôme, part 0,5, mise de base 0,5 : comme si le fantôme avait misé à ½.
        assert [(p.op_id, p.shares) for p in out.proposals] == [("a", want)], prudence
    plain = Weighted(Weighted(Inner(), D("1")), D("0.5"), source=ghost).propose([], {}, main.state, None, "b1")
    assert [p.shares for p in plain.proposals] == [D("40")]  # sans `base` : copie à l'échelle, comme avant
