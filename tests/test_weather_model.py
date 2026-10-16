"""Modèle météo (marchés de température) : lecture des questions, probabilités des tranches."""

from __future__ import annotations

import pytest

from polymarket_agent import weather_model as wm


def test_questions_are_parsed_into_brackets():
    q = wm.parse_question("Will the highest temperature in Paris be 16°C on October 17?")
    assert (q.kind, q.low, q.high, q.unit, q.month, q.day) == ("max", 15.5, 16.5, "C", 10, 17)
    q = wm.parse_question("Will the lowest temperature in Miami be between 76-77°F on October 17?")
    assert (q.kind, q.low, q.high, q.unit) == ("min", 75.5, 77.5, "F")
    assert wm.parse_question("Will the highest temperature in Denver be 41°F or below on October 15?").high == 41.5
    assert wm.parse_question("Will the highest temperature in Seoul be 26°C or higher on October 17?").low == 25.5
    assert wm.parse_question("Will Bitcoin be above 80000 on October 17?") is None


def test_probabilities_sum_to_one_and_observations_rule_out_brackets():
    members = [15.8, 16.2, 16.4, 15.9]
    qs = [wm.parse_question(f"Will the highest temperature in Paris be {t}°C on October 17?") for t in range(5, 30)]
    total = sum(wm.probability(q, members, 1.0) for q in qs)
    assert total == pytest.approx(1.0, abs=1e-3)
    q16 = qs[11]
    assert wm.probability(q16, members, 1.0) > wm.probability(qs[14], members, 1.0)
    # Maximum déjà relevé à 18 °C : la tranche 16 °C est impossible.
    assert wm.probability(q16, members, 1.0, observed_c=18.0) == 0.0
    low, est, high = wm.band(q16, members, 1.0, 1.0, 1.6)
    assert low <= est <= high
    # °F : flou converti (1 °C = 1,8 °F).
    qf = wm.parse_question("Will the highest temperature in Dallas be between 60-61°F on October 17?")
    assert wm.probability(qf, [15.85], 0.5) > 0.5
