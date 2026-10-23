"""Juge le relevé d'ensembles sur les marchés DÉJÀ RÉGLÉS, protocole `tester-une-piste` (23/10/2026).

Entrées (l'une ou l'autre, ou les deux) :
  --base <market.sqlite>   tables meteo_ensemble_releves / meteo_ensemble_membres (cycle de production :
                           `bash scripts/fetch_data.sh` puis gunzip de published_data/backup/essentiel.sqlite.gz)
  --releves <dossier>      anciens relevés manuels experiments/ensemble_meteo/releves/releve_*.json.gz (23/10 15 h 23)
Méthode :
  1. règlement : Gamma /markets/<id> (closed, outcomePrices 1/0), événement et barème de frais ;
  2. probabilité = part des membres (GEFS + ECMWF) dont le max / min du jour LOCAL tombe dans la tranche (règle du
     marché : arrondi, ou troncature à Hong Kong), membres décalés du biais de la station appris sur la 1re MOITIÉ des
     jours (valeur réelle = tranche gagnante), puis floutée de σ (réglage) ; jugée sur la 2de moitié ;
  3. prix à T0 = milieu du carnet relevé (dernier prix si l'écart dépasse 0,2) ; on ÉCARTE les marchés sans échange
     réel dans les 2 h avant T0 (règle du 22/10, experiments/enquetes/README.md) ;
  4. contre le marché d'abord (log-score) ; puis achats au PREMIER VRAI ÉCHANGE dans les 2 h après T0
     (`idea_test.fetch_event_trades` + `taker_cost(after=True)`), frais du marché ; `idea_test.verdict`.
Usage : PYTHONPATH=src python experiments/meteo_ensemble/evaluer_releve.py --releves experiments/ensemble_meteo/releves
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import math
import sqlite3
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from polymarket_agent import idea_test
from polymarket_agent import weather_model as wm
from polymarket_agent.http_client import HttpClient

D = Path(__file__).parent / "donnees"
SIGMAS = (0.3, 0.6, 1.0)
GAPS = (0.05, 0.10, 0.15)


def from_base(path: str) -> list[dict]:
    db = sqlite3.connect(path)
    members = {(r[0], r[1], r[2], r[3]): {"gefs": json.loads(r[4]), "ecmwf": json.loads(r[5])} for r in db.execute(
        "SELECT pris_le, station, jour, type, gefs, ecmwf FROM meteo_ensemble_membres")}
    out = []
    for r in db.execute("SELECT pris_le, marche, evenement, question, station, jour, type, regle, meilleur_acheteur, "
                        "meilleur_vendeur, dernier_prix, jeton_oui FROM meteo_ensemble_releves"):
        mem = members.get((r[0], r[4], r[5], r[6]))
        if mem:
            out.append({"pris_le": r[0], "id": r[1], "question": r[3], "station": r[4], "jour": r[5], "regle": r[7],
                        "bid": r[8], "ask": r[9], "last": r[10], "membres": mem})
    return out


def from_files(folder: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(str(Path(folder) / "releve_*.json.gz"))):
        d = json.load(gzip.open(f, "rt", encoding="utf-8"))
        for m in d["marches"]:
            out.append({"pris_le": d["pris_le"], "id": str(m["id"]), "question": m["q"], "station": m["station"],
                        "jour": m["date"], "regle": "troncature" if m["station"] == "HKO" else "arrondi",
                        "bid": m.get("bid"), "ask": m.get("ask"), "last": m.get("last"), "membres": m["membres"]})
    return out


def settle(http: HttpClient, mid: str) -> dict | None:
    path = D / "marches" / f"{mid}.json"
    if path.exists():
        m = json.loads(path.read_text())
    else:
        try:
            m = http.get_json(f"https://gamma-api.polymarket.com/markets/{mid}")
        except Exception:  # noqa: BLE001
            return None
        if m.get("closed"):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(m))
    try:
        prices = [float(x) for x in json.loads(m["outcomePrices"])]
        tokens = json.loads(m["clobTokenIds"])
    except (KeyError, ValueError, TypeError):
        return None
    if not m.get("closed") or sorted(prices) != [0.0, 1.0]:
        return None
    fs = m.get("feeSchedule") or {}
    return {"won": int(prices[0] == 1.0), "event": str((m.get("events") or [{}])[0].get("id")), "yes": tokens[0], "no": tokens[1],
            "fee": float(fs.get("rate") or 0) if m.get("feesEnabled") else 0.0}


def mid_price(r) -> float | None:
    b, a = r.get("bid"), r.get("ask")
    if b is not None and a is not None and float(a) - float(b) <= 0.2:
        return (float(b) + float(a)) / 2
    return float(r["last"]) if r.get("last") is not None else None


def truth(rows_of_event: list[dict]) -> float | None:
    """Valeur réelle (°C) d'après la tranche gagnante : centre de la tranche selon la règle du marché."""
    for r in rows_of_event:
        if r["won"]:
            q = wm.parse_question(r["question"])
            q = wm.truncated(q) if r["regle"] == "troncature" else q
            lo, hi = q.low, q.high
            v = (lo + hi) / 2 if lo != -wm.INF and hi != wm.INF else (lo + 0.5 if hi == wm.INF else hi - 0.5)
            return (v - 32) / 1.8 if q.unit == "F" else v
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--releves")
    args = ap.parse_args()
    rows = (from_base(args.base) if args.base else []) + (from_files(args.releves) if args.releves else [])
    print(f"{len(rows)} relevés ({len({r['pris_le'] for r in rows})} instants, {len({r['id'] for r in rows})} marchés)")
    http = HttpClient(user_agent="curl/8", max_retries=2)
    with ThreadPoolExecutor(8) as ex:
        settled = dict(zip(sorted({r["id"] for r in rows}), ex.map(lambda i: settle(http, i), sorted({r["id"] for r in rows}))))
    done = [dict(r, **settled[r["id"]]) for r in rows if settled.get(r["id"])]
    print(f"{len(done)} relevés de marchés réglés ({len({r['id'] for r in done})} marchés, {len({r['event'] for r in done})} événements)")
    if not done:
        return
    # Contrôle du règlement : chaque événement relevé a-t-il exactement une tranche gagnante parmi nos lignes ?
    by_event = defaultdict(list)
    for r in done:
        by_event[(r["pris_le"], r["event"])].append(r)
    one = sum(1 for v in by_event.values() if sum(x["won"] for x in v) == 1)
    print(f"contrôle du règlement : {one} événements sur {len(by_event)} avec exactement une tranche gagnante relevée")
    # Biais de station : 1re moitié des jours.
    days = sorted({r["jour"] for r in done})
    cut = days[len(days) // 2] if len(days) > 1 else None
    errs = defaultdict(list)
    for (_, _), v in by_event.items():
        t = truth(v)
        if t is None or cut is None or v[0]["jour"] >= cut:
            continue
        q = wm.parse_question(v[0]["question"])
        pool = v[0]["membres"].get("gefs", []) + v[0]["membres"].get("ecmwf", [])
        if pool:
            errs[(v[0]["station"], q.kind)].append(t - sorted(pool)[len(pool) // 2])
    bias = {k: sum(e) / len(e) for k, e in errs.items()}
    test = [r for r in done if cut is not None and r["jour"] >= cut] or done
    label = "2de moitié des jours" if cut is not None and any(r["jour"] >= cut for r in done) else "TOUT (un seul jour : aucun réglage possible)"
    print(f"jours : {days} ; jugés : {label} ; biais appris pour {len(bias)} stations×type")
    # Prix à T0 avec un vrai échange dans les 2 h avant.
    cache = D / "echanges"
    trades = {}
    for ev in sorted({r["event"] for r in test}):
        trades[ev] = idea_test.fetch_event_trades(http, cache, ev)
    kept = []
    for r in test:
        t0 = int(datetime.fromisoformat(r["pris_le"]).timestamp())
        tr = trades.get(r["event"]) or []
        had = idea_test.taker_cost(tr, r["yes"], r["no"], t0) is not None or idea_test.taker_cost(tr, r["no"], r["yes"], t0) is not None
        if had and mid_price(r) is not None:
            kept.append(dict(r, t0=t0))
    print(f"{len(kept)} relevés jugés avec un vrai échange dans les 2 h avant T0 (sur {len(test)})")
    tries = 0
    for sigma in SIGMAS:
        def prob(r):
            q = wm.parse_question(r["question"])
            q = wm.truncated(q) if r["regle"] == "troncature" else q
            pool = r["membres"].get("gefs", []) + r["membres"].get("ecmwf", [])
            return wm.probability(q, pool, sigma, bias.get((r["station"], q.kind), 0.0))
        ll = lambda p, y: -math.log(min(0.999, max(0.001, p)) if y else 1 - min(0.999, max(0.001, p)))
        lm = sum(ll(prob(r), r["won"]) for r in kept) / max(1, len(kept))
        lk = sum(ll(mid_price(r), r["won"]) for r in kept) / max(1, len(kept))
        print(f"\nσ {sigma} : log loss modèle {lm:.4f} contre marché {lk:.4f} ({len(kept)} relevés ; plus bas = mieux)")
        for gap in GAPS:
            tries += 1
            bets = []
            for r in kept:
                p, tr = prob(r), trades.get(r["event"]) or []
                ask, bid = r.get("ask"), r.get("bid")
                if ask is not None and p - float(ask) >= gap:
                    side, c = 1, idea_test.taker_cost(tr, r["yes"], r["no"], r["t0"], after=True)
                elif bid is not None and (1 - p) - (1 - float(bid)) >= gap:
                    side, c = 0, idea_test.taker_cost(tr, r["no"], r["yes"], r["t0"], after=True)
                else:
                    continue
                if c is None or not 0.01 <= c <= 0.99:
                    continue
                pay = r["won"] if side else 1 - r["won"]
                bets.append({"gain": (pay - c - idea_test.fee(c, r["fee"])) / c, "evenement": r["event"],
                             "mois": r["jour"][:7], "cout": c})
            v = idea_test.verdict(bets)
            print(f"  écart ≥ {gap:.2f} : {v['paris']} achats aux prix payés, rendement moyen {v.get('rendement_moyen', 0):+.3f}, "
                  f"{v.get('evenements', 0)} événements, confiance par événement {v.get('confiance_evenements', 0):+.2f}, "
                  f"z des prix {v.get('z_prix', 0):+.2f} -> {v['verdict']} ({v.get('raison', '')})")
    print(f"\n{tries} réglages essayés (σ × écart).")


if __name__ == "__main__":
    main()
