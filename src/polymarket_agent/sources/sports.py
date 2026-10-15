"""Sources : scores et calendriers OFFICIELS des ligues (chantier n°0, sources de résolution).

Beaucoup de marchés Polymarket sont tranchés d'après le site officiel d'une ligue (inventaire du
15/10/2026 : uefa.com, nfl.com, mlb.com, nhl.com…). Lire la ligue elle-même, c'est regarder le
score au même endroit que l'arbitre. Chaque match devient une observation (« Rays 2 - 3
Guardians, terminé ») rattachée aux marchés qui citent les équipes.

- MLB : https://statsapi.mlb.com/api/v1/schedule?sportId=1&hydrate=linescore (API publique de la
  ligue, sans clé) → {"dates": [{"games": [{"gamePk", "gameDate", "status": {"detailedState",
  "abstractGameState"}, "teams": {"away"|"home": {"team": {"name"}, "score"}}}]}]}.
  Vérifié par un appel réel le 15/10/2026.
- NHL : https://api-web.nhle.com/v1/score/now (API publique de la ligue, sans clé, redirige vers
  la date du jour) → {"games": [{"id", "startTimeUTC", "gameState" (FUT, PRE, LIVE, CRIT, FINAL,
  OFF), "awayTeam"|"homeTeam": {"name": {"default"}, "abbrev", "score"}}]}. Vérifié le 15/10/2026.
- Football (Ligue des champions, Premier League…) : https://api.football-data.org/v4/matches,
  CLÉ GRATUITE requise (variable FOOTBALL_DATA_KEY, en-tête X-Auth-Token ; 10 appels/min) →
  {"matches": [{"id", "utcDate", "status", "competition": {"name"}, "homeTeam"|"awayTeam":
  {"name"}, "score": {"fullTime": {"home", "away"}}}]}. Format d'après la documentation
  officielle ; à revérifier au premier cycle avec la clé. UEFA n'a pas d'API publique.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.observations import Observation
from polymarket_agent.sources._util import parse_date

FINISHED = "terminé"
LIVE = "en cours"
UPCOMING = "à venir"


def game_observation(source: str, game_id: str, start: datetime | None, now: datetime, url: str,
                     domain: str, league: str, home: str, away: str, home_score, away_score,
                     state: str, detail: str = "") -> Observation:
    """Une observation par match ET par état du score (un score qui change est une nouvelle donnée)."""
    if home_score is None or away_score is None:
        score, title = "", f"{league} : {away} contre {home} ({state})"
    else:
        score = f"{away_score}-{home_score}"
        title = f"{league} : {away} {away_score} - {home_score} {home} ({state})"
    published = now if state == LIVE else (start or now)
    return Observation(
        source=source, external_id=f"{source}-{game_id}-{state}-{score}", published_at=min(published, now),
        collected_at=now, url=url, title=title, text=detail, domain=domain,
        data={"ligue": league, "domicile": home, "exterieur": away, "score_domicile": home_score,
              "score_exterieur": away_score, "etat": state, "debut": start.isoformat() if start else None},
    ).finalize()


class MlbSource:
    name = "mlb_stats"
    URL = "https://statsapi.mlb.com/api/v1/schedule"

    def __init__(self, http: HttpClient):
        self.http = http

    def fetch(self, now: datetime) -> list[Observation]:
        raw = self.http.get_json(self.URL, params={"sportId": 1, "hydrate": "linescore",
                                                   "startDate": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
                                                   "endDate": (now + timedelta(days=1)).strftime("%Y-%m-%d")})
        out = []
        for day in (raw or {}).get("dates") or []:
            for g in day.get("games") or []:
                status = g.get("status") or {}
                abstract = status.get("abstractGameState")
                state = {"Final": FINISHED, "Live": LIVE}.get(abstract, UPCOMING)
                teams = g.get("teams") or {}
                home, away = teams.get("home") or {}, teams.get("away") or {}
                inning = (g.get("linescore") or {}).get("currentInningOrdinal")
                out.append(game_observation(
                    self.name, str(g.get("gamePk")), parse_date(g.get("gameDate")), now,
                    f"https://www.mlb.com/gameday/{g.get('gamePk')}", "mlb.com", "MLB",
                    (home.get("team") or {}).get("name", "?"), (away.get("team") or {}).get("name", "?"),
                    home.get("score") if state != UPCOMING else None,
                    away.get("score") if state != UPCOMING else None, state,
                    f"{status.get('detailedState', '')}{f', {inning} manche' if inning and state == LIVE else ''}"))
        return out


class NhlSource:
    name = "nhl_stats"
    URL = "https://api-web.nhle.com/v1/score/now"

    def __init__(self, http: HttpClient):
        self.http = http

    def fetch(self, now: datetime) -> list[Observation]:
        raw = self.http.get_json(self.URL)
        out = []
        for g in (raw or {}).get("games") or []:
            code = g.get("gameState")
            state = FINISHED if code in ("FINAL", "OFF") else LIVE if code in ("LIVE", "CRIT") else UPCOMING
            home, away = g.get("homeTeam") or {}, g.get("awayTeam") or {}

            def name(team):
                return ((team.get("placeName") or {}).get("default", "") + " "
                        + (team.get("name") or {}).get("default", team.get("abbrev", "?"))).strip()
            out.append(game_observation(
                self.name, str(g.get("id")), parse_date(g.get("startTimeUTC")), now,
                f"https://www.nhl.com/gamecenter/{g.get('id')}", "nhl.com", "NHL", name(home), name(away),
                home.get("score") if state != UPCOMING else None,
                away.get("score") if state != UPCOMING else None, state, str(code or "")))
        return out


class FootballDataSource:
    name = "football_data"
    URL = "https://api.football-data.org/v4/matches"
    KEY = "FOOTBALL_DATA_KEY"

    def __init__(self, http: HttpClient):
        self.http = http

    def fetch(self, now: datetime) -> list[Observation]:
        key = os.environ.get(self.KEY)
        if not key:
            raise SourceUnavailable(f"pas de clé {self.KEY}")
        raw = self.http.get_json(self.URL, params={
            "dateFrom": (now - timedelta(days=1)).strftime("%Y-%m-%d"),
            "dateTo": (now + timedelta(days=2)).strftime("%Y-%m-%d")}, headers={"X-Auth-Token": key})
        out = []
        for m in (raw or {}).get("matches") or []:
            code = m.get("status")
            state = (FINISHED if code in ("FINISHED", "AWARDED") else
                     LIVE if code in ("IN_PLAY", "PAUSED", "LIVE") else UPCOMING)
            full = (m.get("score") or {}).get("fullTime") or {}
            league = (m.get("competition") or {}).get("name", "football")
            out.append(game_observation(
                self.name, str(m.get("id")), parse_date(m.get("utcDate")), now,
                f"https://www.football-data.org/match/{m.get('id')}", "football-data.org", league,
                (m.get("homeTeam") or {}).get("name", "?"), (m.get("awayTeam") or {}).get("name", "?"),
                full.get("home") if state != UPCOMING else None,
                full.get("away") if state != UPCOMING else None, state, str(code or "")))
        return out
