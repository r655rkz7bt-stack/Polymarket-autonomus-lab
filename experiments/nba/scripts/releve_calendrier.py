"""Calendrier et scores NBA 2025-26 (basketball-reference.com, pages mensuelles) → donnees/matchs.json."""
import json, re, time, html, subprocess
import requests
from datetime import datetime
D = "donnees"
s = requests.Session(); s.headers["User-Agent"] = "Mozilla/5.0"
games = []
for mois in ["october", "november", "december", "january", "february", "march", "april", "may", "june"]:
    # requests est refusé (403) par ce site, curl non
    page = subprocess.run(["curl", "-s", "-A", "Mozilla/5.0", f"https://www.basketball-reference.com/leagues/NBA_2026_games-{mois}.html"],
                          capture_output=True, text=True).stdout
    if "<table" not in page:
        print(mois, "page vide"); continue
    n0 = len(games)
    for row in re.findall(r"<tr >(.*?)</tr>", page, flags=re.S):
        c = dict(re.findall(r'data-stat="(\w+)"[^>]*>(.*?)</t[hd]>', row, flags=re.S))
        if "visitor_pts" not in c or not re.sub("<.*?>", "", c["visitor_pts"]).strip():
            continue
        txt = lambda k: html.unescape(re.sub("<.*?>", "", c.get(k, ""))).strip()
        d = datetime.strptime(txt("date_game"), "%a, %b %d, %Y").date().isoformat()
        games.append({"date": d, "heure_et": txt("game_start_time"), "away": txt("visitor_team_name"), "home": txt("home_team_name"),
                      "pa": int(txt("visitor_pts")), "ph": int(txt("home_pts")), "ot": txt("overtimes")})
    print(mois, len(games) - n0, flush=True)
    time.sleep(4)
json.dump(games, open(f"{D}/matchs.json", "w"))
print("total", len(games))
