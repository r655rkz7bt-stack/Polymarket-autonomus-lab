"""Piste 16 (`etats_comme_avant`) : prix actuels des marchés « 1re place dans <État> » du 2e tour
comparés aux taux de base officiels (TSE 2006-2022) et au résultat officiel du 1er tour 2026.

Deux références :
1. table brute : part des États qui gardent le même 1er (entre les deux finalistes) selon la marge
   du 1er tour (base_historique.json, 140 cas, sans le « VT » de 2010) ;
2. modèle de bascule uniforme : marge signée au 2e tour = marge du 1er tour + bascule nationale + écart
   propre à l'État. Écart propre : écart-type mesuré 2006-2022. Bascule nationale 2026 : déduite du
   marché Polymarket « marge de victoire » (moyenne et écart-type d'une loi normale ajustée aux
   tranches), donc une seule hypothèse prise au marché : le résultat national.

Prix exécutables : carnets CLOB lus maintenant (meilleur vendeur, quantité, prix moyen pour 200 $ et
1 000 $). Frais : barème Gamma de ces marchés (`zero_fees`, taux 0) ; on les relit quand même.

Lancer : .venv/bin/python -I experiments/bresil_second_tour/etats_comme_avant.py
Écrit etats_comme_avant.json.
"""

from __future__ import annotations

import json
import math
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "src"))

from cache_http import HTTP, cached_json  # noqa: E402
from vitesse_premier_tour import SLUG_UF  # noqa: E402

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
MARGIN_EVENT = "1138953"  # « Second Round: Margin of Victory »
BANDS = [(0, 2), (2, 5), (5, 10), (10, 20), (20, 101)]


