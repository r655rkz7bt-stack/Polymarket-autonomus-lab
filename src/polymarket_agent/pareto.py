"""Entonnoir 80/20 : quel petit morceau des paris d'une stratégie fait l'essentiel de ses gains ?
(demande d'Etienne, 20/10/2026)

« Trouve les 20 % qui créent les 80 % des résultats, et applique ça à tous les entonnoirs, à tout
ce qui fait une grosse croissance. » Pour chaque stratégie qui grandit vite (ou plus vite que sa
mère), chaque opération clôturée est rangée selon plusieurs caractéristiques :
  prix payé, délai jusqu'à l'échéance, issue (oui / non / équipe), heure d'achat (UTC),
  discipline (tennis, Counter-Strike, NFL…), type de pari (vainqueur, handicap, total…),
  mode d'achat (immédiat ou ordre posé) et source de résolution du marché.
Pour chaque caractéristique : résultat, rendement par mise, score de confiance, paris gagnés
contre attendus d'après les prix, et le « cœur » = les morceaux qui font 80 % des gains, avec la
part des paris qu'ils représentent. Les morceaux qui battent la stratégie entière deviennent des
FILLES proposées (filtres de `strategy_engine.Filtered`, sans nouveau code) ; le chercheur les
met dans l'arène, qui tranche. Peu de paris = des pistes, pas des preuves.

Les classements `discipline` et `type_pari` servent aussi de filtres (`disciplines`,
`types_pari`) : l'analyse et les filles rangent les marchés exactement de la même façon.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from datetime import datetime

from polymarket_agent.arena import t_stat
from polymarket_agent.reporting import closed_trades

# ------------------------------------------------------------------ classements (aussi filtres)
_DISCIPLINES = (  # premier motif trouvé dans le libellé (minuscules) ; l'ordre compte
    ("counter-strike", r"counter-strike|\bcs2?\b"), ("lol", r"\blol\b|league of legends"),
    ("dota", r"dota"), ("valorant", r"valorant"), ("esport", r"\(bo\d\)|map \d|game \d winner"),
    ("tennis", r"\bopen\b|atp|wta|challenger|wimbledon|roland|masters 1000|qualification:"),
    ("nfl", r"\bnfl\b|chiefs|eagles|cowboys|patriots|packers|49ers|steelers|ravens|bills|jets|giants|"
            r"commanders|dolphins|broncos|raiders|chargers|bengals|browns|texans|colts|titans|jaguars|"
            r"vikings|bears|lions|saints|falcons|panthers|buccaneers|cardinals|rams|seahawks"),
    ("mlb", r"\bmlb\b|yankees|dodgers|mets|red sox|cubs|astros|braves|phillies|padres|mariners|blue jays|"
            r"orioles|guardians|rays|brewers|twins|tigers|royals|white sox|athletics|angels|rangers|"
            r"pirates|reds|marlins|nationals|rockies|diamondbacks|giants"),
    ("nba", r"\bnba\b|lakers|celtics|warriors|knicks|bucks|nuggets|heat|suns|76ers|mavericks|clippers"),
    ("nhl", r"\bnhl\b|maple leafs|canadiens|bruins|oilers|flames|canucks|penguins|blackhawks|avalanche|"
            r"lightning|capitals|islanders|predators|kraken|senators|sabres|hurricanes|stars|wild"),
    ("football", r" fc\b|\bfc |\bac\b|\bafc\b|united|city|real madrid|barcelona|inter |juventus|bayern|"
                 r"psg|win on 20\d\d|end in a draw|ligue|premier league|serie a|bundesliga|la liga|uefa"),
    ("ufc", r"\bufc\b|fight night"), ("golf", r"\bpga\b|golf|masters"), ("f1", r"grand prix|\bf1\b"),
)
_BET_TYPES = (("handicap", r"spread|handicap|\(-\d|\(\+\d"), ("total", r"o/u|over/under|total"),
              ("score_exact", r"exact score"), ("partie", r"map \d|game \d|set \d|1h|2h|half|quarter|inning"),
              ("nul", r"draw"))


_BY_SOURCE = {"atptour.com": "tennis", "wtatennis.com": "tennis", "itftennis.com": "tennis",
              "hltv.org": "counter-strike", "vlr.gg": "valorant", "lolesports.com": "lol",
              "liquipedia.net": "esport", "mlb.com": "mlb", "nhl.com": "nhl", "nfl.com": "nfl", "nba.com": "nba",
              "ufc.com": "ufc", "pgatour.com": "golf", "formula1.com": "f1"}


def discipline(question: str, source: str = "") -> str:
    """Discipline d'un marché : d'abord sa source de résolution (atptour.com → tennis…), sinon
    le libellé (la moitié des matchs de tennis n'ont que les noms des joueurs)."""
    from polymarket_agent.resolution_sources import domain_of
    domain = domain_of(source) if source else ""
    for known, name in _BY_SOURCE.items():
        if domain == known or domain.endswith("." + known):
            return name
    q = (question or "").lower()
    for name, pattern in _DISCIPLINES:
        if re.search(pattern, q):
            return name
    return "autre"


def bet_type(question: str, sports_market_type: str | None = None) -> str:
    """vainqueur, handicap, total, score_exact, partie (manche, carte…), nul, autre."""
    if sports_market_type:
        return {"moneyline": "vainqueur", "spreads": "handicap", "totals": "total",
                "child_moneyline": "partie"}.get(sports_market_type, sports_market_type)
    q = (question or "").lower()
    for name, pattern in _BET_TYPES:
        if re.search(pattern, q):
            return name
    return "vainqueur" if re.search(r" vs\.? | v ", q) or re.search(r"will .+ win", q) else "autre"


# ------------------------------------------------------------------ opérations et tranches
PRICE_BANDS = ((0.0, 0.80), (0.80, 0.85), (0.85, 0.875), (0.875, 0.90), (0.90, 0.925), (0.925, 0.95), (0.95, 1.0))
HOUR_BANDS = ((0, 3), (3, 6), (6, 12), (12, 24), (24, 72), (72, 168), (168, 1e6))
UTC_BANDS = ((0, 6), (6, 12), (12, 18), (18, 24))
FEATURES = ("prix", "delai", "issue", "heure_utc", "discipline", "type_pari", "mode", "source")
FILTERABLE = {"prix", "delai", "issue", "heure_utc", "discipline", "type_pari"}
NAMES = {"prix": "prix payé", "delai": "délai jusqu'à la fin", "issue": "issue", "heure_utc": "heure d'achat",
         "discipline": "discipline", "type_pari": "type de pari", "mode": "mode d'achat",
         "source": "source de résolution"}


def _band(value: float | None, bands) -> tuple | None:
    if value is None:
        return None
    return next(((lo, hi) for lo, hi in bands if lo <= value < hi), None)


@dataclass
class Bet:
    token_id: str
    pnl: float
    ret: float
    price: float | None
    won: bool | None  # None : revendu avant la fin
    traits: dict = field(default_factory=dict)


def bets_of(entries: list[dict], markets: dict[str, dict] | None = None) -> list[Bet]:
    """Opérations clôturées d'un journal, avec leurs caractéristiques. `markets` :
    {market_id: {"question", "domain", "sports_market_type"}} (base : table market_rules)."""
    markets = markets or {}
    first_buy: dict[str, dict] = {}
    for e in entries:
        if e.get("type") == "BUY":
            first_buy.setdefault(e["data"]["token_id"], e)
    out = []
    for t in closed_trades(entries):
        cost = float(t["cost"])
        if cost <= 0:
            continue
        buy = first_buy.get(t["token_id"])
        extra = (buy or {}).get("data", {}).get("extra") or {}
        shares = float(t["shares_bought"] or 0)
        price = (cost - float(t["fees"])) / shares if shares > 0 else None
        info = markets.get(t["market_id"]) or {}
        question = info.get("question") or ""
        outcome = (t.get("outcome") or "").lower()
        try:
            hours = float(extra.get("horizon_hours"))
        except (TypeError, ValueError):
            hours = None
        hour = datetime.fromisoformat(buy["ts"]).hour if buy else None
        traits = {
            "prix": _band(price, PRICE_BANDS), "delai": _band(hours, HOUR_BANDS),
            "issue": "oui" if outcome == "yes" else "non" if outcome == "no" else "autre",
            "heure_utc": _band(hour, UTC_BANDS),
            "discipline": discipline(question, info.get("domain") or "") if question or info.get("domain") else None,
            "type_pari": bet_type(question, info.get("sports_market_type")) if question else None,
            "mode": "ordre posé" if extra.get("resting_order") or extra.get("order_type") else "immédiat",
            "source": info.get("domain") or None,
        }
        won = None if t.get("payout") is None else float(t["payout"]) > 0.5
        out.append(Bet(t["token_id"], float(t["pnl"]), float(t["pnl"]) / cost, price, won, traits))
    return out


def _stats(bets: list[Bet]) -> dict:
    settled = [b for b in bets if b.won is not None and b.price is not None]
    wins, expected = sum(b.won for b in settled), sum(b.price for b in settled)
    var = sum(b.price * (1 - b.price) for b in settled)
    rets = [b.ret for b in bets]
    return {"n": len(bets), "pnl": round(sum(b.pnl for b in bets), 2),
            "rendement": round(sum(rets) / len(rets), 4) if rets else 0.0, "confiance": t_stat(rets),
            "gagnes": wins, "attendus": round(expected, 1),
            "z": round((wins - expected) / math.sqrt(var), 2) if var > 0 else 0.0}


def label(feature: str, value) -> str:
    if value is None:
        return "inconnu"
    if feature == "prix":
        return f"{value[0]:.3f}-{value[1]:.3f}".replace(".", ",")
    if feature == "delai":
        return f"{value[0]:g}-{value[1]:g} h" if value[1] < 1e5 else f"{value[0]:g} h et plus"
    if feature == "heure_utc":
        return f"{value[0]}-{value[1]} h UTC"
    return str(value)


def dissect(bets: list[Bet], core_share: float = 0.8) -> dict:
    """{caractéristique: {"morceaux": [...], "coeur": {...}}}. Le cœur : les morceaux les plus
    gagnants qui, ensemble, font au moins `core_share` des gains des morceaux gagnants (même si la
    stratégie perd au total : on voit où se trouvent ses gains)."""
    out = {}
    for feature in FEATURES:
        groups: dict = {}
        for b in bets:
            groups.setdefault(b.traits.get(feature), []).append(b)
        slices = sorted(({"valeur": v, "libelle": label(feature, v), **_stats(g)} for v, g in groups.items()),
                        key=lambda s: -s["pnl"])
        total = sum(s["pnl"] for s in slices if s["pnl"] > 0)
        core, acc, n_core = [], 0.0, 0
        for s in slices:
            if total <= 0 or acc >= core_share * total or s["pnl"] <= 0:
                break
            core.append(s["libelle"])
            acc += s["pnl"]
            n_core += s["n"]
        out[feature] = {"morceaux": slices, "coeur": {
            "morceaux": core, "part_des_gains": round(acc / total, 3) if total > 0 else 0.0,
            "part_des_paris": round(n_core / len(bets), 3) if bets else 0.0}}
    return out


def to_filter(feature: str, value) -> dict | None:
    """Filtre de fille (`strategy_engine.Filtered`) qui isole ce morceau, ou None."""
    if value is None or feature not in FILTERABLE or (feature in ("discipline", "type_pari") and value == "autre"):
        return None  # « autre » n'isole rien (ex. toute la crypto pour crypto_threshold)
    if feature == "prix":
        return {"prix_min": value[0], "prix_max": value[1]}
    if feature == "delai":  # délai jusqu'à l'ÉCHÉANCE du marché (comme horizon_hours à l'achat)
        return {"echeance_min": value[0]} if value[1] >= 1e5 else {"echeance_min": value[0], "echeance_max": value[1]}
    if feature == "heure_utc":
        return {"heure_utc": [value[0], value[1]]}
    if feature == "issue":
        return {"issue": [value]}
    if feature == "discipline":
        return {"disciplines": [value]}
    return {"types_pari": [value]}


def proposals(name: str, bets: list[Bet], dissection: dict, min_n: int = 8) -> list[dict]:
    """Filles proposées : un morceau filtrable d'au moins `min_n` opérations, gagnant, dont le
    rendement par mise bat celui de la stratégie entière et qui gagne au moins autant que ses
    prix l'annoncent (z ≥ 0). Classées par résultat ; plus la meilleure paire de morceaux."""
    whole = _stats(bets)
    found = []
    for feature, d in dissection.items():
        for s in d["morceaux"]:
            filt = to_filter(feature, s["valeur"])
            if (filt and s["n"] >= min_n and s["pnl"] > 0 and s["rendement"] > whole["rendement"]
                    and s["z"] >= 0 and s["n"] < whole["n"]):
                found.append({"strategie": name, "morceau": f"{NAMES[feature]} {s['libelle']}", "filtres": filt,
                              "caracteristiques": [(feature, s["valeur"])], **{k: s[k] for k in (
                                  "n", "pnl", "rendement", "confiance", "gagnes", "attendus", "z")}})
    found.sort(key=lambda p: -p["pnl"])
    if len(found) >= 2:  # le meilleur croisement de deux morceaux de caractéristiques différentes
        for a in found:
            for b in found:
                fa, fb = a["caracteristiques"][0], b["caracteristiques"][0]
                if fa[0] >= fb[0]:
                    continue
                both = [x for x in bets if x.traits.get(fa[0]) == fa[1] and x.traits.get(fb[0]) == fb[1]]
                st = _stats(both)
                if st["n"] >= min_n and st["pnl"] > 0 and st["rendement"] > max(a["rendement"], b["rendement"]):
                    found.append({"strategie": name, "morceau": f"{a['morceau']} + {b['morceau']}",
                                  "filtres": {**a["filtres"], **b["filtres"]}, "caracteristiques": [fa, fb],
                                  **{k: st[k] for k in ("n", "pnl", "rendement", "confiance", "gagnes", "attendus", "z")}})
                    return found
    return found


def render(reports: list[dict]) -> str:
    """Rapport lisible (reports/pareto.md)."""
    lines = ["# Entonnoir 80/20 : le petit morceau qui fait les gains", "",
             "Pour chaque stratégie qui grandit vite (ou plus vite que sa mère) : par caractéristique, le",
             "« cœur » = les morceaux qui font 80 % des gains (des morceaux gagnants), et la part des paris",
             "qu'ils représentent.",
             "Peu de paris = des pistes, pas des preuves : l'arène tranche avec les filles proposées.", ""]
    for r in reports:
        w = r["ensemble"]
        lines += [f"## {r['strategie']} — croissance {r['croissance']:+.1%}"
                  + (f" (mère {r['mere']} : {r['croissance_mere']:+.1%})" if r.get("mere") else ""), "",
                  f"{w['n']} opérations, résultat {w['pnl']:+.2f}, rendement moyen {w['rendement']:+.2%} par mise, "
                  f"confiance {w['confiance']:+.2f}, gagnés {w['gagnes']} pour {w['attendus']} attendus (z {w['z']:+.2f}).", "",
                  "| caractéristique | cœur (80 % des gains) | part des paris | morceaux (n, résultat, rendement, z) |",
                  "|---|---|---|---|"]
        for feature, d in r["dissection"].items():
            c = d["coeur"]
            detail = " ; ".join(f"{s['libelle']} ({s['n']}, {s['pnl']:+.0f}, {s['rendement']:+.1%}, {s['z']:+.1f})"
                                for s in d["morceaux"][:6])
            lines.append(f"| {feature} | {', '.join(c['morceaux']) or '—'} | {c['part_des_paris']:.0%} | {detail} |")
        if r["filles"]:
            lines += ["", "**Filles proposées** (morceau qui bat la stratégie entière) :", ""]
            for p in r["filles"]:
                lines.append(f"- {p['morceau']} : {p['n']} opérations, {p['pnl']:+.2f}, {p['rendement']:+.1%} par mise, "
                             f"gagnés {p['gagnes']}/{p['attendus']} → `filtres: {p['filtres']}`"
                             + (" (déjà dans l'arène)" if p.get("existe") else ""))
        lines.append("")
    return "\n".join(lines) + "\n"


def market_labels(db) -> dict[str, dict]:
    """{market_id: {question, domain}} depuis la table market_rules (vide si elle n'existe pas)."""
    try:
        return {r["market_id"]: {"question": r["question"], "domain": r["domain"]}
                for r in db.conn.execute("SELECT market_id, question, domain FROM market_rules")}
    except Exception:  # noqa: BLE001 - base neuve : pas encore de libellés
        return {}


def summary(reports: list[dict], limit: int = 4) -> list[dict]:
    """Pour le tableau de bord : par stratégie, la caractéristique la plus concentrée (le moins de
    paris pour 80 % des gains) et les filles proposées."""
    out = []
    for r in reports[:limit]:
        cores = [(f, d["coeur"]) for f, d in r["dissection"].items()  # un vrai « petit morceau » seulement
                 if d["coeur"]["morceaux"] and d["coeur"]["part_des_gains"] >= 0.8 and d["coeur"]["part_des_paris"] <= 0.7]
        # Le cœur le plus simple d'abord (le moins de morceaux), puis le moins de paris.
        best = min(cores, key=lambda fc: (len(fc[1]["morceaux"]), fc[1]["part_des_paris"]), default=None)
        out.append({"strategie": r["strategie"], "croissance": round(r["croissance"], 4),
                    "mere": r.get("mere"), "croissance_mere": r.get("croissance_mere"),
                    "operations": r["ensemble"]["n"],
                    "coeur": {"caracteristique": best[0], **best[1]} if best else None,
                    "filles": [{k: p[k] for k in ("morceau", "n", "pnl", "rendement", "existe")} for p in r["filles"][:3]]})
    return out


def analyse(entries: dict[str, list[dict]], growth: dict[str, float], mothers: dict[str, str],
            markets: dict[str, dict], configs: dict[str, dict], min_closed: int = 15,
            min_growth: float = 0.05, min_n: int = 8) -> list[dict]:
    """Entonnoir 80/20 de toutes les stratégies qui grandissent : croissance ≥ `min_growth` sur au
    moins `min_closed` opérations, ou croissance supérieure à celle de leur mère (le marqueur
    d'Etienne). `entries` / `growth` : par nom d'arène (« nf_sport_v1.0.0 ») ; `mothers` :
    {stratégie: mère} ; `configs` : config/strategies.yaml (pour repérer les filles déjà créées)."""
    out = []
    for name, rows in entries.items():
        base = name.rsplit("_v", 1)[0]
        bets = bets_of(rows, markets)
        g = growth.get(name)
        if g is None or len(bets) < min(min_closed, 10):
            continue
        mother = mothers.get(base)
        mother_growth = next((v for n, v in growth.items() if n.rsplit("_v", 1)[0] == mother), None) if mother else None
        beats_mother = mother_growth is not None and g > mother_growth
        if not ((g >= min_growth and len(bets) >= min_closed) or beats_mother):
            continue
        d = dissect(bets)
        found = proposals(base, bets, d, min_n)
        mine = (configs.get(base) or {}).get("filtres") or {}
        for p in found:
            wanted = {**mine, **p["filtres"]}
            p["filtres"] = wanted
            p["existe"] = any((c or {}).get("mere") in (base, mother) and (c or {}).get("filtres") == wanted
                              for c in configs.values() if isinstance(c, dict))
        out.append({"strategie": name, "croissance": g, "mere": mother, "croissance_mere": mother_growth,
                    "ensemble": _stats(bets), "dissection": d, "filles": found})
    out.sort(key=lambda r: -r["croissance"])
    return out


def obligations(reports: list[dict], limit: int = 3, full: dict[str, int] | None = None,
                cap: int | None = None) -> list[str]:
    """Pour la feuille de mission : les filles proposées pas encore dans l'arène. `full` : {mère:
    filles vivantes} des mères qui en ont déjà `cap` ou plus (21/10/2026, promotion.yaml → filles) :
    pas de nouvelle fille pour elles, une seule ligne le dit."""
    full = full or {}
    todo = [p for r in reports for p in r["filles"] if not p.get("existe")]
    todo.sort(key=lambda p: -p["pnl"])
    blocked = sorted({p["strategie"] for p in todo if p["strategie"] in full})
    out = [f"Entonnoir 80/20 (reports/pareto.md) : créer la fille de {p['strategie']} « {p['morceau']} » "
           f"({p['n']} opérations, {p['pnl']:+.0f}, {p['rendement']:+.1%} par mise contre la stratégie entière) "
           f"avec `mere: {p['strategie']}` et `filtres: {p['filtres']}`."
           for p in [p for p in todo if p["strategie"] not in full][:limit]]
    if blocked:
        out.append("Entonnoir 80/20 : pas de nouvelle fille pour " + ", ".join(
            f"{m} ({full[m]} filles vivantes)" for m in blocked) + f" : au plus {cap} par mère "
            "(config/promotion.yaml → filles) ; l'arène retire d'elle-même les plus faibles, les muettes et "
            "les doublons. Si un morceau vaut vraiment mieux, retirer d'abord la fille la plus faible.")
    return out
