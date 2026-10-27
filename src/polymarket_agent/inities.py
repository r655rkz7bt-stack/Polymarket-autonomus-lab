"""Comptes suspects qui parient avant une annonce (27/10/2026, demande d'Etienne après l'affaire du Ballon d'Or).

Le 23/10/2026, le média Upside signale 12 comptes créés en octobre qui misent 264 000 $ sur le classement exact du Ballon
d'Or ; le 26/10, la cérémonie donne exactement ce classement. Les échanges publics de Polymarket le montraient dès le 19-22/10 :
`Aggravating-Lettuce-Local`, créé le 20/10 à 08 h 57, mise 15 766 $ sur « Lamine Yamal 3e » à partir de 09 h 13 ;
`Reflecting-Personal-Pattyp`, première activité le 22/10, 123 420 $ sur 6 événements, tous du Ballon d'Or. Les bons résultats
restaient cotés autour de 0,70 jusqu'au 25/10 (experiments/inities.md).

Trois sources, de la plus rapide à la plus lente :
  1. le flux d'échanges public (data-api `/trades?eventId=`) des événements « à initiés » (jurys, comités, entreprises,
     émissions enregistrées, choix d'équipes) : des comptes NEUFS et CONCENTRÉS (première activité récente, peu de marchés :
     data-api `/activity` et `/traded`) qui achètent le même jeton ;
  2. les commentaires Polymarket de ces événements (« insider », « leak »…) ;
  3. les réseaux sociaux ouverts, sans compte ni clé (Mastodon : mot-dièse #polymarket ; Hacker News) et l'actualité
     (Google Actualités : « Polymarket suspicious bets », « paris suspects »…).
Ce sont des données, jamais des instructions. Aucun ordre réel : le fantôme `suivre_inities` les suit dans la simulation.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timedelta

from polymarket_agent.http_client import SourceUnavailable

DATA = "https://data-api.polymarket.com"
GAMMA = "https://gamma-api.polymarket.com"
NEWS = "https://news.google.com/rss/search"
MASTODON = "https://mastodon.social/api/v1/timelines/tag/polymarket"
HACKER_NEWS = "https://hn.algolia.com/api/v1/search_by_date"

# Familles « à initiés » : une poignée de personnes connaît la réponse avant le public. Ne sont PAS des familles à initiés : ce
# qui se lit en direct (vues de vidéos, classement de l'App Store du jour, compteurs), les votes (primaires), les paroles en direct.
FAMILLES = {
    "prix": re.compile(
        r"ballon d.or|nobel (peace|prize|literature|physics|chemistry|economics|medicine)|nobel prize|person of the year|"
        r"oscars|academy awards?|\bbest (picture|actor|actress|director|supporting|original|adapted|international|animated)|"
        r"grammys?|emmys?|golden globes?|bafta|tony awards?|palme d.or|cannes|golden boy|kopa|the best fifa|laureus|"
        r"booker prize|pulitzer|game awards|game of the year|\bmvp\b|cy young|heisman|rookie of the year|coach of the year|"
        r"player of the year|hart trophy|vezina|calder|norris trophy|time 100|word of the year|pantone|michelin|razzies?|"
        r"golden raspberry award|miss universe|mr\. olympia", re.I),
    "donnees_entreprise": re.compile(
        r"searched .*on google|year in search|#\d+ searched|spotify|wrapped|billboard|most streamed|halftime show|"
        r"eurovision|apple event|iphone \d+|release date", re.I),
    "emission": re.compile(
        r"survivor|bachelor(ette)?\b|love island|big brother|the traitors|masked singer|dancing with the stars|the voice|"
        r"american idol|top chef|drag race|beast games", re.I),
    "decision": re.compile(
        r"\bdraft\b.*(pick|overall|drafted|first)|first (overall )?pick|no\. ?1 pick|\bnew pope\b|\bnext pope\b|\bpope\b.*(elected|name)|"
        r"conclave|running mate|fed chair|who will trump nominate|nominate[sd]? .*(supreme court|fed|secretary|ambassador)|"
        r"\bpardon|host city|olympics host|world cup host", re.I),
}
EXCLURE = re.compile(r"what will .* say|\bsay\b.*during|announcers|# of views|views of|app store|primary winner|"
                     r"\bvs\.? |tweets?\b|posts?\b|mention", re.I)
SOUPCON = re.compile(r"insider|inside (info|information|trading)|leak(ed|s)?\b|suspicious|suspect|délit d.initi|initiés?\b|"
                     r"fuit(e|é)|paris suspects|fresh wallets?|new wallets?|new accounts?|rigged|someone knows", re.I)
NOM_PAR_DEFAUT = re.compile(r"^0x[0-9a-fA-F]{40}-(\d{12,14})$")  # profil jamais renommé : « adresse-création en ms »


def famille(titre: str) -> str | None:
    if EXCLURE.search(titre or ""):
        return None
    return next((nom for nom, motif in FAMILLES.items() if motif.search(titre or "")), None)


def creation_par_nom(nom: str) -> int | None:
    m = NOM_PAR_DEFAUT.match(nom or "")
    return int(m.group(1)) // 1000 if m else None


def suspect(profil: dict | None, quand: int, age_max_jours: float, marches_max: int, nom: str = "") -> bool:
    """Compte NEUF (première activité au plus `age_max_jours` avant cet achat) et CONCENTRÉ (au plus `marches_max` marchés)."""
    profil = profil or {}
    premiere = profil.get("premiere") or creation_par_nom(nom)
    marches = profil.get("marches")
    if premiere is None or marches is None:
        return False
    return (quand - int(premiere)) <= age_max_jours * 86400 and int(marches) <= marches_max


def grappes(echanges: list[dict], profils: dict, now: datetime, *, fenetre_heures: float = 72, age_max_jours: float = 7,
            marches_max: int = 15, mise_min: float = 100.0) -> list[dict]:
    """Par jeton : les comptes suspects qui l'ont acheté (≥ `mise_min` $ chacun) dans les `fenetre_heures` dernières heures.
    `echanges` : lignes data-api `/trades` (preneurs) d'un événement ; `profils` : {adresse: {"premiere", "marches"}}.
    Rend [{"jeton", "condition", "comptes", "dollars", "prix_moyen", "premier", "dernier", "adresses"}], plus gros d'abord."""
    debut = int((now - timedelta(hours=fenetre_heures)).timestamp())
    par = defaultdict(lambda: defaultdict(lambda: {"usd": 0.0, "parts": 0.0, "premier": None, "dernier": None, "nom": ""}))
    cond = {}
    for t in echanges:
        try:
            quand, prix, parts = int(t["timestamp"]), float(t["price"]), float(t["size"])
        except (KeyError, TypeError, ValueError):
            continue
        if str(t.get("side")) != "BUY" or quand < debut or prix <= 0:
            continue
        jeton, w = str(t.get("asset")), str(t.get("proxyWallet"))
        cond[jeton] = str(t.get("conditionId") or "")
        a = par[jeton][w]
        a["usd"] += prix * parts
        a["parts"] += parts
        a["premier"] = quand if a["premier"] is None else min(a["premier"], quand)
        a["dernier"] = quand if a["dernier"] is None else max(a["dernier"], quand)
        a["nom"] = a["nom"] or str(t.get("name") or "")
    out = []
    for jeton, comptes in par.items():
        sus = {w: a for w, a in comptes.items()
               if a["usd"] >= mise_min and suspect(profils.get(w), a["premier"], age_max_jours, marches_max, a["nom"])}
        if not sus:
            continue
        usd, parts = sum(a["usd"] for a in sus.values()), sum(a["parts"] for a in sus.values())
        out.append({"jeton": jeton, "condition": cond.get(jeton, ""), "comptes": len(sus), "dollars": round(usd, 2),
                    "prix_moyen": round(usd / parts, 4) if parts else None,
                    "premier": min(a["premier"] for a in sus.values()), "dernier": max(a["dernier"] for a in sus.values()),
                    "adresses": sorted(sus, key=lambda w: -sus[w]["usd"])[:5]})
    out.sort(key=lambda g: -g["dollars"])
    return out


