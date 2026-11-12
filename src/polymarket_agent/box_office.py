"""Course au film le plus rentable de l'année : cohérence entre le marché du PREMIER WEEK-END et celui de l'ANNÉE (12/11/2026).

« Highest grossing movie in 2026? » se règle sur la recette domestique de l'année CIVILE (dates hors 2026 exclues). Un film qui
sort un vendredi de décembre n'a que ses 14 premiers jours dans l'année. Recette au 31/12 = premier week-end (3 jours) × un
multiplicateur de Noël mesuré sur les grosses sorties de décembre (experiments/box_office_annee.md) :
Star Wars VII (même calendrier, vendredi 18/12) 2,63 ; Spider-Man NWH 2,14-2,20 ; Rogue One 2,42 ; The Last Jedi 2,11-2,35 ;
Rise of Skywalker 2,20-2,35 → médiane ≈ 2,35, écart log ≈ 0,08.

La loi du premier week-end vient d'un AUTRE marché Polymarket (« "<film>" Opening Weekend Box Office », tranches) : prix milieu
normalisés → loi log-normale ajustée ; une fois la tranche réglée, loi uniforme dans la tranche. Aucune source externe à lire en
direct : la recette du meneur (`meneur`) est une constante de la configuration (lue dans la presse, à relire avant la sortie).
"""
from __future__ import annotations

import json
import math
import re
from datetime import datetime
from statistics import NormalDist

from polymarket_agent.http_client import HttpClient

GAMMA_EVENT = "https://gamma-api.polymarket.com/events/{id}"
_N = NormalDist()
_TRANCHE = re.compile(r"^\s*(<|)\s*(\d+(?:\.\d+)?)m\s*(?:-\s*(\d+(?:\.\d+)?)m|\+|)\s*$", re.IGNORECASE)


def parse_tranche(titre: str) -> tuple[float, float] | None:
    """« <260m » → (1, 260) ; « 260m-300m » → (260, 300) ; « 400m+ » → (400, inf). En millions de dollars."""
    g = _TRANCHE.match(titre or "")
    if not g:
        return None
    lt, a, b = g.group(1), float(g.group(2)), g.group(3)
    if lt:
        return (1.0, a)
    if b:
        return (a, float(b))
    if (titre or "").strip().endswith("+"):
        return (a, math.inf)
    return None


def tranches_of_event(ev: dict) -> list[dict]:
    out = []
    for m in ev.get("markets") or []:
        t = parse_tranche(m.get("groupItemTitle") or "")
        if t is None:
            continue
        try:
            prices = [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except (TypeError, ValueError):
            continue
        if len(prices) != 2:
            continue
        reglee = bool(m.get("closed")) and prices[0] in (0.0, 1.0)
        out.append({"lo": t[0], "hi": t[1], "p": prices[0], "reglee": reglee})
    return out


def fit_lognormal(tranches: list[dict]) -> tuple[float, float] | None:
    """Médiane et écart log du premier week-end qui collent le mieux aux prix (moindres carrés sur une grille)."""
    tot = sum(t["p"] for t in tranches)
    if tot <= 0 or len(tranches) < 3:
        return None
    best = None
    for med in range(50, 801):
        for k in range(8, 81):
            s = k * 0.005
            err = 0.0
            for t in tranches:
                hi = 1.0 if math.isinf(t["hi"]) else _N.cdf(math.log(t["hi"] / med) / s)
                err += (hi - _N.cdf(math.log(max(t["lo"], 1e-9) / med) / s) - t["p"] / tot) ** 2
            if best is None or err < best[0]:
                best = (err, float(med), s)
    return best[1], best[2]


def p_depasse(tranches: list[dict], meneur: float, ratio: float, ratio_sigma: float) -> dict | None:
    """Chance que premier week-end × multiplicateur dépasse `meneur` (millions de dollars)."""
    gagnee = [t for t in tranches if t["reglee"] and t["p"] == 1.0]
    if gagnee:
        t = gagnee[0]
        lo, hi = t["lo"], (t["hi"] if not math.isinf(t["hi"]) else t["lo"] * 1.25)
        pts = [lo + (hi - lo) * (i + 0.5) / 40 for i in range(40)]
        p = sum(1 - _N.cdf(math.log(meneur / (ow * ratio)) / ratio_sigma) for ow in pts) / len(pts)
        return {"p": p, "mode": "tranche réglée", "ow": f"{lo:.0f}-{hi:.0f}"}
    fit = fit_lognormal([t for t in tranches if not t["reglee"]] or tranches)
    if fit is None:
        return None
    med, s = fit
    sig = math.sqrt(s * s + ratio_sigma * ratio_sigma)
    p = 1 - _N.cdf(math.log(meneur / (med * ratio)) / sig)
    return {"p": p, "mode": "prix du premier week-end", "ow": f"médiane {med:.0f}, écart log {s:.3f}"}


def fetch_box_office(http: HttpClient, courses: list[dict], now: datetime) -> list[dict]:
    rows = []
    for c in courses:
        ev = http.get_json(GAMMA_EVENT.format(id=c["ow_event"]), headers={"User-Agent": "curl/8"})
        tr = tranches_of_event(ev or {})
        r = p_depasse(tr, float(c["meneur"]), float(c.get("ratio", 2.35)), float(c.get("ratio_sigma", 0.08)))
        if r is None:
            continue
        rows.append({"film": c["film"], "annee": int(c.get("annee", now.year)), "meneur": float(c["meneur"]),
                     "jusqu_au": c.get("jusqu_au"), "lu": now.isoformat(), **r,
                     "tranches": [[t["lo"], None if math.isinf(t["hi"]) else t["hi"], t["p"], t["reglee"]] for t in tr]})
    return rows


_QUESTION = re.compile(r"^Will (.+?) be the top grossing movie of (\d{4})\?", re.IGNORECASE)


def attach_box_office(markets, db, now: datetime, max_age_hours: float = 6.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:box_office")
    if seen is None or not rows:
        return 0
    by_film = {(r["film"].lower(), int(r["annee"])): r for r in rows}
    n = 0
    for m in markets:
        g = _QUESTION.match(m.question or "")
        if not g or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        row = by_film.get((g.group(1).strip().lower(), int(g.group(2))))
        if row is None:
            continue
        lu = parse_date(row["lu"])
        fin = parse_date(row["jusqu_au"]) if row.get("jusqu_au") else None
        if lu is None or (now - lu).total_seconds() > max_age_hours * 3600 or (fin is not None and now > fin):
            continue  # relevé trop vieux, ou recettes réelles déjà publiées (le modèle du premier week-end ne sert plus)
        m.references = dict(m.references or {}, box_office={
            "p": round(row["p"], 4), "p_dedup": round(row["p"], 4), "p_rapide": round(row["p"], 4), "vu_le": seen.isoformat(),
            "titre": f"{row['film']} : premier week-end ({row['mode']}, {row['ow']}) × Noël contre {row['meneur']:.0f} M$ : {row['p']:.3f}"})
        n += 1
    return n
