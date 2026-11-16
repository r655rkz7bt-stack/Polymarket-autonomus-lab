"""Suite de sieges.py : pertes de circonscriptions probables (newswire.co.nz, 08/11/2026 : seules Wairarapa, 139 voix,
et Hamilton East, 456 voix, sont des sièges NATIONAUX serrés ; Te Tai Tokerau : Te Pāti Māori +436 sur les Verts)."""
import random, sieges as S
for bruit in (0.5, 0.75, 1.0, 1.5):
    for p_wai, p_ham, p_ttt in ((0.75, 0.4, 0.3), (0.6, 0.25, 0.2), (0.9, 0.55, 0.4)):
        random.seed(3); N = 8000; maj = 0
        for _ in range(N):
            w = [random.random() for _ in S.ECARTS]; s = sum(w)
            e = {p: sum(wi * S.ECARTS[a][p] for wi, a in zip(w, S.ECARTS)) / s + random.gauss(0, bruit) for p in S.ECARTS[2023]}
            v = S.apres_speciaux(e, random.uniform(330_000, 470_000))
            el = dict(S.ELECT)
            el["NAT"] -= (random.random() < p_wai) + (random.random() < p_ham)
            el["TPM"] -= random.random() < p_ttt
            f, t, d, g = S.resultat(v, el); maj += (d > t / 2) or (g > t / 2)
        print(f"bruit {bruit} pertes ({p_wai},{p_ham},{p_ttt}) P(majorité) {maj / N:.3f}")
# cas déterministes : moyenne des trois élections
e = {p: sum(S.ECARTS[a][p] for a in S.ECARTS) / 3 for p in S.ECARTS[2023]}
v = S.apres_speciaux(e)
for nat, tpm in ((42, 5), (41, 5), (40, 5), (41, 4), (40, 4)):
    f, t, d, g = S.resultat(v, {"NAT": nat, "TPM": tpm})
    print("NAT", nat, "TPM", tpm, f, "chambre", t, "droite", d, "majorité", d > t / 2)
