from datetime import datetime, timezone

import pytest

from srs import CardState, schedule


def test_first_successful_review_uses_one_day_interval() -> None:
    before = datetime.now(timezone.utc)
    state, next_review = schedule(4, CardState())

    assert state.repetition == 1
    assert state.interval == 1
    assert next_review > before


def test_second_successful_review_uses_six_days() -> None:
    state, _ = schedule(4, CardState())
    state, _ = schedule(4, state)

    assert state.repetition == 2
    assert state.interval == 6


def test_failed_review_resets_repetition() -> None:
    state = CardState(interval=20, repetition=4, ease=2.5)
    state, _ = schedule(2, state)

    assert state.repetition == 0
    assert state.interval == 1


def test_ease_never_falls_below_minimum() -> None:
    state = CardState(ease=1.3)
    state, _ = schedule(1, state)

    assert state.ease == 1.3


def test_invalid_score_is_rejected() -> None:
    with pytest.raises(ValueError, match="1 through 5"):
        schedule(0, CardState())
