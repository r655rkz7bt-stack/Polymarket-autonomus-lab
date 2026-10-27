"""28/10/2026 : les paris d'une même échelle FDV sont emboîtés (les OUI sous le niveau final gagnent ou perdent ensemble, idem les NON au-dessus) : le z « pari par pari » est donc
trop optimiste. Ici l'unité est l'ÉVÉNEMENT (un jeton) : pour chaque côté (OUI sous le niveau / NON au-dessus), le côté « presque sûr » (prix payé 0,70-0,97) ne perd que si le
pari le moins sûr perd (emboîtement) ; probabilité attendue (par les prix payés) qu'aucun pari du jeton ne perde, comparée au nombre de jetons où un pari a perdu.
Usage : PYTHONPATH=src python niveau_evenement.py [heures_avant_reglement=18]"""
import sys, math, json, datetime as dt, collections
sys.argv_save = sys.argv[:]
exec(open("experiments/fdv_lancement/scripts/analyse.py").read().split("print(\"| réglage")[0])
HH = float(sys.argv_save[1]) if len(sys.argv_save) > 1 else 18
def par_cote(lo, hi, hh):
    r = {}
    for side in ("oui", "non"):
        for b in bets(side, lo, hi, hh / 24):
            r.setdefault((b["evenement"], side), []).append(b)
    return r
def evalue(lo, hi, hh, moitie=None):
    g = par_cote(lo, hi, hh)
    evs = collections.defaultdict(list)
    for (e, side), v in g.items(): evs[e].append((side, v))
    n = pertes = 0; log_p_aucune = 0.0; attendu_pertes = 0.0; paris = 0
    for e, lst in evs.items():
        mois = lst[0][1][0]["mois"]
        if moitie == 1 and mois >= "2026-04": continue
        if moitie == 2 and mois < "2026-04": continue
        p_ok = 1.0; perdu = False
        for side, v in lst:
            p_ok *= min(x["cout"] for x in v)   # emboîtement : le moins sûr des paris du côté décide
            paris += len(v)
            perdu = perdu or any(x["gagne"] == 0 for x in v)
        n += 1; pertes += perdu; log_p_aucune += math.log(p_ok); attendu_pertes += 1 - p_ok
    return n, paris, pertes, attendu_pertes, math.exp(log_p_aucune)
print("| bande | H− | jetons | paris | jetons avec une perte | attendu (prix payés, emboîtement) | P(aucune perte) |")
for lo, hi in ((0.70, 0.97), (0.80, 0.97), (0.90, 0.97)):
    for hh in (30, 24, 18, 12, 6):
        n, paris, pertes, att, p0 = evalue(lo, hi, hh)
        print(f"| {lo}-{hi} | {hh} | {n} | {paris} | {pertes} | {att:.1f} | {p0:.4f} |")
print("\n== deux moitiés (jetons réglés avant / après le 01/04/2026), bande 0,70-0,97 ==")
for hh in (24, 18, 12):
    for m in (1, 2):
        n, paris, pertes, att, p0 = evalue(0.70, 0.97, hh, m)
        print(f"H−{hh} moitié {m} : {n} jetons, {paris} paris, {pertes} jetons avec une perte, attendu {att:.1f}, P(aucune perte) {p0:.4f}")
