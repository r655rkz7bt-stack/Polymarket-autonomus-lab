"""Relevé des messages comptés par XTracker (un fichier par compte), pour le calibrage et le test
contre le marché. À lancer depuis la racine du dépôt ; écrit donnees/xt/<compte>.json."""
import json
import os

import requests

D = "donnees/xt"
os.makedirs(D, exist_ok=True)
for handle in ("elonmusk", "WhiteHouse", "realDonaldTrump", "tedcruz", "ZelenskyyUa", "NYCMayor", "cz_binance", "khamenei_ir"):
    posts = requests.get(f"https://xtracker.polymarket.com/api/users/{handle}/posts", timeout=60).json()["data"]
    times = sorted(p["createdAt"] for p in posts)
    json.dump(times, open(f"{D}/{handle}.json", "w"))
    print(handle, len(times), "messages depuis le", times[0][:10])
