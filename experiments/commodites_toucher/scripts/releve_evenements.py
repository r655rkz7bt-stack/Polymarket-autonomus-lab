"""Relevé (24/10/2026) des événements Gamma « What will <matière> hit … » (WTI, or, argent, gaz naturel, cuivre…) : ouverts et réglés.
Sortie : donnees/evenements.json. Usage : .venv/bin/python releve_evenements.py"""
import json, re, requests
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "donnees"; OUT.mkdir(exist_ok=True)
H = {"User-Agent": "curl/8"}
QS = ["What will WTI Crude Oil hit", "What will Gold hit", "What will Silver hit", "What will Natural Gas hit", "What will Copper hit",
      "What will Brent Crude Oil hit", "What will Platinum hit"]
ev = {}
for q in QS:
    for st in ("active", "closed"):
        for p in range(1, 8):
            r = requests.get("https://gamma-api.polymarket.com/public-search", params={"q": q, "events_status": st, "page": p, "limit_per_type": 50}, headers=H, timeout=40).json()
            for e in r.get("events", []):
                if re.match(r"what will .* hit", e["title"], re.I):
                    ev[e["id"]] = e
            if len(r.get("events", [])) < 50:
                break
json.dump(list(ev.values()), open(OUT / "evenements.json", "w"))
import collections
c = collections.Counter()
for e in ev.values():
    kind = "semaine" if "Week of" in e["title"] else "mois" if " in " in e["title"] else "autre"
    c[(re.search(r"\((\w+)\)", e["title"]).group(1) if re.search(r"\((\w+)\)", e["title"]) else e["title"][:20], kind, bool(e["closed"]))] += 1
for k, v in sorted(c.items()): print(k, v)
