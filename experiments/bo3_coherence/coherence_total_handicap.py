"""26/10/2026 : cohérence entre le total « Under 2,5 » et le handicap −1,5 du favori (BO3). Under 2,5 = « 2-0 » (du favori OU de l'outsider) ⊇ « le favori gagne 2-0 » :
il doit coûter AU MOINS autant que le handicap du favori. Pour chaque BO3 qui a les deux marchés échangés, prix de chaque jeton payé par un preneur dans la même
fenêtre (T − 3 h, 6 h suivantes) : combien de fois Under < handicap, et une paire « Under + NON du handicap » (coût < 1 − part de l'outsider) coûte-t-elle moins de 1 ?
Usage : python experiments/bo3_coherence/coherence_total_handicap.py"""
import gzip, json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
os.environ["INCLURE_50_50"] = "1"
import series  # noqa: E402
from echanges import cout_preneur  # noqa: E402
D = HERE / "donnees"
choisis = set(json.loads((D / "echantillon_esport.json").read_text()))
n = viol = 0; ecarts = []; paires = []
for nom in ("cs2", "lol", "dota2", "val"):
    for ev in json.loads(gzip.decompress((D / f"evenements_{nom}.json.gz").read_bytes())):
        if str(ev["id"]) not in choisis: continue
        ev["serie"] = nom
        c = series.match_cas(ev, "esport")
        p = D / "echanges" / f"{ev['id']}.json.gz"
        if not c or c["bo"] != 3 or not p.exists(): continue
        rows = json.loads(gzip.decompress(p.read_bytes()))
        t0 = c["start"] - 3 * 3600
        m = series.prix_vainqueur(rows, c, t0)
        if m is None or not 0.5 < max(m, 1 - m) < 0.995: continue
        tot = [li for li in c["lies"] if li["kind"] == "total" and li["won"] != -1]
        han = [li for li in c["lies"] if li["kind"] == "handicap" and li["won"] != -1]
        for lt in tot:
            over_idx = 0 if lt["f"](0.9) < 0.5 else 1
            u = 1 - over_idx
            pu = cout_preneur(rows, lt["toks"][u], lt["toks"][over_idx], t0, 6 * 3600, apres=True, fin_max=c["start"])
            if not pu: continue
            for lh in han:
                a_is_issue0 = lh["f"](0.9) > lh["f"](0.1)
                if (m > 0.5) != a_is_issue0: continue  # seulement le handicap du favori
                ph = cout_preneur(rows, lh["toks"][0], lh["toks"][1], t0, 6 * 3600, apres=True, fin_max=c["start"])
                phn = cout_preneur(rows, lh["toks"][1], lh["toks"][0], t0, 6 * 3600, apres=True, fin_max=c["start"])
                if not ph or not phn: continue
                n += 1
                ecarts.append(pu[1] - ph[1])
                # Under (coût pu) + NON du handicap du favori (coût phn) : paie au moins 1 si 2-0 (Under gagne) ou si pas 2-0 du favori (NON gagne) ;
                # paie 2 si l'outsider gagne 2-0 : coût total < 1 = gain sûr.
                paires.append(pu[1] + phn[1])
                if pu[1] < ph[1]: viol += 1
import statistics
print(n, "couples (Under 2,5, handicap −1,5 du favori) avec les prix des deux côtés dans la même fenêtre")
if n:
    print(f"Under < handicap du favori : {viol} fois ({100*viol/n:.1f} %) ; écart moyen Under − handicap {statistics.mean(ecarts):+.3f} (médiane {statistics.median(ecarts):+.3f})")
    print(f"Under + NON(handicap) : moyenne {statistics.mean(paires):.3f} ; < 1,00 : {sum(x < 1 for x in paires)} fois ; < 0,97 : {sum(x < 0.97 for x in paires)} fois")
