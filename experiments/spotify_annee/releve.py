"""Classements Spotify de l'année (Wrapped) : écoutes hebdomadaires mondiales et US de chaque titre (kworb.net, robots.txt « Allow: / »).

Candidats : les 200 titres du classement quotidien mondial du jour + tous les titres restés au moins 3 semaines dans le top 10
hebdomadaire mondial (global_weekly_totals). Pour chacun, la page kworb du titre donne TOUT l'historique hebdomadaire (rang et
écoutes par pays) ; on garde les colonnes Global et US. Sortie : donnees/titres.jsonl (une ligne par titre).
Usage : python releve.py   (≈ 600 pages, 4 fils, ≈ 2 minutes)
"""
import html, json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests

D = Path(__file__).parent / "donnees"
H = {"User-Agent": "curl/8"}


def candidats():
    out = {}
    t = (D / "global_daily.html").read_text()
    for r in re.findall(r"<tr>(.*?)</tr>", t, re.S):
        m = re.search(r'href="\.\./track/([A-Za-z0-9]+)\.html"', r)
        if m:
            out[m.group(1)] = None
    t = (D / "global_weekly_totals.html").read_text()
    for r in re.findall(r"<tr>(.*?)</tr>", t, re.S):
        m = re.search(r'href="\.\./track/([A-Za-z0-9]+)\.html"', r)
        tds = re.findall(r"<td[^>]*>(.*?)</td>", r, re.S)
        if m and len(tds) >= 3 and tds[2].strip().isdigit() and int(tds[2]) >= 3:
            out[m.group(1)] = None
    return list(out)


def cell(c):
    m = re.search(r'class="s">([\d,]+)<', c)
    return int(m.group(1).replace(",", "")) if m else 0


def lire(tid):
    for essai in range(3):
        try:
            r = requests.get(f"https://kworb.net/spotify/track/{tid}.html", headers=H, timeout=30)
            if r.status_code == 200:
                break
        except requests.RequestException:
            pass
        time.sleep(2 + 3 * essai)
    else:
        return None
    t = r.text
    titre = html.unescape(re.sub("<[^>]+>", "", (re.search(r"<title>(.*?)</title>", t, re.S) or [None, ""])[1])).replace(" - Spotify Chart History", "").strip()
    tables = re.findall(r"<table>(.*?)</table>", t, re.S)
    if not tables:
        return None
    entete = re.findall(r"<th>(.*?)</th>", tables[0])
    cols = [re.sub("<[^>]+>", "", h).strip() for h in entete]
    ig, iu = (cols.index("Global") if "Global" in cols else None), (cols.index("US") if "US" in cols else None)
    semaines = {}
    for row in re.findall(r"<tr><td>(20\d\d/\d\d/\d\d)</td>(.*?)</tr>", tables[0], re.S):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", "<td></td>" + row[1], re.S)
        g = cell(tds[ig]) if ig is not None and ig < len(tds) else 0
        u = cell(tds[iu]) if iu is not None and iu < len(tds) else 0
        semaines[row[0].replace("/", "-")] = [g, u]
    return {"id": tid, "titre": titre, "semaines": semaines}


if __name__ == "__main__":
    ids = candidats()
    print(len(ids), "candidats", file=sys.stderr)
    n = 0
    with ThreadPoolExecutor(4) as ex, open(D / "titres.jsonl", "w") as f:
        for res in ex.map(lire, ids):
            if res:
                f.write(json.dumps(res, ensure_ascii=False) + "\n")
                n += 1
    print(n, "titres lus", file=sys.stderr)
