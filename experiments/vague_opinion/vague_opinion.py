"""Vague d'opinion (18/10/2026) : sur les marchés Polymarket LONGS (fin annoncée >= 7 jours après
l'observation), un pic d'attention médiatique sur le sujet du marché (beaucoup plus d'articles que
d'habitude sur les dernières heures) PRÉCÈDE-t-il un mouvement du prix dans le même sens (6 à 72 h) ?
Et « suivre la dérive quand l'attention explose » bat-il le coût d'un aller-retour (écart + frais) ?

Test sur le PASSÉ uniquement (simulation, aucun ordre, aucune clé, aucune API payante).

Usage : .venv/bin/python -I experiments/vague_opinion/vague_opinion.py [étape]
  étapes : select | gkg | gdelt | analyse | all (défaut : all = select, gkg, analyse)
Sorties : experiments/vague_opinion/marches.json (marchés retenus + mots-clés),
          experiments/vague_opinion/resultats.json (tous les chiffres du rapport),
          experiments/vague_opinion/signaux.csv (chaque signal / transaction simulée).
Les téléchargements bruts sont gardés (gzip) dans experiments/vague_opinion/cache/ : relancer le script
ne retélécharge rien (sauf les réponses en erreur, jamais mises en cache).

Sources (gratuites, publiques, sans clé) :
- Polymarket Gamma /markets : choix des marchés (étiquettes Politique 2, Géopolitique 100265, Monde 101970,
  Culture 596), date de fin, barème de frais (feesEnabled, feeSchedule.rate).
- Polymarket data-api /trades : échanges RÉELLEMENT exécutés (horodatage, prix, taille, issue). On n'utilise
  PAS l'historique de prix à 10 min (il fabrique des gains sur des carnets vides).
  Conversion : un échange sur l'issue NO au prix p est compté comme un prix YES de 1 - p (marché binaire,
  YES + NO = 1 à l'écart près).
- Attention, source PRINCIPALE : fichiers publics GDELT GKG 2.0 (un fichier toutes les 15 min, une ligne
  par article de presse en ligne en anglais : titre, adresse, personnes, organisations, lieux). On compte,
  heure par heure, les articles dont le titre / l'adresse / les noms contiennent la requête du marché.
- Attention, recoupement seulement : API GDELT DOC 2.0 (mode timelinevolraw, étape « gdelt »). Elle
  répondait HTTP 429 à ~4 requêtes sur 5 depuis notre adresse (sortie partagée) : impossible de couvrir
  91 sujets x 6 semaines en temps raisonnable ; les quelques tranches obtenues servent à comparer.

Règles anti « regard vers le futur » : à l'heure t, le signal n'utilise que les articles avant t et les
échanges avant t. Les issues (t+6 h, t+24 h, t+72 h, transaction simulée) n'utilisent que l'après.
"""
import csv
import gzip
import hashlib
import json
import math
import os
import random
import re
import ssl
import statistics as st
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
GAMMA = "https://gamma-api.polymarket.com"
DATA = "https://data-api.polymarket.com"
GDELT = "https://api.gdeltproject.org/api/v2/doc/doc"
UTC = timezone.utc

# Période d'observation des signaux (t) et marges autour.
OBS_START = datetime(2026, 9, 15, tzinfo=UTC)
OBS_END = datetime(2026, 10, 15, tzinfo=UTC)            # exclu
ATT_START = OBS_START - timedelta(days=8)                # 7 jours de référence + marge
PRICE_START = OBS_START - timedelta(days=2)
PRICE_END = OBS_END + timedelta(days=6)                  # t + 120 h au maximum
TAGS = {2: "politique", 100265: "géopolitique", 101970: "monde", 596: "culture"}
MIN_END_GAP = timedelta(days=7)                          # fin annoncée >= t + 7 j
N_MARKETS_MAX = 140
MAX_PER_EVENT = 4                                        # diversité : pas 40 candidats d'une même élection

# Paramètres du signal (valeurs de base ; une grille est testée en plus).
SPIKE_MIN = 2.0          # articles 3 h / moyenne 3 h des 7 jours précédents
MIN_ART3 = 5             # minimum absolu d'articles sur les 3 dernières heures
DRIFT_MIN, DRIFT_MAX = 0.02, 0.08
DRIFT_H = 6
COOLDOWN_H = 24
NOSPIKE_MAX = 1.2        # contrôle « sans attention » : rapport < 1,2
MIN_BASE_H = 48          # au moins 48 heures couvertes par GDELT dans les 7 jours de référence
P_MIN, P_MAX = 0.05, 0.95  # prix YES à t (aux extrêmes, +0,05 est impossible et le carnet est vide)
HALF_SPREAD = 0.01
TP, SL, MAX_HOLD_H = 0.05, 0.05, 120
HORIZONS = [6, 24, 72]
DEFAULT_FEE_RATE = 0.04  # politique, si feesEnabled sans barème lisible

_ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE") or None)
_last = defaultdict(float)


def _cache_path(full):
    key = hashlib.sha256(full.encode()).hexdigest()[:24]
    return CACHE / key[:2] / f"{key}.json.gz"


def get(url, params=None, gap=0.3, tries=8, gdelt=False):
    """GET JSON avec cache disque gzip ; poli (gap secondes entre appels au même hôte) ; réessais."""
    full = url + ("?" + urllib.parse.urlencode(params) if params else "")
    path = _cache_path(full)
    if path.exists():
        return json.loads(gzip.decompress(path.read_bytes()))
    host = urllib.parse.urlparse(url).netloc
    for attempt in range(tries):
        wait = gap - (time.time() - _last[host])
        if wait > 0:
            time.sleep(wait)
        _last[host] = time.time()
        try:
            req = urllib.request.Request(full, headers={"User-Agent": "polymarket-lab-research",
                                                        "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=90, context=_ctx) as r:
                raw = r.read()
            text = raw.decode("utf-8", "replace").strip()
            if gdelt and not text.startswith("{"):
                # GDELT répond en texte brut pour les requêtes refusées (mot trop court, etc.)
                data = {"_erreur": text[:300]}
            else:
                data = json.loads(text) if text else {}
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500:
                pause = (25 + 5 * min(attempt, 6)) if gdelt and e.code == 429 else 3 * (attempt + 1)
                if attempt < tries - 1:
                    if not (gdelt and e.code == 429 and attempt % 5):
                        print(f"  HTTP {e.code}, pause {pause} s (essai {attempt + 1})", flush=True)
                    time.sleep(pause)
                    continue
            print("  échec", e.code, full[:140], flush=True)
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ConnectionError) as e:
            if attempt < tries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            print("  échec réseau", repr(e)[:100], full[:140], flush=True)
            return None
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(json.dumps(data).encode()))
    return data