def gros_acheteurs(echanges: list[dict], now: datetime, fenetre_heures: float, seuil: float) -> list[str]:
    """Adresses qui ont acheté au moins `seuil` $ d'un même jeton dans la fenêtre (les seules qu'on profile)."""
    debut = int((now - timedelta(hours=fenetre_heures)).timestamp())
    usd = defaultdict(float)
    for t in echanges:
        try:
            if str(t.get("side")) == "BUY" and int(t["timestamp"]) >= debut:
                usd[(str(t.get("proxyWallet")), str(t.get("asset")))] += float(t["price"]) * float(t["size"])
        except (KeyError, TypeError, ValueError):
            continue
    plus_gros: dict[str, float] = {}
    for (w, _), v in usd.items():
        if v >= seuil:
            plus_gros[w] = max(v, plus_gros.get(w, 0.0))
    return sorted(plus_gros, key=lambda w: -plus_gros[w])


# ------------------------------------------------------------------ sources


def _profil(http, db, adresse: str, now: datetime, max_age_heures: float = 12) -> tuple[dict | None, bool]:
    """(profil, interrogé ?) : première activité et nombre de marchés, gardés en base (`inities:profil:<adresse>`)."""
    cle = f"inities:profil:{adresse}"
    try:
        connu = json.loads(db.get_value(cle) or "null") if db is not None else None
    except (ValueError, TypeError):
        connu = None
    if connu and connu.get("vu_le"):
        try:
            if now - datetime.fromisoformat(connu["vu_le"]) < timedelta(hours=max_age_heures):
                return connu, False
        except ValueError:
            pass
    a = http.get_json(f"{DATA}/activity", params={"user": adresse, "limit": 1, "sortBy": "TIMESTAMP", "sortDirection": "ASC"})
    r = http.get_json(f"{DATA}/traded", params={"user": adresse})
    profil = {"premiere": int(a[0]["timestamp"]) if isinstance(a, list) and a and a[0].get("timestamp") else None,
              "marches": int(r["traded"]) if isinstance(r, dict) and r.get("traded") is not None else None,
              "vu_le": now.isoformat(timespec="seconds")}
    if db is not None:
        db.set_value(cle, json.dumps(profil))
    return profil, True


