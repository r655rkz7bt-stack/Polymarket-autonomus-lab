"""Pistes n° 4 (bo3_coherence, e-sport) et n° 5 (tennis_sets_coherence) : modèle et test sur le passé, communs.

IDÉE. Dans un match en 2 (ou 3) manches gagnantes, si chaque manche (carte, set) est gagnée par A avec la même
chance q, indépendamment des autres (loi binomiale) :
  - vainqueur du match, BO3 : q² (3 − 2q) ; BO5 : q³ (10 − 15q + 6q²) ;
  - manche 1 (ou 2) : q ;
  - handicap −1,5 (A gagne 2-0 en BO3) : q² ; BO5 −1,5 (3-0 ou 3-1) : q³ (4 − 3q) ; BO5 −2,5 (3-0) : q³ ;
  - total de manches, BO3 plus de 2,5 (3 manches) : 2q (1 − q) ; BO5 plus de 3,5 : 1 − q³ − (1 − q)³ ;
    BO5 plus de 4,5 : 6 q² (1 − q)².
Le prix du vainqueur (marché liquide) donne q ; on en déduit le juste prix des marchés liés (minces) et on achète le
côté vendu nettement moins cher que ce calcul.

RÈGLES DU TEST (experiments/enquetes/README.md, règle du 22/10) :
  - décision à T0 = coup d'envoi − h heures ; aucune donnée postérieure à T0 pour le modèle ;
  - prix du vainqueur à T0 = médiane des 5 derniers ÉCHANGES RÉELS dans l'heure avant T0 (sinon : pas de modèle) ;
  - prix d'achat = prix RÉELLEMENT payé par un preneur sur le marché lié : « avant » (dernier échange dans la fenêtre
    avant T0, prix connu à la décision) ou « après » (premier échange après T0, jamais après le coup d'envoi) ;
    frais du marché (rate × p × (1 − p)) ; pas d'échange = pas de pari (compté) ;
  - réglage sur la 1re moitié des jours, jugement sur la 2e ; paris d'un même match regroupés (`idea_test.verdict`).
"""
from __future__ import annotations

import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from polymarket_agent import idea_test as it  # noqa: E402
from echanges import cout_preneur, prix_equivalent  # noqa: E402


# --- modèle binomial -------------------------------------------------------------------------------------------
def p_match(q: float, bo: int) -> float:
    return q * q * (3 - 2 * q) if bo == 3 else q ** 3 * (10 - 15 * q + 6 * q * q)


def q_depuis_match(m: float, bo: int) -> float:
    """Inverse de p_match (croissante) par dichotomie."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if p_match(mid, bo) < m:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def p_handicap(q: float, bo: int, line: float) -> float | None:
    """Chance que l'équipe à −line gagne avec au moins |line| + 0,5 manches d'écart (q = sa chance par manche)."""
    a = abs(line)
    if bo == 3 and a == 1.5:
        return q * q
    if bo == 5 and a == 1.5:
        return q ** 3 * (4 - 3 * q)
    if bo == 5 and a == 2.5:
        return q ** 3
    return None


def p_plus(q: float, bo: int, line: float) -> float | None:
    """Chance de PLUS de `line` manches jouées."""
    if bo == 3 and line == 2.5:
        return 2 * q * (1 - q)
    if bo == 5 and line == 3.5:
        return 1 - q ** 3 - (1 - q) ** 3
    if bo == 5 and line == 4.5:
        return 6 * q * q * (1 - q) ** 2
    return None


# --- lecture des marchés ---------------------------------------------------------------------------------------
def _jl(v):
    try:
        return json.loads(v) if isinstance(v, str) else (v or [])
    except ValueError:
        return []


def _ts(s: str | None) -> int | None:
    """« 2026-10-10 14:00:00+00 » (gameStartTime) ou ISO 8601 -> secondes Unix."""
    if not s:
        return None
    s = str(s).replace(" ", "T").replace("Z", "+00:00")
    if s.endswith("+00"):
        s += ":00"
    try:
        return int(datetime.fromisoformat(s).timestamp())
    except ValueError:
        return None


def regle(m: dict) -> int | None:
    """Indice de l'issue gagnante (0 ou 1) ; None si non réglé net (50-50, litige)."""
    pr = [str(x) for x in _jl(m.get("outcomePrices"))]
    if sorted(pr) != ["0", "1"] or m.get("umaResolutionStatus") not in (None, "", "resolved"):
        return None
    return pr.index("1")


def taux(m: dict) -> float:
    fs = m.get("feeSchedule") or {}
    return float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0


def nom_proche(a: str, b: str) -> bool:
    a, b = a.lower().strip(), b.lower().strip()
    return a == b or a in b or b in a