def iso(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=UTC)


def ts(d):
    return int(d.timestamp())


# ----------------------------------------------------------------------------------------------
# 1. Marchés
# ----------------------------------------------------------------------------------------------
STOP = set("""will the a an of in on by to be is as at for and or with before after end out next new from
than more less into over under during until win wins won become becomes say says said reach hit have has
january february march april may june july august september october november december jan feb mar apr jun
jul aug sep sept oct nov dec yes no who what which when where how does do did any this that its his her
their there not least most top first second third how many much other another us u.s. vs
2024 2025 2026 2027 2028 2029 2030 q1 q2 q3 q4 president prime minister election party leader""".split())


def fee_rate(m):
    if not m.get("feesEnabled"):
        return 0.0, "feesEnabled=false"
    fs = m.get("feeSchedule") or {}
    if isinstance(fs, str):
        try:
            fs = json.loads(fs)
        except json.JSONDecodeError:
            fs = {}
    r = fs.get("rate")
    if isinstance(r, (int, float)):
        return float(r), f"feeSchedule.rate ({m.get('feeType')})"
    return DEFAULT_FEE_RATE, f"défaut {DEFAULT_FEE_RATE} ({m.get('feeType')})"


def _plain(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()


def auto_keywords(m):
    """2 à 4 mots distinctifs : noms propres de la question (ou du nom du candidat du groupe)."""
    q = m.get("question") or ""
    gi = (m.get("groupItemTitle") or "").strip()
    phrases = []
    # suites de mots à majuscule (noms propres), ex. « Gavin Newsom », « Xi Jinping »
    for ph in re.findall(r"(?:[A-Z][\w'.\-]*(?:\s+(?:of|de|la|van|von|der|bin|al)?\s*[A-Z][\w'.\-]*)*)", q):
        words = [w for w in ph.split() if w.lower().strip(".'") not in STOP]
        if not words:
            continue
        ph2 = " ".join(words).strip(" .'?")
        if len(ph2) >= 3 and not ph2.isdigit():
            phrases.append(ph2)
    if gi and not re.search(r"\d", gi) and gi.lower() not in STOP and len(gi) >= 3:
        phrases.insert(0, gi)
    out = []
    for p in phrases:
        if p.lower() not in [o.lower() for o in out] and not any(p.lower() in o.lower() for o in out):
            out.append(p)
    return out[:2]


# Requêtes GDELT relues à la main (clé = début de la question ; valeur = requête GDELT brute).
# Règle : 1 à 3 mots distinctifs (noms propres), variantes d'accents en OU ; les mots-clés automatiques
# (noms propres de la question) servent seulement quand aucune ligne ne correspond.
KW_OVERRIDE = {
    "Will United Russia": '"United Russia"', "Russia Elections: United Russia": '"United Russia"',
    "Will Yabloko": "Yabloko",
    "Will Flávio Bolsonaro": '("Flavio Bolsonaro" OR "Flávio Bolsonaro")',
    "Will Flavio Bolsonaro": '("Flavio Bolsonaro" OR "Flávio Bolsonaro")',
    "Will Luiz Inácio Lula": "Lula Brazil", "Will Lula": "Lula Brazil",
    "Will Renan Santos": '"Renan Santos"', "Will Geraldo Alckmin": "Alckmin",
    "Will Augusto Cury": '"Augusto Cury"', "Will Ronaldo Caiado": "Caiado",
    "Will any presidential candidate win outright in the first round of the Brazil": "Brazil election",
    "Will the U.S. invade Iran": "Iran invasion", "Will the U.S. invade Cuba": "Cuba invasion",
    "Will the Democratic Party control the House": "(midterm OR midterms) House",
    "Will the Republican Party control the House": "(midterm OR midterms) House",
    "Will the Democratic Party control the Senate": "(midterm OR midterms) Senate",
    "Will the Republican Party control the Senate": "(midterm OR midterms) Senate",
    "2026 Balance of Power": "(midterm OR midterms)",
    "Strait of Hormuz traffic": "Hormuz", "Iran-Oman Hormuz": "Oman Hormuz",
    "Iran charges Hormuz fees": "Iran Hormuz",
    "US announces end of Iranian blockade": "Iran blockade",
    "Will China invade Taiwan": "China Taiwan", "Clarity Act": '"Clarity Act"',
    "Will Benjamin Netanyahu": "Netanyahu", "Netanyahu out": "Netanyahu",
    "Will Gadi Eizenkot": "Eizenkot", "Will Avigdor Lieberman": "Lieberman Israel",
    "Will Naftali Bennett": '"Naftali Bennett"',
    "Will Donald Trump win the Nobel": '"Nobel Peace Prize" Trump',
    "Will Yulia Navalnaya": '"Nobel Peace Prize" Navalnaya',
    "Will the International Court of Justice win the Nobel": '"Nobel Peace Prize" "International Court of Justice"',
    "Will Sudan's Emergency Response Rooms": '"Nobel Peace Prize" Sudan',
    "Xi Jinping out": '"Xi Jinping"', "Will Xi Jinping visit US": '"Xi Jinping" visit',
    "Putin out": "Putin", "Will the Iranian regime fall": "Iran regime",
    "Kharg Island": '"Kharg Island"', "Will David Lisnard": "Lisnard", "Will Marine Le Pen": '"Le Pen"',
    "Will Jean-Luc Mélenchon": "(Melenchon OR Mélenchon)",
    "Will Édouard Philippe": '("Edouard Philippe" OR "Édouard Philippe")',
    "Israel x Iran ceasefire": "Israel Iran ceasefire", "Bab el-Mandeb": "Mandeb",
    "Will the Republicans win the Texas Senate": "Paxton", "Will the Democrats win the Texas Senate": "Talarico",
    "Will the Democrats win the Ohio Senate": '"Sherrod Brown"', "Will the Republicans win the Ohio Senate": '"Jon Husted"',
    "Will the Democrats win the Michigan Senate": '"El-Sayed" Michigan',
    "Will the Republicans win the Michigan Senate": '"Mike Rogers" Michigan',
    "Will the Republicans win the Kansas Senate": '"Roger Marshall" Kansas',
    "Will the Democrats win the Kansas Senate": '"Adam Hamilton" Kansas',
    "Will the Democrats win the Maine Senate": '"Troy Jackson" Maine',
    "Will the Republicans win the Maine Senate": '"Susan Collins"',
    "Will the Democrats win the Iowa Senate": '"Josh Turek"', "Will the Republicans win the Iowa Senate": '"Ashley Hinson"',
    "Will the Republicans win the Nebraska Senate": '"Pete Ricketts"',
    "Will the Republicans win the South Carolina Senate": '"Lindsey Graham"',
    "Will the Republicans win the Texas governor": '"Greg Abbott"',
    "Will Mary Peltola": "Peltola", "Will Dan Sullivan": '"Dan Sullivan" Alaska',
    "NATO x Russia": "NATO Russia", "Saudi Oil Pipeline": "Saudi pipeline",
    "Will Aleksandar Vučić": "(Vucic OR Vučić)", "US-Iran Final Nuclear Deal": '"nuclear deal" Iran',
    "Will Crude Oil": '"crude oil"', "Friedrich Merz": "Merz",
    "US x Iran diplomatic meeting": "Iran talks", "Will no qualifying diplomatic US-Iran": "Iran talks",
    "Will the next diplomatic US-Iran meeting": "Iran talks",
    "Iran leadership change": '"supreme leader" Iran', "Will Mojtaba Khamenei": '"Mojtaba Khamenei"',
    "Trump out as President": "Trump", "Will JD Vance": '"JD Vance"', "Will Raphael Warnock": "Warnock",
    "Will Pete Buttigieg": "Buttigieg", "Will Gavin Newsom": "Newsom",
    "Will Alexandria Ocasio-Cortez": '"Ocasio-Cortez"', "Will Nicolás Maduro": "Maduro",
    "Will Delcy Rodríguez": '("Delcy Rodriguez" OR "Delcy Rodríguez")',
    "Trump x Greenland": "Greenland", "Will Trump acquire Greenland": "Greenland",
    "Kanye West performs in Russia": '"Kanye West" Russia',
    "Will Pedro Sánchez": '("Pedro Sanchez" OR "Pedro Sánchez")',
    "Pedro Sánchez out": '("Pedro Sanchez" OR "Pedro Sánchez")',
    "Will Alberto Núñez Feijóo": "(Feijoo OR Feijóo)", "Will Ukraine recapture Crimean": "Crimea Ukraine",
    "Will Puma Shen": '"Puma Shen"', "Will Chiang Wan-an": '"Chiang Wan-an"',
    "Zelenskyy out": "(Zelensky OR Zelenskyy)",
    "Will Russia enter Dopropillia": "(Dobropillia OR Dobropillya OR Dobropolye)",
    "Iran full airspace closure": "Iran airspace", "Israel closes its airspace": "Israel airspace",
    "Will Jon Ossoff": "Ossoff", "Will Steve Hilton": '"Steve Hilton"',
    "Will Iliana Iotova": "Iotova", "Russia x Ukraine ceasefire": "Russia Ukraine ceasefire",
    "Russia-Ukraine peace talks": '"peace talks" Ukraine', "Will Luca Niculescu": "Niculescu",
    "Billionaire one-time wealth tax": '"wealth tax" California',
}
# Marchés écartés : pas une question d'opinion / d'actualité (comptage de messages, religion).
EXCLUDE = ("Will Elon Musk post", "Will Jesus Christ return")


def gdelt_query(kws):
    parts = []
    for k in kws:
        k = _plain(k).replace('"', "")
        parts.append(f'"{k}"' if " " in k else k)
    return " ".join(parts)   # GDELT : espaces = ET logique


def select_markets():
    print("1. Choix des marchés (Gamma)", flush=True)
    cands = {}
    for tag in TAGS:
        for closed in ("false", "true"):
            # fenêtres de date de fin (les grands décalages renvoient parfois HTTP 500)
            windows = [("2026-09-22", "2026-11-01"), ("2026-11-01", "2027-01-01"),
                       ("2027-01-01", "2027-01-02"), ("2027-01-02", "2028-01-01"),
                       ("2028-01-01", "2031-01-01")]
            for a, b in windows:
                off = 0
                while off <= 1500:
                    d = get(f"{GAMMA}/markets", {"tag_id": tag, "closed": closed, "limit": 100,
                                                 "offset": off, "volume_num_min": 100000,
                                                 "end_date_min": a + "T00:00:00Z",
                                                 "end_date_max": b + "T00:00:00Z",
                                                 "start_date_max": "2026-09-15T00:00:00Z"})
                    if not d:
                        break
                    for m in d:
                        m["_tag"] = TAGS[tag]
                        cands.setdefault(m["conditionId"], m)
                    if len(d) < 100:
                        break
                    off += 100
    print(f"  candidats Gamma : {len(cands)}", flush=True)
    rows = []
    for cid, m in cands.items():
        end = iso(m.get("endDate"))
        if not end or end < OBS_START + MIN_END_GAP:
            continue
        try:
            outs = json.loads(m.get("outcomes") or "[]")
        except json.JSONDecodeError:
            continue
        if [o.lower() for o in outs] != ["yes", "no"]:
            continue
        closed_t = iso(m.get("closedTime")) if m.get("closed") else None
        if closed_t and closed_t < OBS_START + timedelta(days=3):
            continue
        ev = (m.get("events") or [{}])[0]
        rows.append({"cid": cid, "question": m["question"], "slug": m.get("slug"),
                     "event": ev.get("slug") or ev.get("id") or cid, "tag": m["_tag"],
                     "end": m["endDate"], "closed": m.get("closed"), "closedTime": m.get("closedTime"),
                     "volume": m.get("volumeNum") or 0, "group": m.get("groupItemTitle"),
                     "fee_rate": fee_rate(m)[0], "fee_src": fee_rate(m)[1],
                     "auto_kw": auto_keywords(m)})
    print(f"  binaires, fin >= 22/09, ouverts pendant la période : {len(rows)}", flush=True)
    # volume RÉEL échangé pendant la période (data-api), puis tri
    for i, r in enumerate(sorted(rows, key=lambda r: -r["volume"])):
        tr = fetch_trades(r["cid"])
        inwin = [t for t in tr if ts(OBS_START) <= t["timestamp"] < ts(OBS_END)]
        r["n_trades_obs"] = len(inwin)
        r["usd_obs"] = round(sum(t["size"] * t["price"] for t in inwin))
        if i % 25 == 0:
            print(f"  échanges {i}/{len(rows)}", flush=True)
    rows = [r for r in rows if r["n_trades_obs"] >= 300 and r["usd_obs"] >= 20000]
    rows.sort(key=lambda r: -r["usd_obs"])
    per_event, keep = defaultdict(int), []
    for r in rows:
        if per_event[r["event"]] >= MAX_PER_EVENT or not r["auto_kw"] or r["question"].startswith(EXCLUDE):
            continue
        per_event[r["event"]] += 1
        keep.append(r)
        if len(keep) >= N_MARKETS_MAX:
            break
    for r in keep:
        ov = [v for k, v in KW_OVERRIDE.items() if r["question"].startswith(k)]
        r["query"] = ov[0] if ov else gdelt_query(r["auto_kw"])
        r["query_source"] = "relue à la main" if ov else "automatique"
    (HERE / "marches.json").write_text(json.dumps(keep, ensure_ascii=False, indent=1))
    print(f"  retenus : {len(keep)} (>= 300 échanges et >= 20 000 $ échangés du 15/09 au 15/10, "
          f"max {MAX_PER_EVENT} par événement)", flush=True)
    return keep


# ----------------------------------------------------------------------------------------------
# 2. Échanges réels
# ----------------------------------------------------------------------------------------------
_trades_mem = {}


def fetch_trades(cid, a=None, b=None):
    """Tous les échanges [a, b) ; découpe la fenêtre en deux si le plafond d'offset (10 000) est atteint."""
    a = a or ts(PRICE_START)
    b = b or ts(PRICE_END)
    key = (cid, a, b)
    if key in _trades_mem:
        return _trades_mem[key]
    out, off, full = [], 0, False
    while True:
        d = get(f"{DATA}/trades", {"market": cid, "limit": 500, "offset": off, "start": a, "end": b,
                                   "takerOnly": "true"}, gap=0.15)
        if not isinstance(d, list):
            full = off > 0
            break
        out.extend(d)
        if len(d) < 500:
            break
        off += 500
        if off > 9500:
            full = True
            break
    if full and b - a > 3600:
        mid = (a + b) // 2
        out = fetch_trades(cid, a, mid) + fetch_trades(cid, mid, b)
    seen, res = set(), []
    for t in out:
        k = (t.get("transactionHash"), t.get("asset"), t.get("price"), t.get("size"), t.get("timestamp"))
        if k in seen or not (a <= t["timestamp"] < b):
            continue
        seen.add(k)
        res.append({"timestamp": int(t["timestamp"]), "price": float(t["price"]), "size": float(t["size"]),
                    "outcome": t.get("outcome"), "outcomeIndex": t.get("outcomeIndex"),
                    "side": t.get("side")})
    res.sort(key=lambda t: t["timestamp"])
    _trades_mem[key] = res
    return res


def yes_ticks(cid):
    """Liste (horodatage, prix YES) ; NO au prix p => YES = 1 - p."""
    out = []
    for t in fetch_trades(cid):
        p = t["price"]
        if t["outcomeIndex"] == 1 or (t["outcome"] or "").lower() == "no":
            p = 1 - p
        if 0 < p < 1:
            out.append((t["timestamp"], p))
    return out


# ----------------------------------------------------------------------------------------------
# 3. Attention médiatique (GDELT)
# ----------------------------------------------------------------------------------------------
GDELT_GAP = 9.0          # secondes entre deux requêtes GDELT (la règle publique est 1 / 5 s)
GDELT_CHUNK_DAYS = 7     # fenêtre par requête (au-delà, GDELT passe à une résolution plus grossière)


def gdelt_chunks():
    out, a = [], ATT_START
    while a < OBS_END:
        b = min(a + timedelta(days=GDELT_CHUNK_DAYS), OBS_END)
        out.append((a, b))
        a = b
    return out


GDELT_OFFLINE = [False]   # l'étape « analyse » ne lit que le cache (le téléchargement est l'étape « gdelt »)


def gdelt_raw(query, a, b):
    params = {"query": query, "mode": "timelinevolraw", "format": "json",
              "startdatetime": a.strftime("%Y%m%d%H%M%S"), "enddatetime": b.strftime("%Y%m%d%H%M%S")}
    if GDELT_OFFLINE[0] and not _cache_path(GDELT + "?" + urllib.parse.urlencode(params)).exists():
        return None
    return get(GDELT, params, gap=GDELT_GAP, tries=40, gdelt=True)


def gdelt_hourly(query):
    """dict heure (horodatage du début d'heure) -> (articles, total suivi par GDELT, résolution)."""
    art, norm, res = defaultdict(int), defaultdict(int), set()
    for a, b in gdelt_chunks():
        d = gdelt_raw(query, a, b)
        if not d or "_erreur" in d:
            return None, (d or {}).get("_erreur", "pas de réponse")
        res.add((d.get("query_details") or {}).get("date_resolution"))
        for serie in d.get("timeline") or []:
            for pt in serie.get("data") or []:
                dt = datetime.strptime(pt["date"], "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
                if not (a <= dt < b):
                    continue
                h = ts(dt) // 3600 * 3600
                art[h] += int(pt.get("value") or 0)
                norm[h] += int(pt.get("norm") or 0)
    return {h: (art[h], norm[h]) for h in set(art) | set(norm)}, ",".join(sorted(str(r) for r in res))


def fetch_attention(markets):
    print("3. Attention GDELT", flush=True)
    cnt = defaultdict(int)
    for m in markets:
        cnt[m["query"]] += 1
    queries = sorted(cnt, key=lambda q: -cnt[q])
    todo = [q for q in queries
            if not all(_cache_path(GDELT + "?" + urllib.parse.urlencode(
                {"query": q, "mode": "timelinevolraw", "format": "json",
                 "startdatetime": a.strftime("%Y%m%d%H%M%S"),
                 "enddatetime": b.strftime("%Y%m%d%H%M%S")})).exists() for a, b in gdelt_chunks())]
    print(f"  {len(queries)} requêtes distinctes, {len(todo)} à télécharger "
          f"(~{len(todo) * len(gdelt_chunks()) * GDELT_GAP / 60:.0f} min)", flush=True)
    for i, q in enumerate(todo):
        gdelt_hourly(q)
        print(f"  {i + 1}/{len(todo)} {q}", flush=True)


# ----------------------------------------------------------------------------------------------
# 3 bis. Attention médiatique à partir des fichiers bruts GDELT GKG (source principale)
# ----------------------------------------------------------------------------------------------
# Pourquoi : l'API DOC de GDELT répond « HTTP 429 » presque tout le temps depuis notre adresse
# (adresse de sortie partagée) : ~1 réponse toutes les 5 min, il aurait fallu ~45 h pour 91 sujets.
# GDELT publie aussi, toutes les 15 min, un fichier public « GKG » (gratuit, prévu pour le
# téléchargement en masse) : une ligne par article de presse en ligne (anglais) avec son titre, son
# adresse, les personnes, organisations et lieux cités. On télécharge ces fichiers une fois, on garde
# une version réduite (titre + adresse + noms) et on compte nous-mêmes les articles qui correspondent
# à chaque requête, heure par heure. Différence avec l'API DOC : on cherche dans le titre, l'adresse et
# les noms extraits par GDELT, pas dans tout le texte -> moins d'articles, mais plus « sur le sujet ».
GKG_URL = "https://data.gdeltproject.org/gdeltv2/{}.gkg.csv.zip"
GKG_DIR = CACHE / "gkg"


def _norm_text(x):
    x = _plain(x).lower()
    return " " + re.sub(r"[^a-z0-9]+", " ", x).strip() + " "


def gkg_slots():
    t, out = ATT_START, []
    while t < OBS_END:
        out.append(t)
        t += timedelta(minutes=15)
    return out


def _gkg_one(t):
    import io
    import zipfile
    import csv as _csv
    name = t.strftime("%Y%m%d%H%M%S")
    path = GKG_DIR / name[:8] / f"{name}.txt.gz"
    if path.exists():
        return "cache"
    for attempt in range(5):
        try:
            req = urllib.request.Request(GKG_URL.format(name), headers={"User-Agent": "polymarket-lab-research"})
            with urllib.request.urlopen(req, timeout=120, context=_ctx) as r:
                raw = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 404:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(gzip.compress(b"#ABSENT\n"))
                return "absent"
            time.sleep(5 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError):
            time.sleep(5 * (attempt + 1))
    else:
        return "échec"
    _csv.field_size_limit(10 ** 9)
    lines = []
    try:
        z = zipfile.ZipFile(io.BytesIO(raw))
        f = io.TextIOWrapper(z.open(z.namelist()[0]), encoding="utf-8", errors="replace")
        for row in _csv.reader(f, delimiter="\t", quoting=_csv.QUOTE_NONE):
            if len(row) < 27:
                continue
            title = re.search(r"<PAGE_TITLE>(.*?)</PAGE_TITLE>", row[26] or "")
            url = row[4] or ""
            slug = urllib.parse.urlparse(url).path
            locs = " ".join(x.split("#")[1] for x in (row[9] or "").split(";") if "#" in x)
            names = " ".join(x.rsplit(",", 1)[0] for x in (row[23] or "").split(";") if x)
            txt = " | ".join([title.group(1) if title else "", slug, row[11] or "", row[13] or "", names, locs])
            lines.append(_norm_text(txt).strip())
    except (zipfile.BadZipFile, KeyError, OSError):
        return "échec"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(("\n".join(lines) + "\n").encode()))
    return "ok"


def fetch_gkg(workers=4):
    from concurrent.futures import ThreadPoolExecutor
    slots = gkg_slots()
    print(f"3 bis. Fichiers GDELT GKG : {len(slots)} tranches de 15 min", flush=True)
    stats = defaultdict(int)
    with ThreadPoolExecutor(workers) as ex:
        for i, res in enumerate(ex.map(_gkg_one, slots)):
            stats[res] += 1
            if i % 200 == 0:
                print(f"  {i}/{len(slots)} {dict(stats)}", flush=True)
    print(f"  fini : {dict(stats)}", flush=True)


def parse_query(q):
    """Requête GDELT -> liste de groupes (ET) ; chaque groupe = alternatives (OU), texte normalisé."""
    groups, i = [], 0
    toks = re.findall(r'\(|\)|"[^"]*"|[^\s()"]+', q)
    cur = None
    for tk in toks:
        if tk == "(":
            cur = []
        elif tk == ")":
            groups.append(cur)
            cur = None
        elif tk.upper() == "OR":
            continue
        else:
            alt = _norm_text(tk.strip('"'))
            if cur is not None:
                cur.append(alt)
            else:
                groups.append([alt])
    return groups


def gkg_counts(queries):
    """dict requête -> {heure: (articles correspondants, total d'articles de l'heure)}."""
    parsed = {q: parse_query(q) for q in queries}
    out = {q: defaultdict(lambda: [0, 0]) for q in queries}
    total = defaultdict(int)
    for t in gkg_slots():
        name = t.strftime("%Y%m%d%H%M%S")
        path = GKG_DIR / name[:8] / f"{name}.txt.gz"
        if not path.exists():
            continue
        lines = gzip.decompress(path.read_bytes()).decode().splitlines()
        if lines and lines[0] == "#ABSENT":
            continue
        h = ts(t) // 3600 * 3600
        total[h] += len(lines)
        for q, groups in parsed.items():
            c = 0
            for ln in lines:
                s_ = " " + ln + " "
                if all(any(a in s_ for a in g) for g in groups):
                    c += 1
            out[q][h][0] += c
    res = {}
    for q in queries:
        res[q] = {h: (out[q][h][0] if h in out[q] else 0, n) for h, n in total.items()}
    return res, total


def gkg_counts_cached(queries):
    """Comptages GKG par requête, mis en cache (cache/gkg_counts.json.gz) ; recalcul des seules requêtes
    nouvelles. Le cache est invalidé si le nombre de fichiers GKG présents change."""
    path = CACHE / "gkg_counts.json.gz"
    n_files = sum(1 for _ in GKG_DIR.glob("*/*.txt.gz")) if GKG_DIR.exists() else 0
    store = {}
    if path.exists():
        store = json.loads(gzip.decompress(path.read_bytes()))
        if store.get("_n_files") != n_files:
            store = {}
    todo = [q for q in queries if q not in store]
    if todo or "_total" not in store:
        print(f"  comptage GKG pour {len(todo)} requêtes ({n_files} fichiers)...", flush=True)
        res, total = gkg_counts(todo)
        for q in todo:
            store[q] = {str(h): v[0] for h, v in res[q].items() if v[0]}
        store["_total"] = {str(h): n for h, n in total.items()}
        store["_n_files"] = n_files
        path.write_bytes(gzip.compress(json.dumps(store).encode()))
    total = {int(h): n for h, n in store["_total"].items()}
    counts = {q: {h: (int(store[q].get(str(h), 0)), n) for h, n in total.items()} for q in queries}
    return counts, total


def doc_crosscheck(queries, counts):
    """Corrélation (par heure) entre nos comptages GKG et l'API DOC, pour les tranches déjà en cache."""
    out = []
    for q in queries:
        for a, b in gdelt_chunks():
            d = gdelt_raw(q, a, b)
            if not d or "_erreur" in d:
                continue
            doc = defaultdict(int)
            for serie in d.get("timeline") or []:
                for pt in serie.get("data") or []:
                    dt = datetime.strptime(pt["date"], "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
                    doc[ts(dt) // 3600 * 3600] += int(pt.get("value") or 0)
            hs = [h for h in counts[q] if ts(a) <= h < ts(b)]
            if len(hs) < 24:
                continue
            x = [counts[q][h][0] for h in hs]
            y = [doc.get(h, 0) for h in hs]
            try:
                r = st.correlation(x, y)
            except st.StatisticsError:
                r = None
            out.append({"requete": q, "debut": a.strftime("%Y-%m-%d"), "heures": len(hs),
                        "articles_gkg": sum(x), "articles_doc": sum(y),
                        "correlation": round(r, 3) if r is not None else None})
    return out


# ----------------------------------------------------------------------------------------------
# 4-6. Signaux, issues, transactions simulées, contrôles
# ----------------------------------------------------------------------------------------------
class Prices:
    def __init__(self, ticks, stop_ts):
        self.t = [x[0] for x in ticks if x[0] < stop_ts]
        self.p = [x[1] for x in ticks if x[0] < stop_ts]

    def before(self, T):
        """Dernier prix échangé STRICTEMENT avant T (et son âge en s), ou (None, None)."""
        import bisect
        i = bisect.bisect_left(self.t, T) - 1
        if i < 0:
            return None, None
        return self.p[i], T - self.t[i]

    def med1h(self, T):
        """Médiane des échanges de [T-1 h, T) ; à défaut, dernier échange avant T."""
        import bisect
        i, j = bisect.bisect_left(self.t, T - 3600), bisect.bisect_left(self.t, T)
        if j - i >= 1:
            return st.median(self.p[i:j]), T - self.t[j - 1]
        return self.before(T)

    def n_between(self, a, b):
        import bisect
        return bisect.bisect_left(self.t, b) - bisect.bisect_left(self.t, a)

    def after(self, a, b):
        import bisect
        i = bisect.bisect_left(self.t, a)
        while i < len(self.t) and self.t[i] < b:
            yield self.t[i], self.p[i]
            i += 1


def fee(rate, p):
    return rate * p * (1 - p)


def simulate(px, t, d, rate, tp=TP, sl=SL, hold_h=MAX_HOLD_H, half=HALF_SPREAD):
    """Achat à t du jeton dans le sens d (+1 = YES, -1 = NO) au dernier prix + half, revente au
    dernier prix - half dès que : +tp (prise de bénéfice), -sl (stop) ou hold_h heures."""
    p0, _ = px.before(t)
    q0 = p0 if d > 0 else 1 - p0
    entry = min(q0 + half, 0.99)
    cost = entry + fee(rate, entry)
    exit_q, reason, t_exit = None, "durée", t + hold_h * 3600
    for tt, p in px.after(t, t + hold_h * 3600):
        q = p if d > 0 else 1 - p
        if q >= q0 + tp:
            exit_q, reason, t_exit = q, "objectif", tt
            break
        if q <= q0 - sl:
            exit_q, reason, t_exit = q, "stop", tt
            break
    if exit_q is None:
        p_end, _ = px.before(t + hold_h * 3600)
        exit_q = p_end if d > 0 else 1 - p_end
        if px.t and px.t[-1] < t + hold_h * 3600 and px.t[-1] < t_exit:
            reason = "durée"
    sell = max(exit_q - half, 0.01)
    proceeds = sell - fee(rate, sell)
    return {"entry": round(entry, 4), "exit": round(sell, 4), "pnl": proceeds - cost,
            "ret": (proceeds - cost) / cost, "reason": reason, "hold_h": (t_exit - t) / 3600,
            "fees": fee(rate, entry) + fee(rate, sell)}


def build_hours(m, att, px, alive, mode="last"):
    """Toutes les heures d'observation valides du marché avec leurs mesures (rien d'après t).
    Une heure sans article correspondant vaut 0 si GDELT a publié des fichiers GKG à cette heure
    (alive), sinon c'est un trou de couverture (heure ignorée).
    mode="last" : prix = dernier échange avant l'heure ; mode="med1h" : médiane des échanges de l'heure
    précédente (moins sensible au va-et-vient entre prix acheteur et prix vendeur)."""
    price = px.before if mode == "last" else px.med1h
    if att is not None:
        att = dict(att)
        for h, nrm in alive.items():
            if h not in att:
                att[h] = (0, nrm)
    end = iso(m["end"])
    rows = []
    t = OBS_START
    while t < OBS_END:
        T = ts(t)
        t += timedelta(hours=1)
        if datetime.fromtimestamp(T, UTC) > end - MIN_END_GAP:
            continue
        p0, age = price(T)
        p6, age6 = price(T - DRIFT_H * 3600)
        if p0 is None or p6 is None or px.n_between(T - 3 * 3600, T) == 0 or age6 > DRIFT_H * 3600:
            continue          # pas d'échange dans les 3 dernières heures (prix non exécutable) ou prix
            #                   « t-6 h » trop ancien (la dérive mesurerait autre chose que 6 h)
        if not (P_MIN <= p0 <= P_MAX):
            continue
        r = {"T": T, "p0": p0, "drift": p0 - p6, "spike": None, "art3": None}
        if att is not None:
            recent = [att.get(T - k * 3600) for k in (1, 2, 3)]
            base = [att.get(T - k * 3600) for k in range(4, 4 + 168)]
            ok_recent = all(x is not None and x[1] > 0 for x in recent)
            cov = [x for x in base if x is not None and x[1] > 0]
            if ok_recent and len(cov) >= MIN_BASE_H:
                a3 = sum(x[0] for x in recent)
                b3 = 3 * sum(x[0] for x in cov) / len(cov)
                r["art3"], r["base3"] = a3, b3
                r["spike"] = a3 / max(b3, 1.0)
        for h in HORIZONS:
            ph, _ = price(T + h * 3600)
            r[f"m{h}"] = ph - p0          # variation du prix YES (le sens est appliqué plus tard)
        rows.append(r)
    return rows


def pick(hours, cond, cooldown_h=COOLDOWN_H):
    out, last = [], -10 ** 12
    for r in hours:
        if cond(r) and r["T"] - last >= cooldown_h * 3600:
            out.append(r)
            last = r["T"]
    return out


def drift_ok(r, lo=DRIFT_MIN, hi=DRIFT_MAX):
    return lo <= abs(r["drift"]) <= hi


def mean(x):
    return sum(x) / len(x) if x else float("nan")


def boot_ci(items, key, n=2000, seed=7):
    """IC 95 % de la moyenne par rééchantillonnage DES SUJETS (requête GDELT) : les signaux d'un même
    sujet (ex. les 4 marchés « blocus iranien ») se ressemblent et ne sont pas indépendants."""
    by = defaultdict(list)
    for it in items:
        by[it["topic"]].append(key(it))
    groups = list(by.values())
    if len(groups) < 3:
        return None
    rnd = random.Random(seed)
    ms = []
    for _ in range(n):
        s, c = 0.0, 0
        for _ in range(len(groups)):
            g = groups[rnd.randrange(len(groups))]
            s += sum(g)
            c += len(g)
        ms.append(s / c)
    ms.sort()
    return [round(ms[int(0.025 * n)], 4), round(ms[int(0.975 * n)], 4)]


def summarize(items):
    if not items:
        return {"n": 0}
    out = {"n": len(items), "marches": len({i["cid"] for i in items}), "sujets": len({i["topic"] for i in items})}
    for h in HORIZONS:
        mv = [i[f"mv{h}"] for i in items]
        out[f"move{h}"] = round(mean(mv), 4)
        out[f"hit{h}"] = round(mean([1.0 if x > 0 else 0.0 for x in mv]), 3)
        out[f"flat{h}"] = round(mean([1.0 if x == 0 else 0.0 for x in mv]), 3)
    out["move24_ic95"] = boot_ci(items, lambda i: i["mv24"])
    out["move72_ic95"] = boot_ci(items, lambda i: i["mv72"])
    out["pnl_ic95"] = boot_ci(items, lambda i: i["pnl"])
    out["pnl"] = round(mean([i["pnl"] for i in items]), 4)
    out["ret"] = round(mean([i["ret"] for i in items]), 4)
    out["ret_med"] = round(st.median([i["ret"] for i in items]), 4)
    out["win"] = round(mean([1.0 if i["pnl"] > 0 else 0.0 for i in items]), 3)
    out["ret_ic95"] = boot_ci(items, lambda i: i["ret"])
    out["fees"] = round(mean([i["fees"] for i in items]), 4)
    out["hold_h"] = round(mean([i["hold_h"] for i in items]), 1)
    out["sorties"] = {k: sum(1 for i in items if i["reason"] == k) for k in ("objectif", "stop", "durée")}
    return out


def run_group(data, cond, sens, cooldown_h=COOLDOWN_H, no_fee=False, **simkw):
    """sens = +1 : suivre la dérive ; -1 : la contrer (fade). no_fee=True : frais mis à 0 (contrôle)."""
    items = []
    for m, hours, px in data:
        for r in pick(hours, cond, cooldown_h):
            d = (1 if r["drift"] > 0 else -1) * sens
            sim = simulate(px, r["T"], d, 0.0 if no_fee else m["fee_rate"], **simkw)
            it = {"cid": m["cid"], "topic": m["query"], "q": m["question"], "T": r["T"], "p0": r["p0"], "drift": r["drift"],
                  "spike": r["spike"], "art3": r["art3"], "d": d}
            for h in HORIZONS:
                it[f"mv{h}"] = d * r[f"m{h}"]
            it.update(sim)
            items.append(it)
    return items


def halves(items):
    mid = ts(OBS_START + (OBS_END - OBS_START) / 2)
    return {"1re moitié (15/09-29/09)": summarize([i for i in items if i["T"] < mid]),
            "2e moitié (30/09-14/10)": summarize([i for i in items if i["T"] >= mid])}


def analyse(markets):
    print("4-6. Analyse", flush=True)
    data, att_info, raw = [], [], []
    queries = sorted({m["query"] for m in markets})
    counts, total = gkg_counts_cached(queries)
    atts = {q: (counts[q], "GKG 15 min -> heure") for q in queries}
    alive = {h: n for h, n in total.items() if n > 0}
    R_cov = {"heures_gkg_presentes": len(alive),
             "heures_attendues": int((OBS_END - ATT_START).total_seconds() // 3600),
             "articles_par_heure_median": st.median(alive.values()) if alive else None,
             "recoupement_api_doc": doc_crosscheck(queries, counts)}
    for m in markets:
        stop = ts(PRICE_END)
        if m.get("closed") and m.get("closedTime"):
            ct = iso(m["closedTime"].replace(" ", "T").replace("+00", "+00:00")
                     if "+00" in m["closedTime"] and "+00:00" not in m["closedTime"] else m["closedTime"])
            if ct:
                stop = min(stop, ts(ct))
        px = Prices(yes_ticks(m["cid"]), stop)
        att, res = atts[m["query"]]
        if att is not None:
            tot = sum(v[0] for v in att.values())
            cov = sum(1 for v in att.values() if v[1] > 0)
        else:
            tot, cov = 0, 0
        att_info.append({"cid": m["cid"], "query": m["query"], "articles": tot, "heures_couvertes": cov,
                         "resolution": res})
        hours = build_hours(m, att, px, alive)
        data.append((m, hours, px))
        raw.append((m, att, px))
    n_hours = sum(len(h) for _, h, _ in data)
    with_att = [(m, h, p) for m, h, p in data if any(r["spike"] is not None for r in h)]
    print(f"  {len(data)} marchés, {n_hours} heures valides, {len(with_att)} marchés avec attention",
          flush=True)

    def spike_cond(thr=SPIKE_MIN, lo=DRIFT_MIN, hi=DRIFT_MAX, amin=MIN_ART3):
        return lambda r: (r["spike"] is not None and r["spike"] >= thr and r["art3"] >= amin
                          and drift_ok(r, lo, hi))

    def calm_cond(lo=DRIFT_MIN, hi=DRIFT_MAX):
        return lambda r: r["spike"] is not None and r["spike"] < NOSPIKE_MAX and drift_ok(r, lo, hi)

    R = {"params": {"SPIKE_MIN": SPIKE_MIN, "MIN_ART3": MIN_ART3, "DRIFT": [DRIFT_MIN, DRIFT_MAX],
                    "DRIFT_H": DRIFT_H, "COOLDOWN_H": COOLDOWN_H, "NOSPIKE_MAX": NOSPIKE_MAX, "MIN_BASE_H": MIN_BASE_H,
                    "P": [P_MIN, P_MAX], "HALF_SPREAD": HALF_SPREAD, "TP": TP, "SL": SL,
                    "MAX_HOLD_H": MAX_HOLD_H},
         "n_marches": len(data), "n_marches_attention": len(with_att), "n_heures": n_hours,
         "frais": defaultdict(int), "couverture_gdelt": R_cov}
    for m, _, _ in data:
        R["frais"][f"{m['fee_rate']} ({m['fee_src']})"] += 1
    groups = {
        "A vague + suivre": (spike_cond(), +1),
        "B sans vague (momentum seul) + suivre": (calm_cond(), +1),
        "C vague + contrer (fade)": (spike_cond(), -1),
        "D sans vague + contrer": (calm_cond(), -1),
        "E toute dérive (attention ignorée) + suivre": (lambda r: drift_ok(r), +1),
    }
    all_items = {}
    R["groupes"] = {}
    for name, (cond, sens) in groups.items():
        src = with_att if not name.startswith("E") else data
        items = run_group(src, cond, sens)
        all_items[name] = items
        R["groupes"][name] = summarize(items)
        R["groupes"][name]["moities"] = halves(items)
        g = R["groupes"][name]
        print(f"  {name}: n={g['n']} move6/24/72={g.get('move6')}/{g.get('move24')}/{g.get('move72')} "
              f"net={g.get('ret')} win={g.get('win')}", flush=True)

    # L'attention annonce-t-elle de l'AGITATION (mouvement absolu), quel que soit le sens ?
    agit = {}
    for lab, cond in (("pic >= 2", lambda r: r["spike"] is not None and r["spike"] >= SPIKE_MIN
                       and r["art3"] >= MIN_ART3),
                      ("calme < 1,2", lambda r: r["spike"] is not None and r["spike"] < NOSPIKE_MAX)):
        sel = [r for _, h, _ in with_att for r in h if cond(r)]
        agit[lab] = {"heures": len(sel), **{f"absmove{h}": round(mean([abs(r[f"m{h}"]) for r in sel]), 4)
                                            for h in HORIZONS},
                     "absdrift6_avant": round(mean([abs(r["drift"]) for r in sel]), 4)}
    R["agitation"] = agit

    # Grille de paramètres (sens « suivre », avec attention)
    grid = []
    for thr in (1.5, 2.0, 3.0, 5.0):
        for lo, hi in ((0.02, 0.08), (0.02, 0.05), (0.04, 0.08), (0.02, 0.15)):
            for tp, sl in ((0.05, 0.05), (0.03, 0.03), (0.08, 0.05), (0.10, 0.10)):
                for hold in (24, 72, 120):
                    for sens in (+1, -1):
                        items = run_group(with_att, spike_cond(thr, lo, hi), sens, tp=tp, sl=sl, hold_h=hold)
                        if not items:
                            continue
                        mid = ts(OBS_START + (OBS_END - OBS_START) / 2)
                        h1 = [i["ret"] for i in items if i["T"] < mid]
                        h2 = [i["ret"] for i in items if i["T"] >= mid]
                        grid.append({"spike": thr, "drift": [lo, hi], "tp": tp, "sl": sl, "hold": hold,
                                     "sens": "suivre" if sens > 0 else "contrer", "n": len(items),
                                     "marches": len({i["cid"] for i in items}),
                                     "ret": round(mean([i["ret"] for i in items]), 4),
                                     "win": round(mean([1.0 if i["pnl"] > 0 else 0 for i in items]), 3),
                                     "ret_h1": round(mean(h1), 4) if h1 else None,
                                     "ret_h2": round(mean(h2), 4) if h2 else None})
    grid.sort(key=lambda g: -g["ret"])
    R["grille_meilleurs"] = [g for g in grid if g["n"] >= 20][:15]
    R["grille_n"] = len(grid)
    R["grille_part_positive"] = round(mean([1.0 if g["ret"] > 0 else 0.0 for g in grid if g["n"] >= 20]), 3)
    # Variante pessimiste sur l'écart (demi-écart 0,02) pour le groupe A
    R["A_demi_ecart_0.02"] = summarize(run_group(with_att, spike_cond(), +1, half=0.02))
    R["A_sans_frais_ni_ecart"] = summarize(run_group(with_att, spike_cond(), +1, half=0.0, no_fee=True))
    R["C_sans_frais_ni_ecart"] = summarize(run_group(with_att, spike_cond(), -1, half=0.0, no_fee=True))
    # Robustesse : prix = médiane des échanges de l'heure précédente (au lieu du dernier échange)
    data_med = [(m, build_hours(m, att, px, alive, mode="med1h"), px) for m, att, px in raw]
    wa_med = [(m, h, p) for m, h, p in data_med if any(r["spike"] is not None for r in h)]
    R["prix_median_1h"] = {
        "A vague + suivre": summarize(run_group(wa_med, spike_cond(), +1)),
        "B sans vague + suivre": summarize(run_group(wa_med, calm_cond(), +1)),
        "C vague + contrer": summarize(run_group(wa_med, spike_cond(), -1)),
        "E toute dérive + suivre": summarize(run_group(data_med, lambda r: drift_ok(r), +1)),
    }
    for k, g in R["prix_median_1h"].items():
        print(f"  [médiane 1h] {k}: n={g['n']} move24={g.get('move24')} net={g.get('ret')}", flush=True)
    R["attention_par_marche"] = att_info
    (HERE / "resultats.json").write_text(json.dumps(R, ensure_ascii=False, indent=1, default=str))
    with open(HERE / "signaux.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["groupe", "question", "t_utc", "p_yes", "derive6h", "pic", "articles3h", "sens",
                    "mv6", "mv24", "mv72", "achat", "vente", "frais", "gain_net_par_part", "rendement",
                    "sortie", "duree_h"])
        for name in ("A vague + suivre", "C vague + contrer (fade)"):
            for i in all_items[name]:
                w.writerow([name[0], i["q"], datetime.fromtimestamp(i["T"], UTC).strftime("%Y-%m-%d %H:%M"),
                            round(i["p0"], 3), round(i["drift"], 3), round(i["spike"], 2), i["art3"],
                            "YES" if i["d"] > 0 else "NO", round(i["mv6"], 3), round(i["mv24"], 3),
                            round(i["mv72"], 3), i["entry"], i["exit"], round(i["fees"], 4),
                            round(i["pnl"], 4), round(i["ret"], 4), i["reason"], round(i["hold_h"], 1)])
    return R


if __name__ == "__main__":
    step = sys.argv[1] if len(sys.argv) > 1 else "all"
    if step in ("select", "all"):
        mk = select_markets()
    else:
        mk = json.loads((HERE / "marches.json").read_text())
    if step in ("gkg", "all"):
        fetch_gkg()
    if step == "gdelt":          # facultatif : API DOC (très limitée en débit), sert de recoupement
        fetch_attention(mk)
    if step in ("analyse", "all"):
        GDELT_OFFLINE[0] = True
        analyse(mk)
