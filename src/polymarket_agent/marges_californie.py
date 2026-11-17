"""Marges des districts californiens de la Chambre pendant le comptage tardif (17/11/2026, piste n° 66, experiments/comptage_tardif.md).

« Will a Democratic Party candidate win the 2026 CA-26 House election by 25%-30%? » se règle sur la marge OFFICIELLE certifiée
(différence des pourcentages des deux premiers sur les voix valides ; égalité à une borne = tranche du dessus). La Californie compte
pendant des semaines après le vote ; le décompte officiel courant est servi sans clé par `api.sos.ca.gov/returns/us-rep/district/<n>`
(pas de robots.txt ; la page des bulletins restants est derrière Incapsula : jamais lue). Les carnets de ces marchés sont « de façade »
(vendeur 0,84-0,98 sur toutes les tranches) : la tranche où tombe la marge courante, que les derniers bulletins ne peuvent presque plus
faire sortir, est vendue au même prix que ses voisines.

Chance = loi de la marge finale s = (s0 + m × r) / (1 + r) : s0 marge courante (signée, D − R, en points), r bulletins restants en part
des voix comptées (log-normale, médiane `R_MED`, dispersion `R_SIGMA` ; San Diego : 4,2 % restants le 12/11 ; État : +0,5 % du 14 au
16/11), m marge des bulletins restants ~ normale(μ, `SD_TARDIVE`), μ = marge des bulletins comptés entre les deux derniers « ReportingTime »
du district (journal `marges_ca:histo`, au moins `MIN_AJOUT` bulletins), sinon s0. Districts dont les deux premiers sont du même parti :
aucune chance (les tranches « Democrat/Republican » n'y ont pas le même sens).
"""
from __future__ import annotations

import math
import re
from datetime import datetime

from polymarket_agent.http_client import HttpClient, SourceUnavailable

API = "https://api.sos.ca.gov/returns/us-rep/district/{n}"
DISTRICTS = range(1, 53)
R_MED = 0.02        # bulletins restants (part des voix comptées), médiane
R_SIGMA = 0.8       # dispersion log-normale : 90 % sous 5,6 %, 99 % sous 13 %
SD_TARDIVE = 15.0   # écart-type de la marge des bulletins restants autour de μ (points)
MIN_AJOUT = 500     # bulletins ajoutés entre deux relevés pour croire leur marge
_Q = re.compile(r"Will a (Democratic|Republican) Party candidate win the 2026 CA-(\d+) House election"
                r"(?: by (\d+(?:\.\d+)?)%(?:-(\d+(?:\.\d+)?)%| or more))?\?$", re.IGNORECASE)
def _phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def _inv_phi(p: float) -> float:
    lo, hi = -10.0, 10.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if _phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# Quantiles de la log-normale (milieux de 40 tranches égales) : intégration sans tirage au hasard.
_Z = [_inv_phi((i + 0.5) / 40) for i in range(40)]


def question(q: str) -> tuple[int, str, float, float] | None:
    """(district, parti « D »/« R », borne basse, borne haute) en points de marge ; « win » sans tranche = (0, ∞)."""
    m = _Q.match((q or "").strip())
    if not m:
        return None
    party = "D" if m.group(1).lower().startswith("dem") else "R"
    lo = float(m.group(3)) if m.group(3) else 0.0
    hi = float(m.group(4)) if m.group(4) else math.inf
    return int(m.group(2)), party, lo, hi


def _n(v) -> int:
    return int(str(v or "0").replace(",", ""))


def lire(d) -> dict | None:
    """Réponse de l'API d'un district → {heure, d, r, total, meme_parti, autre_en_tete} (d − r : marge signée des deux premiers)."""
    if isinstance(d, list):
        d = next((x for x in d if "Districtwide" in str(x.get("raceTitle", ""))), d[-1] if d else None)
    if not isinstance(d, dict) or not d.get("candidates"):
        return None
    cands = sorted(((_n(c.get("Votes")), str(c.get("Party") or "")) for c in d["candidates"]), reverse=True)
    total = sum(v for v, _ in cands)
    if total <= 0 or len(cands) < 2:
        return None
    meme = cands[0][1] == cands[1][1]
    # La règle compte la marge entre les DEUX PREMIERS, quel que soit le parti du second (CA-06, 17/11 : démocrate contre un sans-parti
    # « NPP » ; prendre le premier républicain donnait 0 voix en face et 58,9 points au lieu de 17,76). « d » = voix du premier si c'est un
    # démocrate, sinon du second ; « r » = l'autre des deux premiers : d − r est la marge signée (positive si un démocrate mène).
    (v1, p1), (v2, _) = cands[0], cands[1]
    autre = not (p1.startswith("Dem") or p1.startswith("Rep"))
    dem, rep = (v1, v2) if p1.startswith("Dem") else (v2, v1)
    # Contrôle croisé avec les pourcentages publiés par l'API (arrondis au dixième) : écart des deux premiers.
    pcts = sorted((float(str(c.get("Percent") or "nan").replace(",", ".")) for c in d["candidates"]), reverse=True)
    ecart_api = pcts[0] - pcts[1] if len(pcts) >= 2 and not any(math.isnan(x) for x in pcts[:2]) else None
    return {"heure": str(d.get("ReportingTime") or ""), "d": dem, "r": rep, "total": total, "meme_parti": meme,
            "autre_en_tete": autre, "ecart_api": ecart_api}


