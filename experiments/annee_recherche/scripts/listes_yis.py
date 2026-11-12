"""Relève les listes « Year in Search » de Google (personnes en tendance), monde et États-Unis.

Sortie : experiments/annee_recherche/releves/listes.json
{ "2025": {"GLOBAL": {"People": [...10 noms...], ...}, "US": {...}}, ... }
Source : trends.withgoogle.com/year-in-search/<année>/ (monde) et /<année>/us/ (sans clé).
"""
import json, re, sys, time, html
from pathlib import Path
import requests

H = {"User-Agent": "Mozilla/5.0"}
OUT = Path(__file__).resolve().parents[1] / "releves" / "listes.json"
ITEM = re.compile(r'data-searchterms="([^"]*)"\s*data-locale="([A-Z]+)"\s*data-topic="([^"]*)"')


def parse(page: str) -> dict:
    res: dict = {}
    for term, loc, topic in ITEM.findall(page):
        lst = res.setdefault(loc, {}).setdefault(html.unescape(topic), [])
        term = html.unescape(term)
        if term not in lst:
            lst.append(term)
    return res


def main(years):
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    for y in years:
        for suffix in ("", "us/"):
            r = requests.get(f"https://trends.withgoogle.com/year-in-search/{y}/{suffix}", headers=H, timeout=60)
            if r.status_code != 200:
                print(y, suffix, r.status_code); continue
            for loc, topics in parse(r.text).items():
                data.setdefault(str(y), {})[loc] = topics
            time.sleep(1)
        print(y, {loc: (t.get("People") or [])[:3] for loc, t in data.get(str(y), {}).items()})
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or range(2010, 2026))
