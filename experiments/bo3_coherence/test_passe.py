"""Pistes n° 4 (e-sport) et n° 5 (tennis), étape 4 : le test sur le passé AUX PRIX RÉELLEMENT PAYÉS (méthode : series.py).

Grille de réglages (tous comptés) : h ∈ {1, 3, 6} heures avant le coup d'envoi, fenêtre d'échange ∈ {2 h, 6 h},
prix « avant » ou « après » T0, avance minimale ∈ {0,03 ; 0,06 ; 0,10}, modèle brut ou recalibré (sur l'apprentissage).
Le réglage est CHOISI sur la 1re moitié des jours (meilleur rendement, au moins 30 paris) puis JUGÉ sur la 2e moitié.
Usage : python experiments/bo3_coherence/test_passe.py esport    (ou tennis)"""
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from series import match_cas, candidats, paris, calibrer, resume, jour, it  # noqa: E402

FAM = sys.argv[1]
D = HERE / "donnees"
NOMS = ["cs2", "lol", "dota2", "val"] if FAM == "esport" else ["atp", "wta"]
choisis = set(json.loads((D / f"echantillon_{FAM}.json").read_text()))
cas_list = []
for nom in NOMS:
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        if str(ev["id"]) in choisis:
            ev["serie"] = nom
            c = match_cas(ev, FAM)
            if c:
                cas_list.append(c)
trades = {}
n_tires = len(cas_list)
for c in cas_list:
    p = D / "echanges" / f"{c['event']}.json.gz"
    if p.exists():
        trades[c["event"]] = json.loads(gzip.decompress(p.read_bytes()))
