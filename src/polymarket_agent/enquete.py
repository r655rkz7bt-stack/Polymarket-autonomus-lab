"""Enquête automatique : chercher dans les journaux les défauts qui faussent les résultats.

Demande d'Etienne (20/10/2026) : que le chercheur cherche « les problèmes comme celui qu'on a vu
ensemble du principal qui augmentait les mises ». Chaque contrôle vient d'un vrai défaut trouvé à
la main ; il le retrouve automatiquement s'il revient, ou trouve ses cousins :
  - copie_fidele : le principal ne refaisait pas les paris de la stratégie copiée (18/10, PR #76 :
    Bitcoin misé 3 fois trop gros, anciens paris rattrapés) ;
  - mises : un pari énorme par rapport au capital (Kelly complet allait jusqu'à 40 %) ;
  - estimation_perimee : estimation calculée sur le carnet du début de cycle, achat après une
    chute (20/10 : Moyuka Uchijima estimé 0,98, payé 0,817, 23 % du fantôme) ;
  - chance : gain en euros mais rendement par mise négatif, ou gain venu de 3 paris / d'un seul
    jour (18/10, PR #77 : la confiance calculée en euros récompensait les grosses mises) ;
  - champion_sans_avantage : la championne gagne-t-elle encore plus souvent que ses prix ?
  - filles_periode : une fille est jugée sur une autre période que sa mère (20/10) ;
  - filtre_prix : achats hors de la plage de prix d'une stratégie (20/10 : « prix haut »
    0,875-0,95 achetée à 0,79 par un ordre posé dans un carnet très écarté) ;
  - filtre_delai : achats au comptant hors des fenêtres `echeance_*`, `heures_*`, `heure_utc` d'une fille ;
  - meme_pari_prix_differents : deux stratégies, même pari, prix d'entrée très différents ;
  - selection_multiple : la championne est la meilleure de ~35 stratégies ; son avance sur les prix
    dépasse-t-elle ce que le seul hasard donne au meilleur de 35 ? (20/10 : non, z = 1,86) ;
  - deux_camps : une stratégie achète les deux camps d'un même match (20/10 : 2 matchs, −275 €) ;
  - achats_en_jeu : part des achats faits après le coup d'envoi (20/10 : 84 % pour la championne,
    alors que son « horizon » affiché est de 165 h : c'est la date de fin placeholder de Gamma) ;
  - muettes, positions_oubliees, cycle_arrete : ce qui ne tourne plus.
Les journaux sont lus tels que publiés (données vérifiées par le cycle) ; rien n'est modifié.
Résultat : `reports/enquete.md` ; chaque constat « grave » devient une obligation de la feuille de
mission (enquêter, corriger ou proposer, test de non-régression, compte rendu dans
`experiments/enquetes/`).
"""

from __future__ import annotations

import math
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal

from polymarket_agent.reporting import closed_trades

GRAVE, A_REGARDER = "grave", "à regarder"
# Copie fidèle en service depuis la promotion du 18/10/2026 à 21 h 38 (PR #76) : avant, le
# principal rejouait lui-même les stratégies (aucun jumeau attendu).
COPIE_FIDELE_DEPUIS = datetime.fromisoformat("2026-10-18T21:30:00+00:00")


def _ts(entry: dict) -> datetime:
    return datetime.fromisoformat(entry["ts"])


def _finding(controle: str, gravite: str, titre: str, detail: str, exemples=()) -> dict:
    return {"controle": controle, "gravite": gravite, "titre": titre, "detail": detail, "exemples": list(exemples)[:8]}


def _posted(extra: dict) -> bool:
    return bool(extra.get("resting_order") or extra.get("order_type"))


def _buys(entries: list[dict], since: datetime | None = None) -> list[dict]:
    return [e for e in entries if e["type"] == "BUY" and (since is None or _ts(e) >= since)]


def _cost(data: dict) -> float:
    return float(Decimal(data["shares"]) * Decimal(data["price"]) + Decimal(data["fee"]))


def _returns(trades: list[dict]) -> list[float]:
    return [float(t["pnl"]) / float(t["cost"]) for t in trades if float(t["cost"]) > 0]


