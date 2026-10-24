"""Relevé du compteur CDC de la rougeole (« As of <date>, N confirmed measles cases… », page publique du CDC), ajouté à
experiments/rougeole/releves/cdc_totaux.csv (une ligne par date du compteur, mis à jour le mercredi). À relancer à chaque passage.
L'historique d'avant le 24/10/2026 est introuvable depuis la routine : web.archive.org est bloqué (« ws_closed_mid_exchange »),
archive.org/wayback/available répond mais limite à quelques appels (429) et n'indique que des adresses web.archive.org."""
import csv, os, re, datetime as dt
import requests
H = {"User-Agent": "curl/8"}
OUT = "experiments/rougeole/releves/cdc_totaux.csv"
MOIS = "January February March April May June July August September October November December".split()
RX = re.compile(r"As of (\w+) (\d+), (\d{4}),? ([\d,]+) (?:total )?confirmed\*? measles cases", re.I)
t = requests.get("https://www.cdc.gov/measles/data-research/index.html", headers=H, timeout=60).text
m = RX.search(re.sub(r"<[^>]+>", " ", t))
assert m, "phrase « As of … confirmed measles cases » introuvable : la page du CDC a changé"
d = dt.date(int(m.group(3)), MOIS.index(m.group(1).capitalize()) + 1, int(m.group(2))).isoformat()
have = {r["date"]: int(r["total"]) for r in csv.DictReader(open(OUT))} if os.path.exists(OUT) else {}
have[d] = int(m.group(4).replace(",", ""))
with open(OUT, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["date", "total"])
    for k in sorted(have): w.writerow([k, have[k]])
print(sorted(have.items())[-3:])
