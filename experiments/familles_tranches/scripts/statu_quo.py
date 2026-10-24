"""« Même gagnant que la dernière fois » dans les séries répétitives (App Store du jour, Billboard, Spotify, Netflix) : le prix du gagnant précédent est-il trop bas ou trop haut ?
Pour chaque événement, on retrouve dans le marché la ligne du gagnant de l'événement précédent de la même série (libellé identique) et on lit son prix h heures avant la fin."""
import sys, re, collections, math
sys.path.insert(0, "experiments/familles_tranches/scripts"); sys.path.insert(0, "src")
from favori import *
MOIS = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sept?|Oct|Nov|Dec)\.?"
def serie(t):
    k = re.sub(r"\(.*?\)", "", t); k = re.sub(MOIS + r"\s+\d+(?:\s*-\s*\d+)?", "DATE", k); k = re.sub(r"(?<![#\d])\d+", "N", k)
    return " ".join(k.split())
def run_sq(fams, h, max_gap_days, lo=0.05, hi=0.98, rate=0.05, side=1):
    ser = collections.defaultdict(list)
    for fam in fams:
        for c in cases(fam): ser[(fam, serie(c["e"]["title"]))].append(c)
    bets = []
    for key, v in ser.items():
        if len(v) < 8: continue
        v.sort(key=lambda c: c["end"])
        for a, b in zip(v, v[1:]):
            if b["end"] - a["end"] > max_gap_days * 86400: continue
            wa = [m["git"] for m in a["ms"] if m["win"]][0]
            mb = [m for m in b["ms"] if m["git"] == wa]
            if not mb or wa in (None, "", "Other"): continue
            m = mb[0]; t = b["end"] - h * 3600
            p = last_before(m["series"], t, 12 * 3600)
            if p is None or not lo <= p < hi: continue
            px = taker_buy(b["trades"], m["tokens"][0], m["tokens"][1], t, 3 * 3600, side)
            if px is None: continue
            cost = px + rate * px * (1 - px)
            bets.append({"gain": ((m["win"] if side else 1 - m["win"]) - cost) / cost, "evenement": b["e"]["id"], "mois": datetime.fromtimestamp(b["end"], timezone.utc).strftime("%Y-%m"), "cout": px, "serie": key})
    return bets
if __name__ == "__main__":
    for nom, fams, gap in (("App Store (jour)", ["appstore"], 9), ("Billboard (semaine)", ["billboard"], 9), ("Spotify chanson (semaine)", ["spotify_song"], 9), ("Netflix (semaine)", ["netflix"], 9)):
        for h in (96, 48, 24, 12):
            b = run_sq(fams, h, gap)
            if len(b) < 15: continue
            v = verdict(b)
            print(f"{nom} h={h}: n={v['paris']} ({len({x['serie'] for x in b})} séries) prix moyen {sum(x['cout'] for x in b)/len(b):.2f} gagnés/attendus {sum(1 for x in b if x['gain']>0)}/{sum(x['cout'] for x in b):.1f} rendement {v['rendement_moyen']:+.3f} t {v['confiance_evenements']:+.2f} z_prix {v['z_prix']:+.2f}")

    print("--- NON du gagnant précédent (App Store)")
    for h in (96, 48, 24, 12, 6):
        for lo, hi in ((0.05, 0.98), (0.5, 0.98)):
            b = run_sq(["appstore"], h, 9, lo, hi, side=0)
            if len(b) < 15: continue
            v = verdict(b); g = sorted((x["gain"] for x in b), reverse=True)
            print(f"h={h} OUI {lo}-{hi}: NON n={v['paris']} coût moyen {sum(x['cout'] for x in b)/len(b):.2f} gagnés {sum(1 for x in b if x['gain']>0)} attendus {sum(x['cout'] for x in b):.1f} rendement {v['rendement_moyen']:+.3f} sans 3 meilleurs {sum(g[3:])/(len(g)-3):+.3f} t {v['confiance_evenements']:+.2f} z_prix {v['z_prix']:+.2f} mois {v['mois_gagnants']}")
