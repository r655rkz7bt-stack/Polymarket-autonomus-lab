"""Marchés Wrapped réglés (2024, 2025) : prix de chaque issue à J-20 (13/11) et J-7 avant la publication de Spotify Wrapped.
Sortie : donnees/prix_regles.json ; affiche le favori à chaque date et le gagnant."""
import json, sys, time, datetime as dt
from pathlib import Path
import requests
D = Path(__file__).parent / "donnees"
H = {"User-Agent": "curl/8"}
EVS = [14894, 35754, 53297, 79034, 79112, 79118, 81652, 81653]
DATES = {"2024": ["2024-11-13", "2024-11-27", "2024-12-03"], "2025": ["2025-11-13", "2025-11-26", "2025-12-02"]}
out = []
for ev in EVS:
    e = requests.get(f"https://gamma-api.polymarket.com/events/{ev}", headers=H, timeout=30).json()
    an = "2024" if "2024" in e["title"] else "2025"
    lignes = []
    for m in e["markets"]:
        op = json.loads(m.get("outcomePrices") or "[]")
        if not op:
            continue
        tok = json.loads(m["clobTokenIds"])[0]
        px = {}
        for d in DATES[an]:
            t = int(dt.datetime.fromisoformat(d + "T12:00:00+00:00").timestamp())
            r = requests.get("https://clob.polymarket.com/prices-history", params=dict(market=tok, startTs=t - 6 * 3600, endTs=t + 6 * 3600, fidelity=60), timeout=30)
            h = r.json().get("history", []) if r.status_code == 200 else []
            px[d] = h[len(h) // 2]["p"] if h else None
            time.sleep(0.1)
        lignes.append({"issue": m.get("groupItemTitle"), "gagne": op[0] in ("1", "1.0"), "prix": px, "volume": float(m.get("volume") or 0)})
    out.append({"id": ev, "titre": e["title"], "an": an, "issues": lignes})
    print("##", e["title"])
    for d in DATES[an]:
        cot = sorted([(l["prix"][d] or 0, l["issue"], l["gagne"]) for l in lignes], reverse=True)[:3]
        print("  ", d, " ; ".join(f"{i} {p:.3f}{' (G)' if g else ''}" for p, i, g in cot))
json.dump(out, open(D / "prix_regles.json", "w"), ensure_ascii=False, indent=1)