def match_cas(ev: dict, famille: str) -> dict | None:
    """Un match : marché vainqueur + marchés liés traduits en « chance de l'issue 0 en fonction de q_A »."""
    ml = [m for m in ev["markets"] if m.get("sportsMarketType") == "moneyline"]
    if len(ml) != 1:
        return None
    ml = ml[0]
    outs, toks = _jl(ml.get("outcomes")), _jl(ml.get("clobTokenIds"))
    if len(outs) != 2 or len(toks) != 2:
        return None
    start = _ts(ml.get("gameStartTime"))
    if start is None:
        return None
    title = ev.get("title") or ""
    if famille == "esport":
        mo = re.search(r"\(BO(\d)\)", title)
        bo = int(mo.group(1)) if mo else None
    else:
        lines = {float(m.get("line")) for m in ev["markets"] if m.get("sportsMarketType") == "tennis_set_totals" and m.get("line") is not None}
        q_lines = {float(x) for m in ev["markets"] if m.get("sportsMarketType") == "tennis_set_totals"
                   for x in re.findall(r"O/U (\d\.5)", m.get("question") or "")}
        lines |= q_lines
        bo = 5 if lines & {3.5, 4.5} else 3
    if bo not in (3, 5):
        return None
    A, B = outs
    lies = []
    for m in ev["markets"]:
        t = m.get("sportsMarketType")
        mo_, mt = _jl(m.get("outcomes")), _jl(m.get("clobTokenIds"))
        if len(mo_) != 2 or len(mt) != 2 or m is ml:
            continue
        q_txt = m.get("question") or ""
        kind, f = None, None
        if t in ("child_moneyline", "tennis_first_set_winner", "tennis_set_winner"):
            k = re.search(r"(?:Map|Game|Set) (\d+) Winner", q_txt)
            k = int(k.group(1)) if k else (1 if t == "tennis_first_set_winner" else None)
            if k is None or k > (2 if bo == 3 else 3):
                continue  # une manche qui peut ne pas être jouée : écartée
            if nom_proche(mo_[0], A) and nom_proche(mo_[1], B):
                f = lambda q: q
            elif nom_proche(mo_[0], B) and nom_proche(mo_[1], A):
                f = lambda q: 1 - q
            kind = "manche 1" if k == 1 else f"manche {k}"
        elif t in ("map_handicap", "tennis_set_handicap"):
            line = m.get("line")
            mm = re.search(r"\((-\d+\.5)\)", q_txt)
            line = float(mm.group(1)) if mm else (float(line) if line is not None else None)
            if line is None:
                continue
            fav = mo_[0]  # issue 0 = l'équipe à −line (vérifié sur les libellés « X (−1,5) vs Y (+1,5) »)
            if nom_proche(fav, A):
                f = lambda q, bo=bo, line=line: p_handicap(q, bo, line)
            elif nom_proche(fav, B):
                f = lambda q, bo=bo, line=line: p_handicap(1 - q, bo, line)
            kind = "handicap"
            if f is not None and f(0.5) is None:
                f = None
        elif t in ("totals", "tennis_set_totals"):
            mm = re.search(r"O/U (\d+\.5)", q_txt)
            if not mm:
                continue
            line = float(mm.group(1))
            if p_plus(0.5, bo, line) is None:
                continue
            if mo_[0].lower().startswith("over"):
                f = lambda q, bo=bo, line=line: p_plus(q, bo, line)
            elif mo_[0].lower().startswith("under"):
                f = lambda q, bo=bo, line=line: 1 - p_plus(q, bo, line)
            kind = "total"
        if f is None or kind is None:
            continue
        won = regle(m)
        if won is None:
            continue
        lies.append({"id": m["id"], "kind": kind, "f": f, "toks": mt, "won": won, "rate": taux(m), "vol": m.get("volumeNum") or 0})
    if not lies:
        return None
    return {"event": str(ev["id"]), "slug": ev.get("slug"), "serie": ev.get("serie"), "bo": bo, "start": start, "ml_toks": toks,
            "ml_won": regle(ml), "ml_rate": taux(ml), "lies": lies}


# --- construction des paris ------------------------------------------------------------------------------------
def prix_vainqueur(rows, cas, t0: int) -> float | None:
    pts = prix_equivalent(rows, cas["ml_toks"][0], cas["ml_toks"][1], t0 - 3600, t0)
    if not pts:
        return None
    return statistics.median(p for _, p in pts[-5:])


