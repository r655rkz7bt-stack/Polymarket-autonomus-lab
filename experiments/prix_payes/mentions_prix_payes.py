"""mots_prononces aux PRIX PAYÉS (21/10/2026). Même modèle que ../vingt_pistes/scripts/mentions_taux_historique.py
(taux du mot chez l'orateur, rapproché du taux de l'orateur ; seuls les marchés réglés AVANT la décision),
puis trois façons de compter le prix :
  « horaire »      : prix horaire du CLOB à la décision + 0,02 (méthode du 20/10, reproduite) ;
  « mêmes décisions » : les achats décidés au prix horaire, payés au PREMIER vrai prix de preneur sur le jeton
                     dans la fenêtre après la décision (aucun échange = pas de pari, compté à part) ;
  « décision au prix payé » : on décide avec ce premier vrai prix (comme en direct avec le prix vendeur).
Frais 0,04·p·(1−p) (feeSchedule des marchés mentions, preneur). Lit donnees/mn/data.json,
donnees/prix_payes/mentions_ids.json et le cache des échanges (mentions_releve_echanges.py).
Usage : .venv/bin/python experiments/prix_payes/mentions_prix_payes.py [--detail]"""
import bisect
import json
import math
import os
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(__file__))
from commun import gain, paid, resume, trades  # noqa: E402

FEE, HALF = 0.04, 0.02
d = json.load(open("donnees/mn/data.json"))
ids = json.load(open("donnees/prix_payes/mentions_ids.json"))


def ts(x):
    return datetime.fromisoformat(x.replace("Z", "+00:00")).timestamp() if x else None


rows = [r for r in d["rows"] if ts(r["closed"] or r["end"])]
for r in rows:
    r["c"] = ts(r["closed"] or r["end"])
by_sp = defaultdict(list)
for r in sorted(rows, key=lambda r: r["c"]):
    by_sp[r["sp"]].append(r)
cl_sp = {sp: [x["c"] for x in v] for sp, v in by_sp.items()}
todo = [r for r in d["todo"] if len(r.get("hist") or []) >= 3 and len(r["tok"]) == 2 and not r["sp"].startswith('"')]
for r in todo:
    r["c"] = ts(r["closed"] or r["end"])
    r["cid"] = ids.get(r["tok"][0])
    h0 = r["hist"][0]["t"]
    r["tr"] = trades(r["cid"], h0 + 2 * 3600, h0 + 48 * 3600) if r["cid"] else None


def run(margin, k, minn, delay, minp, win=6, extra=0.0):
    """Rend les paris des trois façons de compter, et le nombre de décisions sans échange."""
    hourly, same, same_h, decided, missing, lags = [], [], [], [], 0, []
    for r in todo:
        h = r["hist"]
        t_ref = h[0]["t"] + delay * 3600
        if t_ref > r["c"] - 3600:
            continue
        p = [x for x in h if x["t"] <= t_ref][-1]["p"]
        if not 0.03 < p < 0.97:
            continue
        j = bisect.bisect_left(cl_sp[r["sp"]], t_ref)
        prior = by_sp[r["sp"]][:j]
        same_w = [x for x in prior if x["w"] == r["w"]]
        if len(same_w) < minn:
            continue
        g = (sum(x["yes"] for x in prior) + 1) / (len(prior) + 2)
        q = (sum(x["yes"] for x in same_w) + k * g) / (len(same_w) + k)
        y = r["yes"]
        mois = datetime.fromtimestamp(t_ref, tz=timezone.utc).strftime("%Y-%m")
        t1 = min(t_ref + win * 3600, r["c"] - 3600)  # jamais d'échange dans la dernière heure avant la clôture
        for side, qq, cost in ((0, q, p + HALF), (1, 1 - q, 1 - p + HALF)):
            won = y if side == 0 else not y
            tok, other = r["tok"][side], r["tok"][1 - side]
            pp = paid(r["tr"], tok, other, t_ref, t1) if r["tr"] is not None else None
            base = {"evenement": r["ev"], "mois": mois, "sp": r["sp"], "side": side, "q": qq}
            if qq - margin > cost and minp <= cost < 0.98:  # décision au prix horaire (méthode du 20/10)
                hourly.append(base | {"gain": gain(won, cost, FEE), "cout": cost, "apparie": pp is not None})
                if pp is None:
                    missing += 1
                else:
                    c = pp[1] + extra
                    if 0 < c < 1:
                        same.append(base | {"gain": gain(won, c, FEE), "cout": c, "horaire": cost, "parts": pp[2]})
                        same_h.append(base | {"gain": gain(won, cost, FEE), "cout": cost})
                        lags.append((pp[0] - t_ref) / 3600)
            if pp is not None:  # décision au premier vrai prix payé
                c = pp[1] + extra
                if qq - margin > c and minp <= c < 0.98 and c > 0:
                    decided.append(base | {"gain": gain(won, c, FEE), "cout": c})
    return hourly, same, same_h, decided, missing, lags


