"""Piste n° 66 (comptage tardif), 16/11/2026 : marge ACTUELLE du décompte officiel californien (api.sos.ca.gov/returns/us-rep/district/<n>,
sans clé, pas de robots.txt ; la page electionresults.sos.ca.gov est protégée par Incapsula : jamais lue) contre les tranches des marchés
« CA-<n> House Election Margin of Victory » (Gamma, carnets du CLOB). Écrit un relevé daté dans releves/ (jsonl.gz) et affiche, par district,
la tranche où tombe la marge actuelle, sa distance aux bornes et les prix acheteur / vendeur."""
from __future__ import annotations

import gzip, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path

import requests

H = {"User-Agent": "curl/8"}
OUT = Path(__file__).parent / "releves"


def bracket(item: str):
    """(parti, bas, haut) en points de marge ; « Republican Win » = (R, 0, 100) pour un district où D est attendu (et inversement)."""
    s = item.replace("–", "-")
    m = re.match(r"(Democrat|Republican)s? (?:win )?by ?(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)%?", s, re.I) or \
        re.match(r"(Democrat|Republican)s? (\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)%?", s, re.I)
    if m:
        return m.group(1)[0].upper(), float(m.group(2)), float(m.group(3))
    m = re.match(r"(Democrat|Republican)s? (\d+(?:\.\d+)?)%?\+", s, re.I)
    if m:
        return m.group(1)[0].upper(), float(m.group(2)), 1000.0
    m = re.match(r"(Democrat|Republican)s? Win", s, re.I)
    if m:
        return m.group(1)[0].upper(), 0.0, 1000.0
    return None


def api_district(n: int):
    r = requests.get(f"https://api.sos.ca.gov/returns/us-rep/district/{n}", headers=H, timeout=30)
    if r.status_code != 200:
        return None
    d = r.json()
    votes = {}
    for c in d.get("candidates", []):
        votes.setdefault(c["Party"], 0)
        votes[c["Party"]] += int(str(c["Votes"]).replace(",", ""))
    return d.get("ReportingTime"), votes, d.get("candidates")


def main():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M")
    evs = []
    for q in ("House Election Margin of Victory",):
        for page in range(1, 12):
            r = requests.get("https://gamma-api.polymarket.com/public-search", headers=H, timeout=30,
                             params={"q": "CA- " + q, "events_status": "active", "limit_per_type": 50, "page": page})
            got = [e for e in (r.json().get("events") or []) if re.match(r"CA-\d+ House Election Margin of Victory", e.get("title", ""))]
            evs += got
            if not r.json().get("events"):
                break
    seen, lignes = set(), []
    for e in evs:
        if e["id"] in seen:
            continue
        seen.add(e["id"])
        n = int(re.match(r"CA-(\d+)", e["title"]).group(1))
        full = requests.get(f"https://gamma-api.polymarket.com/events/{e['id']}", headers=H, timeout=30).json()
        api = api_district(n)
        if api is None:
            continue
        when, votes, cands = api
        tot = sum(votes.values())
        d, rr = votes.get("Dem", 0), votes.get("Rep", 0)
        # deux candidats du même parti (top-two) : marge entre les deux premiers, parti du premier
        top = sorted(((int(str(c["Votes"]).replace(",", "")), c["Party"], c["Name"]) for c in cands), reverse=True)
        marge = 100.0 * (top[0][0] - top[1][0]) / tot if tot else None
        for m in full.get("markets", []):
            if m.get("closed"):
                continue
            b = bracket(m.get("groupItemTitle") or "")
            lignes.append(dict(ts=stamp, district=n, event_id=e["id"], market_id=m["id"], item=m.get("groupItemTitle"), tranche=b,
                               bid=m.get("bestBid"), ask=m.get("bestAsk"), api_heure=when, top=top[:2], total=tot, marge=marge,
                               parti_tete=top[0][1]))
        time.sleep(0.2)
    OUT.mkdir(exist_ok=True)
    with gzip.open(OUT / f"californie_{stamp}.jsonl.gz", "wt") as f:
        for l in lignes:
            f.write(json.dumps(l, ensure_ascii=False) + "\n")
    print(len(seen), "événements", len(lignes), "tranches ->", OUT / f"californie_{stamp}.jsonl.gz")


if __name__ == "__main__":
    main()
