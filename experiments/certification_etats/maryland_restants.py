"""Piste n° 68, gouverneur du Maryland : bulletins restants comté par comté (17/11/2026).
Entrées (pages publiques du State Board of Elections, robots.txt permis) : résultats non officiels par comté
(`gen_results_2026_by_county_<1..24>.html`, colonnes anticipé / jour J / correspondance / provisoire) et
`Absentees_Ballots_Left_To_Count_by_County.xlsx` (reçus, acceptés, restants, au 14/11).
Usage : python maryland_restants.py <dossier des 24 pages> <reçus_par_comté.json>"""
import json
import re
import html
import sys
from pathlib import Path

COMTES = ["ALLEGANY", "ANNE ARUNDEL", "BALTIMORE CITY", "BALTIMORE COUNTY", "CALVERT", "CAROLINE", "CARROLL", "CECIL", "CHARLES",
          "DORCHESTER", "FREDERICK", "GARRETT", "HARFORD", "HOWARD", "KENT", "MONTGOMERY", "PRINCE GEORGE'S", "QUEEN ANNE'S",
          "SAINT MARY'S", "SOMERSET", "TALBOT", "WASHINGTON", "WICOMICO", "WORCESTER"]


def n(x):
    return None if x == "NR" else int(x.replace(",", ""))


def gouverneur(page: str) -> dict:
    t = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", page)))
    bloc = t[t.find("Governor / Lt. Governor Vote for 1"):]
    bloc = bloc[:bloc.find("Comptroller")]
    lig = {}
    for nom, a, b, c, d, tot in re.findall(r"(Democratic|Republican|Green|Working Class Party|Write-Ins|Totals) ([0-9,]+|NR) ([0-9,]+|NR) "
                                           r"([0-9,]+|NR) ([0-9,]+|NR) ([0-9,]+)", bloc):
        lig[nom] = {"anticipe": n(a), "jour": n(b), "corr": n(c), "prov": n(d), "total": n(tot)}
    return lig


if __name__ == "__main__":
    dossier, recus = Path(sys.argv[1]), json.load(open(sys.argv[2]))
    out = {}
    for i, c in enumerate(COMTES, 1):
        out[c] = gouverneur((dossier / f"c{i}.html").read_text(errors="ignore"))
    json.dump(out, open(Path(__file__).parent / "releves" / "maryland_comtes_gouverneur_20261116T2306.json", "w"), indent=1)
    tot_rest, tot_marge = 0, 0.0
    for c in COMTES:
        g = out[c]
        d, r, T = g["Democratic"], g["Republican"], g["Totals"]
        mc = (d["corr"] - r["corr"]) / T["corr"]
        rest = recus[c]["recus"] - T["corr"] / 0.99   # bulletins de gouverneur ≈ 99 % des bulletins acceptés (voir ci-dessous)
        prov = "NR" if T["prov"] is None else T["prov"]
        mp = None if T["prov"] in (None, 0) else (d["prov"] - r["prov"]) / T["prov"]
        print(f"{c:16s} corr comptés {T['corr']:7d} reçus {recus[c]['recus']:7d} restants≈{rest:8.0f} marge corr {100*mc:+6.1f} "
              f"prov {prov} marge prov {'' if mp is None else f'{100*mp:+.1f}'}")
        tot_rest += max(rest, 0)
        tot_marge += max(rest, 0) * mc
    print("restants ≈", round(tot_rest), "marge moyenne", round(100 * tot_marge / max(tot_rest, 1), 1))