def evenements_ouverts(http, now: datetime, etiquettes: list, horizon_jours: float, maximum: int) -> list[dict]:
    """Événements ouverts des familles à initiés (Gamma `/events` par étiquette), qui se règlent dans `horizon_jours`."""
    vus: dict[str, dict] = {}
    for tag in etiquettes:
        lot = http.get_json(f"{GAMMA}/events", params={
            "tag_id": str(tag), "active": "true", "closed": "false", "limit": 100, "order": "volume24hr", "ascending": "false",
            "end_date_min": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date_max": (now + timedelta(days=horizon_jours)).strftime("%Y-%m-%dT%H:%M:%SZ")})
        for e in lot if isinstance(lot, list) else []:
            if isinstance(e, dict) and e.get("id") and famille(str(e.get("title") or "")):
                vus.setdefault(str(e["id"]), e)
    out = sorted(vus.values(), key=lambda e: -float(e.get("volume24hr") or 0))
    return out[:maximum]


def fetch_inities(http, db, now: datetime, cfg: dict) -> list[dict]:
    """Source « inities » : pour chaque événement à initiés ouvert, ses derniers échanges, le profil des gros acheteurs et les
    grappes de comptes suspects ; aussi les commentaires Polymarket qui parlent d'initiés ou de fuite."""
    fenetre = float(cfg.get("fenetre_heures", 72))
    regle = {"fenetre_heures": fenetre, "age_max_jours": float(cfg.get("age_max_jours", 7)),
             "marches_max": int(cfg.get("marches_max", 15)), "mise_min": float(cfg.get("mise_min", 100))}
    budget = int(cfg.get("max_profils", 60))
    rows = []
    evenements = evenements_ouverts(http, now, list(cfg.get("etiquettes") or [18, 100339, 100, 53]),
                                    float(cfg.get("horizon_jours", 45)), int(cfg.get("max_evenements", 30)))
    for e in evenements:
        echanges = []
        for page in range(int(cfg.get("pages", 2))):
            lot = http.get_json(f"{DATA}/trades", params={"eventId": e["id"], "limit": 1000, "offset": page * 1000})
            if not isinstance(lot, list) or not lot:
                break
            echanges += lot
            if len(lot) < 1000:
                break
        profils = {}
        for w in gros_acheteurs(echanges, now, fenetre, float(cfg.get("seuil_profil", 300))):
            try:
                connu, interroge = _profil(http, db, w, now) if budget > 0 else (None, False)
            except SourceUnavailable:
                continue
            budget -= int(interroge)
            if connu:
                profils[w] = connu
        commentaires = []
        if cfg.get("commentaires", True):
            try:
                lot = http.get_json(f"{GAMMA}/comments", params={"parent_entity_type": "Event", "parent_entity_id": e["id"],
                                                                "limit": 40, "order": "createdAt", "ascending": "false"})
                recent = (now - timedelta(days=7)).isoformat()
                commentaires = [str(c.get("body") or "")[:200] for c in lot
                                if isinstance(c, dict) and SOUPCON.search(str(c.get("body") or ""))
                                and str(c.get("createdAt") or "9999") >= recent[:19]]
            except SourceUnavailable:
                commentaires = []
        for g in grappes(echanges, profils, now, **regle):
            rows.append(dict(g, evenement=str(e["id"]), titre=str(e.get("title") or ""), commentaires=commentaires[:3]))
    return rows


def fetch_soupcons(session, now: datetime, cfg: dict) -> list[dict]:
    """Articles et publications des 7 derniers jours qui parlent de paris suspects sur Polymarket : Google Actualités (flux RSS
    public, sans clé ; même usage que sources/google_news.py : quelques recherches par heure) et, sauf `reseaux: false`,
    Mastodon et Hacker News (`_reseaux`). Une source injoignable est sautée ; toutes injoignables : SourceUnavailable."""
    from urllib.parse import quote_plus

    import requests

    from polymarket_agent.sources.google_news import parse_google_news
    if session is None:
        session = requests.Session()
        session.headers.update({"User-Agent": "polymarket-autonomous-lab"})
    out, echecs, requetes = [], 0, cfg.get("requetes") or ["Polymarket insider", "Polymarket suspicious bets",
                                                            "Polymarket paris suspects", "Polymarket délit d'initié", "Polymarket leak"]
    for q in requetes:
        url = f"{NEWS}?q={quote_plus(q + ' when:7d')}&hl=en-US&gl=US&ceid=US:en"
        try:
            resp = session.get(url, timeout=10)
        except requests.RequestException:
            echecs += 1
            continue
        if resp.status_code != 200:
            echecs += 1
            continue
        for it in parse_google_news(resp.content)[: int(cfg.get("par_requete", 20))]:
            if it["title"] and SOUPCON.search(it["title"]):
                out.append({"titre": it["title"][:300], "lien": it["link"], "publie": it["published"], "media": it["publisher"]})
    essais = len(requetes)
    if cfg.get("reseaux", True):
        lignes, n, rates = _reseaux(session, now)
        out, essais, echecs = out + lignes, essais + n, echecs + rates
    if essais and echecs == essais:
        raise SourceUnavailable(f"Google Actualités et réseaux injoignables ({echecs} appels)")
    return out


def _texte(html_text: str) -> str:
    import html
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html.unescape(html_text or ""))).strip()