def fetch_californie(http: HttpClient, now: datetime, districts=DISTRICTS) -> list[dict]:
    rows = []
    for n in districts:
        try:
            x = lire(http.get_json(API.format(n=n)))
        except SourceUnavailable:
            continue
        if x is not None:
            rows.append(dict(x, district=n, lu=now.isoformat()))
    if not rows:
        raise SourceUnavailable("api.sos.ca.gov : aucun district lu")
    return rows


def journal(old: list[dict], rows: list[dict], keep: int = 4) -> list[dict]:
    """Garde les `keep` derniers relevés DISTINCTS (heure officielle) de chaque district : la marge des bulletins comptés entre deux."""
    out = list(old or [])
    seen = {(h["district"], h["heure"]) for h in out}
    for r in rows:
        if (r["district"], r["heure"]) not in seen:
            out.append({k: r[k] for k in ("district", "heure", "d", "r", "total", "lu")})
            seen.add((r["district"], r["heure"]))
    par = {}
    for h in out:
        par.setdefault(h["district"], []).append(h)
    return [h for n in sorted(par) for h in sorted(par[n], key=lambda h: h["lu"])[-keep:]]


def marge_tardive(hist: list[dict], district: int) -> tuple[float, int] | None:
    """Marge signée (D − R, points) des bulletins comptés entre les deux derniers relevés distincts, et leur nombre."""
    hs = sorted((h for h in hist or [] if h["district"] == district), key=lambda h: h["lu"])
    if len(hs) < 2:
        return None
    a, b = hs[-2], hs[-1]
    ajout = b["total"] - a["total"]
    dd, dr = b["d"] - a["d"], b["r"] - a["r"]
    if ajout < MIN_AJOUT or dd < 0 or dr < 0 or dd + dr > ajout:
        return None   # voix qui baissent ou plus de voix aux deux premiers qu'au total : relevés incomparables (calcul d'avant le 17/11)
    return 100.0 * ((b["d"] - a["d"]) - (b["r"] - a["r"])) / ajout, ajout


def chance(s0: float, mu: float, lo: float, hi: float, r_med: float = R_MED, r_sigma: float = R_SIGMA,
           sd: float = SD_TARDIVE) -> float:
    """P(marge finale signée dans [lo ; hi[) ; s = (s0 + m r) / (1 + r), m ~ N(mu, sd), r log-normale."""
    tot = 0.0
    for z in _Z:
        r = r_med * math.exp(r_sigma * z)

        def au_dessus(b: float) -> float:   # P(s >= b)
            if b == -math.inf:
                return 1.0
            if b == math.inf:
                return 0.0
            seuil = (b * (1 + r) - s0) / r
            return 1 - _phi((seuil - mu) / sd)
        tot += au_dessus(lo) - au_dessus(hi)
    return min(max(tot / len(_Z), 0.0), 1.0)


def attach_marges(markets, db, now: datetime, max_age_hours: float = 3.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    from polymarket_agent.sources._util import parse_date
    seen, rows = _load(db, "ref:marges_ca")
    if seen is None or not rows or (now - seen).total_seconds() > max_age_hours * 3600:
        return 0
    hist = _load(db, "marges_ca:histo")[1] or []
    par = {r["district"]: r for r in rows}
    n = 0
    for m in markets:
        q = question(m.question or "")
        if q is None or [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        district, party, lo, hi = q
        r = par.get(district)
        if r is None or r.get("meme_parti") or r.get("autre_en_tete"):
            continue
        s0 = 100.0 * (r["d"] - r["r"]) / r["total"]
        if r.get("ecart_api") is not None and abs(abs(s0) - r["ecart_api"]) > 0.5:
            continue   # notre marge ne redonne pas l'écart des pourcentages officiels : lecture fausse, pas de chance donnée
        tard = marge_tardive(hist, district)
        mu = tard[0] if tard else s0
        # tranche du parti : D « a-b » = s dans [a ; b[ ; R « a-b » = s dans ]−b ; −a] (borne de mesure nulle)
        a, b = (lo, hi) if party == "D" else (-hi, -lo)
        if party == "R" and lo == 0.0:
            b = 0.0
        if party == "D" and lo == 0.0:
            a = 1e-9
        p = chance(s0, mu, a, b)
        lu = parse_date(r.get("lu") or "") or seen
        m.references = dict(m.references or {}, marges_ca={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": lu.isoformat(),
            "titre": (f"CA-{district} {party} {lo:g}-{hi:g} : marge D−R {s0:+.2f} sur {r['total']} voix ({r['heure']}), "
                      f"bulletins tardifs {('%+.1f sur %d' % tard) if tard else 'inconnus'} : {p:.3f}")})
        n += 1
    return n
