"""Pistes n° 4 et 5, étape 2 : INVENTAIRE des marchés liés (existent-ils, depuis quand, avec quel volume ?).
Pour chaque série relevée : par mois, nombre de matchs réglés qui ont un marché « vainqueur » ET au moins un marché lié
(carte / set 1, handicap, total), et volume médian de ces marchés liés. Aucun appel réseau.
Usage : python experiments/bo3_coherence/inventaire.py cs2 lol dota2 val atp wta"""
import collections
import gzip
import json
import statistics
import sys
from pathlib import Path

D = Path(__file__).resolve().parent / "donnees"
LIES = {"child_moneyline", "map_handicap", "totals", "tennis_first_set_winner", "tennis_set_winner", "tennis_set_handicap",
        "tennis_set_totals"}
for nom in sys.argv[1:]:
    evs = json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes()))
    types = collections.Counter(m.get("sportsMarketType") for e in evs for m in e["markets"])
    print(f"== {nom} : {len(evs)} événements réglés ; types de marchés : {dict(types.most_common(12))}")
    par_mois = collections.defaultdict(lambda: collections.Counter())
    vol = collections.defaultdict(list)
    for e in evs:
        ml = [m for m in e["markets"] if m.get("sportsMarketType") == "moneyline"]
        lies = [m for m in e["markets"] if m.get("sportsMarketType") in LIES]
        mois = (ml[0].get("gameStartTime") or e.get("endDate") or "")[:7] if ml else (e.get("endDate") or "")[:7]
        par_mois[mois]["matchs"] += 1
        if ml and lies:
            par_mois[mois]["avec_lies"] += 1
            if any((m.get("volumeNum") or 0) >= 20 for m in lies):
                par_mois[mois]["lies_volume_20"] += 1
        for m in lies:
            vol[m.get("sportsMarketType")].append(m.get("volumeNum") or 0)
    for mois in sorted(par_mois):
        c = par_mois[mois]
        print(f"   {mois} : {c['matchs']:5d} matchs, {c['avec_lies']:5d} avec marchés liés, {c['lies_volume_20']:5d} dont un lié à ≥ 20 $")
    for t, v in vol.items():
        print(f"   volume {t:26s} n={len(v):6d}  médiane {statistics.median(v):9.0f} $  moyenne {statistics.mean(v):9.0f} $  part > 0 : {sum(1 for x in v if x > 0) / len(v):.0%}")
