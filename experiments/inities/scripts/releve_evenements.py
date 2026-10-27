"""Étape 1 : événements RÉGLÉS des familles « à initiés » (une poignée de personnes connaît la réponse avant le public :
jurys, comités, entreprises, émissions enregistrées, choix d'équipes). Gamma `/public-search`, pages de 50.

Usage : .venv/bin/python experiments/inities/scripts/releve_evenements.py [AAAA-MM-JJ début]
Sortie : experiments/inities/donnees/evenements.json.gz
"""

from __future__ import annotations

import sys
from concurrent.futures import ThreadPoolExecutor

from commun import DONNEES, GAMMA, ecrire_gz, http

MOTS = [
    # prix et classements décidés par un jury ou un comité
    "Ballon d'Or", "Nobel", "Person of the Year", "Oscar", "Oscars", "Academy Awards", "Grammy", "Grammys", "Emmy", "Emmys",
    "Golden Globe", "BAFTA", "Tony Award", "Palme d'Or", "Cannes", "Golden Boy", "Kopa", "The Best FIFA", "Laureus",
    "Booker Prize", "Pulitzer", "Game Awards", "Game of the Year", "MVP", "Cy Young", "Heisman", "Rookie of the Year",
    "Coach of the Year", "Defensive Player of the Year", "Hart Trophy", "Vezina", "Calder", "Norris", "TIME 100",
    "Word of the Year", "Pantone", "Michelin", "Golden Raspberry", "Miss Universe", "Mr. Olympia",
    # chiffres d'entreprises connus en interne
    "searched", "Year in Search", "Spotify", "Wrapped", "Billboard", "most streamed", "App Store", "halftime show",
    "Eurovision", "Apple event", "announce", "release date", "GTA",
    # émissions enregistrées à l'avance
    "Survivor", "Bachelor", "Bachelorette", "Love Island", "Big Brother", "Traitors", "Masked Singer", "Dancing with the Stars",
    "The Voice", "American Idol", "Top Chef", "Drag Race", "Beast Games", "MrBeast",
    # choix d'une petite équipe
    "draft", "first pick", "No. 1 pick", "Pope", "conclave", "running mate", "nominee", "nominate", "Fed chair", "cabinet",
    "pardon", "host city", "Olympics host",
]
CHAMPS_MARCHE = ("id", "question", "groupItemTitle", "conditionId", "clobTokenIds", "outcomes", "outcomePrices", "closed",
                 "closedTime", "endDate", "feesEnabled", "feeSchedule", "feeType", "volumeNum", "umaResolutionStatuses")


def chercher(mot: str, debut: str) -> list[dict]:
    out = []
    for page in range(1, 11):
        try:
            r = http().get_json(f"{GAMMA}/public-search", params={"q": mot, "events_status": "closed",
                                                                 "limit_per_type": 50, "page": page})
        except Exception:  # noqa: BLE001 - une page en panne n'arrête pas le relevé
            break
        evs = r.get("events") or []
        for e in evs:
            if str(e.get("endDate") or "") >= debut and e.get("closed"):
                out.append({"id": str(e["id"]), "slug": e.get("slug"), "title": e.get("title"), "endDate": e.get("endDate"),
                            "createdAt": e.get("createdAt"), "volume": float(e.get("volume") or 0), "mot": mot,
                            "tags": [t.get("label") for t in e.get("tags") or [] if isinstance(t, dict)],
                            "markets": [{k: m.get(k) for k in CHAMPS_MARCHE} for m in e.get("markets") or []]})
        if not (r.get("pagination") or {}).get("hasMore"):
            break
    return out


def main() -> None:
    debut = sys.argv[1] if len(sys.argv) > 1 else "2025-09-01"
    with ThreadPoolExecutor(6) as pool:
        lots = list(pool.map(lambda m: chercher(m, debut), MOTS))
    evenements = {}
    for mot, lot in zip(MOTS, lots):
        for e in lot:
            evenements.setdefault(e["id"], e)
        print(f"{mot:28s} {len(lot):4d}")
    ecrire_gz(DONNEES / "evenements.json.gz", list(evenements.values()))
    marches = sum(len(e["markets"]) for e in evenements.values())
    print(f"{len(evenements)} événements réglés depuis le {debut}, {marches} marchés")


if __name__ == "__main__":
    main()
