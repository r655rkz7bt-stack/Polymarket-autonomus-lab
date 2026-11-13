"""Échelles de seuils d'un même événement (13/11/2026, piste n° 47, experiments/echelles_seuils.md).

« Will US unemployment reach at least 6.0% in 2026? » et « … at least 7.0% … » ne diffèrent que par le nombre : atteindre 7 % implique
atteindre 6 %, donc P(7 %) ≤ P(6 %). NON(7 %) + OUI(6 %) paie toujours au moins 1. Même chose vers le bas (« dip below 4.00% » implique
« dip below 4.50% »). Regroupement : même événement, même question une fois le nombre remplacé par « # », sens lu dans la phrase ; toute
question ambiguë (« between », deux nombres, mots des deux sens) est écartée.
"""
from __future__ import annotations

import re
from collections import defaultdict

_NUM = re.compile(r"(?<![\w.])[$€£]?(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)\s*(k|m|b|%|bps)?(?![\w.])", re.IGNORECASE)
# « hit » / « reach » ne disent PAS le sens (13/11 : « Trump's approval rating hit 30 % » est une barrière vers le bas, « hit 45 % » vers
# le haut, même phrase) : seuls les mots sans ambiguïté comptent.
_HAUT = re.compile(r"(\bat least\b|\bor above\b|\bor higher\b|\bor more\b|\babove\b|\bgreater than\b|\bexceeds?\b|\(HIGH\))", re.IGNORECASE)
_BAS = re.compile(r"(\bdip below\b|\bbelow\b|\bunder\b|\bless than\b|\bor lower\b|\bor less\b|\(LOW\))", re.IGNORECASE)
_EXCLU = re.compile(r"\b(between|exactly|closes? (?:at|between)|range|up or down|on \w+ \d{1,2}\b.*\bclose)", re.IGNORECASE)
_MULT = {"k": 1e3, "m": 1e6, "b": 1e9}


def seuil(question: str) -> tuple[str, float, bool] | None:
    """(modèle de la question, nombre, vers le haut ?) ; None si la question n'est pas un seuil simple et sans ambiguïté."""
    q = question or ""
    if _EXCLU.search(q):
        return None
    nums = list(_NUM.finditer(q))
    # années et dates : pas des seuils (« in 2026 », « by December 31 »)
    vals = [g for g in nums if not (g.group(2) is None and re.fullmatch(r"(19|20)\d\d", g.group(1)))
            and not re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s*$",
                              q[:g.start()], re.IGNORECASE)]
    if len(vals) != 1:
        return None
    g = vals[0]
    haut, bas = bool(_HAUT.search(q)), bool(_BAS.search(q))
    if haut == bas:
        return None
    v = float(g.group(1).replace(",", "")) * _MULT.get((g.group(2) or "").lower(), 1.0)
    modele = q[:g.start()] + "#" + q[g.end():]
    return modele, v, haut


def paires(markets) -> list[tuple]:
    """[(marché du seuil le plus FACILE, marché du seuil le plus DIFFICILE, modèle)] pour chaque paire d'une même échelle.
    Facile = plus bas vers le haut (ou plus haut vers le bas) : P(difficile) ≤ P(facile)."""
    groups = defaultdict(list)
    for m in markets:
        if [str(o).lower() for o in getattr(m, "outcomes", [])] != ["yes", "no"] or not getattr(m, "event_id", None):
            continue
        s = seuil(m.question or "")
        if s is not None:
            groups[(m.event_id, s[0], s[2])].append((s[1], m))
    out = []
    for (ev, modele, haut), items in groups.items():
        items.sort(key=lambda x: x[0])
        if len({v for v, _ in items}) < 2:
            continue
        for i, (va, a) in enumerate(items):
            for vb, b in items[i + 1:]:
                if vb == va:
                    continue
                facile, difficile = (a, b) if haut else (b, a)
                # Fenêtre « depuis la création du marché » (Freddie Mac, 13/11/2026) : l'implication ne tient que si le seuil facile
                # compte depuis au moins aussi longtemps et jusqu'à la même date que le difficile.
                cf, cd = getattr(facile, "created_at", None), getattr(difficile, "created_at", None)
                if cf is None or cd is None or (cf - cd).total_seconds() > 86400:
                    continue
                if getattr(facile, "end_date", None) != getattr(difficile, "end_date", None):
                    continue
                out.append((facile, difficile, modele))
    return out
