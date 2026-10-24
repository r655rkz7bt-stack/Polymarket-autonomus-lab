"""Test sur le passé des tranches PortWatch (hebdomadaires et « Avg. # »), protocole tester-une-piste, 23/10/2026.

À chaque instant de décision T (chaque jour à 12 h UTC, de la création du marché jusqu'à la publication du jour cible) :
- données PortWatch connues : jours ≤ commun.connu_jusqua(T) (mise à jour le mardi ≈ 11 h UTC jusqu'au dimanche) ;
- prévision de S(D), somme des 7 jours finissant à D, par un modèle simple (marche aléatoire, erreurs empiriques
  tirées de l'historique PortWatch depuis 2019 et connues à T) ; probabilité de chaque tranche ;
- prix connu à T : dernier prix payé (data-api) pour acheter le OUI ou le NON dans les 24 h avant T ;
- pari si (proba du modèle − prix − frais) > seuil ; achat au PREMIER échange réel dans les 2 h après T
  (`taker_cost(..., after=True)`), un seul achat par marché (le premier signal), gardé jusqu'au règlement.
Événements jugés : D ≥ 01/06/2026 (contrôle du règlement 40/40 ; avant juin, révisions de PortWatch : 7/17).
Usage : PYTHONPATH=src python experiments/detroits/scripts/test_passe.py [--debut 2026-06-01]
"""
import argparse
import collections
import concurrent.futures as cf
import datetime as dt
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, __file__.rsplit("/", 1)[0])
import commun as c  # noqa: E402
from polymarket_agent import idea_test as it  # noqa: E402
from polymarket_agent import references as refs  # noqa: E402
from polymarket_agent.http_client import HttpClient  # noqa: E402

CACHE = Path(c.DONNEES) / "echanges"
UN_JOUR = dt.timedelta(days=1)


class Modele:
    """Loi de S(D) à partir des données connues jusqu'à L. `genre` : abs (erreurs en passages), log (erreurs relatives),
    melange (references.ma7_forecast, loi normale, garde-fou de régime) ; `fenetre` : nombre d'origines récentes (None = depuis 2019)."""

    def __init__(self, nom, genre, fenetre=None):
        self.nom, self.genre, self.fenetre = nom, genre, fenetre
        self.cache = {}

    def probas(self, s7, counts_by_day, L, h, intervalles, type_):
        key = (id(s7), L, h)
        if key not in self.cache:
            self.cache[key] = self._loi(s7, counts_by_day, L, h)
        loi = self.cache[key]
        if loi is None:
            return None
        div = 1 if type_ == "somme" else 7
        if loi[0] == "normale":
            mu, sd = loi[1], loi[2]
            return {k: refs._normal_cdf((b * div / 7 - mu) / sd) - refs._normal_cdf((a * div / 7 - mu) / sd) for k, (a, b) in intervalles.items()}
        tirages = loi[1]
        n = len(tirages)
        return {k: (sum(1 for v in tirages if a <= v / div < b) + 0.5) / (n + 1) for k, (a, b) in intervalles.items()}

    def _loi(self, s7, counts_by_day, L, h):
        if L not in s7:
            return None
        if self.genre == "melange":
            jours = sorted(d for d in counts_by_day if d <= L)
            f = refs.ma7_forecast([counts_by_day[d] for d in jours], h)
            return None if f is None else ("normale", f[0], f[1])
        origines = sorted(d for d in s7 if d + dt.timedelta(days=h) <= L)
        if self.fenetre:
            origines = origines[-self.fenetre:]
        if len(origines) < 60:
            return None
        base = s7[L]
        if self.genre == "abs":
            errs = [s7[j + dt.timedelta(days=h)] - s7[j] for j in origines]
            return ("tirages", [max(0.0, base + e) for e in errs])
        errs = [math.log((s7[j + dt.timedelta(days=h)] + 7) / (s7[j] + 7)) for j in origines]
        return ("tirages", [max(0.0, (base + 7) * math.exp(e) - 7) for e in errs])


MODELES = [Modele("marche_abs_365", "abs", 365), Modele("marche_log_depuis_2019", "log", None),
           Modele("marche_log_90", "log", 90), Modele("melange_normal", "melange")]


def preparer(debut):
    inv = c.charge_inventaire()
    series = {n: c.serie(n) for n in ("Strait of Hormuz", "Bab el-Mandeb Strait")}
    s7 = {n: {d: v for d in s for v in [c.somme7(s, d)] if v is not None} for n, s in series.items()}
    evs = []
    for ev in inv:
        cb = c.cible(ev)
        if not ev["clos"] or ev["detroit"] not in series or not cb or cb[1] < debut:
            continue
        win = c.gagnant(ev)
        if win is None:
            continue
        evs.append((ev, cb[0], cb[1], win))
    return evs, series, s7