if __name__ == "__main__":
    print("marchés du test", len(todo), "avec échanges relevés", sum(r["tr"] is not None for r in todo))
    SETTINGS = [  # (marge, K, précédents, délai h, billet min)
        (0.05, 2, 3, 2, 0.30), (0.05, 2, 3, 12, 0.30), (0.05, 2, 3, 24, 0.30), (0.05, 2, 3, 6, 0.30),
        (0.03, 2, 3, 2, 0.30), (0.08, 2, 3, 2, 0.30), (0.05, 5, 5, 2, 0.30), (0.05, 2, 3, 2, 0.0)]
    out = {}
    for s in SETTINGS:
        hourly, same, same_h, decided, missing, lags = run(*s)
        print(f"\nréglage marge {s[0]} K {s[1]} précédents {s[2]} délai {s[3]} h billet ≥ {s[4]} (fenêtre 6 h)")
        resume(hourly, "horaire (20/10, reproduit)")
        print(f"  décisions horaires sans aucun échange de preneur dans les 6 h : {missing} sur {len(hourly)}")
        resume([b for b in hourly if not b["apparie"]], "horaire, décisions SANS échange")
        resume(same_h, "horaire, mêmes décisions appariées")
        v = resume(same, "PAYÉ, mêmes décisions")
        resume(decided, "PAYÉ, décision au prix payé")
        if lags:
            print(f"  délai médian décision → échange {st.median(lags):.2f} h ; écart prix payé − horaire+0,02 médian "
                  f"{st.median(b['cout'] - b['horaire'] for b in same):+.3f}")
        out[str(s)] = {"horaire": len(hourly), "sans_echange": missing, "paye": v}
    print("\nsensibilité (réglage principal 0,05 / 2 / 3 / 2 h / 0,30)")
    for win, extra in ((1, 0), (24, 0), (6, 0.01)):
        _, same, _, decided, missing, _ = run(0.05, 2, 3, 2, 0.30, win, extra)
        resume(same, f"fenêtre {win} h, +{extra} : mêmes décisions ({missing} sans échange)")
        resume(decided, f"fenêtre {win} h, +{extra} : décision au prix payé")
    hourly, same, same_h, decided, missing, lags = run(0.05, 2, 3, 2, 0.30)
    print("\ndétail du réglage principal, PAYÉ mêmes décisions")
    v = resume(same, "tous")
    print("  par mois", v["mois"])
    print("  par prix", v["par_prix"])
    resume([b for b in same if b["side"] == 0], "OUI")
    resume([b for b in same if b["side"] == 1], "NON")
    for sp in [k for k, _ in sorted(((sp, sum(b["sp"] == sp for b in same)) for sp in {b["sp"] for b in same}), key=lambda x: -x[1])][:6]:
        resume([b for b in same if b["sp"] == sp], f"orateur {sp[:30]}")
    print("  parts du premier échange : médiane", st.median(b["parts"] for b in same))
    print("  prix horaire à 0,50 pile (carnet vide) :", sum(abs(b["cout"] - 0.52) < 1e-9 for b in hourly), "décisions sur", len(hourly),
          "; retard décision → échange, quartiles (h) :", [round(x, 2) for x in st.quantiles(lags, n=4)])
    print("\npar orateur et délai (décision au prix payé ; « sans A/A » = sans the announcers ni anyone, jugés à part le 21/10)")
    for dl in (2, 6, 12, 24):
        hh, sm, _, dc, _, _ = run(0.05, 2, 3, dl, 0.30)
        for sp in ("trump", "the announcers", "anyone"):
            resume([b for b in hh if b["sp"] == sp], f"{dl} h horaire {sp}")
            resume([b for b in sm if b["sp"] == sp], f"{dl} h PAYÉ mêmes déc. {sp}")
            resume([b for b in dc if b["sp"] == sp], f"{dl} h PAYÉ décidé {sp}")
        resume([b for b in sm if b["sp"] not in ("the announcers", "anyone")], f"{dl} h PAYÉ mêmes déc. sans A/A")
        resume([b for b in dc if b["sp"] not in ("the announcers", "anyone")], f"{dl} h PAYÉ décidé sans A/A")
    print("\ndétail du réglage principal, PAYÉ décision au prix payé")
    v = resume(decided, "tous")
    print("  par mois", v["mois"])
    print("  par prix", v["par_prix"])
    json.dump({"reglages": out, "paris_payes": same, "paris_decides": decided}, open("donnees/prix_payes/mentions_resultats.json", "w"))
