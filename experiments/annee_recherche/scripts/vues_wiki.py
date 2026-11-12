"""Vues mensuelles Wikipédia (en) des personnes des listes Year in Search, 2015-07 → aujourd'hui.

Univers d'une année : toutes les catégories « personnes » des listes de cette année (People, Actors,
Athletes, Musicians…, sans Passings), monde et États-Unis. Sortie : releves/vues_wiki.json
{ "<nom>": {"titre": "...", "mois": {"AAAAMM": vues}} } — reprise possible (cache).
Usage : vues_wiki.py [noms supplémentaires...]
"""
import json, sys, time, urllib.parse
from pathlib import Path
import requests

H = {"User-Agent": "polymarket-lab-research/0.1 (simulation; contact via github)"}
R = Path(__file__).resolve().parents[1] / "releves"
OUT = R / "vues_wiki.json"
PERSONNES = ("people",)  # 12/11 : Wikimédia limite le débit (429) ; univers réduit aux listes « People »
PAUSE = 3.0


def _api(params):
    for essai in range(6):
        r = requests.get("https://en.wikipedia.org/w/api.php", headers=H, timeout=30,
                         params={**params, "format": "json"})
        try:
            return r.json()
        except ValueError:
            time.sleep(30 * 2 ** essai)
    raise RuntimeError(f"API Wikipédia muette ({r.status_code})")


def titres_exacts(noms):
    """Titre Wikipédia par nom exact (redirections suivies), 50 noms par appel ; homonymies écartées."""
    res = {}
    noms = list(noms)
    for i in range(0, len(noms), 50):
        lot = noms[i:i + 50]
        q = _api({"action": "query", "titles": "|".join(lot), "redirects": 1, "prop": "pageprops"})["query"]
        alias = {x["from"]: x["to"] for x in q.get("normalized", []) + q.get("redirects", [])}
        pages = {pg["title"]: pg for pg in q.get("pages", {}).values()}
        for n in lot:
            t = n
            while t in alias:
                t = alias[t]
            pg = pages.get(t)
            if pg and "missing" not in pg and "disambiguation" not in pg.get("pageprops", {}):
                res[n] = t
        time.sleep(1)
    return res


def titre(nom):
    hits = _api({"action": "query", "list": "search", "srsearch": nom, "srlimit": 1}).get("query", {}).get("search", [])
    return hits[0]["title"] if hits else None


def vues(t, fin):
    u = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
         f"{urllib.parse.quote(t.replace(' ', '_'), safe='')}/monthly/2015070100/{fin}")
    for essai in range(6):
        r = requests.get(u, headers=H, timeout=30)
        if r.status_code == 429:
            time.sleep(30 * 2 ** essai); continue
        if r.status_code == 404:
            return {}
        r.raise_for_status()
        return {i["timestamp"][:6]: i["views"] for i in r.json()["items"]}
    raise RuntimeError("429 persistant")


def univers():
    d = json.loads((R / "listes.json").read_text())
    noms = set()
    for y, locs in d.items():
        if int(y) < 2016:
            continue
        for topics in locs.values():
            for topic, lst in topics.items():
                if any(k in topic.lower() for k in PERSONNES):
                    noms.update(lst)
    return noms


def main(extra):
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    noms = sorted(univers() | set(extra))
    fin = time.strftime("%Y%m%d00")
    a_faire = [n for n in noms if n not in data or n in extra]
    for i, n in enumerate(a_faire):
        t = n  # titre = nom exact ; les absents (404) sont repris plus tard par titres_exacts
        data[n] = {"titre": t, "mois": vues(t, fin) if t else {}}
        time.sleep(PAUSE)
        if i % 10 == 0:
            OUT.write_text(json.dumps(data, ensure_ascii=False)); print(i, len(noms), n, t, flush=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1:])
