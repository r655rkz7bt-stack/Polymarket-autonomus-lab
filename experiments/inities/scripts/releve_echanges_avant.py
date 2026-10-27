"""Étape 2 ter : échanges des 14 jours AVANT l'instant public (data-api `/trades?eventId=…&end=<public + 1 h>`, en remontant,
40 pages au plus). Sortie : experiments/inities/donnees/echanges_avant/<événement>.json.gz"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from commun import DATA, DONNEES, ecrire_gz, http, lire_gz
from familles import famille

DOSSIER = DONNEES / "echanges_avant"


def relever(item) -> int:
    eid, public = item
    path = DOSSIER / f"{eid}.json.gz"
    if path.exists() or not public:
        return 0
    debut, curseur, rows, vus = public - 14 * 86400, public + 3600, [], set()
    for _ in range(40):
        try:
            lot = http().get_json(f"{DATA}/trades", params={"eventId": eid, "limit": 1000, "end": curseur})
        except Exception:  # noqa: BLE001
            break
        if not isinstance(lot, list) or not lot:
            break
        for t in lot:
            cle = (t.get("transactionHash"), t.get("asset"), t.get("side"), t.get("size"), t.get("proxyWallet"))
            if cle in vus or not t.get("timestamp"):
                continue
            vus.add(cle)
            rows.append([int(t["timestamp"]), str(t.get("proxyWallet")), str(t.get("asset")), str(t.get("side")),
                         float(t.get("price") or 0), float(t.get("size") or 0), str(t.get("conditionId")), str(t.get("name") or "")])
        bas = min(int(t["timestamp"]) for t in lot if t.get("timestamp"))
        if len(lot) < 1000 or bas < debut or bas >= curseur:
            break
        curseur = bas
    ecrire_gz(path, rows)
    return len(rows)


def main() -> None:
    pub = lire_gz(DONNEES / "public.json.gz") or {}
    ids = {e["id"] for e in lire_gz(DONNEES / "evenements.json.gz") if famille(e["title"]) and e["volume"] >= 1000}
    todo = [(k, v) for k, v in pub.items() if k in ids and v]
    DOSSIER.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(6) as pool:
        total = sum(pool.map(relever, todo))
    print(f"{len(todo)} événements, {total} échanges avant l'instant public")


if __name__ == "__main__":
    main()
