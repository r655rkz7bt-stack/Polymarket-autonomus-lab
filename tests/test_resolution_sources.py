"""Chantier n°0 : source de résolution des marchés, scores officiels, sources à clé."""

from __future__ import annotations

import pytest

from conftest import NOW, raw_market
from polymarket_agent import resolution_sources as rs
from polymarket_agent.data_collector import collect
from polymarket_agent.http_client import HttpClient, SourceUnavailable
from polymarket_agent.persistence import Database
from polymarket_agent.sources.crypto_prices import CryptoPricesSource
from polymarket_agent.sources.guardian import GuardianSource
from polymarket_agent.sources.odds_api import OddsApiSource, implied
from polymarket_agent.sources.polymarket_gamma import parse_market
from polymarket_agent.sources.sports import FootballDataSource, MlbSource, NhlSource
from test_sources import FakeHttp

KEYS = ("FOOTBALL_DATA_KEY", "ODDS_API_KEY", "GUARDIAN_API_KEY")


@pytest.fixture(autouse=True)
def no_keys(monkeypatch):
    for k in KEYS:
        monkeypatch.delenv(k, raising=False)


def test_resolution_source_is_parsed_archived_and_inventoried(tmp_path):
    m1 = parse_market(raw_market("1", resolutionSource="https://www.uefa.com/uefachampionsleague/",
                                 description="Resolves per the official result."))
    m2 = parse_market(raw_market("2", resolutionSource="", description=(
        "This market resolves according to the Binance 1 minute candle for BTC/USDT "
        "(https://www.binance.com/en/trade/BTC_USDT), at 12:00 ET.")))
    m3 = parse_market(raw_market("3", description="No link here."))
    assert m1.resolution_source.startswith("https://www.uefa.com") and "official" in m1.description
    assert rs.source_of(m2.resolution_source, m2.description) == (
        "https://www.binance.com/en/trade/BTC_USDT", "binance.com")
    db = Database(tmp_path / "m.sqlite")
    assert rs.archive(db, [m1, m2, m3], NOW) == 3
    rs.archive(db, [m1], NOW)  # rafraîchi, pas dupliqué
    assert rs.domain_for(db, "1") == "uefa.com" and rs.domain_for(db, "inconnu") == ""
    inv = {i["domaine"]: i for i in rs.inventory(db)}
    assert inv["uefa.com"]["lecteur"] == "football_data" and inv["binance.com"]["lecteur"] == "crypto_prices"
    assert inv["(aucun)"]["marches"] == 1
    text = rs.status_text(db)
    assert text.startswith("3 marchés ; lus à la source : 67 %") or text.startswith("3 marchés ; lus à la source : 67%")
    assert "| uefa.com | 1 |" in rs.markdown(db, NOW)


def test_domain_parsing_is_robust():
    assert rs.domain_of("WWW.NHL.com/scores") == "nhl.com"
    assert rs.domain_of("https://user@statsapi.mlb.com:443/x") == "statsapi.mlb.com"
    assert rs.domain_of("") == "" and rs.domain_of("   ") == ""


def test_official_mlb_and_nhl_scores_become_observations():
    mlb = FakeHttp({MlbSource.URL: {"dates": [{"games": [
        {"gamePk": 849818, "gameDate": "2026-10-14T17:00:00Z",
         "status": {"abstractGameState": "Final", "detailedState": "Final"},
         "teams": {"away": {"team": {"name": "Tampa Bay Rays"}, "score": 2},
                   "home": {"team": {"name": "Cleveland Guardians"}, "score": 3}}},
        {"gamePk": 2, "gameDate": "2026-10-14T23:00:00Z", "status": {"abstractGameState": "Preview"},
         "teams": {"away": {"team": {"name": "A"}}, "home": {"team": {"name": "B"}}}}]}]}})
    final, upcoming = MlbSource(mlb).fetch(NOW)
    assert final.title == "MLB : Tampa Bay Rays 2 - 3 Cleveland Guardians (terminé)"
    assert final.data["score_domicile"] == 3 and final.reliability >= 0.9 and final.domain == "mlb.com"
    assert upcoming.data["etat"] == "à venir" and upcoming.data["score_domicile"] is None
    assert mlb.calls[0][1]["sportId"] == 1
    nhl = FakeHttp({NhlSource.URL: {"games": [
        {"id": 7, "startTimeUTC": "2026-10-14T11:00:00Z", "gameState": "LIVE",
         "awayTeam": {"name": {"default": "Sabres"}, "placeName": {"default": "Buffalo"}, "score": 1},
         "homeTeam": {"name": {"default": "Maple Leafs"}, "abbrev": "TOR", "score": 0}}]}})
    live = NhlSource(nhl).fetch(NOW)[0]
    assert live.data["etat"] == "en cours" and "Buffalo Sabres 1 - 0 Maple Leafs" in live.title
    # Un score qui change est une nouvelle observation (identifiant différent).
    assert live.external_id == "nhl_stats-7-en cours-1-0"


