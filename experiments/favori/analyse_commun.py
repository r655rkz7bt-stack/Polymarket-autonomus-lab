"""Fonctions communes aux études du favori (dates, barème de frais estimé, familles)."""
from datetime import datetime


def ts(text):
    try:
        return int(datetime.fromisoformat(str(text).replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None


def fee_rate(tags):  # docs.polymarket.com/trading/fees (16/10/2026), estimé par catégorie
    t = set(tags or [])
    if "geopolitics" in t:
        return 0.0
    if "crypto" in t:
        return 0.07
    if "sports" in t or "esports" in t:
        return 0.05
    if t & {"politics", "finance", "tech", "mentions"}:
        return 0.04
    return 0.05


def family(m):
    t, slug = set(m["tags"] or []), m["slug"] or ""
    if "updown" in slug or "up-or-down" in slug:
        return "crypto hausse/baisse"
    if "crypto" in t:
        return "crypto (seuils)"
    if "esports" in t:
        return "e-sport"
    if "sports" in t:
        return "sport"
    if "weather" in t or "temperature" in slug:
        return "météo"
    if "politics" in t or "elections" in t:
        return "politique"
    if "geopolitics" in t:
        return "géopolitique"
    if t & {"economy", "finance", "fed", "business"}:
        return "économie / finance"
    if t & {"culture", "pop-culture", "movies", "music", "tech", "mentions"}:
        return "culture / tech / mentions"
    return "autres"
