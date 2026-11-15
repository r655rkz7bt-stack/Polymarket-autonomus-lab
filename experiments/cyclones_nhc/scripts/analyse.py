"""Piste n° 63 : intensité de pointe d'un cyclone, prévision officielle du NHC (OFCL) contre le prix Polymarket.

Modèle (aucun regard vers le futur) : à l'instant T, dernier avis du NHC disponible (heure synoptique + 3 h).
  M0 = intensité la plus forte déjà annoncée (avis ≤ T), F = maximum prévu par cet avis (échéances 3 à 120 h),
  pointe finale = max(M0, F + D), D tiré des erreurs passées du NHC (2021-2025, tous les cyclones : D = pointe réelle du
  reste de la vie − F, pour les avis dont F est à ±10 kt). Rien de 2026 n'entre dans l'étalonnage.
Règlement relu : pointe = maximum des intensités d'avis (échéance 3 h, sinon 0 h) ; comparée au résultat Polymarket.
Paris : pour chaque avis et chaque jeton, premier vrai échange de 10 à 180 min après la parution ; achat si
modèle − prix ≥ seuil, au prix de l'échange + frais du marché (weather_fees 5 % × p × (1 − p)).
Usage : python analyse.py [seuil] [parts_min]
"""
import json, sys, re, glob, bisect, collections, datetime as dt
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
from polymarket_agent.idea_test import verdict

D = Path(__file__).resolve().parents[1] / "donnees"
SEUILS_CAT = [64, 83, 96, 113, 137]          # kt : catégorie 1 à 5 (74, 96, 111, 130, 157 mph)

def lire_ofcl(f):
    av = collections.defaultdict(dict)
    for l in open(f):
        p = [x.strip() for x in l.split(",")]
        if len(p) < 9 or not p[8].isdigit():
            continue
        av[p[2]][int(p[5])] = int(p[8])
    out = []
    for base, taus in sorted(av.items()):
        t0 = dt.datetime.strptime(base, "%Y%m%d%H").replace(tzinfo=dt.timezone.utc)
        now = taus.get(3, taus.get(0))
        if now is None:
            continue
        prev = [v for t, v in taus.items() if 3 <= t <= 120] or [now]
        out.append(dict(dispo=t0 + dt.timedelta(hours=3), now=now, F=max(prev)))
    return out

def etalonnage():
    pts = []
    for f in glob.glob(str(D / "adeck" / "a*20[2][1-5].ofcl")):
        avs = lire_ofcl(f)
        for i, a in enumerate(avs):
            R = max(x["now"] for x in avs[i:])
            pts.append((a["F"], R - a["F"]))
    pts.sort()
    return pts

def p_au_moins(thr, M0, F, cal, fen=10):
    if M0 >= thr:
        return 1.0
    i, j = bisect.bisect_left(cal, (F - fen, -999)), bisect.bisect_right(cal, (F + fen, 999))
    ds = [d for _, d in cal[i:j]] or [d for _, d in cal]
    return sum(1 for d in ds if F + d >= thr) / len(ds)

NOMS = {}
for f in glob.glob(str(D / "bdeck" / "b*.dat")):
    c = collections.Counter(l.split(",")[27].strip() for l in open(f) if len(l.split(",")) > 27)
    nom = next((n for n, _ in c.most_common() if n and not n.startswith(("INVEST", "GENESIS"))), None)
    if nom:
        b = Path(f).stem[1:]
        NOMS[(nom, b[-4:])] = b

def seuil_marche(e, m):
    """(seuil kt bas, seuil kt haut ou None) : le jeton OUI gagne si seuil_bas ≤ pointe < seuil_haut."""
    t = (e["titre"] + " " + m["titre"]).lower()
    if "strengthen" in t:
        return 64, None
    if "category 5" in t and "become" in t:
        return 137, None
    if "what category will" in t:     # échelle « au moins »
        k = int(re.findall(r"\d", m["titre"])[0]); return SEUILS_CAT[k - 1], None
    if "how strong" in t:
        if "or weaker" in m["titre"].lower():
            return 0, 83
        k = int(re.findall(r"\d", m["titre"])[0])
        return SEUILS_CAT[k - 1], (SEUILS_CAT[k] if k < 5 else None)
    return None

def echeance(e):
    m = re.search(r"between market creation and ([A-Z][a-z]+ \d+, \d{4}), 11:59 PM ET", e["description"])
    if not m:
        return None
    d = dt.datetime.strptime(m.group(1), "%B %d, %Y") + dt.timedelta(hours=23, minutes=59 + 5 * 60)
    return d.replace(tzinfo=dt.timezone.utc)

