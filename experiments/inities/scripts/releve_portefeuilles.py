"""Étape 3 : âge et étendue des gros acheteurs (≥ 300 $ sur un jeton avant que la réponse soit publique, 14 derniers jours).
Pour chacun : première activité (`/activity?sortBy=TIMESTAMP&sortDirection=ASC&limit=1`) et nombre de marchés échangés
(`/traded`, compté AUJOURD'HUI : léger regard vers le futur, un compte resté concentré l'était aussi à l'époque).

Usage : .venv/bin/python experiments/inities/scripts/releve_portefeuilles.py
Sortie : experiments/inities/donnees/portefeuilles.json.gz
"""

from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from analyse_commun import charger
from commun import DATA, DONNEES, ecrire_gz, http, lire_gz
from familles import famille

FENETRE, SEUIL = 14 * 86400, 300.0


def candidats() -> set[str]:
    out = set()
    for e in lire_gz(DONNEES / "evenements.json.gz"):
        fam = famille(e["title"])
        if not fam:
            continue
        ev = charger(e, fam)
        if ev is None:
            continue
        achats = defaultdict(float)
        for t, w, jeton, cote, p, parts, *_ in ev.echanges:
            if cote == "BUY" and ev.public - FENETRE <= t < ev.public:
                achats[(w, jeton)] += p * parts
        out |= {w for (w, _), usd in achats.items() if usd >= SEUIL}
    return out


def profil(w: str) -> tuple[str, dict]:
    out = {}
    try:
        r = http().get_json(f"{DATA}/traded", params={"user": w})
        out["marches"] = int(r.get("traded")) if isinstance(r, dict) and r.get("traded") is not None else None
    except Exception:  # noqa: BLE001
        out["marches"] = None
    try:
        a = http().get_json(f"{DATA}/activity", params={"user": w, "limit": 1, "sortBy": "TIMESTAMP", "sortDirection": "ASC"})
        out["premiere"] = int(a[0]["timestamp"]) if isinstance(a, list) and a else None
    except Exception:  # noqa: BLE001
        out["premiere"] = None
    return w, out


def main() -> None:
    connus = lire_gz(DONNEES / "portefeuilles.json.gz") or {}
    todo = sorted(candidats() - set(connus))
    print(f"{len(connus)} portefeuilles déjà connus, {len(todo)} à interroger", flush=True)
    with ThreadPoolExecutor(6) as pool:
        for i, (w, p) in enumerate(pool.map(profil, todo), 1):
            connus[w] = p
            if i % 500 == 0:
                ecrire_gz(DONNEES / "portefeuilles.json.gz", connus)
                print(f"  {i}/{len(todo)}", flush=True)
    ecrire_gz(DONNEES / "portefeuilles.json.gz", connus)
    print("fini", len(connus))


if __name__ == "__main__":
    main()
