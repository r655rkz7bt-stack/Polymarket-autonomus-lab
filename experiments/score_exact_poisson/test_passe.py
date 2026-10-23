"""Piste n° 1 (score_exact_poisson), étape 3 : le test sur le passé AUX PRIX RÉELLEMENT PAYÉS.

MODÈLE. Les marchés du match (domicile / nul / extérieur, plus/moins de 2,5 buts, et 1,5 / 3,5 s'ils ont des échanges)
donnent, à T0, les buts attendus de chaque équipe (λ domicile, λ extérieur) : on cherche les deux lois de Poisson
indépendantes qui redonnent le mieux ces prix (moindres carrés, grille puis affinage). On en déduit la chance de chaque
score exact (0-0 … 5-5, « Any Other Score » = le reste), avec ou sans la correction de Dixon-Coles (ρ = −0,1 : un peu
plus de 0-0 et de 1-1).
RÈGLES. Prix du match à T0 = médiane des 5 derniers ÉCHANGES RÉELS (d'au moins 5 $) dans les 2 h avant T0 ; sans
échange sur l'un des 4 marchés indispensables (3 vainqueurs, 2,5 buts) : pas de modèle (compté). Achat d'un score
exact (OUI, ou NON s'il est trop cher) au prix réellement payé par un preneur « avant » ou « après » T0 (jamais après
le coup d'envoi), frais du marché. Réglage choisi sur la 1re moitié des jours, jugé sur la 2e. 72 réglages.
Usage : python experiments/score_exact_poisson/test_passe.py"""
import gzip
import json
import math
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "bo3_coherence"))
from echanges import cout_preneur, prix_equivalent  # noqa: E402
from series import _jl, _ts, regle, taux, jour, resume, it  # noqa: E402

D = HERE / "donnees"
MAXG = 10


def pmf(lam):
    return [math.exp(-lam) * lam ** k / math.factorial(k) for k in range(MAXG + 1)]


def resume_poisson(ph, pa):
    """(domicile, nul, extérieur, plus de 1,5, plus de 2,5, plus de 3,5)."""
    h = d = a = 0.0
    tot = [0.0] * (2 * MAXG + 1)
    for i, x in enumerate(ph):
        for j, y in enumerate(pa):
            p = x * y
            if i > j:
                h += p
            elif i == j:
                d += p
            else:
                a += p
            tot[i + j] += p
    u15, u25, u35 = sum(tot[:2]), sum(tot[:3]), sum(tot[:4])
    return h, d, a, 1 - u15, 1 - u25, 1 - u35


GRILLE = [0.1 + 0.1 * k for k in range(36)]
PMF = {round(l, 3): pmf(l) for l in GRILLE}
PRE = {(lh, la): resume_poisson(PMF[round(lh, 3)], PMF[round(la, 3)]) for lh in GRILLE for la in GRILLE}


def ajuster(cible):
    """cible : {indice : prix} (0 dom, 1 nul, 2 ext, 3 plus 1,5, 4 plus 2,5, 5 plus 3,5) -> (λ dom, λ ext, erreur)."""
    err = lambda v: sum((v[k] - p) ** 2 for k, p in cible.items())
    lh, la = min(PRE, key=lambda k: err(PRE[k]))
    best = (err(PRE[(lh, la)]), lh, la)
    for dh in range(-5, 6):
        for da in range(-5, 6):
            x, y = lh + 0.02 * dh, la + 0.02 * da
            if x <= 0.02 or y <= 0.02:
                continue
            e = err(resume_poisson(pmf(x), pmf(y)))
            if e < best[0]:
                best = (e, x, y)
    return best[1], best[2], best[0]


def scores(lh, la, rho):
    ph, pa = pmf(lh), pmf(la)
    m = {(i, j): ph[i] * pa[j] for i in range(MAXG + 1) for j in range(MAXG + 1)}
    if rho:
        m[(0, 0)] *= 1 - lh * la * rho
        m[(0, 1)] *= 1 + lh * rho
        m[(1, 0)] *= 1 + la * rho
        m[(1, 1)] *= 1 - rho
    return m


