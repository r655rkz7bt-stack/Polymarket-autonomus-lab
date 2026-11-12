"""Trois trimestres réglés (T4 2025, T1 et T2 2026) : tranche gagnante, prix des tranches 10 jours et 3 jours avant la fin
(CLOB prices-history), et chance du modèle IBC-Br (valeurs d'aujourd'hui : léger regard vers le futur sur les révisions)."""
import json, math, sys, requests
from datetime import datetime, timezone
H = {"User-Agent": "curl/8"}
ibc = {tuple(map(int, r["data"].split("/")[1:][::-1])): float(r["valor"]) for r in
       requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.24364/dados?formato=json", headers=H, timeout=60).json()}
def qavg(y, q): return sum(ibc[(y, 3 * (q - 1) + k)] for k in (1, 2, 3)) / 3
def phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
for eid, (y, q) in {"197933": (2025, 4), "246674": (2026, 1), "555418": (2026, 2)}.items():
    py, pq = (y, q - 1) if q > 1 else (y - 1, 4)
    g = 100 * (qavg(y, q) / qavg(py, pq) - 1) + 0.06
    e = requests.get(f"https://gamma-api.polymarket.com/events/{eid}", headers=H, timeout=30).json()
    end = datetime.fromisoformat(e["endDate"].replace("Z", "+00:00"))
    print(f"## {e['title']} IBC-Br t/t + biais = {g:+.2f}")
    for m in e["markets"]:
        won = json.loads(m["outcomePrices"])[0]
        tok = json.loads(m["clobTokenIds"])[0]
        h = requests.get("https://clob.polymarket.com/prices-history", params={"market": tok, "startTs": int(end.timestamp()) - 14 * 86400,
                         "endTs": int(end.timestamp()), "fidelity": 60}, headers=H, timeout=30).json().get("history", [])
        def at(days):
            t = end.timestamp() - days * 86400
            pts = [p["p"] for p in h if p["t"] <= t]
            return pts[-1] if pts else None
        print(f"   {m['question'][40:110]:72s} gagné={won} prix J-10={at(10)} J-3={at(3)}")