def instants(ev, D, heure_maj=11):
    """Chaque jour à 12 h UTC, de la création du marché jusqu'à la publication de D (exclue)."""
    starts = [c.ts(q.get("startDate") or q.get("createdAt")) for q in ev["questions"]]
    t0 = min(s for s in starts if s)
    t = dt.datetime.combine(t0.date(), dt.time(12), tzinfo=dt.timezone.utc)
    if t < t0:
        t += UN_JOUR
    out = []
    while c.connu_jusqua(t, heure_maj) < D and t < dt.datetime.combine(D + dt.timedelta(days=14), dt.time(), tzinfo=dt.timezone.utc):
        out.append(t)
        t += UN_JOUR
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--debut", default="2026-06-01")
    ap.add_argument("--seuils", default="0.05,0.10")
    ap.add_argument("--heure-maj", type=int, default=11, help="heure UTC de la mise à jour du mardi (24 = connue le mercredi seulement)")
    ap.add_argument("--sortie", default="paris.json")
    args = ap.parse_args()
    evs, series, s7 = preparer(dt.date.fromisoformat(args.debut))
    print(len(evs), "événements clos à tranches depuis", args.debut, ":",
          dict(collections.Counter((e[0]["detroit"][:9], e[1]) for e in evs)))
    http = HttpClient(timeout=40, min_interval=0.25)
    with cf.ThreadPoolExecutor(4) as ex:
        trades = dict(ex.map(lambda e: (e[0]["id"], it.fetch_event_trades(http, CACHE, e[0]["id"])), evs))
    print("échanges relevés :", sum(len(v) for v in trades.values()), "; événements sans échange :", sum(1 for v in trades.values() if not v))
    seuils = [float(x) for x in args.seuils.split(",")]
    # Comparaison au marché (log-score) sur tous les couples (marché, T) qui ont un prix connu
    score = collections.defaultdict(lambda: [0.0, 0])
    paris = collections.defaultdict(list)
    sans_echange = collections.Counter()
    for ev, type_, D, win in evs:
        iv = c.intervalles(ev["questions"], "plancher")
        tr = trades[ev["id"]]
        toks = {q["id"]: json.loads(q["clobTokenIds"]) for q in ev["questions"] if q["id"] in iv}
        fees = {q["id"]: c.taux_frais(q) for q in ev["questions"]}
        pris = collections.defaultdict(set)  # (modèle, seuil) → marchés déjà achetés
        for T in instants(ev, D, args.heure_maj):
            L = c.connu_jusqua(T, args.heure_maj)
            h = (D - L).days
            tsT = int(T.timestamp())
            connus = {mid: (it.taker_cost(tr, yes, no, tsT, window=24 * 3600), it.taker_cost(tr, no, yes, tsT, window=24 * 3600))
                      for mid, (yes, no) in toks.items()}
            for mod in MODELES:
                pr = mod.probas(s7[ev["detroit"]], series[ev["detroit"]], L, h, iv, type_)
                if pr is None:
                    continue
                for mid, (yes, no) in toks.items():
                    won = int(mid == win)
                    p_yes, p_no = connus[mid]
                    if p_yes is not None:
                        pm = min(0.999, max(0.001, pr[mid]))
                        pk = min(0.999, max(0.001, p_yes))
                        sc = score[mod.nom]
                        sc[0] += -math.log(pm if won else 1 - pm) + math.log(pk if won else 1 - pk)
                        sc[1] += 1
                    for s in seuils:
                        if mid in pris[(mod.nom, s)]:
                            continue
                        for side, known, tok, other, p_side in ((1, p_yes, yes, no, pr[mid]), (0, p_no, no, yes, 1 - pr[mid])):
                            if known is None or not 0.01 <= known <= 0.99:
                                continue
                            if p_side - known - it.fee(known, fees[mid]) <= s:
                                continue
                            cost = it.taker_cost(tr, tok, other, tsT, window=2 * 3600, after=True)
                            if cost is None or cost >= 0.995:
                                sans_echange[(mod.nom, s)] += 1
                                continue
                            stake = cost + it.fee(cost, fees[mid])
                            gagne = won if side == 1 else 1 - won
                            paris[(mod.nom, s)].append({"gain": gagne / stake - 1, "evenement": ev["id"], "mois": D.strftime("%Y-%m"),
                                                       "cout": stake, "cote": "OUI" if side else "NON", "detroit": ev["detroit"][:9],
                                                       "type": type_, "h": h, "jour": T.date().isoformat(), "modele_p": round(p_side, 3),
                                                       "prix_connu": known, "marche": mid})
                            pris[(mod.nom, s)].add(mid)
                            break
    print("\nlog-score moyen du modèle MOINS celui du marché (négatif = le modèle fait mieux) :")
    for k, (tot, n) in score.items():
        print(f"  {k:24s} {tot / n:+.4f} sur {n} couples (marché, instant)")
    out = {}
    print("\nRéglage | paris | rendement moyen | confiance par événement | z des prix | mois gagnants | verdict")
    for (nom, s), bets in sorted(paris.items()):
        v = it.verdict(bets)
        out[f"{nom} seuil {s}"] = {"verdict": v, "paris": bets}
        par = collections.defaultdict(list)
        for b in bets:
            par[(b["detroit"], b["cote"])].append(b["gain"])
        detail = {f"{k[0]} {k[1]}": (len(g), round(sum(g) / len(g), 3)) for k, g in sorted(par.items())}
        print(f"{nom} seuil {s} | {v['paris']} | {v.get('rendement_moyen')} | {v.get('confiance_evenements')} ({v.get('evenements')} év.) | "
              f"{v.get('z_prix')} | {v.get('mois_gagnants')} | {v['verdict']} | sans échange : {sans_echange[(nom, s)]} | {detail}")
    Path(c.DONNEES, args.sortie).write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str))


if __name__ == "__main__":
    main()
