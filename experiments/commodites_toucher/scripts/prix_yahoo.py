"""Prix horaires des contrats à terme (Yahoo Finance, API de graphique, sans clé) : CL=F (WTI), GC=F (or), SI=F (argent), NG=F (gaz naturel).
Sortie : donnees/<symbole>.json = [[t, open, high, low, close], ...] à l'heure (UTC). Usage : .venv/bin/python prix_yahoo.py"""
import json, requests
from pathlib import Path
OUT = Path(__file__).resolve().parents[1] / "donnees"; OUT.mkdir(exist_ok=True)
for sym in ("CL=F", "GC=F", "SI=F", "NG=F", "HG=F"):
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", params={"range": "1y", "interval": "1h"}, headers={"User-Agent": "Mozilla/5.0"}, timeout=60).json()
    res = r["chart"]["result"][0]; q = res["indicators"]["quote"][0]
    rows = [[t, q["open"][i], q["high"][i], q["low"][i], q["close"][i]] for i, t in enumerate(res["timestamp"]) if q["high"][i] is not None]
    json.dump(rows, open(OUT / f"{sym.replace('=', '_')}.json", "w"))
    print(sym, len(rows), rows[0][0], rows[-1][0], rows[-1][4])