def lire_match(mt):
    """Marchés utiles d'un match : 3 vainqueurs (OUI), totaux (Over), scores exacts (OUI/NON)."""
    start = _ts(mt["start"])
    if start is None:
        return None
    es = []
    home = None
    for m in mt["scores"]:
        q = m.get("question") or ""
        won = regle(m)
        toks = _jl(m.get("clobTokenIds"))
        if won is None or len(toks) != 2:
            continue
        mm = re.match(r"Exact Score: (.+?) (\d+) - (\d+) (.+?)\?$", q)
        if mm:
            home = home or mm.group(1)
            es.append({"id": m["id"], "score": (int(mm.group(2)), int(mm.group(3))), "toks": toks, "won": won, "rate": taux(m)})
        elif "Any Other Score" in q:
            es.append({"id": m["id"], "score": "autre", "toks": toks, "won": won, "rate": taux(m)})
    if not es or not home:
        return None
    ins = {}
    for m in mt["vainqueur"]:
        if m.get("sportsMarketType") != "moneyline":
            continue
        q, toks = m.get("question") or "", _jl(m.get("clobTokenIds"))
        if len(toks) != 2:
            continue
        if "end in a draw" in q:
            ins[1] = toks
        elif q.startswith(f"Will {home} win"):
            ins[0] = toks
        elif q.startswith("Will "):
            ins[2] = toks
    for m in mt["autres"]:
        if m.get("sportsMarketType") == "totals" and m.get("line") in (1.5, 2.5, 3.5):
            toks, outs = _jl(m.get("clobTokenIds")), _jl(m.get("outcomes"))
            if len(toks) == 2 and outs and str(outs[0]).lower().startswith("over"):
                ins[{1.5: 3, 2.5: 4, 3.5: 5}[m["line"]]] = toks
    if not all(k in ins for k in (0, 1, 2, 4)):
        return None
    return {"event": str(mt["event"]), "slug": mt["slug"], "start": start, "es": es, "ins": ins}


def charger(nom):
    p = D / "echanges" / f"{nom}.json.gz"
    return json.loads(gzip.decompress(p.read_bytes())) if p.exists() else None


matchs = json.loads(gzip.decompress((D / "matchs.json.gz").read_bytes()))
cas, sans = [], Counter()
for mt in matchs:
    c = lire_match(mt)
    if c is None:
        sans["marchés du match introuvables (vainqueur / 2,5 buts)"] += 1
        continue
    c["tr_es"], c["tr_in"] = charger(f"es_{c['event']}"), charger(f"in_{c['event']}")
    if c["tr_es"] is None or c["tr_in"] is None:
        sans["échanges non relevés"] += 1
        continue
    cas.append(c)
