"""Lecture d'un événement relevé : jetons, gagnants, instant où la réponse devient publique, achats avant cet instant."""

from __future__ import annotations

import json
from dataclasses import dataclass, field

from commun import DONNEES, NOM_PAR_DEFAUT, lire_gz

PUBLIC_PRIX = 0.95   # la réponse est publique quand le gagnant s'échange à 0,95 ou plus…
PUBLIC_TENU = 0.90   # … et ne redescend plus sous 0,90


@dataclass
class Evenement:
    id: str
    titre: str
    famille: str
    jetons: dict = field(default_factory=dict)   # jeton → {"marche", "question", "issue", "gagne", "frais"}
    echanges: list = field(default_factory=list)  # [ts, portefeuille, jeton, côté, prix, parts, condition, nom], triés
    public: int | None = None                     # instant où la réponse devient publique (ou la fin des échanges)


def frais_du_marche(m: dict) -> float:
    if not m.get("feesEnabled"):
        return 0.0
    sched = m.get("feeSchedule") or {}
    if isinstance(sched, str):
        try:
            sched = json.loads(sched)
        except ValueError:
            sched = {}
    return float(sched.get("rate") or 0.0)


_PUBLIC: dict | None = None


def charger(e: dict, fam: str) -> Evenement | None:
    """Échanges des deux relevés (depuis le règlement, et avant l'instant public), sans doublon ; instant public lu dans
    l'historique des prix (releve_public.py) quand il existe, sinon dans les échanges."""
    global _PUBLIC
    if _PUBLIC is None:
        _PUBLIC = lire_gz(DONNEES / "public.json.gz") or {}
    rows = (lire_gz(DONNEES / "echanges" / f"{e['id']}.json.gz") or []) + (lire_gz(DONNEES / "echanges_avant" / f"{e['id']}.json.gz") or [])
    rows = list({(r[0], r[1], r[2], r[3], r[4], r[5]): r for r in rows}.values())
    if not rows:
        return None
    ev = Evenement(e["id"], e["title"], fam)
    for m in e["markets"]:
        try:
            toks, prix = json.loads(m.get("clobTokenIds") or "[]"), [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except (ValueError, TypeError):
            continue
        if len(toks) != 2 or len(prix) != 2 or sorted(prix) != [0.0, 1.0]:
            continue  # pas réglé net (50-50, en cours)
        for i, t in enumerate(toks):
            ev.jetons[str(t)] = {"marche": str(m.get("id")), "question": m.get("question") or m.get("groupItemTitle") or "",
                                 "issue": i, "gagne": prix[i] == 1.0, "frais": frais_du_marche(m)}
    ev.echanges = sorted((r for r in rows if r[2] in ev.jetons and r[4] > 0), key=lambda r: r[0])
    if not ev.echanges:
        return None
    ev.public = _PUBLIC.get(e["id"]) or instant_public(ev)
    return ev


def instant_public(ev: Evenement) -> int:
    """Premier instant où un jeton GAGNANT s'échange à ≥ 0,95 sans redescendre sous 0,90 ensuite (la nouvelle est sortie) ;
    sinon la fin des échanges. Les signaux et les achats simulés doivent venir AVANT."""
    par_jeton: dict[str, list] = {}
    for r in ev.echanges:
        par_jeton.setdefault(r[2], []).append((r[0], r[4]))
    candidats = []
    for jeton, pts in par_jeton.items():
        if not ev.jetons[jeton]["gagne"]:
            continue
        debut = None
        for t, p in pts:
            if p >= PUBLIC_PRIX and debut is None:
                debut = t
            elif p < PUBLIC_TENU:
                debut = None
        if debut is not None:
            candidats.append(debut)
    return min(candidats) if candidats else ev.echanges[-1][0]


def creation_par_nom(nom: str) -> int | None:
    m = NOM_PAR_DEFAUT.match(nom or "")
    return int(m.group(1)) // 1000 if m else None
