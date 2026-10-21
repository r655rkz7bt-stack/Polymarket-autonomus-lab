"""Projection sur 30 jours du capital principal avec les 3 championnes et les règles du 21/10/2026
(demande d'Etienne). Les journaux ne remontent qu'au 16-17/10 : on rejoue 30 jours en tirant au hasard
parmi les VRAIS paris de chaque championne (à leur rythme réel), copiés par le principal à sa part
engagée actuelle (part × mise sur l'avantage mesuré, plafond 70 %). Deux scénarios :
- « la semaine se répète » : chaque pari tiré garde son vrai résultat ;
- « aucun avantage » : même pari, mais gagné avec la probabilité de son prix (marché juste).
5 000 trajectoires, départ 1 000 €. Écrit projection.svg et resultats.json à côté de ce fichier.
Usage : python experiments/projection_30j/simuler.py
"""
from __future__ import annotations

import json
import random
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, "src")
from polymarket_agent.reporting import closed_trades  # noqa: E402

HERE = Path(__file__).parent
GHOSTS = Path("published_data/ledger/fantome")
# Part engagée par le principal (règles du 21/10 au soir) : part × mise sur l'avantage mesuré.
CHAMPIONS = {"nf_sport_patiente_v1.0.0": 0.58 * 0.67, "contrer_crypto_patiente_v1.0.0": 0.21 * 1.49,
             "favori_politique_v1.0.0": 0.20}
DAYS, RUNS, START = 30, 5000, 1000.0


def profile(name: str) -> tuple[list[tuple[float, float, float]], float]:
    rows = [json.loads(line) for line in open(GHOSTS / f"{name}.jsonl") if line.strip()]
    start = datetime.fromisoformat(next(r["ts"] for r in rows if r["type"] == "GENESIS"))
    end = datetime.fromisoformat(rows[-1]["ts"])
    capital, bets = 1000.0, []
    for t in closed_trades(rows):
        cost, bought, pnl = float(t["cost"]), float(t["shares_bought"]), float(t["pnl"])
        if cost > 0 and bought > 0:
            bets.append((cost / capital, pnl / cost, cost / bought))  # mise / capital, rendement, prix
            capital += pnl
    return bets, len(bets) / max((end - start).total_seconds() / 86400, 0.5)


def poisson(rng: random.Random, lam: float) -> int:
    k, t = 0, rng.expovariate(1.0)
    while t < lam:
        k += 1
        t += rng.expovariate(1.0)
    return k


def run(profiles: dict, fair: bool, rng: random.Random) -> list[float]:
    cap, path = START, [START]
    for _ in range(DAYS):
        day = 0.0
        for name, (bets, rate) in profiles.items():
            for _ in range(poisson(rng, rate) if bets else 0):
                frac, ret, price = rng.choice(bets)
                stake = min(cap, frac * CHAMPIONS[name] * cap)
                if fair:  # même pari, résultat tiré au prix du marché
                    ret = (1 - price) / price if rng.random() < price else -1.0
                day += stake * ret
        cap = max(0.0, cap + day)
        path.append(cap)
    return path


def pct(values: list[float], q: float) -> float:
    v = sorted(values)
    return v[min(len(v) - 1, int(q * len(v)))]