jours = sorted({jour(c["start"]) for c in cas})
coupe = jours[len(jours) // 2]
print(f"# score exact : {len(matchs)} matchs tirés, {len(cas)} utilisables ({dict(sans)}), du {jours[0]} au {jours[-1]} ; "
      f"apprentissage avant le {coupe}")
print("scores exacts réglés :", sum(len(c["es"]) for c in cas), "; échanges du score exact :", sum(len(c["tr_es"]) for c in cas),
      "; listes tronquées (entrées) :", sum(1 for c in cas if len(c["tr_in"]) >= 11000))


def modeles(h):
    """Pour chaque match : (λ dom, λ ext) ajustés sur les prix d'échanges réels à T0 = coup d'envoi − h heures."""
    out, st = {}, Counter()
    for c in cas:
        t0 = c["start"] - h * 3600
        rows = c["tr_in"]
        if len(rows) >= 11000 and min(r[0] for r in rows) > t0 - 7200:
            st["entrées tronquées avant T0"] += 1
            continue
        cible = {}
        for k, toks in c["ins"].items():
            pts = prix_equivalent(rows, toks[0], toks[1], t0 - 7200, t0)
            if pts:
                cible[k] = statistics.median(p for _, p in pts[-5:])
        if not all(k in cible for k in (0, 1, 2, 4)):
            st["match sans échange réel dans les 2 h avant T0 (vainqueur ou 2,5 buts)"] += 1
            continue
        s = cible[0] + cible[1] + cible[2]
        for k in (0, 1, 2):
            cible[k] /= s
        lh, la, e = ajuster(cible)
        out[c["event"]] = (lh, la, e)
        st["matchs avec modèle"] += 1
    return out, st


def candidats(mods, h, fen, mode, rho):
    out, st = [], Counter()
    for c in cas:
        if c["event"] not in mods:
            continue
        lh, la, _ = mods[c["event"]]
        sc = scores(lh, la, rho)
        listed = {e["score"] for e in c["es"] if e["score"] != "autre"}
        t0 = c["start"] - h * 3600
        for e in c["es"]:
            pm = sc.get(e["score"], 0.0) if e["score"] != "autre" else 1 - sum(sc.get(s, 0.0) for s in listed)
            st["scores examinés"] += 1
            vu = False
            for issue in (0, 1):
                got = cout_preneur(c["tr_es"], e["toks"][issue], e["toks"][1 - issue], t0, fen * 3600, apres=(mode == "après"), fin_max=c["start"])
                if got is None:
                    continue
                vu = True
                cost = got[1]
                if not 0.01 <= cost <= 0.99:
                    continue
                out.append({"c": c, "e": e, "issue": issue, "pm": pm if issue == 0 else 1 - pm, "cost": cost, "win": int(e["won"] == issue)})
            if not vu:
                st["score sans échange dans la fenêtre"] += 1
    return out, st


def paris(cands, edge):
    best = {}
    for x in cands:
        fee = it.fee(x["cost"], x["e"]["rate"])
        adv = x["pm"] - x["cost"] - fee
        if adv > edge and (x["e"]["id"] not in best or adv > best[x["e"]["id"]][0]):
            best[x["e"]["id"]] = (adv, x, x["cost"] + fee)
    return [{"gain": x["win"] / paid - 1, "evenement": x["c"]["event"], "cout": paid, "win": x["win"], "mois": jour(x["c"]["start"])[:7],
             "jour": jour(x["c"]["start"]), "cote": "OUI" if x["issue"] == 0 else "NON", "adv": adv} for adv, x, paid in best.values()]


res, cache, essais = [], {}, 0
for h in (1, 3, 6):
    mods, st_m = modeles(h)
    print(f"h={h} : {dict(st_m)}")
    for fen in (2, 6):
        for mode in ("avant", "après"):
            for rho in (0.0, -0.1):
                cands, st = candidats(mods, h, fen, mode, rho)
                cache[(h, fen, mode, rho)] = (cands, st)
                tr = [x for x in cands if jour(x["c"]["start"]) < coupe]
                te = [x for x in cands if jour(x["c"]["start"]) >= coupe]
                for edge in (0.03, 0.06, 0.10):
                    essais += 1
                    btr, bte = paris(tr, edge), paris(te, edge)
                    res.append({"lab": f"h={h} fen={fen}h {mode} avance>{edge} ρ={rho}", "n_train": len(btr),
                                "r_train": sum(b["gain"] for b in btr) / len(btr) if btr else None, "test": bte})
print(f"\n{essais} réglages essayés.")
cands, st = cache[(3, 6, "avant", 0.0)]
print("\n## Diagnostic (h = 3, fenêtre 6 h, « avant », Poisson simple) :", dict(st))
yes = [x for x in cands if x["issue"] == 0]
if yes:
    bm = sum((x["pm"] - x["win"]) ** 2 for x in yes) / len(yes)
    bp = sum((x["cost"] - x["win"]) ** 2 for x in yes) / len(yes)
    print(f"   OUI des scores avec un échange : n={len(yes)} Brier modèle {bm:.4f} / prix payé {bp:.4f} ; gagnés {sum(x['win'] for x in yes)} ; "
          f"attendus modèle {sum(x['pm'] for x in yes):.1f} / prix {sum(x['cost'] for x in yes):.1f} ; écart moyen {sum(abs(x['pm'] - x['cost']) for x in yes) / len(yes):.3f}")
print("\n## Réglages classés sur l'apprentissage, jugés sur la 2e moitié")
print("| réglage | paris appr. | rendement appr. | paris test | matchs | rendement test | t par match | mois gagnants | gagnés / attendus (z) | verdict test |")
print("|---|---|---|---|---|---|---|---|---|---|")
ok = sorted([r for r in res if r["n_train"] >= 30], key=lambda r: -r["r_train"])
for r in ok[:8]:
    v = it.verdict(r["test"]) if r["test"] else None
    if not v:
        print(f"| {r['lab']} | {r['n_train']} | {100 * r['r_train']:+.1f} % | 0 | | | | | | |")
        continue
    w = sum(b["win"] for b in r["test"]); e = sum(b["cout"] for b in r["test"])
    print(f"| {r['lab']} | {r['n_train']} | {100 * r['r_train']:+.1f} % | {v['paris']} | {v['evenements']} | {100 * v['rendement_moyen']:+.1f} % | "
          f"{v['confiance_evenements']:+.2f} | {v['mois_gagnants']} | {w} / {e:.1f} (z {v['z_prix']:+.1f}) | {v['verdict']} |")
print("\n## Période entière, réglages fixes")
print("| réglage | paris | matchs | rendement | t par match | mois gagnants | gagnés / attendus (z) | verdict |")
print("|---|---|---|---|---|---|---|---|")
for key in ((1, 2, "avant", 0.0), (1, 2, "après", 0.0), (3, 6, "avant", 0.0), (3, 6, "après", 0.0), (6, 6, "après", -0.1)):
    cands, _ = cache[key]
    for edge in (0.03, 0.10):
        bets = paris(cands, edge)
        print(resume(bets, f"h={key[0]} fen={key[1]}h {key[2]} avance>{edge} ρ={key[3]}"))
        for cote in ("OUI", "NON"):
            sub = [b for b in bets if b["cote"] == cote]
            if sub:
                print(resume(sub, f"   … {cote} seulement"))
if ok:
    b = ok[0]
    print(f"\n## Réglage choisi : {b['lab']}")
    print(json.dumps(it.verdict(b["test"]) if b["test"] else {}, ensure_ascii=False))
