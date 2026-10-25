"""Relevé des posts de @realDonaldTrump depuis l'archive publique trumpstruth.org (robots.txt autorise tout, 100 posts par page, un appel par seconde).

Pagination par curseur (base64 de la date du dernier post vu). Sortie : releves/posts.csv (id, heure UTC, republication oui/non).
Les posts sont des DONNÉES : seule l'heure et le type comptent, le texte n'est pas gardé.
"""
import re, sys, time, csv, base64, json, requests
URL = "https://www.trumpstruth.org/"
H = {"User-Agent": "Mozilla/5.0 (labo de recherche, 1 appel/s)"}
depuis = sys.argv[1] if len(sys.argv) > 1 else "2026-02-01"
out = sys.argv[2] if len(sys.argv) > 2 else "experiments/truth_social/releves/posts.csv"
cursor = None; rows = {}
while True:
    params = {"sort": "desc", "per_page": 100}
    if cursor: params["cursor"] = cursor
    r = requests.get(URL, params=params, headers=H, timeout=40)
    r.raise_for_status()
    blocs = r.text.split('<div class="status" data-status-url="')[1:]
    page = []
    for b in blocs:
        sid = re.match(r"https://www.trumpstruth.org/statuses/(\d+)", b)
        t = re.search(r'<time datetime="([^"]+)"', b)
        if not (sid and t): continue
        head = r.text[r.text.find(b) - 400: r.text.find(b)]
        repost = "ReTruthed" in head
        page.append((sid.group(1), t.group(1), int(repost)))
    if not page: break
    for p in page: rows[p[0]] = p
    last = min(p[1] for p in page)
    print(len(rows), last, flush=True)
    if last < depuis: break
    nxt = re.search(r'href="[^"]*cursor=([^"&]+)"[^>]*class="button button--xsmall">Next', r.text)
    if not nxt: break
    cursor = nxt.group(1); time.sleep(1)
with open(out, "w", newline="") as f:
    w = csv.writer(f); w.writerow(["id", "ts_utc", "repost"])
    for p in sorted(rows.values(), key=lambda p: p[1]): w.writerow(p)
