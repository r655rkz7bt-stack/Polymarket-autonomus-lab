"""El Niño : les chances chiffrées du prévisionniste officiel (CPC de la NOAA) contre les marchés « peak RONI » (12/11/2026,
piste n° 39, experiments/el_nino.md).

Les marchés « What will the peak RONI be for the 2026–27 El Niño? » (5 tranches), « Will the 2026–27 El Niño be the strongest on
record? » (> 2,40) se règlent sur la RONI publiée par le CPC (première valeur de chaque saison de 3 mois, ASO à DJF). Le même CPC
publie chaque mois (2e jeudi) sa discussion ENSO, qui donne la chance qu'une saison atteigne un seuil (« +2.5°C or more for a
3-month RONI value: the chance is 54% for September-November, 83% for October-December, and 70% for November-January »).

Ce que ces chances prouvent, sans modèle à nous : P(pic >= T) >= max des saisons de P(saison >= T) = L(T). Donc
- marché « pic >= a » (ou « > a ») avec a <= T : P(OUI) >= L(T) ;
- marché « pic < b » ou « a <= pic < b » avec b <= T : P(NON) >= L(T).
On n'achète que le côté borné. Une discussion de plus de `max_age_days` jours n'est pas utilisée (le 12/11 au matin, celle du 08/10
était périmée : la RONI d'ASO, 2,0, est sortie sous la trajectoire qu'elle supposait).
"""
from __future__ import annotations

import html
import re
from datetime import datetime, timezone

from polymarket_agent.http_client import HttpClient

PAGE = "https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso_advisory/ensodisc.shtml"
RONI = "https://www.cpc.ncep.noaa.gov/data/indices/RONI.ascii.txt"
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
_DATE = re.compile(r"\b(\d{1,2}) (" + "|".join(MOIS) + r") (\d{4})\b")
_SEUIL = re.compile(r"(?:\+|≥\s?\+?)(\d\.\d)\s*°C(?: or (?:more|greater|higher|above))?(?=[\s),;])")
_PHRASE = re.compile(r"(?<=[.)])\s+(?=[A-Z])")
_SAISON = "(" + "|".join(MOIS) + r")-(" + "|".join(MOIS) + ")"
# Deux tournures relevées : « …(+2.5°C or more …): the chance is 54% for September-November, 83% for October-December… » (08/10/2026)
# et « During the October-December 2026 season, there is a 69% chance of a historic event … (+2.5°C or more …) » (13/08, 10/09/2026).
# Troisième (12/11/2026) : « … (+2.5°C or more for a 3-month RONI value ) are now ~60% for the October-December and November-January
# periods » : « the », et une seule chance pour deux saisons.
_CHANCE_POUR = re.compile(r"(\d{1,3})\s?%\s+for\s+(?:the\s+)?" + _SAISON + r"(?:\s+and\s+(?:the\s+)?" + _SAISON + ")?")
_DURANT = re.compile(r"During the " + _SAISON + r"(?: \d{4}(?:-\d{2,4})?)? season, there is an? (\d{1,3})\s?% chance")


def _texte(page: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page or "")))


def parse_discussion(page: str) -> dict | None:
    """{"emis": "AAAA-MM-JJ", "seuils": {"2.5": {"Oct-Dec": 0.83, …}}} ou None (page illisible)."""
    x = _texte(page)
    emis = None
    for g in _DATE.finditer(x):
        if "scheduled for" in x[max(0, g.start() - 40):g.start()]:
            continue  # date de la PROCHAINE discussion
        emis = datetime(int(g.group(3)), MOIS.index(g.group(2)) + 1, int(g.group(1)), tzinfo=timezone.utc)
        break
    if emis is None:
        return None
    seuils: dict[str, dict[str, float]] = {}
    for phrase in _PHRASE.split(x):
        t = _SEUIL.search(phrase)
        if not t or "RONI" not in phrase:
            continue  # les marchés se règlent sur la RONI : une chance sur le Niño-3.4 classique (discussions de 2023) ne borne rien
        ch = {}
        for p, a, b, c, d in _CHANCE_POUR.findall(phrase):
            ch[f"{a[:3]}-{b[:3]}"] = int(p) / 100
            if c:
                ch[f"{c[:3]}-{d[:3]}"] = int(p) / 100
        ch.update({f"{a[:3]}-{b[:3]}": int(p) / 100 for a, b, p in _DURANT.findall(phrase)})
        if not ch:  # tournure libre : une seule chance et une seule saison dans la phrase (« 35% chance … (≥ 2.0°C) for the November-January season »)
            ps, ss = re.findall(r"(?<![\d-])(\d{1,3})(?:-\d{1,3})?\s?% chance", phrase), re.findall(_SAISON, phrase)  # « 75-85% » : 75
            if len(ps) == 1 and len(set(ss)) == 1:
                ch = {f"{ss[0][0][:3]}-{ss[0][1][:3]}": int(ps[0]) / 100}
        if ch:
            seuils.setdefault(t.group(1), {}).update(ch)
    return {"emis": emis.date().isoformat(), "seuils": seuils}


