import sys; sys.path.insert(0, "experiments/contrer_football"); sys.path.insert(0, "src")
import analyse as A, math
for J, back, delay in ((0.25, 300, 60), (0.25, 300, 180), (0.35, 300, 60), (0.35, 300, 180)):
    r = A.run(J, back, delay)
    print("== contre", J, back // 60, delay // 60, A.resume(r))
    for nom, f in (("minute<45", lambda x: x["minute"] < 45), ("45-70", lambda x: 45 <= x["minute"] < 70), ("70-95", lambda x: 70 <= x["minute"] < 95), (">=95", lambda x: x["minute"] >= 95),
                   ("prix<0.3", lambda x: x["p"] < 0.3), ("0.3-0.6", lambda x: 0.3 <= x["p"] < 0.6), ("0.6-0.85", lambda x: 0.6 <= x["p"] < 0.85), (">=0.85", lambda x: x["p"] >= 0.85),
                   ("hausse", lambda x: x["dlt"] > 0), ("baisse", lambda x: x["dlt"] < 0)):
        print("  ", nom.ljust(10), A.resume([x for x in r if f(x)]))
    mois = sorted({x["day"] for x in r})
    for mth in mois: print("   mois", mth, A.resume([x for x in r if x["day"] == mth]))