def main() -> int:
    profiles = {n: profile(n) for n in CHAMPIONS}
    out = {"paris": {n: {"nombre": len(b), "par_jour": round(r, 1)} for n, (b, r) in profiles.items()}}
    for label, fair in (("semaine_repetee", False), ("aucun_avantage", True)):
        rng = random.Random(7)
        paths = [run(profiles, fair, rng) for _ in range(RUNS)]
        out[label] = {"mediane": [round(pct([p[d] for p in paths], 0.5), 1) for d in range(DAYS + 1)],
                      "bas_10": [round(pct([p[d] for p in paths], 0.1), 1) for d in range(DAYS + 1)],
                      "haut_90": [round(pct([p[d] for p in paths], 0.9), 1) for d in range(DAYS + 1)],
                      "sous_700": round(sum(min(p) < 700 for p in paths) / RUNS, 3),
                      "perte": round(sum(p[-1] < START for p in paths) / RUNS, 3)}
    (HERE / "resultats.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    svg(out)
    for k in ("semaine_repetee", "aucun_avantage"):
        r = out[k]
        print(k, "médiane J30", r["mediane"][-1], "10 %", r["bas_10"][-1], "90 %", r["haut_90"][-1],
              "passe sous 700 €", r["sous_700"], "finit en perte", r["perte"])
    print(out["paris"])
    return 0


def svg(out: dict) -> None:
    W, H, L, R, T, B = 760, 430, 64, 150, 56, 46
    ys = out["semaine_repetee"]["haut_90"] + out["aucun_avantage"]["bas_10"] + [START]
    lo, hi = min(ys) * 0.95, max(ys) * 1.03
    sx = lambda d: L + d / DAYS * (W - L - R)  # noqa: E731
    sy = lambda v: T + (hi - v) / (hi - lo) * (H - T - B)  # noqa: E731
    line = lambda s: " ".join(f"{'M' if i == 0 else 'L'}{sx(i):.1f},{sy(v):.1f}" for i, v in enumerate(s))  # noqa: E731
    band = lambda a, b: line(a) + " " + " ".join(f"L{sx(i):.1f},{sy(v):.1f}" for i, v in reversed(list(enumerate(b)))) + " Z"  # noqa: E731
    rep, fair = out["semaine_repetee"], out["aucun_avantage"]
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif">',
         f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
         f'<text x="{L}" y="26" font-size="17" font-weight="600" fill="#1f2328">Capital principal projeté sur 30 jours (départ 1 000 €)</text>',
         f'<text x="{L}" y="44" font-size="12" fill="#57606a">3 championnes, règles du 21/10 · 5 000 tirages parmi leurs vrais paris du 16 au 21/10</text>']
    step = 500 if hi - lo > 1500 else 100 if hi - lo > 400 else 50
    v = int(lo // step + 1) * step
    while v < hi:
        g.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(v):.1f}" y2="{sy(v):.1f}" stroke="#e6e8eb"/>')
        g.append(f'<text x="{L - 8}" y="{sy(v) + 4:.1f}" font-size="11" text-anchor="end" fill="#57606a">{v}</text>')
        v += step
    for d in (0, 10, 20, 30):
        g.append(f'<text x="{sx(d):.1f}" y="{H - 22}" font-size="11" text-anchor="middle" fill="#57606a">jour {d}</text>')
    g.append(f'<line x1="{L}" x2="{W - R}" y1="{sy(START):.1f}" y2="{sy(START):.1f}" stroke="#8c959f" stroke-dasharray="3 3"/>')
    g.append(f'<path d="{band(rep["haut_90"], rep["bas_10"])}" fill="#2f6fdb" opacity="0.14"/>')
    g.append(f'<path d="{band(fair["haut_90"], fair["bas_10"])}" fill="#c2410c" opacity="0.10"/>')
    g.append(f'<path d="{line(fair["mediane"])}" fill="none" stroke="#c2410c" stroke-width="2.2" stroke-dasharray="6 4"/>')
    g.append(f'<path d="{line(rep["mediane"])}" fill="none" stroke="#2f6fdb" stroke-width="2.6"/>')
    for s, col, lab in ((rep, "#2f6fdb", "la semaine se répète"), (fair, "#c2410c", "aucun avantage")):
        y = sy(s["mediane"][-1])
        g.append(f'<circle cx="{sx(DAYS):.1f}" cy="{y:.1f}" r="4" fill="{col}"/>')
        g.append(f'<text x="{sx(DAYS) + 10:.1f}" y="{y - 2:.1f}" font-size="12" font-weight="600" fill="#1f2328">{s["mediane"][-1]:,.0f} €</text>'.replace(",", " "))
        g.append(f'<text x="{sx(DAYS) + 10:.1f}" y="{y + 13:.1f}" font-size="11" fill="#57606a">{lab}</text>')
    g.append(f'<text x="{L}" y="{H - 6}" font-size="11" fill="#57606a">Trait = cas le plus probable (médiane) · zone = 8 chances sur 10 · pointillé gris = départ</text>')
    g.append("</svg>")
    (HERE / "projection.svg").write_text("\n".join(g), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
