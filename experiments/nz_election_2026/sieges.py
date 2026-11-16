"""Élection néo-zélandaise du 07/11/2026 : sièges finals après les votes spéciaux (MMP, Sainte-Laguë, dépassement).
Données : résultats préliminaires (Electoral Commission via presse, 08/11) ; écarts des votes spéciaux 2017-2023
(différence entre la part d'un parti chez les spéciaux et dans le préliminaire, déduite des résultats préliminaires et
officiels). Usage : python sieges.py"""
import random, statistics

PRELIM = {"LAB": 710330, "NAT": 706680, "GRN": 321902, "ACT": 264121, "NZF": 236630, "TOP": 144298, "TPM": 13845}
AUTRES = 2_433_000 - sum(PRELIM.values())          # votes valides des petits partis (≈ 35 000)
ELECT = {"NAT": 42, "TPM": 5}                       # partis en dépassement (sièges de circonscription)
SPECIAUX = 399_000                                   # estimation de la Commission
# Part chez les spéciaux moins part au préliminaire (points), par élection : (Nat, Lab, Grn, ACT, NZF, TPM)
ECARTS = {
    2017: {"NAT": -9.4, "LAB": +6.5, "GRN": +2.4, "ACT": -0.2, "NZF": -1.8, "TPM": +0.5, "TOP": +0.6},
    2020: {"NAT": -7.1, "LAB": +5.3, "GRN": +1.8, "ACT": -2.4, "NZF": -0.6, "TPM": +1.2, "TOP": +0.6},
    2023: {"NAT": -4.5, "LAB": +0.0, "GRN": +4.1, "ACT": -1.7, "NZF": -1.9, "TPM": +2.4, "TOP": +0.0},
}


def sainte_lague(votes, seats=120):
    q = {p: 0 for p in votes}
    for _ in range(seats):
        p = max(votes, key=lambda k: votes[k] / (2 * q[k] + 1))
        q[p] += 1
    return q


def resultat(votes, elect):
    alloc = sainte_lague(votes)
    final = {p: max(alloc[p], elect.get(p, 0)) for p in votes}
    total = sum(final.values())
    droite = final["NAT"] + final["ACT"] + final["NZF"]
    gauche = final["LAB"] + final["GRN"] + final["TPM"]
    return final, total, droite, gauche


def apres_speciaux(ecart, n_spec=SPECIAUX):
    tot_pre = sum(PRELIM.values()) + AUTRES
    v = {}
    for p, n in PRELIM.items():
        part = n / tot_pre + ecart.get(p, 0) / 100
        v[p] = n + max(part, 0) * n_spec
    return v


if __name__ == "__main__":
    f, t, d, g = resultat(PRELIM, ELECT)
    print("préliminaire", f, "chambre", t, "droite", d, "gauche", g, "majorité droite", d > t / 2)
    for an, e in ECARTS.items():
        v = apres_speciaux(e)
        f, t, d, g = resultat(v, ELECT)
        lab_nat = (v["LAB"] - v["NAT"]) / sum(v.values()) * 100
        print(an, f, "chambre", t, "droite", d, "gauche", g, "majorité", d > t / 2, f"Lab-Nat {lab_nat:+.2f} pts")
    # Monte-Carlo : écart moyen tiré entre les trois élections (± bruit), spéciaux 330-470 k, 0-3 circonscriptions
    # nationales perdues (6 à moins de 1 000 voix ; chaque perte réduit National et la chambre d'un siège).
    random.seed(1)
    maj = lab = 0; N = 20000; droites = []
    for _ in range(N):
        w = [random.random() for _ in ECARTS]; s = sum(w)
        e = {p: sum(wi * ECARTS[a][p] for wi, a in zip(w, ECARTS)) / s + random.gauss(0, 1.5) for p in ECARTS[2023]}
        v = apres_speciaux(e, random.uniform(330_000, 470_000))
        el = dict(ELECT); el["NAT"] -= random.choices([0, 1, 2, 3], [0.45, 0.35, 0.15, 0.05])[0]
        f, t, d, g = resultat(v, el)
        maj += (d > t / 2) or (g > t / 2); lab += v["LAB"] > v["NAT"]; droites.append(d - t / 2)
    print(f"P(un bloc majoritaire) = {maj / N:.3f} ; P(Labour devant au vote de parti) = {lab / N:.4f}")
