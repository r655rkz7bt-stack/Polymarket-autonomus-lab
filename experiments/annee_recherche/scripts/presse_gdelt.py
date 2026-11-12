"""Volume quotidien d'articles de presse (GDELT DOC 2.0, sans clé) par personne, 2017 → aujourd'hui.

Univers : listes « People » Year in Search 2017-2025 (monde et États-Unis) + noms donnés en argument
(candidats des marchés 2026). Une requête par nom, une toutes les 6 s (règle de GDELT : une par 5 s).
Sortie : releves/presse_gdelt.json  { "<nom>": {"AAAAMMJJ": articles, ...} }  (reprise possible).
"""
import json, sys, time
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1] / "releves"
OUT = R / "presse_gdelt.json"
URL = "https://api.gdeltproject.org/api/v2/doc/doc"


def univers():
    """Noms des listes « People » 2017-2025, les mieux classés d'abord (rang 1 de chaque liste, puis 2…)."""
    d = json.loads((R / "listes.json").read_text())
    rang = {}
    for y, locs in d.items():
        if 2017 <= int(y):
            for topics in locs.values():
                for i, n in enumerate(topics.get("People", [])):
                    rang[n] = min(rang.get(n, 99), i)
    return sorted(rang, key=lambda n: (rang[n], n))


def serie(nom, fin):
    for essai in range(5):
        try:
            r = requests.get(URL, timeout=120, params={"query": f'"{nom}"', "mode": "timelinevolraw", "format": "json",
                                                        "startdatetime": "20170101000000", "enddatetime": fin})
        except requests.RequestException as exc:
            print('  erreur', nom, type(exc).__name__, flush=True)
            time.sleep(15 * (essai + 1)); continue
        if r.text.startswith("{"):
            print("  ok", nom, r.elapsed.total_seconds(), flush=True)
            tl = r.json().get("timeline") or []
            return {x["date"][:8]: x["value"] for x in (tl[0]["data"] if tl else [])}
        print("  refus", nom, r.status_code, r.text[:80].replace("\n", " "), flush=True)
        time.sleep(15 * (essai + 1))
    return None


def main(extra):
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    fin = time.strftime("%Y%m%d000000")
    noms = list(dict.fromkeys(list(extra) + univers()))
    for i, n in enumerate(noms):
        if n in data:
            continue
        s = serie(n, fin)
        if s is not None:
            data[n] = s
        time.sleep(6)
        if True:  # sauvegarde à chaque nom (un arrêt ne perd rien)
            OUT.write_text(json.dumps(data)); print(i, len(noms), n, sum((s or {}).values()), flush=True)
    OUT.write_text(json.dumps(data))


if __name__ == "__main__":
    main(sys.argv[1:])
