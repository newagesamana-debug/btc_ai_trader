import pandas as pd

from src.strategy.engine import StrategyEngine

from src.strategy.setup.models import SetupDirection

from src.strategy.signal.models import (
    SignalDirection,
    SignalReason,
)


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


def test_strategy_engine_produces_long_position():

    engine = StrategyEngine()

    result = engine.evaluate(
        create_row()
    )

    assert result.setup.valid is True

    assert result.setup.direction == SetupDirection.LONG

    assert result.signal.valid is True

    assert result.signal.direction == SignalDirection.LONG

    assert result.position.valid is True

    assert result.position.direction == SignalDirection.LONG

    assert result.position.entry is not None
    assert result.position.stop_loss is not None
    assert result.position.take_profit is not None

    assert result.position.risk_amount == 100

    assert result.position.risk_reward == 3.0

    assert result.position.max_loss == 100

    assert result.position.potential_profit == 300

    assert result.signal.reason == SignalReason.BULLISH_BOS


def test_strategy_engine_produces_short_position():

    engine = StrategyEngine()

    result = engine.evaluate(
        create_row(
            h4_ema_20=95,
            h4_ema_50=100,
            h4_ema_200=105,

            h1_ema_20=96,
            h1_ema_50=100,
            h1_ema_200=104,

            h4_rsi=40,
            h1_rsi=42,

            structure_label="LL",

            event_type="BOS",
            event_direction="BEARISH",
        )
    )

    assert result.setup.valid is True

    assert result.setup.direction == SetupDirection.SHORT

    assert result.signal.valid is True

    assert result.signal.direction == SignalDirection.SHORT

    assert result.position.valid is True

    assert result.position.direction == SignalDirection.SHORT

    assert result.position.entry is not None
    assert result.position.stop_loss is not None
    assert result.position.take_profit is not None

    assert result.position.risk_reward == 3.0

    assert result.position.max_loss == 100

    assert result.position.potential_profit == 300

    assert result.signal.reason == SignalReason.BEARISH_BOS


def test_strategy_engine_rejects_range():

    engine = StrategyEngine()

    result = engine.evaluate(
        create_row(
            h4_ema_20=100,
            h4_ema_50=100,
            h4_ema_200=100,

            h1_ema_20=100,
            h1_ema_50=100,
            h1_ema_200=100,

            h4_rsi=50,
            h1_rsi=50,

            structure_label=None,

            event_type=None,
            event_direction=None,
        )
    )

    assert result.setup.valid is False

    assert result.signal.valid is False

    assert result.position.valid is False

    assert result.signal.direction == SignalDirection.NONE