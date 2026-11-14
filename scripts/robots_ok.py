"""Lire robots.txt AVANT le premier appel à un nouveau site (règle n° 7, docs/ROUTINE_CHERCHEUR.md, astuce du 12/11/2026).

Usage : .venv/bin/python scripts/robots_ok.py <url> [<url> …]
Affiche « permis » / « INTERDIT » / « pas de robots.txt lisible » pour chaque adresse et sort avec le code 1 si une seule est
interdite. À lancer SEUL, jamais enchaîné avec le téléchargement dans la même commande (14/11/2026 : `graph.txt` de la NASA
et `api.bls.gov` lus dans la même commande que leur robots.txt, tous deux interdits aux robots).
"""
from __future__ import annotations

import sys
import urllib.robotparser
from urllib.parse import urlsplit

import requests

AGENT = "*"


def verdict(robots_text: str | None, url: str) -> str:
    """« permis », « INTERDIT » ou « pas de robots.txt lisible » (un robots.txt absent ou illisible n'interdit rien, mais on le dit)."""
    if robots_text is None:
        return "pas de robots.txt lisible"
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(robots_text.splitlines())
    return "permis" if rp.can_fetch(AGENT, url) else "INTERDIT"


def lire_robots(url: str, timeout: float = 20) -> str | None:
    p = urlsplit(url)
    try:
        r = requests.get(f"{p.scheme}://{p.netloc}/robots.txt", headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
    except requests.RequestException:
        return None
    if r.status_code == 404:
        return ""          # pas de robots.txt : tout est permis
    if r.status_code != 200 or "<html" in r.text[:500].lower():
        return None        # page d'erreur (« Access Denied ») : on ne sait pas
    return r.text


def main(urls: list[str]) -> int:
    code = 0
    for u in urls:
        v = verdict(lire_robots(u), u)
        print(f"{v:28s} {u}")
        code |= v == "INTERDIT"
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
