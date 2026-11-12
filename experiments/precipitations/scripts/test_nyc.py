"""Test sur le passé, NYC (Central Park), janvier → octobre 2026 : le 11 de chaque mois à 12 h UTC, chance de chaque tranche =
cumul observé du 1er au 10 (ACIS) + reste du mois tiré des mêmes dates 1951-2025 ; contre le prix (milieu horaire du CLOB) et
l'issue Gamma. Rien d'après le 10 du mois n'entre dans le modèle (pas de regard vers le futur ; la climatologie s'arrête en 2025).
Sortie : log-score modèle contre marché, achats simulés (milieu + 0,02) quand chance − prix >= 0,08."""
import json, math, re, datetime as dt
import requests

H = {"User-Agent": "curl/8"}
EVENTS = {1: 131194, 2: 193622, 3: 232661, 4: 303983, 5: 427844, 6: 531291, 7: 686198, 8: 763089, 9: 941972, 10: 1108649}
r = requests.post("https://data.rcc-acis.org/StnData", json={"sid": "94728", "sdate": "1951-01-01", "edate": "2026-11-10",
                  "elems": [{"name": "pcpn"}]}, headers=H, timeout=120).json()
P = {}
for d, v in r["data"]:
    P[d] = 0.0 if v == "T" else (float(v.rstrip("A")) if v not in ("M", "S") else None)


def bornes(nom):
    x = [float(t) for t in re.findall(r"\d+(?:\.\d+)?", nom)]
    if "<" in nom: return 0.0, x[0]
    if ">" in nom or "+" in nom: return x[0], 99.0
    return x[0], x[1]


ls_m = ls_p = 0.0; n = 0; paris = []
for mois, eid in EVENTS.items():
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=60).json()
    fin = (dt.date(2026, mois % 12 + 1, 1) if mois < 12 else dt.date(2027, 1, 1)) - dt.timedelta(days=1)
    vu = sum(P.get(f"2026-{mois:02d}-{j:02d}") or 0.0 for j in range(1, 11))
    restes = []
    for an in range(1951, 2026):
        vals = [P.get(f"{an}-{mois:02d}-{j:02d}") for j in range(11, fin.day + 1)]
        if sum(v is None for v in vals) <= 1:
            restes.append(sum(v or 0.0 for v in vals))
    tot = [vu + x for x in restes]
    t = int(dt.datetime(2026, mois, 11, 12, tzinfo=dt.timezone.utc).timestamp())
    for m in e["markets"]:
        if "outcomePrices" not in m: continue
        a, b = bornes(m.get("groupItemTitle") or "")
        q = max(min(sum(1 for x in tot if a <= x < b) / len(tot), 0.98), 0.02)
        h = requests.get("https://clob.polymarket.com/prices-history", timeout=30, params={
            "market": json.loads(m["clobTokenIds"])[0], "startTs": t - 86400, "endTs": t, "fidelity": 60}).json().get("history", [])
        if not h: continue
        p = min(max(h[-1]["p"], 0.01), 0.99); y = float(json.loads(m["outcomePrices"])[0]) > 0.5
        ls_m += math.log(q if y else 1 - q); ls_p += math.log(p if y else 1 - p); n += 1
        for cote, est, px, gagne in (("OUI", q, p, y), ("NON", 1 - q, 1 - p, not y)):
            if est - (px + 0.02) >= 0.08 and px + 0.02 <= 0.95:
                paris.append((mois, m.get("groupItemTitle"), cote, round(est, 3), round(px + 0.02, 3), gagne))
    print(mois, "cumul au 10 :", round(vu, 2), "issue :", [m.get("groupItemTitle") for m in e["markets"] if "outcomePrices" in m and float(json.loads(m["outcomePrices"])[0]) > 0.5], flush=True)
print("tranches", n, "log-score moyen modèle", round(ls_m / n, 3), "marché", round(ls_p / n, 3))
g = sum(1 for p in paris if p[5]); att = sum(p[4] for p in paris)
rend = sum((1 / p[4] - 1) if p[5] else -1 for p in paris) / max(len(paris), 1)
print("paris", len(paris), "gagnés", g, "attendus (prix)", round(att, 1), "attendus (modèle)", round(sum(p[3] for p in paris), 1), "rendement par mise", round(rend, 3))
for p in paris: print("  ", p)
