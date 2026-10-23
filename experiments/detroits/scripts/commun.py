"""Outils communs du test des détroits (23/10/2026) : règles des marchés PortWatch, séries, retard de publication.

Grandeur réglée :
- tranches hebdomadaires (« How many ships transit … week of … ») : SOMME des passages du premier au dernier jour (7 jours) ;
- tranches « Avg. # of ships transiting … » : MOYENNE sur 7 jours publiée pour la date cible (= somme des 7 jours finissant
  à cette date / 7).
Les deux sont donc la somme S(D) des 7 jours finissant à la date D (D = dernier jour de la semaine, ou date cible).
"""
import csv
import datetime as dt
import json
import re

MOIS = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august",
                                        "september", "october", "november", "december"])}
FICHIERS = {"Strait of Hormuz": "hormuz", "Bab el-Mandeb Strait": "bab", "Suez Canal": "suez", "Panama Canal": "panama"}
DONNEES = "experiments/detroits/donnees"


def serie(nom):
    """{date: passages} depuis le CSV PortWatch téléchargé (portwatch.py)."""
    rows = csv.DictReader(open(f"{DONNEES}/{FICHIERS[nom]}.csv"))
    return {dt.date.fromisoformat(r["jour"]): int(r["n_total"]) for r in rows}


def _date(mois, jour, an="2026"):
    return dt.date(int(an), MOIS[mois.lower()], int(jour))


def cible(ev):
    """(type, date D) : type « somme » (tranches hebdomadaires) ou « moyenne » (moyenne sur 7 jours à D) ; None sinon."""
    d, t = ev["description"], ev["titre"]
    m = re.search(r"from (\w+) (\d+), (\d{4}),? through (\w+) (\d+), (\d{4})", d)
    if m and ("how many ships transit" in t.lower()):
        debut, fin = _date(m.group(1), m.group(2), m.group(3)), _date(m.group(4), m.group(5), m.group(6))
        return ("somme", fin) if (fin - debut).days == 6 else None
    if t.lower().startswith("avg. #"):
        m = re.search(r"reports for (\w+) (\d+), (\d{4})", d)
        if m:
            return "moyenne", _date(*m.groups())
        m = re.search(r" on (\w+) (\d+)\?", t)
        if m:
            return "moyenne", _date(m.group(1), m.group(2))
    return None


TRANCHE = re.compile(r"(?:(?:fewer|less) than (\d+)|between (\d+) and (\d+)|(\d+)-(\d+)|(\d+) or more)\s+(?:average daily transits|ships|on )", re.I)


def etiquette(question):
    """(bas, haut) lus dans la question ; None = ouvert. « 220-229 ships » → (220, 229)."""
    m = TRANCHE.search(question or "")
    if not m:
        return None
    if m.group(1):
        return (None, float(m.group(1)))
    if m.group(6):
        return (float(m.group(6)), None)
    lo, hi = (m.group(2), m.group(3)) if m.group(2) else (m.group(4), m.group(5))
    return float(lo), float(hi)


def intervalles(questions, lecture="plancher"):
    """{id du marché: [bas, haut[} pour un événement. Tranches jointives (« 0 et 10 », « 10 et 20 » : la valeur exactement
    entre deux va à la plus haute) → [bas, haut[. Tranches entières (« 25 et 27 », « 28 et 30 », « 220-229 ») → [bas, haut + 1[
    (« plancher ») ou [bas − 0,5, haut + 0,5[ (« arrondi »). Les bornes ouvertes : « fewer than 25 » → ]−∞, 25[ ;
    « 40 or more » → [40, ∞[ (avec la même lecture que les autres tranches pour la frontière)."""
    lab = {q["id"]: etiquette(q["question"]) for q in questions}
    lab = {k: v for k, v in lab.items() if v}
    fermees = sorted(v for v in lab.values() if v[0] is not None and v[1] is not None)
    jointif = any(b[0] == a[1] for a, b in zip(fermees, fermees[1:]))
    out = {}
    for k, (lo, hi) in lab.items():
        if jointif:
            a, b = (lo if lo is not None else -1e9), (hi if hi is not None else 1e9)
        else:
            dec = 0.5 if lecture == "arrondi" else 0.0
            a = -1e9 if lo is None else lo - dec
            b = 1e9 if hi is None else (hi - dec if lo is None else hi + 1 - dec)
        out[k] = (a, b)
    return out


def valeur(type_, s7):
    return s7 if type_ == "somme" else s7 / 7


def somme7(series, d):
    jours = [series.get(d - dt.timedelta(days=k)) for k in range(7)]
    return None if any(v is None for v in jours) else sum(jours)


def gagnant(ev):
    """Identifiant du marché gagnant (prix final 1) ou None."""
    for q in ev["questions"]:
        p = json.loads(q["outcomePrices"]) if isinstance(q["outcomePrices"], str) else q["outcomePrices"]
        if p and str(p[0]) == "1":
            return q["id"]
    return None


def connu_jusqua(t: dt.datetime, heure_maj=11):
    """Dernier jour publié par PortWatch à l'instant t (UTC) : mise à jour le mardi vers `heure_maj` h UTC, jusqu'au dimanche
    précédent (rythme mesuré, voir controle_reglement.py)."""
    mardi = t.date() - dt.timedelta(days=(t.weekday() - 1) % 7)
    if mardi == t.date() and t.hour + t.minute / 60 < heure_maj:
        mardi -= dt.timedelta(days=7)
    return mardi - dt.timedelta(days=2)


def taux_frais(q):
    fs = q.get("feeSchedule") if isinstance(q.get("feeSchedule"), dict) else {}
    return float(fs.get("rate") or 0) if q.get("feesEnabled") else 0.0


def ts(text):
    if not text:
        return None
    text = str(text).replace(" ", "T")
    if text.endswith("+00"):
        text += ":00"
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def charge_inventaire():
    return json.load(open(f"{DONNEES}/inventaire.json"))
