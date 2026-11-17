"""Marges du Maryland pendant le comptage tardif (17/11/2026, piste n° 68, experiments/comptage_tardif.md « Maryland »).

« Will the Democratic Party candidate win the 2026 MD-05 House election by 40%-45%? » (et « … 2026 Maryland gubernatorial election
by 35%-40%? ») se règle, comme en Californie, sur la marge OFFICIELLE certifiée des deux premiers (voix valides, égalité à une borne =
tranche du dessus). Le décompte non officiel courant est publié par le State Board of Elections en pages publiques
(`elections.maryland.gov/elections/2026/general_results/`, robots.txt : permis), avec une colonne par type de bulletin (anticipé,
jour J, correspondance, provisoire ; « NR » = pas encore publié). Au 14/11, ≈ 26 000 bulletins par correspondance reçus restaient à
compter (`Absentees_Ballots_Left_To_Count_by_County.xlsx`) et les provisoires de Montgomery n'étaient pas publiés : ≈ 1-2 % des voix.

Chance : même loi que `marges_californie.chance` (restants log-normaux, médiane `R_MED`, marge des restants ~ normale(μ, 15 points)),
avec μ = marge des bulletins par correspondance ET provisoires déjà comptés de la course (les restants sont de ces deux types ; au
Maryland ils penchent bien plus à gauche que le total : gouverneur 34,6 points au total, 61 sur la correspondance). Les références
sont rattachées sous la clé `marges_ca` : c'est la même expérience que `marges_californie` (même hypothèse, même stratégie).
"""
from __future__ import annotations

import html as _html
import re
from datetime import datetime

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.marges_californie import chance

BASE = "https://elections.maryland.gov/elections/2026/general_results/"
PAGES = {"MD-GOV": "gen_results_2026_1.html", **{f"MD-{n:02d}": f"gen_results_2026_4_{n}.html" for n in range(1, 9)}}
R_MED = 0.015       # restants ≈ 1,5 % des voix comptées (26 000 correspondances + provisoires de Montgomery pour 2,23 M au 14-16/11)
R_SIGMA = 0.8       # 99 % sous ≈ 10 % (20 % quand les provisoires de la course ne sont pas publiés : médiane doublée)
_Q = re.compile(r"Will the (Democratic|Republican) Party candidate win the 2026 (?:MD-(\d+) House|Maryland gubernatorial) election"
                r"(?: by (\d+(?:\.\d+)?)%(?:-(\d+(?:\.\d+)?)%| or more))?\?$", re.IGNORECASE)
_PARTIS = ("Democratic", "Republican", "Green", "Libertarian", "Working Class Party", "Unaffiliated", "Other Candidates")
_NB = r"([0-9,]+|NR)"


def question(q: str) -> tuple[str, str, float, float] | None:
    """(course « MD-05 » / « MD-GOV », parti « D »/« R », borne basse, borne haute) en points ; « win » sans tranche = (0, ∞)."""
    m = _Q.match((q or "").strip())
    if not m:
        return None
    party = "D" if m.group(1).lower().startswith("dem") else "R"
    course = f"MD-{int(m.group(2)):02d}" if m.group(2) else "MD-GOV"
    lo = float(m.group(3)) if m.group(3) else 0.0
    hi = float(m.group(4)) if m.group(4) else float("inf")
    return course, party, lo, hi


def _n(v: str) -> int | None:
    return None if v == "NR" else int(v.replace(",", ""))