cas_list = [c for c in cas_list if c["event"] in trades]  # échantillon effectivement relevé (relevé interruptible)
print(f"matchs tirés {n_tires}, dont échanges relevés {len(cas_list)}")
jours = sorted({jour(c["start"]) for c in cas_list})
coupe = jours[len(jours) // 2]
print(f"# {FAM} : {len(cas_list)} matchs de l'échantillon, {sum(len(c['lies']) for c in cas_list)} marchés liés réglés, "
      f"du {jours[0]} au {jours[-1]} ; apprentissage avant le {coupe}")
print("types de marchés liés :", dict(Counter(li["kind"] for c in cas_list for li in c["lies"])))
print("BO :", dict(Counter(c["bo"] for c in cas_list)), "; échanges indisponibles :", sum(1 for v in trades.values() if v is None),
      "; tronqués :", sum(1 for v in trades.values() if v and len(v) >= 11000))

resultats, essais = [], 0
cache_cands = {}
for h in (1, 3, 6):
    for fen in (2, 6):
        for mode in ("avant", "après"):
            cands, stats = candidats(cas_list, trades, h, fen * 3600, mode)
            cache_cands[(h, fen, mode)] = (cands, stats)
            train = [c for c in cands if jour(c["cas"]["start"]) < coupe]
            test = [c for c in cands if jour(c["cas"]["start"]) >= coupe]
            calib = calibrer(train, {"manche 1", "manche 2", "manche 3", "handicap", "total"})
            for edge in (0.03, 0.06, 0.10):
                for cal in (False, True):
                    essais += 1
                    btr = paris(train, edge, calib if cal else None)
                    bte = paris(test, edge, calib if cal else None)
                    mtr = sum(b["gain"] for b in btr) / len(btr) if btr else None
                    resultats.append({"h": h, "fen": fen, "mode": mode, "edge": edge, "cal": cal, "n_train": len(btr),
                                      "r_train": mtr, "test": bte, "train": btr})
print(f"\n{essais} réglages essayés.")

# Diagnostic : le modèle binomial prédit-il les marchés liés mieux que leur propre prix payé ?
print("\n## Diagnostic (h = 3, fenêtre 6 h, prix « avant ») : Brier du modèle contre Brier du prix payé, issue 0 des marchés liés")
cands, stats = cache_cands[(3, 6, "avant")]
print("comptes :", dict(stats))
vus = {}
for c in cands:
    if c["issue"] == 0:
        vus[c["li"]["id"]] = c
par_kind = defaultdict(list)
for c in vus.values():
    par_kind[c["li"]["kind"]].append(c)
for k, cs in sorted(par_kind.items()):
    bm = sum((c["pm"] - c["win"]) ** 2 for c in cs) / len(cs)
    bp = sum((c["cost"] - c["win"]) ** 2 for c in cs) / len(cs)
    ecart = sum(abs(c["pm"] - c["cost"]) for c in cs) / len(cs)
    print(f"   {k:10s} n={len(cs):5d}  Brier modèle {bm:.4f}  Brier prix payé {bp:.4f}  écart moyen |modèle − prix| {ecart:.3f}  "
          f"gagnés {sum(c['win'] for c in cs)} / attendus modèle {sum(c['pm'] for c in cs):.1f} / prix {sum(c['cost'] for c in cs):.1f}")

print("\n## Réglages classés sur l'apprentissage (1re moitié), jugés sur la 2e moitié")
print("| réglage | paris appr. | rendement appr. | paris test | matchs | rendement test | t par match | mois gagnants | gagnés / attendus (z) | verdict test |")
print("|---|---|---|---|---|---|---|---|---|---|")
ok = [r for r in resultats if r["n_train"] >= 30]
ok.sort(key=lambda r: -(r["r_train"] or -9))
for r in ok[:8]:
    lab = f"h={r['h']} fen={r['fen']}h {r['mode']} avance>{r['edge']} {'recalibré' if r['cal'] else 'brut'}"
    v = it.verdict(r["test"]) if r["test"] else {"paris": 0, "evenements": 0, "rendement_moyen": 0, "confiance_evenements": 0, "mois_gagnants": "-", "z_prix": 0, "verdict": "-"}
    w = sum(b["win"] for b in r["test"]); e = sum(b["cout"] for b in r["test"])
    print(f"| {lab} | {r['n_train']} | {100 * r['r_train']:+.1f} % | {v['paris']} | {v['evenements']} | {100 * v['rendement_moyen']:+.1f} % | "
          f"{v['confiance_evenements']:+.2f} | {v['mois_gagnants']} | {w} / {e:.1f} (z {v['z_prix']:+.1f}) | {v['verdict']} |")
best = ok[0] if ok else None
print("\n## Période entière, quelques réglages fixes (pas de choix sur le résultat)")
print("| réglage | paris | matchs | rendement | t par match | mois gagnants | gagnés / attendus (z) | verdict |")
print("|---|---|---|---|---|---|---|---|")
for (h, fen, mode) in ((1, 2, "avant"), (1, 2, "après"), (3, 6, "avant"), (3, 6, "après"), (6, 6, "après")):
    cands, _ = cache_cands[(h, fen, mode)]
    for edge in (0.03, 0.10):
        print(resume(paris(cands, edge), f"h={h} fen={fen}h {mode} avance>{edge} brut"))
print("\n## Sans modèle : acheter toujours le même côté d'un type de marché lié (h = 3, fenêtre 6 h), « avant » puis « après »")
print("| côté acheté | paris | matchs | rendement | t par match | mois gagnants | gagnés / attendus (z) | verdict |")
print("|---|---|---|---|---|---|---|---|")
for mode in ("avant", "après"):
    cands, _ = cache_cands[(3, 6, mode)]
    for k in ("manche 1", "handicap", "total"):
        for issue in (0, 1):
            sub = [c for c in cands if c["li"]["kind"] == k and c["issue"] == issue]
            bets = []
            for c in sub:
                paid = c["cost"] + it.fee(c["cost"], c["li"]["rate"])
                bets.append({"gain": c["win"] / paid - 1, "evenement": c["cas"]["event"], "cout": paid, "win": c["win"],
                             "mois": jour(c["cas"]["start"])[:7]})
            nom = {"manche 1": ["équipe / joueur A", "B"], "handicap": ["côté −1,5 (gagne sans perdre de manche en BO3)", "côté +1,5"],
                   "total": ["plus (3 manches en BO3)", "moins"]}[k][issue]
            print(resume(bets, f"{mode} : {k}, {nom}"))
print("\n## Prix « avant » : âge du dernier échange (T0 − heure de l'échange) des paris du réglage h=3 fen=6h avance>0,03 brut")
cands, _ = cache_cands[(3, 6, "avant")]
bets_age = defaultdict(list)
for c in cands:
    paid = c["cost"] + it.fee(c["cost"], c["li"]["rate"])
    if c["pm"] - paid > 0.03:
        got = None
        from echanges import cout_preneur as _cp
        tok, autre = c["li"]["toks"][c["issue"]], c["li"]["toks"][1 - c["issue"]]
        got = _cp(trades[c["cas"]["event"]], tok, autre, c["cas"]["start"] - 3 * 3600, 6 * 3600, apres=False)
        age = (c["cas"]["start"] - 3 * 3600 - got[0]) / 3600 if got else None
        tranche = "moins de 30 min" if age is not None and age < 0.5 else "30 min à 2 h" if age is not None and age < 2 else "2 à 6 h"
        bets_age[tranche].append({"gain": c["win"] / paid - 1, "evenement": c["cas"]["event"], "cout": paid, "win": c["win"],
                                  "mois": jour(c["cas"]["start"])[:7]})
for k in ("moins de 30 min", "30 min à 2 h", "2 à 6 h"):
    print(resume(bets_age.get(k, []), f"échange vieux de {k}"))
if best:
    print(f"\n## Réglage choisi sur l'apprentissage : h={best['h']} fen={best['fen']}h {best['mode']} avance>{best['edge']} {'recalibré' if best['cal'] else 'brut'}")
    v = it.verdict(best["test"]) if best["test"] else None
    print(json.dumps(v, ensure_ascii=False))
    for key in ("kind", "serie"):
        g = defaultdict(list)
        for b in best["test"]:
            g[b[key]].append(b)
        for k, bs in sorted(g.items()):
            print(resume(bs, f"test, {key} = {k}"))
    cands, stats = cache_cands[(best["h"], best["fen"], best["mode"])]
    print("comptes (période entière) :", dict(stats))
