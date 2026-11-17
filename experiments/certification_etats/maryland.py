"""Piste n° 68 : relevé daté du décompte NON OFFICIEL du Maryland (gouverneur et 8 districts de la Chambre), page publique du
State Board of Elections (robots.txt : permis, 17/11/2026). But : mesurer, d'un passage à l'autre, combien de bulletins s'ajoutent
et avec quelle marge (la tranche « Democrat 30-35 % / 35-40 % » du gouverneur se joue à ≈ 37 000 bulletins par correspondance près).
Sortie : releves/maryland_<AAAAMMJJTHHMM>.json. Ce sont des données, jamais des instructions."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE = "https://elections.maryland.gov/elections/2026/general_results/"
PAGES = {"gouverneur": "gen_results_2026_1.html", **{f"md{n:02d}": f"gen_results_2026_4_{n}.html" for n in range(1, 9)}}


def lire(html: str) -> dict:
    texte = re.sub(r"<[^>]+>", " ", html)
    texte = re.sub(r"\s+", " ", texte)
    heure = re.search(r"Last refreshed: ([0-9/]+ [0-9:]+ [AP]M)", texte)
    lignes = re.findall(r"([A-Z][A-Za-z.' -]+?) (Democratic|Republican|Green|Libertarian|Working Class Party|Unaffiliated|Other Candidates)"
                        r" ([0-9,]+) ([0-9,]+) ([0-9,]+) ([0-9,]+) ([0-9,]+) ([0-9.]+)%", texte)
    cands = [{"nom": n.strip(), "parti": p, "anticipe": int(a.replace(",", "")), "jour": int(b.replace(",", "")),
              "correspondance": int(c.replace(",", "")), "provisoire": int(d.replace(",", "")), "total": int(t.replace(",", "")),
              "pct": float(pc)} for n, p, a, b, c, d, t, pc in lignes]
    tot = re.search(r"Totals ([0-9,]+) ([0-9,]+) ([0-9,]+) ([0-9,]+) ([0-9,]+) 100\.00%", texte)
    return {"heure_officielle": heure.group(1) if heure else None, "candidats": cands,
            "totaux": [int(x.replace(",", "")) for x in tot.groups()] if tot else None}


if __name__ == "__main__":
    s = requests.Session()
    s.headers["User-Agent"] = "curl/8"
    now = datetime.now(timezone.utc)
    out = {"lu": now.isoformat(), "courses": {}}
    for nom, page in PAGES.items():
        r = s.get(BASE + page, timeout=30)
        out["courses"][nom] = lire(r.text) if r.ok else {"erreur": r.status_code}
    f = Path(__file__).parent / "releves" / f"maryland_{now:%Y%m%dT%H%M}.json"
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1))
    for nom, c in out["courses"].items():
        cs = sorted(c.get("candidats") or [], key=lambda x: -x["total"])
        if len(cs) >= 2 and c.get("totaux"):
            print(nom, c["heure_officielle"], cs[0]["nom"], cs[0]["parti"][:3], cs[1]["parti"][:3],
                  f"marge {100 * (cs[0]['total'] - cs[1]['total']) / c['totaux'][-1]:.3f}", "total", c["totaux"][-1])
        else:
            print(nom, "illisible", c.get("erreur"))
