import sys; sys.path.insert(0, "experiments/courbe_de_risque"); sys.path.insert(0, "src")
import analyse as A
for H in (21, 30, 45, 60):
    r = A.run(H, "non")
    print("== NON à", H, "j", A.resume(r))
    for nom, f in (("NON<0.70", lambda x: x["p"] < 0.70), ("0.70-0.85", lambda x: .70 <= x["p"] < .85), ("0.85-0.95", lambda x: .85 <= x["p"] < .95), (">=0.95", lambda x: x["p"] >= .95)):
        print("    ", nom.ljust(10), A.resume([x for x in r if f(x)]))
    for mth in sorted({x["mois"] for x in r}): print("     mois", mth, A.resume([x for x in r if x["mois"] == mth]))
