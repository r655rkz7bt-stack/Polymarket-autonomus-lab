"""Piste n° 24 : un pari par marché (premier échange que la carte publiée dit bon), idea_test.verdict, plusieurs réglages."""
import contextlib
import io
import json
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2] / "src"))
from polymarket_agent.idea_test import verdict  # noqa: E402

import analyse as A  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    res = A.main()
rows = sorted(res["avant (carte de 1 sem.)"], key=lambda r: r["ts"])
for seuil in (0.02, 0.05, 0.10, 0.20):
    for prix_min in (0.0, 0.10):
        for parts_min in (0, 20):
            vus, bets = set(), []
            for r in rows:
                k = (r["etat"], r["w"])
                if k in vus or r["prix"] < prix_min or r["parts"] < parts_min or r["p"] - r["prix"] - r["frais"] < seuil:
                    continue
                vus.add(k)
                bets.append({"gain": ((1 if r["gagne"] else 0) - r["prix"] - r["frais"]) / r["prix"], "evenement": r["w"],
                             "mois": r["w"][:7], "cout": r["prix"], "p": r["p"], "gagne": r["gagne"]})
            v = verdict(bets, min_bets=20)
            print(f"seuil {seuil:.2f} prix ≥ {prix_min:.2f} parts ≥ {parts_min:3}: {len(bets):3} paris, gagnés {sum(b['gagne'] for b in bets)} "
                  f"pour {sum(b['p'] for b in bets):.1f} (carte) / {sum(b['cout'] for b in bets):.1f} (prix) ; "
                  f"rendement {v.get('rendement_moyen', v.get('rendement', 0)):+.1%} t/sem {v.get('confiance_evenements')} "
                  f"z {v.get('z_prix')} mois {v.get('mois')} → {v['verdict']}")
