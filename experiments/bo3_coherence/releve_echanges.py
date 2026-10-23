"""Pistes n° 4 et 5, étape 3 : échanges réels (data-api) d'un ÉCHANTILLON de matchs, tiré au hasard mois par mois.

Seuls les matchs BO3/BO5 avec un marché vainqueur et au moins un marché lié réglé, de volume > 0, sont tirés (un marché
sans aucun volume n'a aucun échange : il ne donnerait aucun pari). Tirage fixe (graine 7), au plus N matchs par mois
et par série, pour tenir dans le temps d'un passage. Cache : donnees/echanges/<id d'événement>.json.gz.
Usage : python experiments/bo3_coherence/releve_echanges.py <N par mois> cs2 lol dota2 val
        python experiments/bo3_coherence/releve_echanges.py <N par mois> atp wta"""
import gzip
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from echanges import en_parallele  # noqa: E402
from series import match_cas, jour  # noqa: E402

D = HERE / "donnees"
N = int(sys.argv[1])
noms = sys.argv[2:]
famille = "tennis" if set(noms) & {"atp", "wta", "itf"} else "esport"
par_mois = defaultdict(list)
for nom in noms:
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        ev["serie"] = nom
        cas = match_cas(ev, famille)
        if cas and any(li["vol"] > 0 for li in cas["lies"]):
            par_mois[(nom, jour(cas["start"])[:7])].append(cas["event"])
rng = random.Random(7)
listes = []
for k in sorted(par_mois):
    ids = sorted(par_mois[k])
    rng.shuffle(ids)
    listes.append(ids[:N])
# Ordre « tourniquet » (1er de chaque mois, puis 2e…) : si le relevé est interrompu, l'échantillon reste équilibré.
choisis = [lst[i] for i in range(N) for lst in listes if i < len(lst)]
print(famille, "matchs utilisables", sum(len(v) for v in par_mois.values()), "; tirés", len(choisis), flush=True)
(D / f"echantillon_{famille}.json").write_text(json.dumps(choisis))
res = en_parallele([(e, {"eventId": e}) for e in choisis], D / "echanges", fils=int(os.environ.get("FILS", "8")))
print("fini :", sum(1 for v in res.values() if v is not None), "événements lus,", sum(1 for v in res.values() if v is None), "en échec ;",
      sum(1 for v in res.values() if v and len(v) >= 11000), "tronqués (≥ 11 000 échanges)")