def _t(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    sd = statistics.stdev(values)
    return statistics.mean(values) / sd * math.sqrt(len(values)) if sd > 0 else 0.0


def _won_vs_expected(trades: list[dict]) -> tuple[int, float]:
    won = sum(1 for t in trades if float(t["pnl"]) > 0)
    expected = sum(float(t["cost"]) / float(t["shares_bought"]) for t in trades if float(t["shares_bought"]) > 0)
    return won, expected


# ------------------------------------------------------------------ contrôles


def copie_fidele(entries: dict[str, list[dict]], since: datetime | None = None) -> list[dict]:
    """Chaque achat du principal doit avoir son jumeau dans le fantôme copié (même stratégie, même
    jeton, même cycle), au même prix à 2 centimes près."""
    principal = entries.get("principal") or []
    twins: dict[tuple, dict] = {}
    for name, rows in entries.items():
        if name == "principal":
            continue
        for e in _buys(rows):
            twins.setdefault((name, e["data"]["token_id"], (e["data"].get("extra") or {}).get("cycle_id")), e)
    orphans, prices, full = [], [], []
    since = max(since or COPIE_FIDELE_DEPUIS, COPIE_FIDELE_DEPUIS)
    for e in _buys(principal, since):
        d, x = e["data"], e["data"].get("extra") or {}
        ghost = f"{d['strategy_id']}_v{d['strategy_version']}"
        if ghost not in entries:
            continue  # stratégie disparue de l'arène : rien à comparer
        twin = twins.get((ghost, d["token_id"], x.get("cycle_id")))
        label = f"{e['ts'][:16]} {d['strategy_id']} « {d['outcome']} » {d['shares']} parts à {float(d['price']):.3f}"
        if twin is None:
            orphans.append(label)
            continue
        g = twin["data"]
        if abs(float(d["price"]) - float(g["price"])) > 0.02:
            prices.append(f"{label} ; fantôme à {float(g['price']):.3f}")
        if (g.get("extra") or {}).get("fill_status") == "PARTIAL" and float(d["shares"]) >= 0.95 * float(g["shares"]):
            full.append(f"{label} ; fantôme {g['shares']} parts (exécution partielle)")
    out = []
    if orphans:
        out.append(_finding("copie_fidele", GRAVE, f"{len(orphans)} achat(s) du principal sans jumeau dans le fantôme copié",
                            "Le principal doit refaire les paris du fantôme (copie fidèle) : un achat sans jumeau "
                            "veut dire qu'il joue une autre stratégie que celle que l'arène note.", orphans))
    if prices:
        out.append(_finding("copie_fidele", A_REGARDER, f"{len(prices)} achat(s) copiés à un autre prix (> 2 centimes)",
                            "Même pari, prix différent : vérifier l'ordre d'exécution et la liquidité partagée.", prices))
    if full:
        out.append(_finding("copie_fidele", A_REGARDER, f"{len(full)} copie(s) à 100 % sur une exécution partielle",
                            "Le fantôme n'a obtenu qu'une partie de sa mise ; le principal, qui ne devait en copier "
                            "qu'une part, a obtenu autant que lui : sur les marchés peu liquides la copie n'est plus "
                            "proportionnelle (le principal pèse plus lourd que prévu sur ces paris).", full))
    return out


def mises(entries: dict[str, list[dict]], max_principal: float = 0.10, max_ghost: float = 0.25,
          since: datetime | None = None) -> list[dict]:
    """Mises rapportées au capital estimé (dernier battement avant l'achat). Principal : au-delà de son
    plafond `principal.max_mise` (grave). Fantômes : au-delà de `max_ghost`, regroupées."""
    big_main, big_ghosts = [], []
    for name, rows in entries.items():
        limit = max_principal * 1.05 if name == "principal" else max_ghost
        capital = 1000.0
        for e in rows:
            if e["type"] in ("GENESIS", "RESET"):
                capital = float(e["data"].get("initial_capital") or capital)
            elif e["type"] == "HEARTBEAT" and e["data"].get("total_estimated"):
                capital = float(e["data"]["total_estimated"])
            elif e["type"] == "BUY" and (since is None or _ts(e) >= since) and capital > 0:
                share = _cost(e["data"]) / capital
                if share > limit:
                    label = (f"{e['ts'][:16]} {name if name != 'principal' else e['data']['strategy_id']} "
                             f"« {e['data']['outcome']} » {_cost(e['data']):.0f} € = {share:.0%} du capital")
                    (big_main if name == "principal" else big_ghosts).append((share, label))
    out = []
    if big_main:
        out.append(_finding("mises", GRAVE, f"principal : {len(big_main)} mise(s) au-dessus de son plafond de {max_principal:.0%}",
                            "Le plafond `principal.max_mise` devait l'empêcher : chercher par où la mise est passée "
                            "(copie, ordre posé, rachat du même marché).", [b[1] for b in sorted(big_main, reverse=True)]))
    if big_ghosts:
        out.append(_finding("mises", A_REGARDER, f"{len(big_ghosts)} mise(s) de fantôme au-dessus de {max_ghost:.0%} de leur capital",
                            "Kelly complet sur une estimation trop optimiste : une seule mise fait le résultat (chance, "
                            "pas avantage). Regarder l'estimation de ces paris.", [b[1] for b in sorted(big_ghosts, reverse=True)]))
    return out


def estimation_perimee(entries: dict[str, list[dict]], since: datetime | None = None, extra_gap: float = 0.08) -> list[dict]:
    """Achats immédiats dont l'écart estimation − prix payé dépasse de `extra_gap` l'écart habituel
    de la stratégie (médiane de ses achats immédiats) : estimation calculée sur un autre carnet."""
    out = []
    for name, rows in entries.items():
        gaps = []
        for e in _buys(rows):
            x = e["data"].get("extra") or {}
            if x.get("est_probability") and not _posted(x):
                gaps.append((float(x["est_probability"]) - float(e["data"]["price"]), e))
        if len(gaps) < 5:
            continue
        usual = statistics.median(g for g, _ in gaps)
        odd = [(g, e) for g, e in gaps if g > usual + extra_gap and (since is None or _ts(e) >= since)]
        if odd:
            odd.sort(key=lambda r: -r[0])
            out.append(_finding("estimation_perimee", A_REGARDER,
                                f"{name} : {len(odd)} achat(s) estimés {extra_gap:.0%} au-dessus de l'écart habituel ({usual:+.3f})",
                                "L'estimation ne correspond pas au prix payé : carnet périmé (le prix a bougé pendant "
                                "le cycle), mauvais marché rattaché, ou modèle qui s'emballe. La mise, calculée sur "
                                "cette estimation, est trop grosse.",
                                [f"{e['ts'][:16]} « {e['data']['outcome']} » estimé {float(e['data']['extra']['est_probability']):.3f}, "
                                 f"payé {float(e['data']['price']):.3f}, mise {_cost(e['data']):.0f} €" for _, e in odd]))
    return out


def copied_by_principal(entries: dict[str, list[dict]], now: datetime, hours: float = 24) -> set[str]:
    """Fantômes que le principal copie : dernier champion promu + stratégies de ses achats récents."""
    principal = entries.get("principal") or []
    recent = {f"{e['data']['strategy_id']}_v{e['data']['strategy_version']}"
              for e in _buys(principal, now - timedelta(hours=hours))}
    champions = [e["data"].get("champion") for e in principal if e["type"] == "PROMOTION"]
    return {c for c in champions[-1:] if c and c in entries} | {n for n in recent if n in entries}


def chance(entries: dict[str, list[dict]], min_trades: int = 15, min_pnl: float = 30,
           copied: set[str] | None = None) -> list[dict]:
    """Gain en euros sans avantage par mise, ou gain concentré (3 paris, un seul jour). Grave pour
    une stratégie que le principal copie : c'est son argent qui suit ce gain fragile."""
    out = []
    for name, rows in entries.items():
        if name == "principal":
            continue
        trades = closed_trades(rows)
        if len(trades) < min_trades:
            continue
        pnl = sum(float(t["pnl"]) for t in trades)
        r = _returns(trades)
        if pnl < min_pnl:
            continue
        level = GRAVE if name in (copied or set()) else A_REGARDER
        won, expected = _won_vs_expected(trades)
        if statistics.mean(r) < 0:
            out.append(_finding("chance", level, f"{name} : +{pnl:.0f} € mais rendement par mise {statistics.mean(r):+.1%}",
                                f"Le gain vient de la taille des mises, pas d'un avantage ({won} gagnés pour {expected:.1f} "
                                "attendus par les prix).", []))
        top = sorted(trades, key=lambda t: -float(t["pnl"]))[:3]
        top_pnl = sum(float(t["pnl"]) for t in top)
        by_day: dict[str, float] = defaultdict(float)
        for t in trades:
            by_day[t["opened_at"][:10]] += float(t["pnl"])
        best_day, best = max(by_day.items(), key=lambda kv: kv[1])
        if top_pnl > 0.8 * pnl and len(trades) >= 20:
            out.append(_finding("chance", level, f"{name} : 3 paris font {top_pnl / pnl:.0%} du gain (+{pnl:.0f} €)",
                                "Résultat fragile : retirer ces 3 paris et regarder ce qui reste.",
                                [f"{t['opened_at'][:16]} « {t['outcome']} » {float(t['pnl']):+.0f} €" for t in top]))
        if len(by_day) >= 3 and best > 0.8 * pnl:
            out.append(_finding("chance", level, f"{name} : le {best_day} fait {best / pnl:.0%} du gain (+{pnl:.0f} €)",
                                "Avantage concentré sur une journée : vérifier qu'il existe encore les autres jours.",
                                [f"{d} : {v:+.0f} €" for d, v in sorted(by_day.items())]))
    return out


def champion_sans_avantage(entries: dict[str, list[dict]], now: datetime, last: int = 30,
                           hours: float = 24) -> list[dict]:
    """La (les) stratégie(s) copiée(s) par le principal ces `hours` dernières heures gagnent-elles
    encore plus souvent que leurs prix sur leurs `last` dernières opérations ?"""
    out = []
    for name in sorted(copied_by_principal(entries, now, hours)):
        trades = closed_trades(entries.get(name) or [])[-last:]
        if len(trades) < 15:
            continue
        won, expected = _won_vs_expected(trades)
        r = _returns(trades)
        if won <= expected or statistics.mean(r) <= 0:
            out.append(_finding("champion_sans_avantage", GRAVE,
                                f"{name} (copiée par le principal) : {won} gagnés pour {expected:.1f} attendus sur ses "
                                f"{len(trades)} dernières opérations, rendement {statistics.mean(r):+.1%}",
                                "Plus d'avantage mesurable récemment : chercher d'où venait le gain (jour, sport, prix, "
                                "mode d'achat) et si ses règles d'entrée au capital doivent changer.", []))
    return out


def filles_periode(entries: dict[str, list[dict]], configs: dict, min_trades: int = 8) -> list[dict]:
    """Une fille comparée à sa mère sur la MÊME période (opérations ouvertes après la naissance de la fille)."""
    rows = []
    for key, cfg in configs.items():
        if not isinstance(cfg, dict) or not cfg.get("mere"):
            continue
        name, mother = f"{key}_v{cfg.get('version', '1.0.0')}", configs.get(str(cfg["mere"]))
        if name not in entries or not isinstance(mother, dict):
            continue
        mother_name = f"{cfg['mere']}_v{mother.get('version', '1.0.0')}"
        if mother_name not in entries or not entries[name]:
            continue
        born = entries[name][0]["ts"]
        child = closed_trades(entries[name])
        same = [t for t in closed_trades(entries[mother_name]) if t["opened_at"] >= born]
        if len(child) < min_trades or len(same) < min_trades:
            continue
        rc, rm = statistics.mean(_returns(child)), statistics.mean(_returns(same))
        rows.append((rc - rm, f"{key} {rc:+.1%} contre sa mère {cfg['mere']} {rm:+.1%} depuis le {born[:10]} "
                              f"({len(child)} et {len(same)} opérations)"))
    if not rows:
        return []
    rows.sort(reverse=True)
    return [_finding("filles_periode", A_REGARDER, f"{len(rows)} fille(s) comparée(s) à leur mère sur la même période",
                     "Juger une fille contre sa mère ENTIÈRE mélange deux périodes : une fille née un mauvais jour "
                     "paraît mauvaise même si elle fait mieux que sa mère ce jour-là. Comparer ces chiffres-ci.",
                     [r[1] for r in rows])]


def _price_range(cfg: dict) -> tuple[float, float] | None:
    """Plage de prix d'une stratégie : `min_ask`/`max_ask` de ses paramètres, resserrée par les
    `prix_min`/`prix_max` de ses `filtres` (21/10 : les filles n'étaient jamais contrôlées)."""
    params = cfg.get("params") or {}
    lo, hi = (params.get(k, {}).get("value") if isinstance(params.get(k), dict) else None for k in ("min_ask", "max_ask"))
    filters = cfg.get("filtres") or {}
    if lo is None and hi is None and "prix_min" not in filters and "prix_max" not in filters:
        return None
    lows = [float(v) for v in (lo, filters.get("prix_min")) if v is not None]
    highs = [float(v) for v in (hi, filters.get("prix_max")) if v is not None]
    return (max(lows) if lows else 0.0), (min(highs) if highs else 1.0)


def filtre_prix(entries: dict[str, list[dict]], configs: dict, since: datetime | None = None) -> list[dict]:
    """Achats hors de la plage de prix de la stratégie (3 centimes de tolérance)."""
    out = []
    for key, cfg in configs.items():
        if not isinstance(cfg, dict):
            continue
        rng = _price_range(cfg)
        name = f"{key}_v{cfg.get('version', '1.0.0')}"
        if rng is None or name not in entries:
            continue
        lo, hi = rng
        odd = [e for e in _buys(entries[name], since)
               if not lo - 0.03 <= float(e["data"]["price"]) <= hi + 0.03]
        if odd:
            out.append(_finding("filtre_prix", A_REGARDER, f"{key} : {len(odd)} achat(s) hors de sa plage {lo:g}–{hi:g}",
                                "Le morceau testé n'est pas celui qu'on croit : souvent un ordre posé au meilleur "
                                "acheteur dans un carnet très écarté (la plage est vérifiée sur le prix de vente).",
                                [f"{e['ts'][:16]} « {e['data']['outcome']} » à {float(e['data']['price']):.3f}"
                                 f"{' (ordre posé)' if _posted(e['data'].get('extra') or {}) else ''}" for e in odd]))
    return out


def filtre_delai(entries: dict[str, list[dict]], configs: dict, since: datetime | None = None, tol: float = 0.5) -> list[dict]:
    """Achats au comptant hors des fenêtres de temps des `filtres` d'une fille : `echeance_min/max`
    (heures jusqu'à l'échéance notées à l'achat, `horizon_hours`), `heures_min/max` (heures jusqu'au
    coup d'envoi, champ `depuis_coup_d_envoi_h` de signe opposé) et `heure_utc`. Les ordres posés sont
    ignorés : ils sont servis plus tard que la décision."""
    out = []
    for key, cfg in configs.items():
        f = cfg.get("filtres") if isinstance(cfg, dict) else None
        name = f"{key}_v{cfg.get('version', '1.0.0')}" if f else None
        if not f or name not in entries:
            continue
        odd = []
        for e in _buys(entries[name], since):
            x = e["data"].get("extra") or {}
            if _posted(x):
                continue
            why = None
            h = x.get("horizon_hours")
            if h not in (None, "") and ("echeance_min" in f or "echeance_max" in f):
                if not float(f.get("echeance_min", -1e9)) - tol <= float(h) <= float(f.get("echeance_max", 1e9)) + tol:
                    why = f"échéance dans {float(h):.1f} h"
            g = x.get("depuis_coup_d_envoi_h")
            if why is None and g not in (None, "") and ("heures_min" in f or "heures_max" in f):
                if not float(f.get("heures_min", -1e9)) - tol <= -float(g) <= float(f.get("heures_max", 1e9)) + tol:
                    why = f"coup d'envoi dans {-float(g):.1f} h"
            if why is None and "heure_utc" in f:
                a, b = (int(v) for v in f["heure_utc"])
                hour = _ts(e).hour
                if not (a <= hour < b if a <= b else hour >= a or hour < b):
                    why = f"acheté à {hour} h UTC"
            if why:
                odd.append(f"{e['ts'][:16]} « {e['data']['outcome']} » {why}")
        if odd:
            out.append(_finding("filtre_delai", A_REGARDER, f"{key} : {len(odd)} achat(s) hors de sa fenêtre de temps",
                                "Le filtre de délai ou d'heure ne coupe pas ce qu'il annonce : la fille ne teste pas le morceau "
                                "qu'on croit (mauvaise date lue, ou heure de décision différente de l'heure du journal).", odd))
    return out


def meme_pari_prix_differents(entries: dict[str, list[dict]], min_common: int = 8, gap: float = 0.04) -> list[dict]:
    """Deux fantômes qui font les mêmes paris doivent les payer à peu près pareil."""
    first: dict[str, dict[str, float]] = {}
    for name, rows in entries.items():
        if name == "principal":
            continue
        prices: dict[str, float] = {}
        for e in _buys(rows):
            prices.setdefault(e["data"]["token_id"], float(e["data"]["price"]))
        first[name] = prices
    rows = []
    names = sorted(first)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            common = set(first[a]) & set(first[b])
            if len(common) >= min_common:
                diff = statistics.mean(abs(first[a][t] - first[b][t]) for t in common)
                if diff > gap:
                    rows.append((diff, f"{a} / {b} : {len(common)} paris communs, écart moyen {diff:.3f}"))
    if not rows:
        return []
    rows.sort(reverse=True)
    return [_finding("meme_pari_prix_differents", A_REGARDER, f"{len(rows)} paire(s) de stratégies : mêmes paris, autres prix",
                     "Même marché, prix d'entrée très différents : moment d'achat, ordre posé ou carnet relu. "
                     "La différence de résultat entre elles vient alors du prix, pas du choix des paris.",
                     [r[1] for r in rows])]


def muettes(entries: dict[str, list[dict]], active: list[str], now: datetime, hours: float = 48,
            abstentions: dict | None = None) -> list[dict]:
    """Stratégies sans aucun achat. `abstentions` (21/10/2026, clé « abstentions » de la base, écrite
    à chaque cycle) : marchés vus et raisons les plus fréquentes du dernier cycle, ajoutées au constat."""
    silent = []
    seen = (abstentions or {}).get("portefeuilles") or {}
    for name in active:
        rows = entries.get(name)
        if rows and _ts(rows[0]) < now - timedelta(hours=hours) and not _buys(rows):
            why = ""
            for info in (seen.get(f"fantome:{name}") or {}).values():
                reasons = ", ".join(f"{k} ×{v}" for k, v in (info.get("raisons") or {}).items()) or "aucune raison notée"
                why = f" — dernier cycle : {info.get('marches', 0)} marchés vus, {info.get('propositions', 0)} propositions ; {reasons}"
            silent.append(f"{name} (née le {rows[0]['ts'][:10]}){why}")
    return [_finding("muettes", A_REGARDER, f"{len(silent)} stratégie(s) sans aucun achat depuis plus de {hours:.0f} h",
                     "Une stratégie muette ne teste rien : lire ses abstentions (journal du cycle, tableau de bord) "
                     "et corriger le filtre ou la source qui la bloque.", silent)] if silent else []


def positions_oubliees(entries: dict[str, list[dict]], now: datetime, grace_hours: float = 72,
                       active: list[str] | None = None) -> list[dict]:
    """Positions ouvertes bien après l'échéance notée à l'achat. Ne regarde que les stratégies qui tournent
    (`active`) : une stratégie coupée ne règle plus rien (reversion, 20/10 : marché de Dallas réglé le 18/10,
    position jamais réglée car la stratégie est coupée depuis le 17/10) ; ni les teneurs de marché, dont
    `horizon_hours` est la durée de la cote et non l'échéance du marché (market_maker, 20/10)."""
    out = []
    for name, rows in entries.items():
        if (active is not None and name not in active) or name.startswith("market_maker"):
            continue
        opened: dict[str, dict] = {}
        shares: dict[str, Decimal] = defaultdict(Decimal)
        for e in rows:
            token = e["data"].get("token_id") if isinstance(e.get("data"), dict) else None
            if e["type"] == "RESET":
                opened.clear()
                shares.clear()
            elif e["type"] == "BUY":
                opened.setdefault(token, e)
                shares[token] += Decimal(e["data"]["shares"])
            elif e["type"] == "SELL" and token in opened:
                shares[token] -= Decimal(e["data"]["shares"])
                if shares[token] <= 0:
                    opened.pop(token, None)
            elif e["type"] == "SETTLE":
                opened.pop(token, None)
        late = []
        for e in opened.values():
            horizon = float((e["data"].get("extra") or {}).get("horizon_hours") or 0)
            if horizon and _ts(e) + timedelta(hours=horizon + grace_hours) < now:
                late.append(f"{e['ts'][:16]} « {e['data']['outcome']} » (marché {e['data']['market_id']}, échéance "
                            f"dépassée de {((now - _ts(e)).total_seconds() / 3600 - horizon):.0f} h)")
        if late:
            out.append(_finding("positions_oubliees", A_REGARDER, f"{name} : {len(late)} position(s) ouverte(s) bien après l'échéance",
                                "Marché contesté, règlement manqué ou mauvaise échéance : l'argent reste bloqué.", late))
    return out


def cycle_arrete(entries: dict[str, list[dict]], now: datetime, minutes: float = 30) -> list[dict]:
    beats = [e for e in entries.get("principal") or [] if e["type"] == "HEARTBEAT"]
    if beats and _ts(beats[-1]) < now - timedelta(minutes=minutes):
        return [_finding("cycle_arrete", GRAVE, f"dernier cycle du principal le {beats[-1]['ts'][:16]}",
                         "Le cycle de production ne tourne plus (ou n'écrit plus) : voir les exécutions du workflow "
                         "cycle et l'alerte labo-alerte.", [])]
    return []


def _p_one_sided(z: float) -> float:
    return 0.5 * math.erfc(z / math.sqrt(2))


def selection_multiple(entries: dict[str, list[dict]], copied: set[str], min_trades: int = 15,
                       alpha: float = 0.05) -> list[dict]:
    """Une stratégie copiée gagne-t-elle plus souvent que ses prix, APRÈS correction du fait qu'on
    l'a choisie parmi N ? (20/10 : la championne a z = 1,86 ; le meilleur de 35 stratégies sans aucun
    avantage atteint en moyenne 2,1 : son avance ne se distingue pas de la chance de la sélection.)"""
    zs: dict[str, tuple[float, int, float]] = {}
    for name, rows in entries.items():
        if name == "principal":
            continue
        trades = closed_trades(rows)
        if len(trades) < min_trades:
            continue
        won, expected = _won_vs_expected(trades)
        var = sum((float(t["cost"]) / float(t["shares_bought"])) * (1 - float(t["cost"]) / float(t["shares_bought"]))
                  for t in trades if float(t["shares_bought"]) > 0)
        if var > 0:
            zs[name] = ((won - expected) / math.sqrt(var), len(trades), expected)
    n = len(zs)
    out = []
    for name in sorted(copied & set(zs)):
        z, count, expected = zs[name]
        adjusted = min(1.0, _p_one_sided(z) * n)
        if adjusted > alpha:
            best = max(v[0] for v in zs.values())
            out.append(_finding("selection_multiple", A_REGARDER,
                                f"{name} : z = {z:+.2f} sur {count} paris, mais choisie parmi {n} stratégies",
                                f"P(hasard) corrigée = {adjusted:.2f} (> {alpha}) : le meilleur z de l'arène est {best:+.2f}, "
                                f"ce que {n} stratégies sans avantage donnent déjà. Ne pas confondre « première du classement » "
                                "et « avantage prouvé » : confirmer sur de nouveaux paris (ou un test sur le passé).", []))
    return out


def deux_camps(entries: dict[str, list[dict]], since: datetime | None = None, min_price: float = 0.7) -> list[dict]:
    """Même stratégie, même marché, les deux camps achetés CHERS (prix ≥ 0,70 : un favori puis le camp opposé
    devenu favori ; les jambes à 0,50 des teneurs de marché et paires sont voulues) : le deuxième achat
    rattrape un favori qui vient de s'effondrer (en jeu) ; la mise est doublée sur un seul match."""
    out = []
    for name, rows in entries.items():
        if name == "principal":
            continue
        by_market: dict[str, dict[str, dict]] = defaultdict(dict)
        for e in _buys(rows, since):
            d = e["data"]
            slot = by_market[d["market_id"]].setdefault(d["token_id"], {"outcome": d["outcome"], "cost": 0.0, "ts": e["ts"],
                                                                        "price": float(d["price"])})
            slot["cost"] += _cost(d)
        pairs = [v for v in by_market.values() if len(v) > 1 and all(x["price"] >= min_price for x in v.values())]
        if pairs:
            total = sum(x["cost"] for v in pairs for x in v.values())
            out.append(_finding("deux_camps", A_REGARDER,
                                f"{name} : {len(pairs)} marché(s) dont les deux camps sont achetés ({total:.0f} € misés)",
                                "Le deuxième achat suit l'effondrement du premier favori : regarder si la stratégie doit "
                                "refuser le camp opposé d'une position ouverte ou fermée.",
                                [" ↔ ".join(f"{x['ts'][:16]} « {x['outcome']} » {x['cost']:.0f} €" for x in v.values())
                                 for v in pairs]))
    return out


def achats_en_jeu(entries: dict[str, list[dict]], copied: set[str], since: datetime | None = None,
                  min_trades: int = 10, share: float = 0.5) -> list[dict]:
    """Part des achats faits après le coup d'envoi (champ `depuis_coup_d_envoi_h` du journal, ajouté le
    20/10/2026). L'échéance Gamma d'un match est une date placeholder (jusqu'à +7 jours) : `horizon_hours`
    ne dit rien de la date réelle de règlement (championne : horizon médian 165 h, règlement réel 2,2 h)."""
    out = []
    for name in sorted(copied & set(entries)):
        timed = [float((e["data"].get("extra") or {})["depuis_coup_d_envoi_h"]) for e in _buys(entries[name], since)
                 if (e["data"].get("extra") or {}).get("depuis_coup_d_envoi_h") not in (None, "")]
        if len(timed) < min_trades:
            continue
        live = sum(1 for h in timed if h > 0)
        if live / len(timed) > share:
            out.append(_finding("achats_en_jeu", A_REGARDER,
                                f"{name} : {live} achats sur {len(timed)} faits après le coup d'envoi",
                                "La stratégie achète des favoris EN COURS de match, pas des « paris patients » : ses filtres "
                                "d'échéance (`echeance_*`, `delai` du pareto) mesurent la date placeholder de Gamma, pas le "
                                "temps réel ; utiliser `heures_min/heures_max` (coup d'envoi) pour découper par délai.", []))
    return out


# ------------------------------------------------------------------ ensemble


def run(entries: dict[str, list[dict]], configs: dict, active: list[str], now: datetime,
        max_principal: float = 0.10, days: float = 3, abstentions: dict | None = None) -> list[dict]:
    """Tous les contrôles ; les achats sont regardés sur les `days` derniers jours (les défauts déjà
    corrigés ne reviennent pas à chaque passage), les résultats sur toute la vie des stratégies."""
    since = now - timedelta(days=days)
    findings = (cycle_arrete(entries, now) + copie_fidele(entries, since) + mises(entries, max_principal, since=since)
                + champion_sans_avantage(entries, now) + estimation_perimee(entries, since)
                + chance(entries, copied=copied_by_principal(entries, now))
                + selection_multiple(entries, copied_by_principal(entries, now))
                + deux_camps(entries, since) + achats_en_jeu(entries, copied_by_principal(entries, now), since)
                + filles_periode(entries, configs) + filtre_prix(entries, configs, since)
                + filtre_delai(entries, configs, since)
                + meme_pari_prix_differents(entries) + muettes(entries, active, now, abstentions=abstentions)
                + positions_oubliees(entries, now, active=active))
    return sorted(findings, key=lambda f: f["gravite"] != GRAVE)


def obligations(findings: list[dict]) -> list[str]:
    return [f"Enquête obligatoire ({f['controle']}) : {f['titre']}. Trouver la cause, corriger (ou proposition si "
            "noyau), test de non-régression, compte rendu dans experiments/enquetes/ (reports/enquete.md)."
            for f in findings if f["gravite"] == GRAVE]


def render(findings: list[dict], now: datetime) -> str:
    lines = [f"# Enquête automatique — {now.isoformat(timespec='minutes')}", "",
             "Défauts possibles trouvés dans les journaux publiés (enquete.py). « grave » = obligation de la "
             "feuille de mission ; « à regarder » = piste pour l'enquête manuelle (docs/ROUTINE_CHERCHEUR.md).", ""]
    if not findings:
        return "\n".join(lines + ["Aucun constat."]) + "\n"
    for f in findings:
        lines += [f"## [{f['gravite']}] {f['titre']}", "", f"*Contrôle `{f['controle']}`* — {f['detail']}", ""]
        lines += [f"- {x}" for x in f["exemples"]]
        lines.append("")
    return "\n".join(lines)