def parse_roni(text: str) -> list[tuple[str, int, float]]:
    out = []
    for line in (text or "").splitlines():
        p = line.split()
        if len(p) == 3 and p[1].isdigit():
            try:
                out.append((p[0], int(p[1]), float(p[2])))
            except ValueError:
                continue
    return out


def fetch_enso(http: HttpClient, now: datetime) -> list[dict]:
    d = parse_discussion(http.get_text(PAGE, headers={"User-Agent": "Mozilla/5.0"}))
    if d is None:
        return []
    roni = parse_roni(http.get_text(RONI, headers={"User-Agent": "Mozilla/5.0"}))
    return [dict(d, roni_dernier=list(roni[-1]) if roni else None, lu=now.isoformat())]


_Q_PIC = re.compile(r"^Will the peak RONI for the [\d–-]+ El Ni(?:ñ|n)o be (below ([\d.]+)|at least ([\d.]+) but below ([\d.]+)|([\d.]+) or above)\?",
                    re.IGNORECASE)
_Q_RECORD = re.compile(r"^Will the [\d–-]+ El Ni(?:ñ|n)o be the strongest on record\?", re.IGNORECASE)


def intervalle(question: str, description: str = "") -> tuple[float, float] | None:
    """(a, b) : le marché paie OUI si a <= pic < b (a exclu pour le record, sans effet sur les bornes utilisées)."""
    g = _Q_PIC.match(question or "")
    if g:
        if g.group(2):
            return (-1e9, float(g.group(2)))
        if g.group(3):
            return (float(g.group(3)), float(g.group(4)))
        return (float(g.group(5)), 1e9)
    if _Q_RECORD.match(question or ""):
        r = re.search(r"above \+?(\d\.\d+)\s*°C", description or "")
        return (float(r.group(1)) if r else 2.40, 1e9)
    return None


def borne(inter: tuple[float, float], seuils: dict[str, dict[str, float]]) -> tuple[int, float] | None:
    """(côté, borne basse de sa chance) : 0 = OUI, 1 = NON ; None si les chances du CPC ne bornent pas ce marché."""
    a, b = inter
    best = None
    for t, ch in seuils.items():
        t, low = float(t), max(ch.values())
        if b >= 1e9 and a <= t and (best is None or low > best[1]):
            best = (0, low)
        elif b <= t and (best is None or low > best[1]):
            best = (1, low)
    return best


def attach_enso(markets, db, now: datetime, max_age_days: float = 7.0) -> int:
    if db is None:
        return 0
    from polymarket_agent.references import _load
    seen, rows = _load(db, "ref:enso")
    if seen is None or not rows or not rows[0].get("seuils"):
        return 0
    row = rows[0]
    emis = datetime.fromisoformat(row["emis"]).replace(tzinfo=timezone.utc)
    if (now - emis).total_seconds() > max_age_days * 86400:
        return 0
    n = 0
    for m in markets:
        if [str(o).lower() for o in m.outcomes] != ["yes", "no"]:
            continue
        inter = intervalle(m.question or "", getattr(m, "description", "") or "")
        if inter is None:
            continue
        bn = borne(inter, row["seuils"])
        if bn is None:
            continue
        side, low = bn
        p = low if side == 0 else 1 - low
        m.references = dict(m.references or {}, enso={
            "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "cotes": [side], "vu_le": seen.isoformat(),
            "titre": f"CPC du {row['emis']} : {'OUI' if side == 0 else 'NON'} >= {low:.2f}"})
        n += 1
    return n