def test_keyed_sources_are_disabled_without_key_and_never_called(tmp_path):
    http = FakeHttp({})
    settings = {"sources": {n: {"enabled": True, "every_minutes": 5} for n in
                            ("football_data", "odds_api", "guardian")}}
    result = collect(settings, http, Database(tmp_path / "m.sqlite"), [], NOW)
    assert result.status["football_data"] == "désactivée (pas de clé FOOTBALL_DATA_KEY)"
    assert result.status["odds_api"] == "désactivée (pas de clé ODDS_API_KEY)"
    assert result.status["guardian"] == "désactivée (pas de clé GUARDIAN_API_KEY)"
    assert not any("football-data" in c[0] or "odds-api" in c[0] or "guardian" in c[0] for c in http.calls)


def test_football_data_sends_its_key_in_its_own_header_only(monkeypatch):
    monkeypatch.setenv("FOOTBALL_DATA_KEY", "cle-test")
    http = FakeHttp({FootballDataSource.URL: {"matches": [
        {"id": 5, "utcDate": "2026-10-14T19:00:00Z", "status": "FINISHED",
         "competition": {"name": "UEFA Champions League"},
         "homeTeam": {"name": "Real Madrid CF"}, "awayTeam": {"name": "AS Roma"},
         "score": {"fullTime": {"home": 2, "away": 1}}}]}})
    obs = FootballDataSource(http).fetch(NOW)[0]
    assert obs.title == "UEFA Champions League : AS Roma 1 - 2 Real Madrid CF (terminé)"
    assert http.calls[0][2]["X-Auth-Token"] == "cle-test"
    assert "X-Auth-Token" not in http.session.headers  # jamais dans la session partagée


def test_odds_are_turned_into_bookmaker_probabilities(monkeypatch):
    books = [{"key": "a", "markets": [{"key": "h2h", "outcomes": [{"name": "X", "price": 1.5}, {"name": "Y", "price": 3.0}]}]},
             {"key": "b", "markets": [{"key": "h2h", "outcomes": [{"name": "X", "price": 2.0}, {"name": "Y", "price": 2.0}]}]},
             {"key": "c", "markets": [{"key": "spreads", "outcomes": []}]}]
    probs = implied(books)
    assert probs["X"] == pytest.approx((2 / 3 + 0.5) / 2, abs=1e-4) and sum(probs.values()) == pytest.approx(1)
    monkeypatch.setenv("ODDS_API_KEY", "cle-test")
    http = FakeHttp({"https://api.the-odds-api.com/v4/sports/baseball_mlb/odds": [
        {"id": "e1", "sport_title": "MLB", "commence_time": "2026-10-14T23:00:00Z",
         "home_team": "Y", "away_team": "X", "bookmakers": books}]},
        down=("https://api.the-odds-api.com/v4/sports/icehockey_nhl",))
    obs = OddsApiSource(http, ["baseball_mlb", "icehockey_nhl"]).fetch(NOW)
    assert len(obs) == 1 and obs[0].data["probabilites"]["X"] > 0.5 and "X 58%" in obs[0].text
    with pytest.raises(SourceUnavailable) as err:
        OddsApiSource(FakeHttp({}, down=("https://",)), ["baseball_mlb"]).fetch(NOW)
    assert "cle-test" not in str(err.value)


def test_guardian_articles_and_key_never_in_error(monkeypatch):
    monkeypatch.setenv("GUARDIAN_API_KEY", "cle-test")
    http = FakeHttp({GuardianSource.URL: {"response": {"status": "ok", "results": [
        {"id": "world/2026/oct/14/x", "webTitle": "Fed holds rates", "webUrl": "https://www.theguardian.com/x",
         "webPublicationDate": "2026-10-14T10:00:00Z", "fields": {"trailText": "<strong>Rates</strong> unchanged"}}]}}})
    art = GuardianSource(http).fetch(["Fed rates"], NOW)[0]
    assert art.title == "Fed holds rates" and art.text == "Rates unchanged" and art.domain == "theguardian.com"
    with pytest.raises(SourceUnavailable) as err:
        GuardianSource(FakeHttp({}, down=("https://",))).fetch(["x"], NOW)
    assert "cle-test" not in str(err.value)


