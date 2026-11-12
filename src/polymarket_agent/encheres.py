"""Ventes aux enchères : « <artiste>'s “<œuvre>” Sale Price » (tranches de prix, Polymarket) contre l'estimation de la maison (12/11/2026).

Les marchés se règlent sur le prix final affiché par la maison (frais d'acheteur compris) ; un lot retiré ou invendu tombe dans la
tranche la plus basse. Sur 41 gros lots (estimation basse >= 10 M$) des ventes du soir de Christie's à New York, octobre 2020 -
mai 2026 (experiments/encheres.md), le prix final vaut 1,16 fois l'estimation basse en médiane, 80 % entre 1,04 et 1,53 ;
3 invendus (aucun garanti). Chance d'une tranche = part des rapports passés qui y tombent ; lot garanti : pas d'invendu, mais un
risque de retrait `P_RETRAIT` compté dans la tranche la plus basse. Les lots suivis et leur estimation sont écrits par le chercheur
dans `config/encheres.yaml` (estimation lue sur la page du lot de la maison) ; aucun achat le jour de la vente (après le marteau,
le marché connaît le résultat).
"""

from __future__ import annotations

import logging
import re
from datetime import date, datetime
from pathlib import Path

import yaml

log = logging.getLogger(__name__)

TABLE = Path(__file__).resolve().parents[2] / "config" / "encheres.yaml"
P_RETRAIT = 0.02
# Prix final / estimation basse des 38 gros lots vendus (Christie's, ventes du soir de New York, 2020-2026 ; experiments/encheres/analyse.py)
RATIOS = (0.801, 0.962, 0.992, 1.042, 1.054, 1.083, 1.083, 1.087, 1.105, 1.109, 1.113, 1.129, 1.136, 1.137, 1.137, 1.139, 1.147,
          1.151, 1.153, 1.158, 1.163, 1.165, 1.171, 1.177, 1.191, 1.214, 1.214, 1.278, 1.307, 1.331, 1.361, 1.395, 1.432, 1.442,
          1.478, 2.034, 2.151, 2.177)
INVENDUS = 3   # sur 41 lots (aucun garanti)

_MONTANT = r"\$?\s*([0-9]+(?:\.[0-9]+)?)\s*([mk]?)"


def _m(x: str, unite: str) -> float:
    return float(x) * (1e-3 if unite == "k" else 1.0)


def tranche(titre: str) -> tuple[float, float] | None:
    """« <$60m » → (0, 60) ; « $60m-$75m » → (60, 75) ; « $105m+ » → (105, inf), en millions de dollars."""
    t = (titre or "").strip().lower().replace("–", "-").replace(",", "")
    if m := re.fullmatch(r"<\s*" + _MONTANT, t):
        return 0.0, _m(m.group(1), m.group(2))
    if m := re.fullmatch(_MONTANT + r"\s*\+", t):
        return _m(m.group(1), m.group(2)), float("inf")
    if m := re.fullmatch(_MONTANT + r"\s*-\s*" + _MONTANT, t):
        return _m(m.group(1), m.group(2)), _m(m.group(3), m.group(4))
    return None


def p_tranche(basse: float, lo: float, hi: float, garanti: bool, plus_basse: bool,
              ratios=RATIOS, invendus: int = INVENDUS, p_retrait: float = P_RETRAIT) -> float:
    """Chance que le prix final (estimation basse × rapport passé) tombe dans [lo ; hi[ ; invendus et retraits dans la plus basse."""
    n = len(ratios) + (0 if garanti else invendus)
    p = sum(1 for r in ratios if lo <= r * basse < hi) / n
    if plus_basse and not garanti:
        p += invendus / n
    p *= 1 - p_retrait
    return p + (p_retrait if plus_basse else 0.0)


def lots(path: Path | None = None) -> dict[str, dict]:
    """Lots suivis, par identifiant d'événement Gamma ; une ligne mal formée est ignorée (journalisée)."""
    path = path or TABLE
    if not Path(path).exists():
        return {}
    try:
        raw = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError) as exc:
        log.warning("encheres.yaml illisible : %s", exc)
        return {}
    out = {}
    for l in raw.get("lots") or []:
        try:
            out[str(l["evenement"])] = {**l, "estimation_basse": float(l["estimation_basse"]), "garanti": bool(l.get("garanti")),
                                        "vente": date.fromisoformat(str(l["vente"]))}
        except (KeyError, TypeError, ValueError) as exc:
            log.warning("lot d'enchères ignoré (%s) : %s", exc, l)
    return out


def attach_encheres(markets, db, now: datetime, path: Path | None = None) -> int:
    """Référence `encheres` sur chaque tranche d'un lot suivi, jusqu'à la veille de la vente (jour de la vente : rien)."""
    suivis = lots(path)
    if not suivis:
        return 0
    par_evenement: dict[str, list] = {}
    for m in markets:
        if str(m.event_id) in suivis and [str(o).lower() for o in m.outcomes] == ["yes", "no"]:
            par_evenement.setdefault(str(m.event_id), []).append(m)
    n = 0
    for ev, ms in par_evenement.items():
        lot = suivis[ev]
        if now.date() >= lot["vente"]:
            continue
        bornes = {m.market_id: tranche(m.group_title) for m in ms}
        if any(b is None for b in bornes.values()):
            continue
        plus_basse = min(b[0] for b in bornes.values())
        for m in ms:
            lo, hi = bornes[m.market_id]
            p = p_tranche(lot["estimation_basse"], lo, hi, lot["garanti"], lo == plus_basse)
            m.references = dict(m.references or {}, encheres={
                "p": round(p, 4), "p_dedup": round(p, 4), "p_rapide": round(p, 4), "vu_le": now.isoformat(),
                "titre": f"{lot.get('nom', ev)} : estimation basse {lot['estimation_basse']:g} M$, tranche {m.group_title} : {p:.3f}"})
            n += 1
    return n
