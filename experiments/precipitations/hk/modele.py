"""Pluie de novembre à l'Observatoire de Hong Kong : cumul observé + reste du mois tiré des mêmes dates (1947-2025)."""
# Données : curl -o donnees/daily_HKO_RF_ALL.csv https://data.weather.gov.hk/weatherAPI/cis/csvfile/HKO/ALL/daily_HKO_RF_ALL.csv
import csv, collections, sys
rows = collections.defaultdict(dict)
for r in csv.reader(open("donnees/daily_HKO_RF_ALL.csv", encoding="utf-8-sig")):
    if len(r) < 4 or not r[0].isdigit(): continue
    v = r[3].strip()
    if v == "***": continue
    rows[int(r[0])][(int(r[1]), int(r[2]))] = 0.0 if v in ("Trace", "微量", "") else float(v)
BINS = [("<5", 0, 5), ("5-10", 5, 10), ("10-25", 10, 25), ("25-35", 25, 35), ("35-60", 35, 60), ("60-95", 60, 95), ("95+", 95, 1e9)]
def tranche(x):  # « pile sur une borne → tranche du dessus »
    for n, a, b in BINS:
        if a <= x < b: return n
def loi(obs, d0, d_sec=None, sec_max=None, ans=range(1947, 2026)):
    """obs = cumul jusqu'à d0-1 ; jours d0..30 tirés ; si d_sec : jours d0..d_sec gardés seulement si leur pluie <= sec_max."""
    c = collections.Counter(); n = 0
    for y in ans:
        if (11, 30) not in rows[y]: continue
        if d_sec is not None and sum(rows[y].get((11, d), 0) for d in range(d0, d_sec + 1)) > sec_max: continue
        tot = obs + sum(rows[y].get((11, d), 0) for d in range(d0, 31)); c[tranche(tot)] += 1; n += 1
    return n, {b[0]: round(c[b[0]] / n, 3) for b in BINS}
if __name__ == "__main__":
    obs = float(sys.argv[1]) if len(sys.argv) > 1 else 3.2
    d0 = int(sys.argv[2]) if len(sys.argv) > 2 else 13
    print("climatologie", loi(obs, d0))
    print("1991-2025   ", loi(obs, d0, ans=range(1991, 2026)))
    for m in (2, 5, 10):
        print(f"jours {d0}-23 <= {m} mm", loi(obs, d0, 23, m))
    tots = sorted(sum(rows[y].get((11, d), 0) for d in range(1, 31)) for y in range(1947, 2026) if (11, 30) in rows[y])
    print("novembres entiers : médiane", tots[len(tots)//2], "quartiles", tots[len(tots)//4], tots[3*len(tots)//4])
