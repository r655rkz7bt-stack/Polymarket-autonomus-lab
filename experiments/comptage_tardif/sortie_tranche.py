"""Piste n° 66, 17/11/2026 : pour chaque district californien, combien de bulletins restants (en % des voix déjà comptées)
faudrait-il pour faire SORTIR la marge courante de sa tranche, sous trois hypothèses sur la marge des bulletins restants :
celle observée entre les deux derniers relevés (direction_californie.py), et la marge cumulée ± 25 points (très défavorable).
Affiche aussi le vendeur de la tranche courante (carnet du relevé). Lecture : une tranche dont la sortie demande plus de
bulletins qu'il n'en reste est presque sûre ; son prix vendeur dit si le marché l'a vu."""
import gzip, json, sys
from collections import defaultdict
from pathlib import Path

R = Path(__file__).parent / "releves"
a, b = sorted(R.glob("californie_*.jsonl.gz"))[-2:]


def load(p):
    out = defaultdict(list)
    for l in gzip.open(p, "rt"):
        x = json.loads(l)
        out[x["district"]].append(x)
    return out


def besoin(M, B, m):
    """Part X/T de bulletins à la marge m qui amène la marge M à la borne B (inf si impossible)."""
    if (M - B) * (B - m) <= 0 or B == m:
        return float("inf")
    return (M - B) / (B - m)


A, Bb = load(a), load(b)
for n in sorted(Bb):
    xb = Bb[n][0]
    M, T = xb["marge"], xb["total"]
    xa = A.get(n, [None])[0]
    m_obs = None
    if xa and xb["total"] - xa["total"] >= 500:
        ta = {t[2]: t[0] for t in xa["top"]}
        tb = {t[2]: t[0] for t in xb["top"]}
        l, o = xb["top"][0][2], xb["top"][1][2]
        m_obs = 100.0 * ((tb[l] - ta.get(l, 0)) - (tb[o] - ta.get(o, 0))) / (xb["total"] - xa["total"])
    cur = [x for x in Bb[n] if x["tranche"] and x["tranche"][0] == xb["parti_tete"][0] and x["tranche"][1] <= M < x["tranche"][2]]
    for x in cur:
        lo, hi = x["tranche"][1], x["tranche"][2]
        scen = [M - 25, M + 25] + ([m_obs] if m_obs is not None else [])
        need = min(min(besoin(M, lo, m) for m in scen) if lo > 0 else float("inf"),
                   min(besoin(M, hi, m) for m in scen) if hi < 999 else float("inf"))
        need_obs = (min(besoin(M, lo, m_obs) if lo > 0 else float("inf"), besoin(M, hi, m_obs) if hi < 999 else float("inf"))
                    if m_obs is not None else None)
        print(f"CA-{n:2d} {x['item']:18} marge {M:6.2f} T {T:7d} obs {m_obs if m_obs is None else round(m_obs,1)!s:>6} "
              f"sortie ±25 : {100*need:6.1f} % ; sortie obs : {'—' if need_obs is None else f'{100*need_obs:.1f} %':>8} ; "
              f"vendeur {x['ask']} acheteur {x['bid']} marché {x['market_id']}")