def candidats(cas_list, trades, h: int, fenetre: int, mode: str):
    """Pour chaque marché lié et chaque issue : (cas, lié, issue, chance du modèle brute, coût payé, gagné ?).
    Compte aussi les cas sans modèle (vainqueur sans échange) et sans prix (marché lié sans échange)."""
    out, stats = [], Counter()
    for cas in cas_list:
        rows = trades.get(cas["event"])
        if rows is None:
            stats["échanges indisponibles"] += 1
            continue
        t0 = cas["start"] - h * 3600
        if rows and len(rows) >= 11000 and min(r[0] for r in rows) > t0 - fenetre:
            stats["échanges tronqués avant T0"] += 1
            continue
        m = prix_vainqueur(rows, cas, t0)
        if m is None or not 0.02 < m < 0.98:
            stats["vainqueur sans échange réel dans l'heure avant T0"] += 1
            continue
        q = q_depuis_match(m, cas["bo"])
        for li in cas["lies"]:
            stats["marchés liés examinés"] += 1
            p0 = li["f"](q)
            if p0 is None:
                continue
            vu = False
            for issue in (0, 1):
                tok, autre = li["toks"][issue], li["toks"][1 - issue]
                got = cout_preneur(rows, tok, autre, t0, fenetre, apres=(mode == "après"), fin_max=cas["start"])
                if got is None:
                    continue
                vu = True
                _, cost = got
                if not 0.01 <= cost <= 0.99:
                    continue
                pm = p0 if issue == 0 else 1 - p0
                out.append({"cas": cas, "li": li, "issue": issue, "pm": pm, "cost": cost, "win": int(li["won"] == issue)})
            if not vu:
                stats["marché lié sans échange dans la fenêtre"] += 1
    return out, stats


def jour(ts: int) -> str:
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d")


def calibrer(cands, kinds) -> dict:
    """Recalibrage logistique logit(vrai) = a + b·logit(modèle) par type de marché lié, ajusté sur `cands`
    (apprentissage seulement). Descente de gradient simple, une issue par marché (issue 0)."""
    res = {}
    for k in kinds:
        seen = set()
        data = []
        for c in cands:
            if c["li"]["kind"] == k and c["li"]["id"] not in seen:
                seen.add(c["li"]["id"])
                p0 = c["pm"] if c["issue"] == 0 else 1 - c["pm"]
                data.append((min(0.99, max(0.01, p0)), c["li"]["won"] == 0))
        if len(data) < 50:
            res[k] = (0.0, 1.0)
            continue
        a, b = 0.0, 1.0
        for _ in range(300):
            ga = gb = 0.0
            for p, y in data:
                x = math.log(p / (1 - p))
                z = 1 / (1 + math.exp(-(a + b * x)))
                ga += z - y
                gb += (z - y) * x
            a -= 0.5 * ga / len(data)
            b -= 0.5 * gb / len(data)
        res[k] = (a, b)
    return res


def appliquer(pm: float, ab) -> float:
    a, b = ab
    p = min(0.995, max(0.005, pm))
    return 1 / (1 + math.exp(-(a + b * math.log(p / (1 - p)))))


def paris(cands, edge: float, calib: dict | None = None):
    """Au plus un pari par marché lié : l'issue dont l'avance (modèle − coût − frais) est la plus grande, si > edge."""
    best = {}
    for c in cands:
        pm = c["pm"]
        if calib:
            p0 = pm if c["issue"] == 0 else 1 - pm
            p0 = appliquer(p0, calib.get(c["li"]["kind"], (0.0, 1.0)))
            pm = p0 if c["issue"] == 0 else 1 - p0
        cost = c["cost"]
        fee = it.fee(cost, c["li"]["rate"])
        adv = pm - cost - fee
        if adv <= edge:
            continue
        key = c["li"]["id"]
        if key not in best or adv > best[key][0]:
            best[key] = (adv, c, cost + fee)
    out = []
    for adv, c, paid in best.values():
        out.append({"gain": c["win"] / paid - 1, "evenement": c["cas"]["event"], "cout": paid, "win": c["win"],
                    "mois": jour(c["cas"]["start"])[:7], "jour": jour(c["cas"]["start"]), "kind": c["li"]["kind"],
                    "serie": c["cas"]["serie"], "adv": adv})
    return out


def resume(bets, label: str) -> str:
    if not bets:
        return f"| {label} | 0 | | | | | | |"
    v = it.verdict(bets)
    w = sum(b["win"] for b in bets)
    e = sum(b["cout"] for b in bets)
    return (f"| {label} | {v['paris']} | {v['evenements']} | {100 * v['rendement_moyen']:+.1f} % | {v['confiance_evenements']:+.2f} | "
            f"{v['mois_gagnants']} | {w} / {e:.1f} (z {v['z_prix']:+.1f}) | {v['verdict']} |")
