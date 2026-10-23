"""Piste n° 4, suite : la découverte « sans modèle » (acheter le MOINS de cartes : la série se finit 2-0) tient-elle ?

Trouvée parmi 12 essais « sans modèle » de test_passe.py (6 côtés × avant/après) ; ici on la contrôle AUX PRIX « après »
(premier échange réel après T0, jamais après le coup d'envoi, frais du marché) : par moitié de période (la 1re moitié
n'a servi à rien choisir ici, mais l'idée vient de la période entière : la 2e moitié n'est donc pas un vrai hors-échantillon),
par délai, par jeu, par BO et par tranche de prix. Même tirage d'échantillon (donnees/echantillon_esport.json).
Usage : python experiments/bo3_coherence/sous_2_5.py [esport|tennis]"""
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from echanges import cout_preneur  # noqa: E402
from series import match_cas, jour, resume, it  # noqa: E402

FAM = sys.argv[1] if len(sys.argv) > 1 else "esport"
D = HERE / "donnees"
NOMS = ["cs2", "lol", "dota2", "val"] if FAM == "esport" else ["atp", "wta"]
choisis = set(json.loads((D / f"echantillon_{FAM}.json").read_text()))
cas_list = []
for nom in NOMS:
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        if str(ev["id"]) in choisis:
            ev["serie"] = nom
            c = match_cas(ev, FAM)
            p = D / "echanges" / f"{ev['id']}.json.gz"
            if c and p.exists():
                c["rows"] = json.loads(gzip.decompress(p.read_bytes()))
                cas_list.append(c)
jours = sorted({jour(c["start"]) for c in cas_list})
coupe = jours[len(jours) // 2]


def paris(h, fen, issue=1, mode="après"):
    """issue 1 = « Under » (moins de cartes / sets) ; issue 0 = « Over »."""
    out = []
    for c in cas_list:
        t0 = c["start"] - h * 3600
        for li in c["lies"]:
            if li["kind"] != "total":
                continue
            got = cout_preneur(c["rows"], li["toks"][issue], li["toks"][1 - issue], t0, fen * 3600, apres=(mode == "après"), fin_max=c["start"])
            if not got or not 0.01 <= got[1] <= 0.99:
                continue
            paid = got[1] + it.fee(got[1], li["rate"])
            out.append({"gain": int(li["won"] == issue) / paid - 1, "evenement": c["event"], "cout": paid, "win": int(li["won"] == issue),
                        "mois": jour(c["start"])[:7], "jour": jour(c["start"]), "serie": c["serie"], "bo": c["bo"]})
    return out


print(f"# {FAM} : {len(cas_list)} matchs ; coupure des moitiés le {coupe}")
print("| réglage | paris | matchs | rendement | t par match | mois gagnants | gagnés / attendus (z) | verdict |")
print("|---|---|---|---|---|---|---|---|")
for h in (1, 3, 6):
    for fen in (2, 6):
        b = paris(h, fen)
        print(resume(b, f"MOINS, après, h={h} fen={fen}h, période entière"))
b = paris(3, 6)
print(resume([x for x in b if x["jour"] < coupe], "MOINS, après, h=3 fen=6h, 1re moitié"))
print(resume([x for x in b if x["jour"] >= coupe], "MOINS, après, h=3 fen=6h, 2e moitié"))
for key in ("serie", "bo"):
    g = defaultdict(list)
    for x in b:
        g[x[key]].append(x)
    for k, v in sorted(g.items()):
        print(resume(v, f"MOINS, après, h=3 fen=6h, {key} = {k}"))
v = it.verdict(b)
print("par tranche de prix payé (h=3, 6 h) :", json.dumps(v.get("par_prix"), ensure_ascii=False))
print(resume(paris(3, 6, issue=0), "PLUS, après, h=3 fen=6h (contre-épreuve)"))
print(resume(paris(3, 6, mode="avant"), "MOINS, avant, h=3 fen=6h"))
