"""Sélection adverse des ordres posés, sur l'historique (28/10/2026) : tennis (ATP, WTA) et e-sport, favori à 0,75-0,95 à T (dernier prix échangé de moins de 3 h).
Ordre posé : achat du favori à (prix de T − 1 centime) valable `VIE` heures ; servi au premier échange de preneur qui vend à ce prix ou en dessous (règle prudente du simulateur).
Comparaison, sur les MÊMES matchs : achat immédiat au premier échange de preneur après T. T = coup d'envoi + `dec` heures (négatif : avant le match)."""
import sys, math, os, json
sys.path.insert(0, "experiments/sauts_en_jeu/scripts"); sys.path.insert(0, "src")
import analyse as a
from polymarket_agent import idea_test as it
VIE = float(os.environ.get("VIE", 3))
COUPE = os.environ.get("COUPE") == "1"   # COUPE=1 : l'ordre posé avant le match tombe au coup d'envoi (aucune exécution après)
HORS = os.environ.get("HORS") == "1"     # HORS=1 : seulement les exécutions APRÈS le coup d'envoi d'un ordre posé avant (sélection adverse pure)
def run(MS, dec, lo=0.75, hi=0.95):
    out = []
    for M in MS:
        prs = M["prs"]
        if sorted(prs) != [0.0, 1.0]: continue
        T = M["start"] + dec * 3600
        p0 = a.price_at(M, T, fresh=3 * 3600)
        if p0 is None: continue
        buy0 = p0 >= 0.5
        fav = p0 if buy0 else 1 - p0
        if not lo <= fav < hi: continue
        tok, oth = (M["toks"][0], M["toks"][1]) if buy0 else (M["toks"][1], M["toks"][0])
        pay = prs[0 if buy0 else 1]
        rate = ((M["m"].get("feeSchedule") or {}).get("rate")) if M["m"].get("feesEnabled") else 0
        rate = rate or 0
        # immédiat
        c = it.taker_cost(M["trades"], tok, oth, T, window=3600, after=True)
        if c is None or c < 0.03 or c > 0.97: continue
        imm = (pay - c - it.fee(c, rate)) / c
        # posé : prix limite = fav - 0,01 ; servi par un échange (jeton vendu à <= limite, ou autre jeton acheté à >= 1 - limite) dans [T, T + VIE]
        lim = round(fav - 0.01, 2)
        fill = None
        for t in M["trades"]:
            if t[0] < T: continue
            if t[0] > T + VIE * 3600: continue
            if COUPE and dec < 0 and t[0] >= M["start"]: continue
            if HORS and (dec >= 0 or t[0] < M["start"]): continue
            px = t[3] if t[1] == tok else (1 - t[3]) if t[1] == oth else None
            if px is None: continue
            sell_side = (t[1] == tok and t[2] == "SELL") or (t[1] == oth and t[2] == "BUY")
            if sell_side and px <= lim + 1e-9 and (fill is None or t[0] < fill):
                fill = t[0]
        posted = None
        if fill is not None:
            posted = (pay - lim - 0.0) / lim   # posé : pas de frais preneur (barème taker seulement)
        out.append(dict(imm=imm, posted=posted, price=fav, lim=lim, win=pay, evenement=M["e"]["id"]))
    return out
def summarize(r, titre):
    n = len(r); f = [x for x in r if x["posted"] is not None]
    if n == 0: print(titre, "aucun"); return
    imm_all = sum(x["imm"] for x in r) / n
    imm_f = sum(x["imm"] for x in f) / len(f) if f else float("nan")
    post_f = sum(x["posted"] for x in f) / len(f) if f else float("nan")
    ev_post = sum((x["posted"] or 0) for x in r) / n
    won_f = sum(x["win"] for x in f); exp_f = sum(x["lim"] for x in f); var = sum(x["lim"] * (1 - x["lim"]) for x in f)
    print(f"{titre:34s} matchs {n:4d} servis {len(f):4d} ({100*len(f)/n:4.1f} %) | posé servi {100*post_f:+6.1f} % (z des prix {(won_f-exp_f)/math.sqrt(var) if var else 0:+.2f}) | immédiat, mêmes matchs {100*imm_f:+6.1f} % | immédiat tous {100*imm_all:+6.1f} % | EV par occasion : posé {100*ev_post:+.2f} % contre immédiat {100*imm_all:+.2f} %", flush=True)
if __name__ == "__main__":
    for groupe in (("atp", "wta"), ("cs2", "lol", "dota2", "val")):
        MS = a.load(groupe); print(groupe, len(MS), "matchs, vie de l'ordre", VIE, "h", flush=True)
        for dec in (-6, -3, -1, 0.25, 0.75, 1.5):
            summarize(run(MS, dec), f"T = coup d'envoi {dec:+.2f} h")
