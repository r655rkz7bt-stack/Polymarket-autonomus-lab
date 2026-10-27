"""Étape 4 : suivre les grappes de comptes suspects (27/10/2026, demande d'Etienne après l'affaire du Ballon d'Or).

Compte suspect au moment de son achat : première activité depuis au plus `age` jours ET au plus `marches` marchés
échangés (comptés aujourd'hui). Grappe : au moins K comptes suspects distincts achètent le MÊME jeton (≥ 100 $ chacun) en
72 h, pour au moins S $ ensemble, à un prix ≤ 0,85, AVANT que la réponse soit publique (gagnant à ≥ 0,95 sans retour sous
0,90). On suit : achat au prix du premier échange réel du jeton au moins `delai` après le déclenchement (notre retard),
avant l'instant public, à 0,92 au plus ; frais du marché compris. Un pari par jeton.
Témoins : la même règle avec de VIEUX comptes (> 90 jours, > 50 marchés), et avec n'importe quels comptes.

Usage : .venv/bin/python experiments/inities/scripts/test_grappes.py
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from itertools import product

from analyse_commun import charger, creation_par_nom
from commun import DONNEES, lire_gz
from familles import famille

from polymarket_agent.idea_test import verdict

FENETRE, GRAPPE, PRIX_MAX, ENTREE_MAX, MISE_MIN = 14 * 86400, 72 * 3600, 0.85, 0.92, 100.0


def charger_tout():
    evs = []
    for e in lire_gz(DONNEES / "evenements.json.gz"):
        fam = famille(e["title"])
        if fam:
            ev = charger(e, fam)
            if ev is not None:
                evs.append(ev)
    return evs


def est_suspect(profils, w, t, nom, regle):
    p = profils.get(w) or {}
    premiere, marches = p.get("premiere"), p.get("marches")
    if premiere is None:
        premiere = creation_par_nom(nom)
    if regle == "tous":
        return True
    if premiere is None or marches is None:
        return False
    age = (t - premiere) / 86400
    if regle == "anciens":
        return age > 90 and marches > 50
    age_max, marches_max = regle
    return age <= age_max and marches <= marches_max


def paris(evs, profils, regle, k, s, delai):
    out = []
    for ev in evs:
        par_jeton = defaultdict(list)
        for r in ev.echanges:
            if r[3] == "BUY" and ev.public - FENETRE <= r[0] < ev.public:
                par_jeton[r[2]].append(r)
        for jeton, achats in par_jeton.items():
            fenetre, declenche = [], None
            for t, w, _, _, p, parts, _, nom in achats:
                fenetre = [x for x in fenetre if x[0] >= t - GRAPPE]
                if p * parts >= MISE_MIN and est_suspect(profils, w, t, nom, regle):
                    fenetre.append((t, w, p * parts))
                comptes = defaultdict(float)
                for _, ww, usd in fenetre:
                    comptes[ww] += usd
                if len(comptes) >= k and sum(comptes.values()) >= s and p <= PRIX_MAX:
                    declenche = (t, len(comptes), sum(comptes.values()))
                    break
            if declenche is None:
                continue
            entree = next(((t, p) for t, _, _, _, p, *_ in achats if t >= declenche[0] + delai), None)
            if entree is None or entree[0] >= ev.public or entree[1] > ENTREE_MAX:
                continue
            q = entree[1]
            info = ev.jetons[jeton]
            cout = q + info["frais"] * q * (1 - q)
            gain = (1 - cout) / cout if info["gagne"] else -1.0
            out.append({"gain": gain, "evenement": ev.id, "mois": datetime.fromtimestamp(entree[0], tz=timezone.utc).strftime("%Y-%m"),
                        "cout": cout, "famille": ev.famille, "titre": ev.titre, "question": info["question"], "gagne": info["gagne"],
                        "heures_avant_public": (ev.public - entree[0]) / 3600, "comptes": declenche[1], "dollars": declenche[2]})
    return out


def resume(titre, bets):
    v = verdict(bets)
    gagnes, attendus = sum(b["gagne"] for b in bets), sum(b["cout"] for b in bets)
    print(f"{titre:52s} {v['paris']:4d} paris / {v.get('evenements', 0):3d} év., gagnés {gagnes:3d} / attendus {attendus:6.1f}, "
          f"rendement {v.get('rendement_moyen', 0):+.1%}, t év. {v.get('confiance_evenements', 0):+.2f}, z prix {v.get('z_prix', 0):+.2f}, "
          f"mois {v.get('mois_gagnants', '-')} → {v['verdict']}")
    return v


def main() -> None:
    evs = charger_tout()
    profils = lire_gz(DONNEES / "portefeuilles.json.gz") or {}
    print(f"{len(evs)} événements avec échanges, {sum(len(e.echanges) for e in evs)} échanges, {len(profils)} portefeuilles profilés\n")
    essais = 0
    for k, s, age, marches, delai in product((2, 3), (500, 2000), (3, 7), (5, 15), (900, 7200)):
        essais += 1
        resume(f"suspects K={k} S={s} âge≤{age} j marchés≤{marches} retard {delai // 60} min",
               paris(evs, profils, (age, marches), k, s, delai))
    print()
    for regle in ("anciens", "tous"):
        for k, s in ((2, 500), (3, 2000)):
            essais += 1
            resume(f"témoin {regle} K={k} S={s} retard 15 min", paris(evs, profils, regle, k, s, 900))
    print(f"\n{essais} réglages essayés")
    base = paris(evs, profils, (7, 15), 2, 500, 900)
    print("\nRéglage de référence (K=2, S=500, âge ≤ 7 j, ≤ 15 marchés, 15 min) : paris un par un")
    for b in sorted(base, key=lambda b: b["mois"]):
        print(f"  {b['mois']} {b['famille']:18s} {'GAGNÉ' if b['gagne'] else 'perdu'} à {b['cout']:.2f}, {b['heures_avant_public']:6.1f} h avant, "
              f"{b['comptes']} comptes {b['dollars']:7.0f} $ | {b['titre'][:45]} | {b['question'][:50]}")
    for fam in ("prix", "donnees_entreprise", "emission", "decision"):
        resume(f"  référence, famille {fam}", [b for b in base if b["famille"] == fam])


if __name__ == "__main__":
    main()