def main(seuil=0.10, parts_min=0.0, fen_min=10, fen_max=180, verbose=True):
    cal = etalonnage()
    ev = json.loads((D / "evenements.json").read_text())
    tr = collections.defaultdict(list)
    for l in open(D / "echanges.jsonl"):
        r = json.loads(l); tr[r["jeton"]].append(r)
    for v in tr.values():
        v.sort(key=lambda r: r["ts"])
    paris, controle, logs = [], [], []
    for e in ev:
        noms = re.findall(r"(?:Tropical Storm|Hurricane|Storm)?\s*([A-Z][a-z]+)", e["titre"])
        an = (e["debut"] or "")[:4]
        atcf = None
        mm = re.search(r"NHC designation ([A-Z]{2}\d{6})", e["description"])
        if mm:
            atcf = mm.group(1).lower()
        else:
            for n in noms:
                if (n.upper(), an) in NOMS:
                    atcf = NOMS[(n.upper(), an)]; break
        if not atcf or not Path(D / "adeck" / f"a{atcf}.ofcl").exists():
            continue
        avs = lire_ofcl(D / "adeck" / f"a{atcf}.ofcl")
        fin = echeance(e)
        for m in e["marches"]:
            s = seuil_marche(e, m)
            if not s or not m["jetons"]:
                continue
            lo, hi = s
            pointe = max(a["now"] for a in avs if fin is None or a["dispo"] <= fin)
            oui = pointe >= lo and (hi is None or pointe < hi)
            officiel = m["prix"][0] == "1"
            controle.append((e["titre"][:40], m["titre"][:20], pointe, oui, officiel))
            taux = 0.05 if m["frais"] == "weather_fees" else 0.0
            for i, a in enumerate(avs):
                if fin and a["dispo"] > fin:
                    break
                M0 = max(x["now"] for x in avs[: i + 1])
                p_lo = p_au_moins(lo, M0, a["F"], cal) if lo > 0 else 1.0
                p_hi = p_au_moins(hi, M0, a["F"], cal) if hi else 0.0
                p_oui = max(0.0, p_lo - p_hi)
                t0 = a["dispo"].timestamp() + fen_min * 60
                for k, jeton in enumerate(m["jetons"][:2]):
                    pm = p_oui if k == 0 else 1 - p_oui
                    ts = tr.get(jeton, [])
                    j = bisect.bisect_left([r["ts"] for r in ts], t0)
                    if j >= len(ts) or ts[j]["ts"] > a["dispo"].timestamp() + fen_max * 60:
                        continue
                    r = ts[j]
                    if r["parts"] < parts_min:
                        continue
                    prix = r["prix"]
                    if not 0.02 <= prix <= 0.98 or pm - prix < seuil:
                        continue
                    gagne = (oui == officiel) if k == 0 else (oui != officiel)
                    gagne = (officiel if k == 0 else not officiel)
                    cout = prix + taux * prix * (1 - prix)
                    paris.append(dict(gain=(1.0 if gagne else 0.0) / cout - 1, evenement=atcf, mois=a["dispo"].strftime("%Y-%m"),
                                      cout=prix, p=pm, gagne=gagne, marche=m["id"], k=k))
    return paris, controle, cal

if __name__ == "__main__":
    seuil = float(sys.argv[1]) if len(sys.argv) > 1 else 0.10
    pmin = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
    paris, controle, cal = main(seuil, pmin)
    ok = sum(1 for c in controle if c[3] == c[4])
    print(f"étalonnage : {len(cal)} avis 2021-2025 ; règlement relu {ok}/{len(controle)}")
    for c in controle:
        if c[3] != c[4]: print("  ÉCART", c)
    if paris:
        n = len(paris); g = sum(p["gagne"] for p in paris); att = sum(p["cout"] for p in paris); mod = sum(p["p"] for p in paris)
        print(f"seuil {seuil} parts≥{pmin} : {n} paris, {len(set(p['evenement'] for p in paris))} cyclones, gagnés {g} pour {att:.1f} payés (modèle {mod:.1f}), rendement {sum(p['gain'] for p in paris)/n:+.1%}")
        v = verdict(paris, min_bets=10)
        print({k: v[k] for k in v if k in ("verdict", "rendement_moyen", "t_evenement", "mois", "par_prix", "z_prix", "moitie_1", "moitie_2", "evenements")})
