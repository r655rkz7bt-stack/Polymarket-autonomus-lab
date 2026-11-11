"""Lectures horaires de Budapest (HU442027) sur DanubeHIS, page par page (25 heures par page), pour repérer les crues passées
et juger la prévision OVF à 4 jours (rapports quotidiens archivés). Politesse : 3 fils, petite pause."""
import json, re, sys, time
from concurrent.futures import ThreadPoolExecutor
import requests
FROM, TO, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
URL = "https://www.danubehis.org/results/HU442027_HYDRO"
def page(k):
    for essai in range(3):
        try:
            t = requests.get(URL, params={"symbol[h]": "h", "time_from": FROM, "time_to": TO, "order": "time", "sort": "asc", "page": k},
                             headers={"User-Agent": "Mozilla/5.0"}, timeout=60).text
            t = re.sub(r"\s+", " ", t)
            time.sleep(0.2)
            return re.findall(r"(20\d\d-\d\d-\d\d \d\d:\d\d) </td> <td[^>]*> (-?[\d.]+) </td>", t)
        except Exception:
            time.sleep(2)
    return []
n = int(sys.argv[4])
with ThreadPoolExecutor(3) as ex:
    rows = [r for lot in ex.map(page, range(n)) for r in lot]
data = {t: float(v) for t, v in rows}
json.dump(data, open(OUT, "w"))
print(len(data), min(data), max(data))
