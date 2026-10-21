"""Outils communs du test « aux prix payés » (21/10/2026) : vrais échanges des preneurs (data-api),
premier prix payé après une décision, résumé des paris. Lancer les scripts depuis la racine du dépôt.

Échanges : GET https://data-api.polymarket.com/trades?market=<conditionId>&takerOnly=true&start=&end=
(`start` / `end` en secondes Unix filtrent bien la fenêtre ; décalage maximal 10 000 : au-delà, la
fenêtre est coupée en deux). Cache gzip dans donnees/prix_payes/echanges/ (ignoré par Git)."""
import gzip
import json
import math
import statistics as st
import sys
import threading
import time
from collections import defaultdict
from pathlib import Path

import requests

sys.path.insert(0, "src")
from polymarket_agent.idea_test import verdict  # noqa: E402

TRADES = "https://data-api.polymarket.com/trades"
CACHE = Path("donnees/prix_payes/echanges")
_local = threading.local()


def get(url, params, tries=6):
    """GET poli : 6 essais, attente 1, 2, 4… s. Réponse 400 (décalage trop grand) rendue telle quelle."""
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
        _local.s.headers["User-Agent"] = "polymarket-autonomous-lab (recherche, simulation)"
    for k in range(tries):
        try:
            r = _local.s.get(url, params=params, timeout=40)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 400:
                return {"erreur": r.text[:200]}
        except Exception:  # réseau : on réessaie
            pass
        time.sleep(min(30, 2 ** k))
    raise RuntimeError(f"pas de réponse : {url} {params}")


def _window(cid, a, b):
    rows = []
    for page in range(10):
        batch = get(TRADES, {"market": cid, "takerOnly": "true", "limit": 1000, "offset": page * 1000, "start": a, "end": b})
        if not isinstance(batch, list):
            break
        rows += [[int(t["timestamp"]), str(t["asset"]), str(t["side"]), float(t["price"]), float(t["size"])]
                 for t in batch if t.get("timestamp") and t.get("price") is not None]
        if len(batch) < 1000:
            return rows, True
    return rows, False  # 10 000 échanges ou plus : fenêtre à couper


def trades(cid, a, b):
    """Tous les échanges de preneurs du marché entre a et b (secondes Unix, bornes comprises), triés."""
    path = CACHE / f"{cid}_{a}_{b}.json.gz"
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    rows, complete = _window(cid, a, b)
    if not complete:
        mid = (a + b) // 2
        rows = trades(cid, a, mid) + trades(cid, mid + 1, b)
    rows.sort()
    CACHE.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(rows).encode()))
    return rows


def cached(cid, a, b):
    """Échanges déjà relevés pour cette fenêtre, ou None (rien n'est téléchargé)."""
    path = CACHE / f"{cid}_{a}_{b}.json.gz"
    return json.loads(gzip.decompress(path.read_bytes())) if path.exists() else None


def paid(rows, token, other, t0, t1):
    """Premier échange de preneur qui ACHÈTE `token` entre t0 et t1 : achat du jeton au prix p, ou vente
    de l'autre issue au prix p (= jeton à 1 − p). C'est le prix qu'on aurait payé en achetant à t0.
    Rend (heure, prix du jeton, parts) ou None (aucun échange : pas de pari)."""
    for t in rows:  # triés par heure
        if t[0] < t0:
            continue
        if t[0] > t1:
            break
        if t[1] == token and t[2] == "BUY":
            return t[0], t[3], t[4]
        if t[1] == other and t[2] == "SELL":
            return t[0], 1 - t[3], t[4]
    return None


def gain(won, cost, rate):
    """Résultat par euro misé : 1 part achetée à `cost`, frais du barème rate·p·(1−p) par part."""
    return ((1.0 if won else 0.0) - cost - rate * cost * (1 - cost)) / cost


def tstat(v):
    if len(v) < 3:
        return float("nan")
    s = st.stdev(v)
    return st.mean(v) / s * math.sqrt(len(v)) if s > 0 else float("nan")


def resume(bets, label="", min_bets=30):
    """bets : dicts {gain, evenement, mois, cout}. Une ligne lisible + le verdict d'idea_test."""
    if len(bets) < 3:
        print(f"  {label:40} {len(bets)} achats")
        return None
    g = [b["gain"] for b in bets]
    ev = defaultdict(list)
    for b in bets:
        ev[b["evenement"]].append(b["gain"])
    em = [st.mean(v) for v in ev.values()]
    v = verdict(bets, min_bets=min_bets)
    print(f"  {label:40} {len(g):5} achats {st.mean(g):+.3f} (t {tstat(g):+.2f}) | {len(em):4} évén. {st.mean(em):+.3f} "
          f"(t {tstat(em):+.2f}) | mois + {v['mois_gagnants']} | prix moyen {st.mean(b['cout'] for b in bets):.3f} → {v['verdict']}")
    return v
