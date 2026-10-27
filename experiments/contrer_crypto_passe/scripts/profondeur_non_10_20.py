"""27/10/2026 : le NON crypto payé 0,10-0,20 est-il EXÉCUTABLE en quantité ? Pour chaque pari de la tranche (mêmes règles que baseline_non.py), taille du premier échange
payé et total des parts de NON achetées par des preneurs à ≤ prix payé + 0,02 dans l'heure qui suit la décision (profondeur observée, pas un carnet).
Puis rendement des seuls paris où au moins Q parts étaient disponibles (Q = 20, 100, 400). MARCHES=marches_2024.jsonl,marches_2025.jsonl,marches_2026.jsonl"""
import gzip, json, bisect
src = open("experiments/contrer_crypto_passe/scripts/baseline_non.py").read().split("# Référence")[0]
src = src.replace('kind=kind(m["question"]),', 'mid=m["id"], kind=kind(m["question"]),', 1)
exec(compile(src, "baseline_non", "exec"))
base = [b for b in bets_for(0.10, 0.45, 0, base_side=1) if b["cout"] < 0.20]
by_id = {d["m"]["id"]: d for d in data}
for b in base:
    d = by_id[b["mid"]]; m = d["m"]; no = m["no"]
    j = json.loads(gzip.decompress((D / "echanges" / f"{m['id']}.json.gz").read_bytes()))
    # parts de NON achetées par un preneur (côté BUY du jeton NON, ou SELL du OUI) dans l'heure suivant t, à ≤ prix payé + 0,02
    q = 0.0; first = None
    for ts_, tok, side, price, size in sorted(j["echanges"]):
        if ts_ < b["t"] or ts_ > b["t"] + 3600: continue
        p_no = price if tok == no else 1 - price
        if (tok == no and side == "BUY") or (tok != no and side == "SELL"):
            if first is None: first = size
            if p_no <= b["cout"] + 0.02: q += size
    b["q"], b["first"] = q, (first or 0)
import statistics
print(len(base), "paris payés 0,10-0,20 ; taille du premier échange payé : médiane", round(statistics.median(b["first"] for b in base), 1),
      "; parts achetables à ≤ prix + 0,02 dans l'heure : médiane", round(statistics.median(b["q"] for b in base), 1))
print("| parts disponibles ≥ | paris | rendement | gagnés / attendus | z |\n|---|---|---|---|---|")
for Q in (0, 20, 100, 400):
    bs = [b for b in base if b["q"] >= Q]
    if len(bs) < 10: print(f"| {Q} | {len(bs)} | | | |"); continue
    v = it.verdict(bs)
    print(f"| {Q} | {len(bs)} | {v['rendement_moyen']:+.1%} | {sum(b['gagne'] for b in bs)} / {sum(b['cout'] for b in bs):.1f} | {v['z_prix']:+.2f} |")
