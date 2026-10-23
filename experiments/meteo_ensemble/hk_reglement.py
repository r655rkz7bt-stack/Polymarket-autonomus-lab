"""Contrôle du règlement des marchés de température de Hong Kong (23/10/2026).

Question : la tranche gagnante d'un marché « highest / lowest temperature in Hong Kong » est-elle
celle qui contient le maximum (minimum) quotidien de l'Observatoire, arrondi comment ?
L'Observatoire publie au dixième (« 32,6 °C ») ; les tranches sont des degrés entiers (« 32°C »).
Données : relevés quotidiens officiels (open data HKO, CLMMAXT / CLMMINT, station HKO) et
événements réglés de Gamma (slug `highest-temperature-in-hong-kong-on-<mois>-<jour>-2026`).
Usage : PYTHONPATH=src python experiments/meteo_ensemble/hk_reglement.py
"""
import json
import math
import time
from pathlib import Path

import requests

H = {"User-Agent": "curl/8"}
D = Path(__file__).parent / "donnees"
D.mkdir(exist_ok=True)
HKO = "https://data.weather.gov.hk/weatherAPI/opendata/opendata.php"
MONTHS = "january february march april may june july august september october november december".split()


def daily(kind: str) -> dict[tuple[int, int], float]:
    path = D / f"{kind}_2026.json"
    if not path.exists():
        r = requests.get(HKO, params={"dataType": kind, "rformat": "json", "station": "HKO", "year": 2026}, timeout=60)
        path.write_text(r.text)
    rows = json.loads(path.read_text())["data"]
    return {(int(r[1]), int(r[2])): float(r[3]) for r in rows if r[3] not in ("***", "")}


def winner(slug: str) -> str | None:
    path = D / f"ev_{slug}.json"
    if not path.exists():
        r = requests.get("https://gamma-api.polymarket.com/events", params={"slug": slug}, headers=H, timeout=60)
        path.write_text(r.text)
        time.sleep(0.2)
    ev = json.loads(path.read_text())
    if not ev:
        return None
    for m in ev[0].get("markets") or []:
        if json.loads(m.get("outcomePrices") or "[]")[:1] == ["1"]:
            return m["question"]
    return None


def bucket_of(question: str):
    from polymarket_agent import weather_model as wm
    return wm.parse_question(question)


def main():
    from polymarket_agent import weather_model as wm
    values = {"highest": daily("CLMMAXT"), "lowest": daily("CLMMINT")}
    rules = {"arrondi": lambda v: math.floor(v + 0.5), "troncature": math.floor}
    ok = {k: 0 for k in rules}
    n = 0
    for kind in ("highest", "lowest"):
        for month in (8, 9):
            for day in range(1, 32):
                v = values[kind].get((month, day))
                if v is None:
                    continue
                q = winner(f"{kind}-temperature-in-hong-kong-on-{MONTHS[month - 1]}-{day}-2026")
                if q is None:
                    continue
                b = wm.parse_question(q)
                if b is None:
                    continue
                n += 1
                line = []
                for name, rule in rules.items():
                    w = rule(v)
                    good = b.low <= w <= b.high
                    ok[name] += good
                    line.append(f"{name} {'oui' if good else 'NON'}")
                print(f"{kind:8} {month:02d}-{day:02d} HKO {v:5.1f} gagnante « {q} » : " + ", ".join(line))
    print(f"\n{n} marchés réglés relus : " + ", ".join(f"{k} {v}/{n}" for k, v in ok.items()))


if __name__ == "__main__":
    main()
