"""Garde dans un relevé de marchés (releve_marches.py) seulement les questions que modele.parse sait lire (above / less than / reach / dip sur un actif connu) et
dont le règlement est net : évite de télécharger les échanges de milliers de marchés « FDV », « airdrop », etc. Usage : python filtre_marches.py entree.jsonl sortie.jsonl"""
import json, sys, re
sys.argv_save = sys.argv; ASSETS = {"bitcoin", "ethereum", "solana", "xrp", "dogecoin", "bnb"}
def garde(q):
    ql = q.lower()
    if not any(a in ql for a in ASSETS) or len(re.findall(r"\$([\d,]+(?:\.\d+)?)", q)) != 1: return False
    return bool(re.search(r"price of \w+ be (above|less than|below)", ql) or (re.search(r"\b(reach|hit)\b", ql) or re.search(r"\bdip to\b", ql)) and " on " in ql)
n = k = 0
with open(sys.argv[2], "w") as f:
    for l in open(sys.argv[1]):
        m = json.loads(l); n += 1
        if (m["vol"] or 0) >= 5000 and "up or down" not in m["question"].lower() and sorted(map(str, m["prices"])) == ["0", "1"] and garde(m["question"]):
            f.write(l); k += 1
print(n, "lus,", k, "gardés")
