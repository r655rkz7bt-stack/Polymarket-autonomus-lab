"""Étape 2 : échanges réels (preneurs) de chaque événement « à initiés », en remontant le temps depuis le règlement
(data-api `/trades?eventId=…&end=…`, pages de 1 000) jusqu'à 21 jours avant, 30 pages au plus par événement.

Usage : .venv/bin/python experiments/inities/scripts/releve_echanges.py
Sortie : experiments/inities/donnees/echanges/<événement>.json.gz
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

from commun import DATA, DONNEES, ecrire_gz, http, lire_gz
from familles import famille

DOSSIER = DONNEES / "echanges"
JOURS, PAGES = 21, 30


def ts(texte: str | None) -> int | None:
    if not texte:
        return None
    try:
        return int(datetime.fromisoformat(str(texte).replace("Z", "+00:00").replace(" ", "T").split("+")[0] + "+00:00").timestamp())
    except ValueError:
        return None


def relever(e: dict) -> tuple[str, int]:
    path = DOSSIER / f"{e['id']}.json.gz"
    if path.exists():
        return e["id"], -1
    fins = [t for t in (ts(m.get("closedTime")) for m in e["markets"]) if t]
    fin = (max(fins) if fins else ts(e.get("endDate")) or 0) + 3600
    debut = fin - JOURS * 86400
    rows, vus, curseur = [], set(), fin
    for _ in range(PAGES):
        try:
            lot = http().get_json(f"{DATA}/trades", params={"eventId": e["id"], "limit": 1000, "end": curseur})
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
    return e["id"], len(rows)


def main() -> None:
    evs = [e for e in lire_gz(DONNEES / "evenements.json.gz") if famille(e["title"]) and e["volume"] >= 1000]
    DOSSIER.mkdir(parents=True, exist_ok=True)
    print(f"{len(evs)} événements à relever")
    faits = 0
    with ThreadPoolExecutor(6) as pool:
        for eid, n in pool.map(relever, evs):
            faits += 1
            if faits % 50 == 0:
                print(f"  {faits}/{len(evs)}", flush=True)
    print("fini")


if __name__ == "__main__":
    main()
