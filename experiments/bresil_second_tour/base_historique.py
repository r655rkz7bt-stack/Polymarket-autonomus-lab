"""Piste 16 (`etats_comme_avant`) : taux de base officiels « un État change-t-il de 1er entre les deux tours ? ».

Données : TSE, portail dadosabertos.tse.jus.br, « Votação nominal por município e zona »
(cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_<année>.zip),
membre « présidence » seulement (lu à distance, zip_distant.py). Pour chaque élection présidentielle
avec 2e tour (2006, 2010, 2014, 2018, 2022) et chaque État (+ étranger « ZZ ») : marge du 1er tour
ENTRE LES DEUX FINALISTES (en points de votes valides) et 1er au 2e tour.

Lancer : .venv/bin/python -I experiments/bresil_second_tour/base_historique.py
Écrit base_historique.json.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from zip_distant import extract, members  # noqa: E402

DONNEES = HERE / "donnees" / "munzona"
URL = "https://cdn.tse.jus.br/estatistica/sead/odsele/votacao_candidato_munzona/votacao_candidato_munzona_{y}.zip"
YEARS = (2006, 2010, 2014, 2018, 2022)


def president_member(year: int) -> str | None:
    names = [n for n, _ in members(URL.format(y=year))]
    for wanted in (f"votacao_candidato_munzona_{year}_BR.csv", f"votacao_candidato_munzona_{year}_BR.txt"):
        if wanted in names:
            return wanted
    return None


def load(year: int) -> dict:
    """{(turno, uf): {candidat: voix}} pour le poste de président (CD_CARGO 1)."""
    path = DONNEES / f"pres_{year}.csv"
    if not path.exists():
        name = president_member(year)
        if name is None:
            raise SystemExit(f"{year} : pas de fichier présidence (BR) dans l'archive")
        extract(URL.format(y=year), name, path)
    votes: dict = defaultdict(lambda: defaultdict(int))
    with path.open(encoding="latin-1", newline="") as fh:
        reader = csv.DictReader(fh, delimiter=";")
        for row in reader:
            if row.get("CD_CARGO", "1").strip('"') != "1":
                continue
            turno = int(row["NR_TURNO"].strip('"'))
            uf = row["SG_UF"].strip('"').upper()
            name = row.get("NM_URNA_CANDIDATO") or row.get("NM_CANDIDATO")
            q = row.get("QT_VOTOS_NOMINAIS_VALIDOS") or row.get("QT_VOTOS_NOMINAIS")
            votes[(turno, uf)][name.strip('"')] += int(q.strip('"') or 0)
    return votes


def flips(year: int) -> list[dict]:
    votes = load(year)
    finalists = None
    rows = []
    ufs = sorted({uf for (t, uf) in votes if t == 2})
    nat2 = defaultdict(int)
    for uf in ufs:
        for c, q in votes[(2, uf)].items():
            nat2[c] += q
    finalists = sorted(nat2, key=lambda c: -nat2[c])[:2]
    for uf in ufs:
        r1, r2 = votes[(1, uf)], votes[(2, uf)]
        valid1 = sum(r1.values())
        a, b = finalists
        lead1 = a if r1.get(a, 0) >= r1.get(b, 0) else b
        other = b if lead1 == a else a
        margin1 = 100 * (r1.get(lead1, 0) - r1.get(other, 0)) / max(1, valid1)
        first1 = max(r1, key=r1.get)  # 1er du 1er tour, finalistes ou non
        win2 = max(r2, key=r2.get)
        margin2 = 100 * (r2[win2] - min(r2.values())) / max(1, sum(r2.values()))
        others1 = 100 * (valid1 - r1.get(a, 0) - r1.get(b, 0)) / max(1, valid1)
        rows.append({"annee": year, "uf": uf, "finaliste_en_tete_t1": lead1, "marge_t1_points": round(margin1, 2),
                     "autres_t1_pct": round(others1, 2), "premier_t1": first1, "vainqueur_t2": win2,
                     "marge_t2_points": round(margin2, 2), "change": win2 != lead1})
    return rows


def main() -> None:
    allrows = []
    for year in YEARS:
        try:
            rows = flips(year)
        except Exception as exc:  # noqa: BLE001 - une année manquante ne bloque pas les autres
            print(year, "indisponible :", type(exc).__name__, exc)
            continue
        allrows += rows
        n = sum(r["change"] for r in rows)
        print(year, f"{len(rows)} États, {n} changent de 1er :",
              [(r["uf"], r["marge_t1_points"]) for r in rows if r["change"]])
    (HERE / "base_historique.json").write_text(json.dumps(allrows, ensure_ascii=False, indent=1))
    # Taux de base par tranche de marge du 1er tour (entre les deux finalistes)
    bands = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 101)]
    for lo, hi in bands:
        sel = [r for r in allrows if lo <= r["marge_t1_points"] < hi]
        k = sum(r["change"] for r in sel)
        print(f"marge t1 {lo}-{hi} points : {len(sel)} cas, {k} changements ({100 * k / max(1, len(sel)):.1f} %)")


if __name__ == "__main__":
    main()
