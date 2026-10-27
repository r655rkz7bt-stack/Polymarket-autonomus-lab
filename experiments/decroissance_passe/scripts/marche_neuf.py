"""27/10/2026 : `marche_neuf` (favori d'un marché de moins de 24 h, prix 0,60-0,88, renforcé) rejouée sur les marchés « d'ici / avant » hors sport du relevé (6 511 marchés avec échanges).
À T = création + h (h = 2, 6, 12, 23 heures) : prix du OUI = dernier échange dans les 3 h avant T ; le favori est le côté à >= 0,5 ; si son prix est dans [0,60 ; 0,88], achat au premier échange
réel de preneur sur ce côté dans les 6 h après T, frais payés ; règlement Gamma. Un pari par marché et par h. Lancer depuis la racine."""
import sys, json, math, collections
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/decroissance_passe/scripts")
import analyse as a
from polymarket_agent import idea_test as it
EV = a.charge(("marches.jsonl", "marches_tags.jsonl"))
def paris(h, lo=0.60, hi=0.88):
    res = []
    for e, by_all in EV:
        for m in e["markets"]:
            try:
                op = [float(x) for x in json.loads(m["outcomePrices"])]; yes, no = json.loads(m["clobTokenIds"]); outs = json.loads(m["outcomes"])
            except Exception: continue
            if outs != ["Yes", "No"] or max(op) < 0.99: continue
            start = a.ts(m.get("startDate")); closed = a.ts(m.get("closedTime"))
            if not start: continue
            T = start + int(h * 3600)
            if closed and T > closed - 3600: continue
            by = {yes: by_all.get(yes, []), no: by_all.get(no, [])}
            now = a.prix_oui(by, yes, no, T - 3 * 3600, T)
            if now is None: continue
            side = 0 if now >= 0.5 else 1; fav = now if side == 0 else 1 - now
            if not lo <= fav <= hi: continue
            pay = a.premier_achat_non(by, no, yes, T, 6 * 3600) if side == 0 else a.premier_achat_non(by, yes, no, T, 6 * 3600)
            if pay is None or not lo - 0.05 <= pay <= hi + 0.05: continue
            rate = ((m.get("feeSchedule") or {}).get("rate")) or 0.0; f = it.fee(pay, rate); win = op[side] > 0.5
            res.append(dict(eid=e["id"], mid=m["id"], H=h, now=now, pay=pay, win=win, fee=f, gain=(win - pay - f) / (pay + f), mois=(m.get("endDate") or "")[:7], titre=m["question"][:70], side=side))
    return res
if __name__ == "__main__":
    for h in (2, 6, 12, 23):
        R = paris(h); print("h =", h, "heures après la création :", a.resume(R))
        print("     favori OUI :", a.resume([r for r in R if r["side"] == 0]), "| favori NON :", a.resume([r for r in R if r["side"] == 1]))