def test_binance_is_read_first_because_it_resolves_crypto_markets():
    klines = [[1792000000000 + 3_600_000 * i, "0", "0", "0", str(82000 + 10 * (i % 5)), "0"] for i in range(170)]
    http = FakeHttp({"https://data-api.binance.vision/api/v3/klines": klines})
    q = CryptoPricesSource(http).quote("btc")
    assert q.source == "binance" and q.price == 82000 + 10 * (169 % 5) and q.as_of.year == 2026
    assert http.calls[0][1]["symbol"] == "BTCUSDT"


def test_per_request_headers_never_leak_into_the_shared_session():
    class Resp:
        status_code = 200
        headers = {}

        @staticmethod
        def json():
            return {}

    class Session:
        def __init__(self):
            self.headers, self.seen = {}, []

        def request(self, method, url, **kw):
            self.seen.append(kw.get("headers"))
            return Resp()

    s = Session()
    client = HttpClient(session=s, sleep=lambda x: None, min_interval=0)
    client.get_json("https://a.example", headers={"Authorization": "Bearer x"})
    client.get_json("https://b.example")
    assert s.seen == [{"Authorization": "Bearer x"}, None] and "Authorization" not in s.headers


def test_temperature_markets_get_the_official_readings_of_their_station():
    from datetime import timedelta
    from polymarket_agent.sources.weather import MetarSource, day_max, station_of
    m = parse_market(raw_market("9", resolutionSource="https://www.weather.gov/wrh/timeseries?site=nzwn"))
    other = parse_market(raw_market("10"))
    assert station_of(m.resolution_source) == "NZWN" and station_of("", "see weather.gov/wrh/timeseries?site=kdal") == "KDAL"
    # Nouveau format de Gamma (19-20/10/2026) : source METAR directe, avec ou sans autres paramètres devant « ids ».
    assert station_of("https://aviationweather.gov/api/data/metar?ids=EGLC&format=raw&date=2026-10-25T02:00:00Z&hours=30") == "EGLC"
    assert station_of("https://aviationweather.gov/api/data/metar?format=raw&ids=KJFK") == "KJFK"
    assert station_of("https://aviationweather.gov/api/data/taf?ids=KJFK") is None
    # Wellington (longitude 175 → UTC+12) ; NOW = 14/10 12:00 UTC = 15/10 00:00 locale.
    base = int((NOW - timedelta(hours=10)).timestamp())  # 14/10 14:00 locale
    rows = [{"icaoId": "NZWN", "obsTime": base + 1800 * i, "temp": 10 + (i % 4), "name": "Wellington Intl",
             "lon": 174.8} for i in range(20)]
    http = FakeHttp({"https://aviationweather.gov/api/data/metar": rows})
    obs = MetarSource(http).fetch([m, other], NOW + timedelta(hours=-1))  # 14/10 23:00 locale
    assert len(obs) == 1 and obs[0].market_ids == ["9"] and http.calls[0][1]["ids"] == "NZWN"
    assert obs[0].data["jour_local"] == "2026-10-14" and obs[0].data["max_jour_c"] == 13
    assert "max prudent du 2026-10-14 : 13.0 °C" in obs[0].text
    # Relevés hors de la fenêtre 03 h - 21 h locale (fuseau incertain) : ignorés.
    day, mx, n = day_max([(int(NOW.timestamp()) - 3600 * 23, 30.0)], 174.8, NOW - timedelta(hours=1))  # 01 h locale
    assert (day, mx, n) == ("2026-10-14", None, 0)
    assert MetarSource(FakeHttp({})).fetch([other], NOW) == []  # aucune station : aucun appel


def test_regression_crypto_quote_time_is_the_fetch_time_not_the_open_of_the_running_candle():
    """16/10/2026 : `as_of` valait l'ouverture de la bougie horaire en cours (jusqu'à 1 h avant le
    prix réel) ; avec la limite d'âge de 20 min, crypto_threshold s'abstenait ≈ 40 min par heure."""
    from datetime import datetime, timedelta, timezone
    from polymarket_agent.sources.crypto_prices import CryptoPricesSource
    start = 1792000000000
    klines = [[start + 3_600_000 * i, "0", "0", "0", str(82000 + 10 * (i % 5)), "0"] for i in range(170)]
    http = FakeHttp({"https://data-api.binance.vision/api/v3/klines": klines})
    running = datetime.fromtimestamp(klines[-1][0] / 1000, tz=timezone.utc)
    now = running + timedelta(minutes=45)
    obs = CryptoPricesSource(http).fetch(["btc"], now)
    assert obs[0].published_at == now
    later = running + timedelta(hours=3)  # bougie terminée depuis longtemps : sa fin, pas « maintenant »
    assert CryptoPricesSource(http).fetch(["btc"], later)[0].published_at == running + timedelta(hours=1)


