"""Communiqués « Gross domestic product by industry » du Quotidien de Statistique Canada (www150.statcan.gc.ca/n1/daily-quotidien/
AAMMJJ/dqAAMMJJa-eng.htm ; robots.txt : permis, délai de 2 s) : chiffre officiel du mois et estimation anticipée du mois suivant.
On essaie les jours 22 → 5 du mois suivant autour de la fin de mois. Sortie : releves/communiques.json
{"AAAA-MM" (mois publié): {"date": AAMMJJ, "officiel": x, "anticipe_mois": "AAAA-MM", "anticipe": y}}"""
import html, json, re, sys, time
from datetime import date, timedelta
from pathlib import Path
import requests

R = Path(__file__).resolve().parents[1] / "releves"
import os
OUT = R / os.environ.get("SORTIE", "communiques.json")
H = {"User-Agent": "Mozilla/5.0 (recherche ; simulation)"}
MOIS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
VERB = r"(rose|increased|grew|edged up|edged down|fell|declined|decreased|contracted|was essentially unchanged|was unchanged|was flat|remained essentially unchanged)"
NUM = r"(?:\s+(?:approximately |about |by |roughly )?(\d+(?:\.\d+)?)%)?"


def val(verb, x):
    if "unchanged" in verb or "flat" in verb:
        return 0.0
    v = float(x) if x else 0.0
    return -v if verb in ("edged down", "fell", "declined", "decreased", "contracted") else v


def lire(texte):
    x = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", texte)))
    if "Gross domestic product by industry" not in x:
        return None
    mois = "(" + "|".join(MOIS) + ")"
    o = re.search(r"Real gross domestic product \(\s*GDP\s*\) " + VERB + NUM + r" in " + mois, x)
    a = re.search(r"Advance information indicates that real GDP(?: by industry)? " + VERB + NUM + r" in " + mois, x)
    if not o:
        return None
    r = {"officiel_mois": o.group(3), "officiel": val(o.group(1), o.group(2))}
    if a:
        r.update(anticipe_mois=a.group(3), anticipe=val(a.group(1), a.group(2)))
    return r


def main():
    data = json.loads(OUT.read_text()) if OUT.exists() else {}
    vus = {v["date"] for v in data.values()}
    y0 = int(sys.argv[1]) if len(sys.argv) > 1 else 2023
    for y in range(y0, 2027):
        for m in range(1, 13):
            if (y, m) > (2026, 10):
                break
            debut = date(y, m, 22)
            trouve = False
            for k in range(15):
                d = debut + timedelta(days=k)
                if d.weekday() >= 5:
                    continue
                code = d.strftime("%y%m%d")
                if code in vus:
                    trouve = True; break
                r = None
                for suffixe in "ab":   # fin de trimestre : « a » = PIB trimestriel, « b » = PIB mensuel par industrie
                    url = f"https://www150.statcan.gc.ca/n1/daily-quotidien/{code}/dq{code}{suffixe}-eng.htm"
                    time.sleep(2)
                    try:
                        t = requests.get(url, headers=H, timeout=60)
                    except requests.RequestException:
                        continue
                    if t.status_code == 200:
                        r = lire(t.text)
                    if r is not None or t.status_code != 200:
                        break
                if r is None:
                    continue
                mo = MOIS.index(r["officiel_mois"]) + 1
                yy = y if mo <= m else y - 1
                r["date"] = code
                data[f"{yy}-{mo:02d}"] = r
                OUT.write_text(json.dumps(data, indent=0))
                print(code, r, flush=True)
                trouve = True
                break
            if not trouve:
                print("rien", y, m, flush=True)


if __name__ == "__main__":
    main()