def _reseaux(session, now: datetime) -> tuple[list[dict], int, int]:
    """Réseaux sociaux ouverts, lus sans compte ni clé : publications publiques du mot-dièse #polymarket (Mastodon) et
    histoires ou commentaires de Hacker News (API Algolia) des 7 derniers jours qui parlent d'initiés. X est payant (interdit
    n° 2) ; Bluesky et Reddit refusent les lectures sans compte (403, 27/10/2026). Rend (lignes, appels, échecs)."""
    from urllib.parse import urlencode

    import requests
    debut = now - timedelta(days=7)
    appels = (("Mastodon", f"{MASTODON}?limit=40"),
              ("Hacker News", f"{HACKER_NEWS}?" + urlencode({"query": "polymarket", "tags": "(story,comment)", "hitsPerPage": 50,
                                                              "numericFilters": f"created_at_i>{int(debut.timestamp())}"})))
    out, echecs = [], 0
    for media, url in appels:
        try:
            resp = session.get(url, timeout=10)
            data = json.loads(resp.content) if resp.status_code == 200 else None
        except (requests.RequestException, ValueError, TypeError):
            data = None
        if media == "Mastodon" and isinstance(data, list):
            posts = [(str(p.get("created_at") or ""), _texte(p.get("content")), str(p.get("url") or "")) for p in data
                     if isinstance(p, dict)]
        elif media == "Hacker News" and isinstance(data, dict) and isinstance(data.get("hits"), list):
            posts = [(str(h.get("created_at") or ""),
                      " — ".join(x for x in (h.get("title") or h.get("story_title") or "",
                                             _texte(h.get("comment_text") or h.get("story_text"))) if x),
                      f"https://news.ycombinator.com/item?id={h.get('objectID')}") for h in data["hits"] if isinstance(h, dict)]
        else:
            echecs += 1
            continue
        for quand, texte, lien in posts:
            if quand[:19] >= debut.isoformat()[:19] and SOUPCON.search(texte):
                out.append({"titre": texte[:300], "lien": lien, "publie": quand, "media": media})
    return out, len(appels), echecs


