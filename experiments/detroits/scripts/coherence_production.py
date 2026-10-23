"""Le code de production (references.s7_draws + tranche_intervals) redonne-t-il les probabilités du test sur le passé
(test_passe.py, modèle « marche_log_depuis_2019 ») ? Rejoue chaque pari retenu et compare. Usage : PYTHONPATH=src python …"""
import datetime as dt
import json
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import commun as c  # noqa: E402
from polymarket_agent import references as refs  # noqa: E402

data = json.load(open(f"{c.DONNEES}/paris_prudent.json"))["marche_log_depuis_2019 seuil 0.05"]["paris"]
inv = {e["id"]: e for e in c.charge_inventaire()}
series = {n: c.serie(n) for n in ("Strait of Hormuz", "Bab el-Mandeb Strait")}
ecarts = []
for b in data:
    ev = inv[b["evenement"]]
    type_, D = c.cible(ev)
    s = series[ev["detroit"]]
    L = D - dt.timedelta(days=b["h"])
    counts = [s[d] for d in sorted(s) if d <= L]
    draws = refs.s7_draws(counts, b["h"])
    labels = {q["id"]: refs.tranche_label(q["question"]) for q in ev["questions"]}
    iv = refs.tranche_intervals({k: v for k, v in labels.items() if v})
    a, bb = iv[b["marche"]]
    vals = [v if type_ == "somme" else v / 7 for v in draws]
    p = (sum(1 for v in vals if a <= v < bb) + 0.5) / (len(vals) + 1)
    p_side = p if b["cote"] == "OUI" else 1 - p
    ecarts.append(abs(p_side - b["modele_p"]))
print(len(ecarts), "paris rejoués ; écart maximal de probabilité", round(max(ecarts), 4), "; moyen", round(sum(ecarts) / len(ecarts), 5))