def test_odds_are_bought_only_for_leagues_with_a_game_soon_within_a_daily_budget(monkeypatch):
    """19/10/2026 : la liste des matchs (gratuite) dit quelles ligues ont un match dans les 6 h ;
    seules celles-là sont relevées (le match le plus proche d'abord), au plus `daily_budget`
    crédits par jour et une fois toutes les 2 h 30 par ligue ; Pinnacle est gardé à part."""
    from datetime import timedelta
    monkeypatch.setenv("ODDS_API_KEY", "cle-test")

    class State(dict):
        def get_value(self, k):
            return self.get(k)

        def set_value(self, k, v):
            self[k] = v

    def ev(hours):
        return [{"id": "e", "commence_time": (NOW + timedelta(hours=hours)).isoformat().replace("+00:00", "Z")}]
    books = [{"key": "pinnacle", "markets": [{"key": "h2h", "outcomes": [{"name": "X", "price": 1.25}, {"name": "Y", "price": 5.0}]}]},
             {"key": "b", "markets": [{"key": "h2h", "outcomes": [{"name": "X", "price": 2.0}, {"name": "Y", "price": 2.0}]}]}]
    odds = [{"id": "o", "commence_time": "2026-10-14T23:00:00Z", "home_team": "Y", "away_team": "X", "bookmakers": books}]

    class Http:
        def __init__(self, cost="0"):
            self.calls, self.last_headers, self.cost = [], {}, cost

        def get_json(self, url, params=None, headers=None):
            self.calls.append(url.split("/sports/")[1])
            self.last_headers = {"x-requests-last": self.cost if url.endswith("/events") else "1"}
            sport = url.split("/sports/")[1].split("/")[0]
            if url.endswith("/events"):
                return {"mlb": ev(2), "nhl": ev(1), "nba": ev(30)}[sport]
            return odds
    state, http = State(), Http()
    obs = OddsApiSource(http, ["mlb", "nhl", "nba"], state=state, daily_budget=1).fetch(NOW)
    assert http.calls == ["mlb/events", "nhl/events", "nba/events", "nhl/odds"]  # NHL d'abord ; NBA trop loin
    assert len(obs) == 1 and obs[0].data["reference"]["X"] == pytest.approx(0.8) and obs[0].data["reference_nom"] == "pinnacle"
    assert state[f"odds_api:credits:{NOW:%Y-%m-%d}"] == "1"
    http.calls.clear()
    OddsApiSource(http, ["mlb", "nhl", "nba"], state=state, daily_budget=1).fetch(NOW)
    assert "mlb/odds" not in http.calls  # budget du jour épuisé
    http.calls.clear()
    OddsApiSource(http, ["mlb", "nhl", "nba"], state=state, daily_budget=5).fetch(NOW + timedelta(hours=1))
    assert "nhl/events" not in http.calls and "mlb/odds" in http.calls  # NHL relevée il y a 1 h : pas encore
    # Si la liste des matchs coûte des crédits : ancien rythme (toutes les 12 h par ligue).
    paid, st2 = Http(cost="1"), State()
    OddsApiSource(paid, ["mlb", "nhl"], state=st2).fetch(NOW)
    assert st2["odds_api:events_payants"] == "oui" and paid.calls == ["mlb/events", "mlb/odds", "nhl/odds"]


def test_sports_link_prefers_the_reference_bookmaker():
    from datetime import timedelta
    from polymarket_agent import sports_link
    from polymarket_agent.observations import Observation
    import json as _json
    start = NOW + timedelta(hours=3)
    m = parse_market(raw_market("g", question="Dodgers vs. Brewers", outcomes=_json.dumps(["Dodgers", "Brewers"]),
                                gameStartTime=start.strftime("%Y-%m-%d %H:%M:%S+00")))
    o = Observation(source="odds_api", external_id="o", published_at=NOW, collected_at=NOW, url="", title="", text="",
                    data={"domicile": "Milwaukee Brewers", "exterieur": "Los Angeles Dodgers", "debut": start.isoformat(),
                          "probabilites": {"Milwaukee Brewers": 0.5, "Los Angeles Dodgers": 0.5},
                          "reference": {"Milwaukee Brewers": 0.4, "Los Angeles Dodgers": 0.6}})
    assert sports_link.link(m, [o])["cotes"] == [0.6, 0.4]
