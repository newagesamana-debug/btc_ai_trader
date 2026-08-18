import pandas as pd
import pytest

from src.strategy.pipeline.engine import StrategyPipeline

from src.strategy.setup.models import SetupDirection
from src.strategy.signal.models import SignalDirection


def create_row(**overrides):

    data = {
        "h4_ema_20": 105,
        "h4_ema_50": 100,
        "h4_ema_200": 95,

        "h1_ema_20": 104,
        "h1_ema_50": 100,
        "h1_ema_200": 96,

        "h4_rsi": 60,
        "h1_rsi": 58,

        "h4_atr_pct": 1.5,
        "h1_atr_pct": 1.0,
        "m15_atr_pct": 0.6,

        "close": 100_000,
        "atr": 1_000,

        "swing_low": 98_000,
        "swing_high": 102_000,

        "structure_label": "HH",

        "event_type": "BOS",
        "event_direction": "BULLISH",
    }

    data.update(overrides)

    return pd.Series(data)


def test_pipeline_creates_long_position():

    pipeline = StrategyPipeline()

    result = pipeline.process(
        row=create_row(),
        account_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    assert result.setup.valid is True
    assert result.setup.direction == SetupDirection.LONG

    assert result.signal.valid is True
    assert result.signal.direction == SignalDirection.LONG

    assert result.position.valid is True
    assert result.position.direction == SignalDirection.LONG

    assert result.position.risk_amount == 100
    assert result.setup.entry == 100_000
    assert result.setup.stop_loss == 97_800
    assert result.setup.take_profit == 106_600

    assert result.signal.entry == 100_000
    assert result.signal.stop_loss == 97_800
    assert result.signal.take_profit == 106_600

    assert result.position.entry == 100_000
    assert result.position.stop_loss == 97_800
    assert result.position.take_profit == 106_600

    assert result.position.position_size == pytest.approx(100 / 2200)
    assert result.position.notional_value == pytest.approx(100_000 * (100 / 2200))

    assert result.position.max_loss == pytest.approx(100)
    assert result.position.potential_profit == pytest.approx(300)
    assert result.position.position_size == pytest.approx(100 / 2200)
    assert result.position.max_loss == 100
    assert result.position.potential_profit == 300