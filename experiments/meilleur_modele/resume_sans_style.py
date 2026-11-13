"""Résumé limité aux événements mensuels « best AI model end of <mois> » réglés sur le classement SANS contrôle de style
(règle lue dans la description), hors LiveBench, code et « fin d'année » : meneur à J-k contre prix du meneur."""
import runpy, io, contextlib
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    g = runpy.run_path("analyse.py")
rows = [r for r in g["rows"] if r["style"]]
vus = set()
uniq = []
for r in rows:                       # « end of August 2025 » a été relevé avec la fin juillet : un seul compte par (mois, délai)
    k = (r["mois"], r["k"])
    if k not in vus:
        vus.add(k); uniq.append(r)
for k in (14, 10, 7, 3):
    r = [x for x in uniq if x["k"] == k]
    perdus = [(x["mois"], round(x["prix"], 3)) for x in r if not x["garde"]]
    print(f"J-{k}: {len(r)} mois, meneur garde {sum(x['garde'] for x in r)} pour {sum(x['prix'] for x in r):.2f} attendues au prix ;"
          f" coût moyen {sum(x['prix'] for x in r)/len(r):.3f} ; perdus {perdus}")
for x in uniq:
    if x["k"] == 14:
        print(x["mois"], x["meneur"], round(x["ecart"], 1), x["prix"], x["garde"])
