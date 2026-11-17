"""Relevé de l'historique public de githubstatus.com (page /history, permise par robots.txt ; l'API /api/ est INTERDITE).
Chaque page donne 3 mois d'incidents (code, nom, impact, « Nov 16, 11:59 - 16:26 UTC »). Usage : python releve.py <pages> <sortie.jsonl>
17/11/2026 (passage de 16 h), piste n° 70 (experiments/github_pannes.md)."""
import html, json, re, sys, time
import requests

UA = {"User-Agent": "Mozilla/5.0"}


def page(n):
    s = requests.get(f"https://www.githubstatus.com/history?page={n}", headers=UA, timeout=60).text
    props = [json.loads(html.unescape(m)) for m in re.findall(r'data-react-props="([^"]*)"', s)]
    return [p for p in props if "months" in p][0]["months"]


if __name__ == "__main__":
    out = open(sys.argv[2], "w")
    for n in range(1, int(sys.argv[1]) + 1):
        for m in page(n):
            for i in m["incidents"]:
                out.write(json.dumps(dict(i, mois=m["name"], annee=m["year"]), ensure_ascii=False) + "\n")
        time.sleep(2)