def lire(page: str) -> dict | None:
    """Page de résultats d'une course → {heure, d, r, total, meme_parti, autre_en_tete, ecart_api, tard_d, tard_r, tard_total}.
    d − r = marge signée des deux premiers (d = voix du premier si c'est un démocrate, sinon du second) ; « tard_* » = voix des
    colonnes correspondance + provisoire (les types de bulletins encore à compter). Seul le PREMIER tableau de la page est lu."""
    t = _html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page or "")))
    heure = re.search(r"Last refreshed: ([0-9/]+ [0-9:]+ [AP]M)", t)
    debut = t.find("Vote for 1")
    if debut < 0:
        return None
    fin = t.find("Totals", debut)
    tot = re.match(rf"Totals {_NB} {_NB} {_NB} {_NB} ([0-9,]+) 100\.00%", t[fin:]) if fin > 0 else None
    if tot is None:
        return None
    bloc = t[debut:fin]
    cands = []
    for parti, a, b, c, d, total, pct in re.findall(rf"({'|'.join(_PARTIS)}) {_NB} {_NB} {_NB} {_NB} ([0-9,]+) ([0-9.]+)%", bloc):
        cands.append({"parti": parti, "total": _n(total), "pct": float(pct), "tard": (_n(c) or 0) + (_n(d) or 0)})
    total = _n(tot.group(5))
    if not total or len(cands) < 2:
        return None
    cands.sort(key=lambda x: -x["total"])
    p1, p2 = cands[0], cands[1]
    meme = p1["parti"] == p2["parti"]
    autre = p1["parti"] not in ("Democratic", "Republican")
    dem, rep = (p1, p2) if p1["parti"] == "Democratic" else (p2, p1)
    tard_total = (_n(tot.group(3)) or 0) + (_n(tot.group(4)) or 0)
    return {"heure": heure.group(1) if heure else "", "d": dem["total"], "r": rep["total"], "total": total, "meme_parti": meme,
            "autre_en_tete": autre, "ecart_api": round(p1["pct"] - p2["pct"], 2), "tard_d": dem["tard"], "tard_r": rep["tard"],
            "tard_total": tard_total, "provisoires_publies": tot.group(4) not in ("NR", "0")}


def fetch_maryland(http: HttpClient, now: datetime, pages: dict | None = None) -> list[dict]:
    rows = []
    for course, page in (pages or PAGES).items():
        try:
            x = lire(http.get_text(BASE + page))
        except SourceUnavailable:
            continue
        if x is not None:
            rows.append(dict(x, district=course, lu=now.isoformat()))
    if not rows:
        raise SourceUnavailable("elections.maryland.gov : aucune course lue")
    return rows


def attach_marges_md(markets, db, now: datetime, max_age_hours: float = 3.0) -> int:
    """Rattache la chance de chaque tranche du Maryland sous la clé `marges_ca` (stratégie `marges_californie`)."""
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:marges_md")
    if seen is None or not rows or (now - seen).total_seconds() > max_age_hours * 3600:
        return 0
    par = {r["district"]: r for r in rows}
    n = 0
    for m in markets:
        q = question(m.question or "")
        if q is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        course, party, lo, hi = q
        r = par.get(course)
        if r is None or r.get("meme_parti") or r.get("autre_en_tete"):
            continue
        s0 = 100.0 * (r["d"] - r["r"]) / r["total"]
        if r.get("ecart_api") is not None and abs(abs(s0) - r["ecart_api"]) > 0.5:
            continue   # notre marge ne redonne pas l'écart des pourcentages publiés : lecture fausse, pas de chance donnée
        tard = r.get("tard_total") or 0
        mu = 100.0 * (r["tard_d"] - r["tard_r"]) / tard if tard >= 500 else s0
        a, b = (lo, hi) if party == "D" else (-hi, -lo)
        if party == "R" and lo == 0.0:
            b = 0.0
        if party == "D" and lo == 0.0:
            a = 1e-9
        # Provisoires pas encore publiés (« NR » ou 0 : MD-08, tout à Montgomery, le 16/11) : restants attendus doublés.
        p = chance(s0, mu, a, b, r_med=R_MED * (1 if r.get("provisoires_publies") else 2), r_sigma=R_SIGMA)
        lu = parse_date(r.get("lu") or "") or seen
        m.references = dict(m.references or {}, marges_ca={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": lu.isoformat(),
            "titre": (f"{course} {party} {lo:g}-{hi:g} : marge D−R {s0:+.2f} sur {r['total']} voix ({r['heure']}), "
                      f"correspondance et provisoires comptés {mu:+.1f}{'' if r.get('provisoires_publies') else ' (provisoires non publiés)'} : {p:.3f}")})
        n += 1
    return n
