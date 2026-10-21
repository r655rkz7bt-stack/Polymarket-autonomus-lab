"""compteur_tweets_non aux PRIX PAYÉS (21/10/2026). Cas de tweets_cas.py (modèle inchangé de compteur_tweets),
achats de NON seulement, sans NYC Mayor. Trois façons de compter le prix :
  « horaire »            : prix horaire du CLOB + demi-écart (0,01 Elon, 0,02 les autres), méthode du 21/10 ;
  « mêmes décisions »    : les achats décidés au prix horaire, payés au PREMIER vrai prix de preneur sur le
                           jeton NON dans la fenêtre (achat du NON, ou vente du OUI à p = NON à 1 − p) ;
  « décision au prix payé » : on décide avec ce premier vrai prix (comme en direct avec le prix vendeur).
Aucun échange dans la fenêtre (ou avant la fin de la période) = pas de pari, compté à part.
Frais 0,05·p·(1−p) (feeSchedule des marchés de tweets, preneur). Usage : tweets_prix_payes.py"""
import json
import os
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from commun import cached, gain, paid, resume, tstat  # noqa: E402
from tweets_releve_echanges import LOURD, SETTINGS  # noqa: E402

FEE = 0.05
ev = json.load(open("donnees/xt/marches.json"))
ids = json.load(open("donnees/prix_payes/tweets_ids.json"))
start6 = {e["slug"]: int(datetime.fromisoformat(e["debut"]).timestamp()) + 6 * 3600 for e in ev}
CASES = {d: json.load(open(f"donnees/prix_payes/tweets_cas_{d}.json")) for d in sorted({s[0] for s in SETTINGS})}


def rows_for(c):
    m = ids.get(c["slug"], {}).get(c["titre"])
    if not m or not m["cid"] or len(m["tok"]) != 2:
        return None, None
    if m["vol"] <= LOURD:
        return m, cached(m["cid"], start6[c["slug"]], c["fin"])
    return m, cached(m["cid"], c["t"], min(c["t"] + 24 * 3600, c["fin"]))  # lourde : relevée après chaque achat horaire


def run(disp, margin, minp, win=6, extra=0.0, all_sides=False):
    hourly, same, same_h, decided, missing = [], [], [], [], 0
    for c in CASES[disp]:
        if c["h"] == "NYCMayor" and not all_sides:
            continue
        spread = 0.01 if c["h"] == "elonmusk" else 0.02
        mois = datetime.fromtimestamp(c["t"], tz=timezone.utc).strftime("%Y-%m")
        base = {"evenement": c["slug"], "mois": mois, "h": c["h"], "b": tuple(c["b"]), "t": c["t"], "fin": c["fin"]}
        for side in ((0, 1) if all_sides else (1,)):
            qq, cost = (c["q"], c["p"] + spread) if side == 0 else (1 - c["q"], 1 - c["p"] + spread)
            won = c["won"] if side == 0 else not c["won"]
            hourly_buy = max(0.01, minp) <= cost < 0.99 and qq - margin > cost
            if all_sides:
                if hourly_buy:
                    hourly.append(base | {"gain": gain(won, cost, FEE), "cout": cost, "side": side})
                continue
            m, rows = rows_for(c)
            pp = None
            if rows is not None:
                pp = paid(rows, m["tok"][1], m["tok"][0], c["t"], min(c["t"] + win * 3600, c["fin"]))
            if hourly_buy:
                hourly.append(base | {"gain": gain(won, cost, FEE), "cout": cost, "apparie": pp is not None})
                if pp is None:
                    missing += 1
                elif 0 < pp[1] + extra < 1:
                    k = pp[1] + extra
                    same.append(base | {"gain": gain(won, k, FEE), "cout": k, "horaire": cost, "parts": pp[2],
                                        "retard": (pp[0] - c["t"]) / 3600})
                    same_h.append(base | {"gain": gain(won, cost, FEE), "cout": cost})
            if pp is not None:
                k = pp[1] + extra
                if max(0.01, minp) <= k < 0.99 and qq - margin > k:
                    decided.append(base | {"gain": gain(won, k, FEE), "cout": k})
    return hourly, same, same_h, decided, missing


def first_per_bucket(bets):
    seen, out = set(), []
    for b in sorted(bets, key=lambda b: b["t"]):
        if (b["evenement"], b["b"]) not in seen:
            seen.add((b["evenement"], b["b"]))
            out.append(b)
    return out


