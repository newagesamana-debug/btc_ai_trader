from datetime import datetime, timezone

import pytest

from src.data.schemas import Candle
from src.data.validator import (
    validate_candle,
    validate_candles,
)


def create_valid_candle(timestamp: int) -> Candle:
    return Candle(
        timestamp=datetime.fromtimestamp(
            timestamp,
            tz=timezone.utc,
        ),
        open=100.0,
        high=105.0,
        low=95.0,
        close=102.0,
        volume=1000.0,
    )


def test_valid_candle():
    candle = create_valid_candle(1000)

    assert candle.is_valid
    validate_candle(candle)


def test_invalid_candle_price_structure():
    candle = Candle(
        timestamp=datetime.fromtimestamp(
            1000,
            tz=timezone.utc,
        ),
        open=100.0,
        high=90.0,
        low=95.0,
        close=102.0,
        volume=1000.0,
    )

    assert not candle.is_valid

    with pytest.raises(ValueError):
        validate_candle(candle)


def test_candles_must_be_chronological():
    candle_1 = create_valid_candle(2000)
    candle_2 = create_valid_candle(1000)

    with pytest.raises(ValueError):
        validate_candles([candle_1, candle_2])