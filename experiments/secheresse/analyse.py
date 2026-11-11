"""Piste n° 24 : D4 par État. Règlement relu sur l'USDM, loi de transition apprise sur 2000-2025, échanges réels classés selon la
dernière carte PUBLIÉE au moment de l'échange (jeudi 8 h 30, heure de l'Est ; aucune carte vue avant sa publication)."""
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ICI = Path(__file__).parent
ET = ZoneInfo("America/New_York")
SEUIL = 0.05
usdm = json.load(open(ICI / "donnees" / "usdm.json"))
marches = json.load(open(ICI / "marches.json"))
echanges = json.load(open(ICI / "donnees" / "echanges.json"))
MOIS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September",
                                     "October", "November", "December"], 1)}


def semaine(titre):
    m = re.search(r"week of (\w+) (\d+), (\d{4})", titre)
    return datetime(int(m.group(3)), MOIS[m.group(1)], int(m.group(2))).date()


def publication(mardi):
    """Jeudi qui suit la carte du mardi, 8 h 30 heure de l'Est, en UTC."""
    jeudi = mardi + timedelta(days=2)
    return datetime(jeudi.year, jeudi.month, jeudi.day, 8, 30, tzinfo=ET).astimezone(timezone.utc)


carte = {e: {r["date"]: r for r in rows} for e, rows in usdm.items()}


def d4(etat, mardi):
    r = carte.get(etat, {}).get(str(mardi))
    return None if r is None else r["d4"]


def classe(r):
    """Case de la loi de transition d'après la carte connue : part en D4 et part en D3."""
    if r["d4"] >= 5:
        return "D4>=5"
    if r["d4"] >= SEUIL:
        return "D4 0,05-5"
    if r["d4"] > 0:
        return "D4 <0,05"
    if r["d3"] >= 10:
        return "D3>=10"
    if r["d3"] >= 1:
        return "D3 1-10"
    if r["d3"] > 0:
        return "D3 <1"
    if r["d2"] > 0:
        return "D2 seul"
    return "rien"


def loi(avant=2026, pas=1):
    """P(D4 >= 0,05 % à la carte t + pas semaines | case de la carte t), 2000 → avant (exclu), tous les États."""
    n, k = defaultdict(int), defaultdict(int)
    for etat, rows in usdm.items():
        rows = [r for r in rows if r["date"] < f"{avant}"]
        for a, b in zip(rows, rows[pas:]):
            c = classe(a)
            n[c] += 1
            k[c] += b["d4"] >= SEUIL
    return {c: ((k[c] + 0.5) / (n[c] + 1), n[c], k[c]) for c in n}


def main():
    L1, L2 = loi(pas=1), loi(pas=2)
    print("Loi de transition 2000-2025 (une et deux semaines) :")
    for c in sorted(L1, key=lambda c: -L1[c][0]):
        print(f"  {c:10} P1 {L1[c][0]:.4f} ({L1[c][2]}/{L1[c][1]})   P2 {L2[c][0]:.4f}")
    # 1. Contrôle du règlement
    ok = bad = manque = 0
    info = {}
    for m in marches:
        if not m["clos"]:
            continue
        w = semaine(m["titre"])
        v = d4(m["etat"], w)
        oui = m["prix"][0] == "1"
        if v is None:
            manque += 1
            continue
        if (v >= SEUIL) == oui:
            ok += 1
        else:
            bad += 1
            print("  règlement différent :", m["etat"], w, v, "OUI" if oui else "NON")
        info[m["condition"]] = (m, w, oui)
    print(f"Règlement : {ok} conformes, {bad} différents, {manque} sans carte")
    # 2. Échanges classés
    seuil = float(sys.argv[1]) if len(sys.argv) > 1 else 0.05
    res = defaultdict(list)
    for t in echanges:
        if t["condition_id"] not in info:
            continue
        m, w, oui = info[t["condition_id"]]
        ts = datetime.fromtimestamp(t["timestamp"], timezone.utc)
        rel = publication(w)
        # dernière carte publiée à l'instant de l'échange
        connu = max((d for d in carte[m["etat"]] if publication(datetime.fromisoformat(d).date()) <= ts), default=None)
        if connu is None:
            continue
        conn = datetime.fromisoformat(connu).date()
        ecart = (w - conn).days // 7      # 0 = carte du marché déjà publiée ; 1 = la carte de la semaine d'avant ; 2…
        r = carte[m["etat"]][connu]
        if ecart <= 0:
            p_oui = 1.0 if r["d4"] >= SEUIL else 0.0
            regime = "après publication"
        else:
            p_oui = (L1 if ecart == 1 else L2)[classe(r)][0]
            regime = f"avant (carte de {ecart} sem.)"
        # le preneur achète le jeton `outcome` au prix `price` (BUY) ou le vend (SELL : on aurait pu acheter l'autre côté à 1 − prix)
        jeton_oui = t["outcome"] == "Yes"
        if t["side"] == "BUY":
            achete_oui, prix = jeton_oui, t["price"]
        else:
            achete_oui, prix = (not jeton_oui), 1 - t["price"]
        p = p_oui if achete_oui else 1 - p_oui
        gagne = oui if achete_oui else (not oui)
        frais = 0.05 * prix * (1 - prix)
        res[regime].append(dict(etat=m["etat"], w=str(w), ts=ts, prix=prix, p=p, gagne=gagne, frais=frais, parts=t["size"],
                                oui=achete_oui, ecart_pub=(ts - rel).total_seconds() / 3600, classe=classe(r)))
    for regime, rows in sorted(res.items()):
        print(f"\n== {regime} : {len(rows)} échanges, {len({(r['etat'], r['w']) for r in rows})} marchés")
        bons = [r for r in rows if r["p"] - r["prix"] - r["frais"] >= seuil]
        mauvais = [r for r in rows if r["p"] - r["prix"] - r["frais"] < -seuil]
        for nom, lot in (("achats que la carte dit bons", bons), ("échanges contre la carte", mauvais)):
            if not lot:
                print(f"  {nom} : 0")
                continue
            mise = sum(r["prix"] * r["parts"] for r in lot)
            gain = sum(((1 if r["gagne"] else 0) - r["prix"] - r["frais"]) * r["parts"] for r in lot)
            g = sum(r["gagne"] for r in lot)
            att = sum(r["p"] for r in lot)
            pay = sum(r["prix"] for r in lot)
            print(f"  {nom} : {len(lot)} échanges, {len({(r['etat'], r['w']) for r in lot})} marchés, gagnés {g} pour {att:.1f} "
                  f"attendus (carte) et {pay:.1f} payés ; {sum(r['parts'] for r in lot):.0f} parts, mise {mise:.0f} $, "
                  f"résultat {gain:+.0f} $ ({gain / mise:+.1%})")
    return res


if __name__ == "__main__":
    main()