def phi(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def history() -> list[dict]:
    return [r for r in json.loads((HERE / "base_historique.json").read_text()) if r["uf"] != "VT"]


def band_table(rows: list[dict]) -> list[dict]:
    out = []
    for lo, hi in BANDS:
        sel = [r for r in rows if lo <= r["marge_t1_points"] < hi]
        k = sum(r["change"] for r in sel)
        out.append({"marge_t1": f"{lo}-{hi if hi < 100 else '+'}", "cas": len(sel), "changements": k,
                    "garde_pct": round(100 * (1 - k / len(sel)), 1) if sel else None})
    return out


def _residuals(rows: list[dict], year: int, toward: str | None = None) -> dict[str, float]:
    """Pour une élection : (bascule de l'État − bascule médiane des États), marges signées vers `toward`
    (par défaut le vainqueur de la plupart des États au 2e tour)."""
    sel = [r for r in rows if r["annee"] == year]
    winner = toward or statistics.mode(r["vainqueur_t2"] for r in sel)

    def signed(r, which):
        m = r["marge_t1_points"] if which == 1 else r["marge_t2_points"]
        lead = r["finaliste_en_tete_t1"] if which == 1 else r["vainqueur_t2"]
        return m if lead == winner else -m
    swings = {r["uf"]: signed(r, 2) - signed(r, 1) for r in sel}
    nat = statistics.median(swings.values())
    return {uf: s - nat for uf, s in swings.items()}


def residual_sigma(rows: list[dict]) -> float:
    """Écart-type de (bascule de l'État − bascule nationale), marges signées vers le vainqueur national."""
    res = []
    for year in sorted({r["annee"] for r in rows}):
        res += list(_residuals(rows, year).values())
    return statistics.pstdev(res)


def leans_2022(rows: list[dict]) -> dict[str, float]:
    """Penchant propre de chaque État au 2e tour 2022 (même affiche : Lula contre un Bolsonaro), en points
    vers Bolsonaro : positif = l'État a plus basculé vers Bolsonaro que la médiane des États."""
    return {uf: -r for uf, r in _residuals(rows, 2022, toward="LULA").items()}


def national_swing() -> tuple[float, float, dict]:
    """Loi normale (moyenne, écart-type) de la marge Flávio − Lula au 2e tour, ajustée aux tranches du marché."""
    event = cached_json(f"{GAMMA}/events/{MARGIN_EVENT}", name=f"event_{MARGIN_EVENT}_now", refresh=True)
    probs = {}
    for m in event["markets"]:
        if not m.get("active") or m.get("closed") or not m.get("acceptingOrders"):
            continue
        title = m.get("groupItemTitle") or ""
        p = (float(m.get("bestBid") or 0) + float(m.get("bestAsk") or 0)) / 2
        probs[title] = p
    total = sum(probs.values())
    probs = {k: v / total for k, v in probs.items()}
    # Bornes signées (Flávio positif) : P(marge < x)
    def get(name):
        return next((v for k, v in probs.items() if k.replace("á", "a").startswith(name)), 0.0)
    lula = sum(v for k, v in probs.items() if k.startswith("Lula"))
    cdf = {-4.0: lula - get("Lula da Silva <4%"), 0.0: lula, 4.0: lula + get("Flavio Bolsonaro <4%"),
           8.0: lula + get("Flavio Bolsonaro <4%") + get("Flavio Bolsonaro 4-8%")}
    best = None
    for mu10 in range(-50, 101):
        for tau10 in range(10, 101):
            mu, tau = mu10 / 10, tau10 / 10
            err = sum((phi((x - mu) / tau) - p) ** 2 for x, p in cdf.items())
            if best is None or err < best[0]:
                best = (err, mu, tau)
    return best[1], best[2], {"tranches": probs, "cdf": cdf}


def book(token: str) -> dict:
    raw = HTTP.get_json(f"{CLOB}/book", params={"token_id": token})
    asks = sorted(((float(a["price"]), float(a["size"])) for a in raw.get("asks") or []))
    bids = sorted(((float(b["price"]), float(b["size"])) for b in raw.get("bids") or []), reverse=True)
    def avg_for(usd):
        spent = got = 0.0
        for p, q in asks:
            take = min(q, (usd - spent) / p)
            spent += take * p
            got += take
            if spent >= usd - 1e-9:
                break
        return round(spent / got, 4) if got and spent >= usd - 1e-6 else None
    best = asks[0][0] if asks else None
    return {"meilleur_vendeur": best, "parts_au_meilleur": asks[0][1] if asks else 0,
            "usd_a_1_centime": round(sum(p * q for p, q in asks if best is not None and p <= best + 0.01), 2),
            "prix_moyen_200usd": avg_for(200), "prix_moyen_1000usd": avg_for(1000),
            "meilleur_acheteur": bids[0][0] if bids else None}


def main() -> None:
    rows = history()
    table = band_table(rows)
    sigma = residual_sigma(rows)
    sigma22 = residual_sigma([r for r in rows if r["annee"] == 2022])
    lean = leans_2022(rows)
    mu, tau, market = national_swing()
    tse = json.loads((HERE / "tse_6257_etats.json").read_text())
    nat = tse.get("br") or None
    allev = json.loads((HERE / "donnees" / "all_events_search.json").read_text())
    nat_r1 = 47.027772356 - 45.162767911  # marge nationale du 1er tour (TSE, br-c0001-e006257-u.json)
    swing = mu - nat_r1
    print(f"taux de base : {table}")
    print(f"écart propre aux États (2006-2022) : σ = {sigma:.2f} points ; marché national : marge Flávio "
          f"{mu:+.1f} ± {tau:.1f} → bascule {swing:+.2f} points depuis le 1er tour ({nat_r1:+.2f})")
    out = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for e0 in sorted(allev.values(), key=lambda e: e["slug"]):
        slug = e0["slug"]
        if "brazil-presidential-election-second-round-1st-place-" not in slug:
            continue
        key = slug.split("1st-place-", 1)[1].removeprefix("in-")
        uf = SLUG_UF[key]
        event = cached_json(f"{GAMMA}/events/{e0['id']}", name=f"event_{e0['id']}_now", refresh=True)
        r1 = tse[uf]["candidatos"]
        valid = tse[uf]["validos"]
        fl = next(c for c in r1 if "FLAVIO" in c["nome"])
        lu = next(c for c in r1 if c["nome"] == "LULA")
        s1 = 100 * (fl["votos"] - lu["votos"]) / valid  # marge signée (Flávio positif)
        p_model = phi((s1 + swing) / math.sqrt(sigma ** 2 + tau ** 2))
        # 3e référence : comme en 2022 (σ de 2022 et penchant propre de l'État au 2e tour 2022)
        p_2022 = phi((s1 + swing + lean.get(uf.upper(), 0.0)) / math.sqrt(sigma22 ** 2 + tau ** 2))
        lead = "Flávio" if s1 > 0 else "Lula"
        band = next(b for b, (lo, hi) in zip(table, BANDS) if lo <= abs(s1) < hi)
        keep = band["garde_pct"] / 100
        p_base_flavio = keep if lead == "Flávio" else 1 - keep
        row = {"uf": uf, "event_id": event["id"], "titre": event["title"], "marge_t1_flavio_moins_lula": round(s1, 2),
               "en_tete_t1": lead, "taux_de_base_garde": band, "p_flavio_taux_de_base": round(p_base_flavio, 3),
               "p_flavio_modele_bascule": round(p_model, 3), "penchant_2022_vers_bolsonaro": round(lean.get(uf.upper(), 0.0), 2),
               "p_flavio_comme_2022": round(p_2022, 3), "lu_a": now}
        for m in event["markets"]:
            name = m.get("groupItemTitle") or ""
            if not m.get("acceptingOrders") or not m.get("active") or m.get("closed"):
                continue
            side = "flavio" if "Flavio" in name or "Flávio" in name else ("lula" if "Lula" in name else None)
            if side is None:
                continue
            yes = json.loads(m["clobTokenIds"])[0]
            row[f"{side}_market_id"] = m["id"]
            row[f"{side}_frais"] = (m.get("feeSchedule") or {}).get("rate")
            row[f"{side}_carnet"] = book(yes)
        fa = (row.get("flavio_carnet") or {}).get("meilleur_vendeur")
        la = (row.get("lula_carnet") or {}).get("meilleur_vendeur")
        row["avance_flavio_modele"] = round(p_model - fa, 3) if fa else None
        row["avance_lula_modele"] = round((1 - p_model) - la, 3) if la else None
        row["avance_flavio_base"] = round(p_base_flavio - fa, 3) if fa else None
        row["avance_lula_base"] = round((1 - p_base_flavio) - la, 3) if la else None
        row["avance_flavio_2022"] = round(p_2022 - fa, 3) if fa else None
        row["avance_lula_2022"] = round((1 - p_2022) - la, 3) if la else None
        out.append(row)
        fc, lc = row.get("flavio_carnet", {}), row.get("lula_carnet", {})
        print(f"{uf} t1 {s1:+6.2f} | base P(F) {p_base_flavio:.2f} modèle {p_model:.2f} 2022 {p_2022:.2f} | Flávio ask {fa} "
              f"({fc.get('usd_a_1_centime')}$, 1000$→{fc.get('prix_moyen_1000usd')}) Lula ask {la} "
              f"({lc.get('usd_a_1_centime')}$, 1000$→{lc.get('prix_moyen_1000usd')}) | avance modèle F {row['avance_flavio_modele']} "
              f"L {row['avance_lula_modele']}")
    (HERE / "etats_comme_avant.json").write_text(json.dumps(
        {"lu_a": now, "taux_de_base": table, "sigma_etat": round(sigma, 2), "sigma_2022": round(sigma22, 2),
         "marge_nationale_marche": [mu, tau],
         "bascule": round(swing, 2), "marche_marge": market, "etats": out}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