def detail(bets, label):
    print(f"\ndétail {label}")
    v = resume(bets, "tous")
    if not v:
        return
    print("  par mois", v["mois"])
    print("  par prix", v["par_prix"])
    for h in sorted({b["h"] for b in bets}):
        resume([b for b in bets if b["h"] == h], f"compte {h}")
    resume([b for b in bets if b["mois"] <= "2026-08"], "1re moitié (juillet-août)")
    resume([b for b in bets if b["mois"] >= "2026-09"], "2e moitié (septembre-octobre)")
    resume([b for b in bets if b["fin"] - b["t"] <= 48 * 3600], "48 dernières heures")
    resume([b for b in bets if b["fin"] - b["t"] > 48 * 3600], "5 premiers jours")
    resume(first_per_bucket(bets), "premier achat par tranche et période")
    ev = defaultdict(list)
    for b in bets:
        ev[b["evenement"]].append(b["gain"])
    pg = sorted(st.mean(v) for v in ev.values())
    print(f"  par période sans les 3 meilleures : {st.mean(pg[:-3]):+.3f} (t {tstat(pg[:-3]):+.2f}) ; périodes gagnantes {sum(x > 0 for x in pg)}/{len(pg)}")


if __name__ == "__main__":
    h_all, *_ = run(12.0, 0.03, 0.10, all_sides=True)
    print("contrôle : mère compteur_tweets (OUI et NON, tous comptes) au prix horaire")
    resume(h_all, "mère, horaire (21/10 : 4 389 achats, +12,2 %)")
    out = {}
    for s in SETTINGS:
        hourly, same, same_h, decided, missing = run(*s)
        print(f"\nréglage dispersion {s[0]} marge {s[1]} billet ≥ {s[2]} (NON sans NYC Mayor, fenêtre 6 h)")
        resume(hourly, "horaire (21/10, reproduit)")
        print(f"  décisions horaires sans aucun échange de preneur dans les 6 h : {missing} sur {len(hourly)}")
        resume([b for b in hourly if not b["apparie"]], "horaire, décisions SANS échange")
        resume(same_h, "horaire, mêmes décisions appariées")
        v = resume(same, "PAYÉ, mêmes décisions")
        resume(first_per_bucket(same), "PAYÉ, mêmes décisions, 1er par tranche")
        resume(decided, "PAYÉ, décision au prix payé")
        if same:
            print(f"  délai médian décision → échange {st.median(b['retard'] for b in same):.2f} h ; écart prix payé − "
                  f"(horaire + écart) médian {st.median(b['cout'] - b['horaire'] for b in same):+.3f}, moyen "
                  f"{st.mean(b['cout'] - b['horaire'] for b in same):+.3f}")
        out[str(s)] = {"horaire": len(hourly), "sans_echange": missing, "paye": v}
    print("\nsensibilité (réglage principal 12 / 0,03 / 0,10)")
    for win, extra in ((0.5, 0), (1, 0), (2, 0), (24, 0), (6, 0.01)):
        _, same, same_h, decided, missing = run(12.0, 0.03, 0.10, win, extra)
        resume(same_h, f"fenêtre {win} h : horaire des décisions appariées")
        resume(same, f"fenêtre {win} h, +{extra} : mêmes décisions ({missing} sans échange)")
        resume(decided, f"fenêtre {win} h, +{extra} : décision au prix payé")
    hourly, same, same_h, decided, missing = run(12.0, 0.03, 0.10)
    detail(hourly, "réglage principal, HORAIRE (référence du 21/10)")
    detail(same, "réglage principal, PAYÉ mêmes décisions")
    detail(decided, "réglage principal, PAYÉ décision au prix payé")
    print("\nparts du premier échange (mêmes décisions) : médiane", st.median(b["parts"] for b in same))
    print("\ntranche de prix PAYÉ 0,30-0,70 (repérée le 21/10 au prix horaire : 0,30-0,60 +39 %) et ≥ 0,70, six réglages")
    for s in SETTINGS:
        _, sm, _, dc, _ = run(*s)
        resume([b for b in sm if 0.30 <= b["cout"] < 0.70], f"{s} mêmes déc. 0,30-0,70")
        resume([b for b in dc if 0.30 <= b["cout"] < 0.70], f"{s} décidé 0,30-0,70")
        resume([b for b in dc if b["cout"] >= 0.70], f"{s} décidé ≥ 0,70")
    detail([b for b in decided if 0.30 <= b["cout"] < 0.70], "réglage principal, décidé au prix payé 0,30-0,70")
    json.dump({"reglages": out, "paris_payes": same, "paris_decides": decided}, open("donnees/prix_payes/tweets_resultats.json", "w"),
              default=list)
