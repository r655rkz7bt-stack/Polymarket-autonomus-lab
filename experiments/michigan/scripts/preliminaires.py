"""Valeurs PRÉLIMINAIRES du sentiment des consommateurs (Michigan) relues dans les titres de presse (Google Actualités RSS, fenêtre
de 3 jours autour du 2e vendredi du mois) ; finales : fichier officiel tbmics.csv (sca.isr.umich.edu). Sortie :
releves/preliminaires.json {"AAAA-MM": {"prelim": x, "titres": [...], "final": y}}. Usage : preliminaires.py 2022"""
import collections, csv, html, io, json, re, sys, time
from datetime import date, timedelta
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1] / "releves"
R.mkdir(exist_ok=True)
OUT = R / "preliminaires.json"
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
NUM = re.compile(r"(?<![\d.])(\d{2}\.\d)(?![\d.])")


def finales():
    t = requests.get("https://www.sca.isr.umich.edu/files/tbmics.csv", headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text
    return {f"{r['YYYY']}-{MOIS.index(r['Month']) + 1:02d}": float(r["ICS_ALL"]) for r in csv.DictReader(io.StringIO(t))}


def titres(y, m):
    d0 = date(y, m, 1)
    # le préliminaire sort d'habitude le 2e vendredi (parfois le 1er) : fenêtre du 1er au 16
    q = f'michigan consumer sentiment {MOIS[m - 1]} after:{d0.isoformat()} before:{(d0 + timedelta(days=16)).isoformat()}'
    t = requests.get("https://news.google.com/rss/search", params={"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"}, timeout=60).text
    return [html.unescape(x) for x in re.findall(r"<item>.*?<title>(.*?)</title>", t, re.S)]


def main():
    y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2022
    fin = finales()
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    for y in range(y0, 2027):
        for m in range(1, 13):
            k = f"{y}-{m:02d}"
            if k in data or (y == 2026 and m > 11):
                continue
            ts = titres(y, m)
            c = collections.Counter()
            for t in ts:
                tl = t.lower()
                if "sentiment" not in tl or "final" in tl or "revised" in tl or (MOIS[m - 1].lower() not in tl and "prelim" not in tl):
                    continue
                for x in NUM.findall(t):
                    v = float(x)
                    if 40 <= v <= 110:
                        c[v] += 1
            data[k] = {"prelim": c.most_common(1)[0][0] if c else None, "votes": c.most_common(4), "titres": ts[:8], "final": fin.get(k)}
            OUT.write_text(json.dumps(data, indent=0, ensure_ascii=False))
            print(k, data[k]["prelim"], c.most_common(3), data[k]["final"], flush=True)
            time.sleep(1.5)


if __name__ == "__main__":
    main()
