"""Piste n° 4, contrôle du 25/10 : « Under » des totaux de cartes AVEC les règlements 50-50.

`series.regle` écartait les marchés réglés 0,5/0,5 (en silence). Le fantôme moins_de_cartes en a eu 4 sur 42 en direct
(25/10, enquête famille 2). Ici ils comptent : l'« Under » acheté est payé 0,5. Même code que sous_2_5.py (esport).
Usage : [LOT=2] python experiments/bo3_coherence/sous_2_5_50_50.py"""
import gzip
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["INCLURE_50_50"] = "1"
import series  # noqa: E402
from echanges import cout_preneur  # noqa: E402
from series import jour, resume, it  # noqa: E402

D = HERE / "donnees"
LOT = os.environ.get("LOT", "1")  # 1 : cs2 lol dota2 val (tirage du 25/10) ; 2 : autres jeux (hok mlbb codmw r6siege rl sc2 ow) ; 3 : hok mlbb codmw sc2 tirés plus largement (200 par mois)
NOMS = {"1": ["cs2", "lol", "dota2", "val"], "2": ["hok", "mlbb", "codmw", "r6siege", "rl", "sc2", "ow"], "3": ["hok", "mlbb", "codmw", "sc2"]}[LOT]
choisis = set(json.loads((D / f"echantillon_esport_lot{LOT}.json").read_text()))
cas_list = []
for nom in NOMS:
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        if str(ev["id"]) in choisis:
            ev["serie"] = nom
            c = series.match_cas(ev, "esport")
            p = D / "echanges" / f"{ev['id']}.json.gz"
            if c and p.exists():
                c["rows"] = json.loads(gzip.decompress(p.read_bytes()))
                cas_list.append(c)
jours = sorted({jour(c["start"]) for c in cas_list})
coupe = jours[len(jours) // 2]


def paris(h, fen, issue=1, inclure=True, mode="après"):
    out = []
    for c in cas_list:
        t0 = c["start"] - h * 3600
        for li in c["lies"]:
            if li["kind"] != "total" or (li["won"] == -1 and not inclure):
                continue
            got = cout_preneur(c["rows"], li["toks"][issue], li["toks"][1 - issue], t0, fen * 3600, apres=(mode == "après"), fin_max=c["start"])
            if not got or not 0.01 <= got[1] <= 0.99:
                continue
            paid = got[1] + it.fee(got[1], li["rate"])
            pay = 0.5 if li["won"] == -1 else float(li["won"] == issue)
            out.append({"gain": pay / paid - 1, "evenement": c["event"], "cout": paid, "win": pay,
                        "mois": jour(c["start"])[:7], "jour": jour(c["start"]), "serie": c["serie"], "bo": c["bo"], "n5050": li["won"] == -1})
    return out


tot = sum(1 for c in cas_list for li in c["lies"] if li["kind"] == "total")
n55 = sum(1 for c in cas_list for li in c["lies"] if li["kind"] == "total" and li["won"] == -1)
print(f"# {len(cas_list)} matchs, {tot} totaux réglés (50-50 compris : {n55} = {100 * n55 / max(tot, 1):.1f} %)")
print("| réglage | paris | matchs | rendement | t par match | mois gagnants | gagnés / attendus (z) | verdict |")
print("|---|---|---|---|---|---|---|---|")
for h in (1, 3, 6):
    for fen in (2, 6):
        print(resume(paris(h, fen, inclure=False), f"sans 50-50, h={h} fen={fen}h"))
        print(resume(paris(h, fen), f"AVEC 50-50, h={h} fen={fen}h"))
b = paris(3, 6)
print(resume([x for x in b if x["jour"] < coupe], "AVEC, h=3 fen=6h, 1re moitié"))
print(resume([x for x in b if x["jour"] >= coupe], "AVEC, h=3 fen=6h, 2e moitié"))
for key in ("serie", "bo"):
    g = defaultdict(list)
    for x in b:
        g[x[key]].append(x)
    for k, v in sorted(g.items()):
        n = sum(1 for x in v if x["n5050"])
        print(resume(v, f"AVEC, h=3 fen=6h, {key} = {k} ({n} en 50-50)"))
print("tranches de prix :", json.dumps(it.verdict(b).get("par_prix"), ensure_ascii=False))
print(resume(paris(3, 6, issue=0), "PLUS (contre-épreuve), AVEC 50-50"))
for mode in ("après", "avant"):
    b5 = [x for x in paris(3, 6, mode=mode) if x["bo"] == 5]
    print(resume(b5, f"BO5 seulement, {mode}, h=3 fen=6h"))
    print(resume([x for x in b5 if x["serie"] == "lol"], f"BO5 LoL, {mode}, h=3 fen=6h"))
