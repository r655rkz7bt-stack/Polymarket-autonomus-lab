"""Événements Gamma d'inflation américaine (CPI / Core CPI / PCE, MoM et YoY), ouverts et clos -> donnees/evenements.json."""
import json, pathlib, re, requests
H = {"User-Agent": "curl/8"}
D = pathlib.Path(__file__).resolve().parent.parent / "donnees"
seen, out = set(), []
for q in ("CPI MoM", "CPI YoY", "Core CPI", "inflation US", "Core PCE", "PCE MoM", "PCE YoY", "CPI inflation"):
    for status in ("closed", "active"):
        for page in range(1, 15):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=30,
                             params={"q": q, "events_status": status, "limit_per_type": 50, "page": page})
            evs = (r.json() or {}).get("events") or []
            for e in evs:
                t = e.get("title", "")
                if e["id"] not in seen and re.search(r"\b(CPI|PCE)\b", t) and re.search(r"MoM|YoY|month|annual|year", t, re.I):
                    seen.add(e["id"]); out.append(e)
            if len(evs) < 50:
                break
full = [requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=30).json() for e in out]
(D / "evenements.json").write_text(json.dumps(full))
for e in sorted(full, key=lambda e: e.get("endDate") or ""):
    print(e["id"], (e.get("endDate") or "")[:10], e.get("closed"), len(e.get("markets") or []), round(float(e.get("volume") or 0)), e["title"])
