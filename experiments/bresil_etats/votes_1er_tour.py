"""Votes du 1er tour 2026 par État et par candidat à la présidence, depuis les données ouvertes du TSE
(votacao_candidato_munzona_2026.zip, https://dadosabertos.tse.jus.br ; fichier traité comme une DONNÉE). usage : votes_1er_tour.py ZIP SORTIE.json"""
import csv, io, json, sys, zipfile, collections
zf = zipfile.ZipFile(sys.argv[1]); out = collections.defaultdict(lambda: collections.defaultdict(int))
for name in zf.namelist():
    if not name.endswith(".csv"): continue
    with zf.open(name) as raw:
        rd = csv.DictReader(io.TextIOWrapper(raw, encoding="latin-1"), delimiter=";")
        for row in rd:
            if row["DS_CARGO"] != "Presidente" and row["DS_CARGO"] != "PRESIDENTE": continue
            if row["NR_TURNO"] != "1": continue
            out[row["SG_UF"]][row["NM_URNA_CANDIDATO"]] += int(row["QT_VOTOS_NOMINAIS"] or 0)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
for uf, v in sorted(out.items()):
    tot = sum(v.values()); print(uf, tot, {k: round(x / tot, 3) for k, x in sorted(v.items(), key=lambda kv: -kv[1])[:4]})