# ------------------------------------------------------------------ rattachement


VIDES = {"will", "the", "who", "win", "winner", "wins", "2025", "2026", "2027", "what", "which", "polymarket", "kalshi", "bets",
         "bet", "betting", "suspicious", "suspect", "suspects", "insider", "insiders", "trading", "leak", "leaked", "paris", "sur",
         "les", "des", "une", "and", "for", "with", "this", "that", "from", "after", "before", "over", "odds", "market", "markets"}


def _mots(texte: str) -> set[str]:
    """Mots porteurs de sens, apostrophes typographiques ramenées à « ' » (« Ballon d’Or » = « Ballon d'Or »)."""
    texte = (texte or "").lower().replace("\u2019", "'").replace("`", "'")
    return {w for w in re.findall(r"[a-zà-ÿ0-9']+", texte) if len(w) > 2 and w not in VIDES}


def _meme_sujet(article: str, evenement: str) -> bool:
    """Deux mots porteurs de sens en commun au moins, et pas deux années différentes (27/10/2026 : l'affaire du Ballon d'Or
    2026, terminée, ne doit pas rendre suspect le marché du Ballon d'Or 2027)."""
    ya, ye = set(re.findall(r"\b20\d\d\b", article or "")), set(re.findall(r"\b20\d\d\b", evenement or ""))
    if ya and ye and not ya & ye:
        return False
    return len(_mots(article) & _mots(evenement)) >= 2


def attach_inities(markets, db, now: datetime, max_age_heures: float = 6) -> int:
    """Rattache à chaque marché scanné la grappe suspecte qui porte sur l'un de ses jetons (référence `inities`), et les
    articles qui parlent de paris suspects sur son événement (deux mots porteurs de sens en commun au moins)."""
    if db is None:
        return 0
    from polymarket_agent.references import _load
    vu, rows = _load(db, "ref:inities")
    if vu is None or not rows or now - vu > timedelta(hours=max_age_heures):
        return 0
    _, articles = _load(db, "ref:soupcons")
    par_jeton = {str(r["jeton"]): r for r in rows if r.get("jeton")}
    n = 0
    for m in markets:
        for issue, jeton in enumerate(m.token_ids):
            r = par_jeton.get(str(jeton))
            if r is None:
                continue
            titre = r.get("titre") or m.event_title or ""
            presse = [a["titre"] for a in articles or [] if _meme_sujet(a.get("titre", ""), titre)]
            m.references = dict(m.references or {}, inities=dict(r, issue=issue, presse=presse[:3]))
            n += 1
            break
    return n

