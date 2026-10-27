"""Étape 2 bis : instant où la réponse devient publique, lu dans l'historique des prix du CLOB (pas dans les échanges : les
30 pages relevées depuis le règlement par releve_echanges.py sont, pour un gros événement, toutes APRÈS l'annonce).
Public = premier instant où le jeton GAGNANT du marché le plus échangé cote ≥ 0,95 sans redescendre sous 0,90 ensuite.

Usage : .venv/bin/python experiments/inities/scripts/releve_public.py
Sortie : experiments/inities/donnees/public.json.gz  {événement: instant (s)}
"""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor

from commun import DONNEES, ecrire_gz, http, lire_gz
from familles import famille
from releve_echanges import ts

CLOB = "https://clob.polymarket.com/prices-history"


def gagnant(e: dict) -> tuple[str, int] | None:
    best = None
    for m in e["markets"]:
        try:
            toks, prix = json.loads(m.get("clobTokenIds") or "[]"), [float(x) for x in json.loads(m.get("outcomePrices") or "[]")]
        except (ValueError, TypeError):
            continue
        if len(toks) == 2 and sorted(prix) == [0.0, 1.0] and prix[0] == 1.0:  # un OUI gagnant
            fin = ts(m.get("closedTime")) or ts(e.get("endDate"))
            vol = float(m.get("volumeNum") or 0)
            if fin and (best is None or vol > best[2]):
                best = (str(toks[0]), fin, vol)
    return (best[0], best[1]) if best else None


def public(e: dict) -> tuple[str, int | None]:
    g = gagnant(e)
    if g is None:
        return e["id"], None
    jeton, fin = g
    pts = []
    for a in range(fin - 60 * 86400, fin + 86400, 13 * 86400):
        try:
            r = http().get_json(CLOB, params={"market": jeton, "startTs": a, "endTs": min(a + 13 * 86400, fin + 86400), "fidelity": 60})
            pts += r.get("history") or []
        except Exception:  # noqa: BLE001
            continue
    debut = None
    for p in sorted(pts, key=lambda x: x["t"]):
        if p["p"] >= 0.95 and debut is None:
            debut = int(p["t"])
        elif p["p"] < 0.90:
            debut = None
    return e["id"], debut


def main() -> None:
    evs = [e for e in lire_gz(DONNEES / "evenements.json.gz") if famille(e["title"]) and e["volume"] >= 1000]
    with ThreadPoolExecutor(6) as pool:
        out = dict(pool.map(public, evs))
    ecrire_gz(DONNEES / "public.json.gz", out)
    print(f"{sum(1 for v in out.values() if v)} instants publics sur {len(out)} événements")


if __name__ == "__main__":
    main()
