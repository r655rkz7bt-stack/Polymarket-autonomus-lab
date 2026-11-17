"""Piste n° 69 : le METAR dit « il a plu » avant que le marché « Where will it rain on <date>? » ne cote le OUI à ~1 ?

Pour chaque marché réglé : jour climatique = minuit-minuit heure LOCALE STANDARD (règle du marché) ; T_oui = premier METAR (routine
ou spécial) du jour avec p01i ≥ 0,01 pouce, + `RETARD` minutes (diffusion du METAR). Achat = premier VRAI échange « Yes / BUY » après
T_oui (un preneur a payé ce prix à un vendeur : prix exécutable), au plus `FENETRE` heures après ; on regarde aussi la quantité
achetée à ≤ prix + 0,02 dans l'heure. Frais : 0,05 × p × (1 − p) par part (weather_fees), 0 sinon. Jamais de regard vers le futur :
T_oui n'utilise que des METAR publiés avant l'achat. Contrôle du règlement : CLI (IEM) contre prix final Gamma.
Usage : python analyse.py [RETARD_MIN] [FENETRE_H]"""
import bisect
import csv
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from polymarket_agent.idea_test import verdict  # noqa: E402

D = Path(__file__).parent / "donnees"
RETARD = float(sys.argv[1]) if len(sys.argv) > 1 else 10.0
FENETRE = float(sys.argv[2]) if len(sys.argv) > 2 else 48.0
DECALAGE = {"LAX": -8, "SFO": -8, "SEA": -8, "PHX": -7, "DEN": -7, "IAH": -6, "DFW": -6, "MSY": -6, "MDW": -6,
            "MIA": -5, "ATL": -5, "DCA": -5, "PHL": -5, "NYC": -5, "BOS": -5}
MOIS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september",
                                     "october", "november", "december"], 1)}


def jour(titre):
    if "4th of July" in titre:
        return datetime(2026, 7, 4)
    m = re.search(r"on (\w+) (\d+)\?", titre)
    return datetime(2026, MOIS[m.group(1).lower()], int(m.group(2)))


def metar(st):
    out = []
    for r in csv.DictReader(open(D / f"metar_{st}.csv")):
        v = r["p01i"]
        if v in ("M", ""):
            continue
        x = 0.0001 if v == "T" else float(v)
        out.append((datetime.strptime(r["valid"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc), x))
    return sorted(out)


def cli(st):
    d = json.load(open(D / f"cli_{st}.json"))["results"]
    return {r["valid"]: (0.0001 if r["precip"] == "T" else r["precip"]) for r in d}


def main():
    ms = [m for m in json.load(open(D / "marches.json")) if m["station"] and m["closed"]]
    tr = defaultdict(list)
    for l in open(D / "echanges.jsonl"):
        t = json.loads(l)
        tr[t["cond"]].append(t)
    for v in tr.values():
        v.sort(key=lambda t: t["ts"])
    met = {st: metar(st) for st in DECALAGE}
    cl = {st: cli(st) for st in DECALAGE}
    paris, ctrl, ctrl_metar, sans_achat = [], [0, 0], [0, 0, 0], 0
    for m in ms:
        st, j = m["station"], jour(m["titre"])
        oui = m["prix_final"][0] == "1"
        if m["prix_final"] not in (["1", "0"], ["0", "1"]):
            continue
        p = cl[st].get(j.strftime("%Y-%m-%d"))
        if p not in (None, "M"):
            ctrl[0] += 1
            ctrl[1] += (p >= 0.01) == oui
        debut = j.replace(tzinfo=timezone.utc) - timedelta(hours=DECALAGE[st])
        fin = debut + timedelta(hours=24)
        obs = [(t, x) for t, x in met[st] if debut <= t < fin]
        t_oui = next((t for t, x in obs if x >= 0.01), None)
        if t_oui is None:
            continue
        ctrl_metar[0] += 1
        ctrl_metar[1] += oui
        t_dec = t_oui + timedelta(minutes=RETARD)
        lst = tr.get(m["condition"], [])
        ts = [t["ts"] for t in lst]
        i = bisect.bisect_left(ts, t_dec.timestamp())
        achat = next((t for t in lst[i:] if t["outcome"] == "Yes" and t["side"] == "BUY"
                      and t["ts"] <= (t_dec + timedelta(hours=FENETRE)).timestamp()), None)
        if achat is None:
            sans_achat += 1
            continue
        px = achat["price"]
        prof = sum(t["size"] for t in lst[i:] if t["outcome"] == "Yes" and t["side"] == "BUY" and t["price"] <= px + 0.02
                   and achat["ts"] <= t["ts"] <= achat["ts"] + 3600)
        frais = 0.05 * px * (1 - px) if m["feeType"] == "weather_fees" else 0.0
        gain = ((1.0 if oui else 0.0) - px - frais) / px
        paris.append({"gain": gain, "evenement": m["event"], "mois": j.strftime("%Y-%m"), "cout": px, "oui": oui,
                      "prof": prof, "st": st, "delai_h": (achat["ts"] - t_oui.timestamp()) / 3600, "fin_jour": achat["ts"] < fin.timestamp(),
                      "q": m["question"], "date": j.strftime("%m-%d")})
    print(f"RETARD {RETARD} min, FENETRE {FENETRE} h ; marchés réglés {len(ms)}")
    print(f"contrôle du règlement : CLI ≥ 0,01 = prix final {ctrl[1]}/{ctrl[0]}")
    print(f"METAR ≥ 0,01 dans le jour : {ctrl_metar[0]} marchés, réglés OUI {ctrl_metar[1]} ; sans achat de OUI ensuite : {sans_achat}")
    for nom, f in [("tous", lambda b: True), ("prix < 0,97", lambda b: b["cout"] < 0.97), ("prix < 0,90", lambda b: b["cout"] < 0.90),
                   ("prof ≥ 20 parts", lambda b: b["prof"] >= 20), ("< 0,97 et ≥ 20 parts", lambda b: b["cout"] < 0.97 and b["prof"] >= 20),
                   ("pendant le jour", lambda b: b["fin_jour"])]:
        bs = [b for b in paris if f(b)]
        if not bs:
            continue
        v = verdict(bs, min_bets=10)
        g = sum(b["oui"] for b in bs)
        att = sum(b["cout"] for b in bs)
        print(f"  {nom:22s} n={len(bs):4d} gagnés {g} pour {att:.1f} attendus, rendement {100*sum(b['gain'] for b in bs)/len(bs):+.2f} % "
              f"; verdict {v.get('verdict')} t_ev {v.get('t_evenement', v.get('t_event'))} mois {v.get('mois')}")
    perdus = [b for b in paris if not b["oui"]]
    for b in perdus[:15]:
        print("  PERDU", b["st"], b["date"], b["cout"], round(b["delai_h"], 2), b["q"][:60])
    json.dump(paris, open(D / f"paris_{int(RETARD)}_{int(FENETRE)}.json", "w"))


if __name__ == "__main__":
    main()
