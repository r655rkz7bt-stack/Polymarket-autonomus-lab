"""Catégories des marchés « d'ici / avant <date> » (27/10/2026) : contrôle par catégories (6 × 2 côtés) puis IA (étiquettes depuis 2025), profondeur, moitiés, pannes ChatGPT.
Lancer depuis la racine : .venv/bin/python experiments/decroissance_passe/scripts/analyse3.py > experiments/decroissance_passe/resultats_categories.txt"""
import sys, re, json, collections, statistics
sys.path.insert(0, "src"); sys.path.insert(0, "experiments/decroissance_passe/scripts")
import analyse as a
from polymarket_agent import idea_test as it
CAT = {"geopolitique": r"iran|israel|ukrain|russia|ceasefire|cease-fire|strike|war\b|invade|invasion|china|taiwan|venezuela|gaza|hamas|nato|military|sanction|hormuz|nuclear|peace|troops|blockade",
       "personnes_hors_fonction": r"\bout\b|resign|step down|leave office|fired|impeach|indict|arrest|convict|pardon",
       "crypto": r"bitcoin|ethereum|solana|crypto|\bxrp\b|token|coin|megaeth|fdv|airdrop",
       "ia_tech": r"\bgpt|openai|anthropic|gemini|claude|\bai\b|apple|tesla|nvidia|spacex|starship|launch|release|iphone",
       "trump_politique": r"trump|biden|congress|senate|house|shutdown|tariff|fed\b|rate cut|supreme court|executive order|musk"}
def cat(t):
    t = t.lower()
    for k, p in CAT.items():
        if re.search(p, t): return k
    return "autre"
AI = re.compile(r"\bgpt|openai|anthropic|gemini|claude|grok|llama|deepseek|mythos|\bai\b|chatgpt|\bmodel\b|sora|copilot|\bmistral|\bqwen", re.I)
OUT = re.compile(r"outage|app store|apple store|#1", re.I)
EV1 = a.charge(("marches.jsonl",))
print("== catégories, marchés de février-octobre 2026 (relevé général)")
for cote in ("non", "oui"):
    R = a.paris(EV1, gap_min=-1, cote=cote, ymin=0.03, ymax=0.35); by = collections.defaultdict(list)
    for r in R: by[cat(r["titre"])].append(r)
    print(cote.upper(), "tous :", a.resume(R))
    for k, v in sorted(by.items()): print("  ", k.ljust(24), a.resume(v))
EV = a.charge(("marches.jsonl", "marches_tags.jsonl"))
print("== IA (relevé général + étiquettes IA / tech, depuis 2025) :", len(EV), "événements")
for lab, f in (("IA (mot IA)", lambda t: AI.search(t)), ("IA hors pannes et classement app", lambda t: AI.search(t) and not OUT.search(t))):
    for side, lo, hi in (("oui", 0.03, 0.35), ("non", 0.03, 0.35), ("oui", 0.10, 0.40)):
        print(lab.ljust(34), side, lo, hi, a.resume([r for r in a.paris(EV, gap_min=-1, cote=side, ymin=lo, ymax=hi) if f(r["titre"])]))
R = [r for r in a.paris(EV, gap_min=-1, cote="oui", ymin=0.10, ymax=0.40) if AI.search(r["titre"]) and not OUT.search(r["titre"])]
Rs = sorted(R, key=lambda r: r["mois"]); m = len(Rs) // 2
print("hors pannes 0,10-0,40 : 1re moitié", a.resume(Rs[:m]), "| 2e", a.resume(Rs[m:]))
g = collections.defaultdict(float)
for x in R: g[x["eid"]] += x["win"] - x["pay"] - x["fee"]
top = sorted(g, key=g.get, reverse=True)[:5]; print("sans les 5 meilleurs événements", a.resume([x for x in R if x["eid"] not in top]))
for H in (30, 14, 7, 3, 1): print("  H", H, a.resume([r for r in R if r["H"] == H]))
RA = [r for r in a.paris(EV, gap_min=-1, cote="oui", ymin=0.10, ymax=0.40) if AI.search(r["titre"])]
idx = {mk["id"]: (by) for e, by in EV for mk in e["markets"]}; mks = {mk["id"]: mk for e, by in EV for mk in e["markets"]}
def prof(r):
    mk = mks[r["mid"]]; by = idx[r["mid"]]; yes, no = json.loads(mk["clobTokenIds"]); T = a.ts(mk["endDate"]) - int(r["H"] * 86400); tot = 0
    for t in by.get(yes, []):
        if T <= t[0] <= T + 3600 and t[2] == "BUY" and t[3] <= r["pay"] + 0.02: tot += t[4]
    for t in by.get(no, []):
        if T <= t[0] <= T + 3600 and t[2] == "SELL" and 1 - t[3] <= r["pay"] + 0.02: tot += t[4]
    return tot
for r in RA: r["prof"] = prof(r)
print("IA 0,10-0,40 (avec pannes) : profondeur médiane", round(statistics.median(r["prof"] for r in RA), 1))
for seuil in (0, 20, 100, 400): print("  parts achetables >=", seuil, a.resume([r for r in RA if r["prof"] >= seuil]))
OUTR = re.compile(r"outage", re.I)
print("== pannes ChatGPT")
for side in ("oui", "non"):
    print(side, a.resume([r for r in a.paris(EV, gap_min=-1, cote=side, ymin=0.03, ymax=0.97, horizons=(14, 10, 7, 5, 3, 2, 1)) if OUTR.search(r["titre"])]))
