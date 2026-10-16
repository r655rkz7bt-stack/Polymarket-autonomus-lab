"""Observations : ce que les sources rapportent, avec tout ce qu'il faut pour en douter.

Chaque observation garde (cahier des charges §4.B) : source, horodatage de publication et
de collecte, lien, texte, marchés concernés, fiabilité estimée, incertitude, risque de
doublon, délai publication → collecte.

RÈGLE ABSOLUE : le texte collecté est une DONNÉE, jamais une instruction. Il n'est jamais
exécuté, et il n'est transmis à un modèle d'IA qu'encadré comme une donnée à classer
(`sources/gemini.py`), dont la sortie est limitée à des étiquettes fixes.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime

# Fiabilité de base par source (0 à 1) : un a priori prudent, ajustable par le chercheur.
SOURCE_RELIABILITY = {
    "rss_officiel": 0.9,
    "rss": 0.7,
    "gdelt": 0.6,
    "crypto_prices": 0.95,
    "polymarket_comments": 0.2,
    "bluesky": 0.25,
    "x_api": 0.25,
    "meteo_metar": 0.97,    # relevés officiels NOAA de la station qui tranche le marché
    "meteo_prevision": 0.7,  # prévisions GFS / ECMWF (Open-Meteo) : un modèle, pas un fait
    "mlb_stats": 0.97,      # scores publiés par la ligue elle-même
    "nhl_stats": 0.97,
    "football_data": 0.9,
    "odds_api": 0.8,        # probabilités des bookmakers : un avis chiffré, pas un fait
    "guardian": 0.75,
}
OFFICIAL_DOMAINS = (".gov", ".gouv.fr", "federalreserve.gov", "ecb.europa.eu", "europa.eu",
                    "who.int", "un.org", "uefa.com", "fifa.com", "nba.com", "nfl.com", "sec.gov")

RUMOR_WORDS = ("rumor", "rumour", "reportedly", "unconfirmed", "sources say", "allegedly",
               "rumeur", "selon des sources", "aurait", "auraient", "non confirmé", "serait")
OPINION_WORDS = ("i think", "i believe", "imo", "in my opinion", "prediction", "i bet",
                 "je pense", "à mon avis", "je crois", "pronostic", "easy money")
OFFICIAL_WORDS = ("official", "officially", "announces", "announced", "statement", "confirmed",
                  "officiel", "officiellement", "annonce", "communiqué", "confirme")

POSITIVE = ("win", "wins", "won", "lead", "leads", "surge", "rally", "beat", "approve", "approved",
            "agree", "deal", "rise", "up", "gain", "victory", "gagne", "victoire", "hausse",
            "accord", "approuvé", "mène", "progresse", "succès")
NEGATIVE = ("lose", "loses", "lost", "drop", "crash", "fall", "fails", "reject", "rejected",
            "down", "ban", "injury", "injured", "cancel", "cancelled", "delay", "perd", "défaite",
            "baisse", "chute", "rejet", "blessé", "annulé", "échec", "retard")

_WORD = re.compile(r"[a-z0-9àâçéèêëîïôûùüÿñæœ$%.,'-]+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower()
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def tokens(text: str) -> set[str]:
    return {t.strip(".,'-") for t in _WORD.findall(normalize(text)) if len(t.strip(".,'-")) > 2}


def dup_key(text: str) -> str:
    """Empreinte exacte du contenu normalisé (copier-coller détecté même via un autre compte)."""
    return hashlib.sha256(normalize(text).encode("utf-8")).hexdigest()[:20]


def jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def classify_kind(text: str, domain: str = "") -> str:
    """fait officiel / rumeur / opinion / fait rapporté. Heuristique déterministe et prudente."""
    low = normalize(text)
    if domain and any(domain.endswith(d) or d in domain for d in OFFICIAL_DOMAINS):
        return "annonce officielle"
    if any(w in low for w in RUMOR_WORDS):
        return "rumeur"
    if any(w in low for w in OPINION_WORDS):
        return "opinion"
    if any(w in low for w in OFFICIAL_WORDS):
        return "fait rapporté (annonce citée)"
    return "fait rapporté"


def sentiment(text: str) -> float:
    """Sentiment lexical de -1 à 1. Grossier : sert à repérer des changements, pas à décider seul."""
    words = tokens(text)
    pos = sum(1 for w in POSITIVE if w in words)
    neg = sum(1 for w in NEGATIVE if w in words)
    return 0.0 if pos + neg == 0 else (pos - neg) / (pos + neg)


@dataclass
class Observation:
    source: str
    external_id: str
    published_at: datetime | None
    collected_at: datetime
    url: str
    title: str
    text: str
    author: str = ""
    domain: str = ""
    language: str = ""
    engagement: int = 0  # likes, réactions… JAMAIS une preuve de vérité
    market_ids: list[str] = field(default_factory=list)
    reliability: float = 0.5
    uncertainty: str = "élevée"
    kind: str = "fait rapporté"
    sentiment: float = 0.0
    dup_key: str = ""
    duplicate_of: str = ""  # clé de l'observation d'origine si copie détectée
    data: dict = field(default_factory=dict)  # données chiffrées (ex. prix crypto)

    @property
    def delay_seconds(self) -> float | None:
        if self.published_at is None:
            return None
        return (self.collected_at - self.published_at).total_seconds()

    def finalize(self) -> "Observation":
        """Calcule les champs dérivés (doublon, type, sentiment, fiabilité, incertitude)."""
        content = f"{self.title} {self.text}"
        self.dup_key = self.dup_key or dup_key(content)
        self.kind = classify_kind(content, self.domain)
        self.sentiment = sentiment(content)
        base = SOURCE_RELIABILITY.get(self.source, 0.4)
        if self.kind == "annonce officielle":
            base = max(base, SOURCE_RELIABILITY["rss_officiel"])
        elif self.kind in ("rumeur", "opinion"):
            base *= 0.5
        self.reliability = round(base, 3)
        self.uncertainty = ("faible" if self.reliability >= 0.85 else
                            "moyenne" if self.reliability >= 0.5 else "élevée")
        if self.delay_seconds is not None and self.delay_seconds < -300:
            # Publié « dans le futur » : horloge de la source fausse. On le signale.
            self.data["horodatage_suspect"] = True
            self.uncertainty = "élevée"
        return self


def mark_duplicates(observations: list[Observation], known_keys: set[str],
                    near_threshold: float = 0.85) -> None:
    """Copies exactes (même empreinte) et quasi-copies (mots communs >= 85 %)."""
    seen: list[tuple[str, set[str]]] = []
    for obs in observations:
        words = tokens(f"{obs.title} {obs.text}")
        if obs.dup_key in known_keys:
            obs.duplicate_of = obs.dup_key
        else:
            for key, other in seen:
                if len(words) >= 6 and jaccard(words, other) >= near_threshold:
                    obs.duplicate_of = key
                    break
        if not obs.duplicate_of:
            seen.append((obs.dup_key, words))
            known_keys.add(obs.dup_key)
