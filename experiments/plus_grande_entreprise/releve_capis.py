"""Relevé pour la piste « plus grande entreprise du monde » (13/11/2026) : capitalisations hebdomadaires (companiesmarketcap.com,
robots.txt relu : pages /<société>/marketcap/ autorisées) et cours quotidiens (Yahoo Finance chart, RECHERCHE seulement).
Sortie : donnees/<SYM>.json (cours) et donnees/<SYM>_mc.json (capitalisation hebdomadaire, unité 100 000 $)."""
import json, re, sys, time
from pathlib import Path
import requests

UA = {"User-Agent": "Mozilla/5.0"}
SOC = {"AAPL": "apple", "NVDA": "nvidia", "MSFT": "microsoft", "GOOGL": "alphabet-google", "AMZN": "amazon",
       "META": "meta-platforms", "AVGO": "broadcom", "TSM": "taiwan-semiconductor-manufacturing", "2222.SR": "saudi-aramco",
       "TSLA": "tesla"}
OUT = Path(__file__).parent / "donnees"
OUT.mkdir(exist_ok=True)
for sym, slug in SOC.items():
    t = requests.get(f"https://companiesmarketcap.com/{slug}/marketcap/", headers=UA, timeout=30).text
    m = re.search(r"data = (\[.*?\]);", t, re.S)
    (OUT / f"{sym}_mc.json").write_text(m.group(1) if m else "[]")
    c = requests.get(f"https://query2.finance.yahoo.com/v8/finance/chart/{sym}?range=5y&interval=1d", headers=UA, timeout=30)
    (OUT / f"{sym}.json").write_text(c.text)
    print(sym, bool(m), c.status_code, len(c.text), file=sys.stderr)
    time.sleep(1)
