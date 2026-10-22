"""Budget des cotes (22/10/2026) : les 12 crédits du jour étaient épuisés dès la matinée, plus de cotes pour les matchs du soir."""

from datetime import datetime, timezone

from polymarket_agent.sources.odds_api import OddsApiSource


def _at(hour: int) -> datetime:
    return datetime(2026, 10, 21, hour, 30, tzinfo=timezone.utc)


def test_daily_credits_are_spread_over_the_day():
    source = OddsApiSource(http=None, sports=["basketball_nba"], daily_budget=12)
    allowed = [source.allowed_today(_at(h)) for h in range(24)]
    assert allowed[0] == 2 and allowed[12] == 8 and allowed[20] == 12 and allowed[23] == 12
    assert allowed == sorted(allowed)          # jamais moins tard dans la journée
    assert allowed[13] < 12                    # le 21/10 le budget entier était dépensé à 12 h 57 : plus maintenant
    assert OddsApiSource(http=None, sports=[], daily_budget=1).allowed_today(_at(0)) == 1  # jamais plus que le budget
