import pandas as pd

from src.strategy.regime.models import MarketRegime
from src.strategy.setup.engine import SetupEngine
from src.strategy.setup.models import (
    SetupDirection,
    SetupType,
)


def create_row(**overrides):

    data = {
        "regime": MarketRegime.BULLISH,
        "regime_confidence": 0.85,

        "close": 100_000,
        "atr": 1_000,

        "structure_score": 0.8,

        "event_type": "BOS",
        "event_direction": "BULLISH",

        "swing_low": 98_000,
        "swing_high": 102_000,
    }

    data.update(overrides)

    return pd.Series(data)


def test_bullish_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row()
    )

    assert result.valid is True

    assert result.direction == SetupDirection.LONG

    assert result.entry == 100_000

    assert result.stop_loss < result.entry
    assert result.take_profit > result.entry

    assert result.risk > 0
    assert result.reward > 0

    assert result.risk_reward >= 2.5


def test_bearish_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime=MarketRegime.BEARISH,
            structure_score=-0.8,
            event_type="BOS",
            event_direction="BEARISH",
        )
    )

    assert result.valid is True

    assert result.direction == SetupDirection.SHORT

    assert result.stop_loss > result.entry
    assert result.take_profit < result.entry

    assert result.risk > 0
    assert result.reward > 0

    assert result.risk_reward >= 2.5


def test_long_stop_uses_swing_low():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            swing_low=97_000,
        )
    )

    expected_stop = (
        97_000
        - 1_000 * 0.20
    )

    assert result.stop_loss == expected_stop


def test_short_stop_uses_swing_high():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime=MarketRegime.BEARISH,
            structure_score=-0.8,
            event_direction="BEARISH",
            swing_high=103_000,
        )
    )

    expected_stop = (
        103_000
        + 1_000 * 0.20
    )

    assert result.stop_loss == expected_stop


def test_low_confidence_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime_confidence=0.50,
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE


def test_bullish_regime_with_bearish_structure_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            structure_score=-0.5,
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE


def test_bearish_regime_with_bullish_structure_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime=MarketRegime.BEARISH,
            structure_score=0.5,
            event_direction="BULLISH",
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE


def test_range_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime=MarketRegime.RANGE,
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE


def test_bos_is_continuation():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            event_type="BOS",
        )
    )

    assert result.setup_type == SetupType.BOS_CONTINUATION


def test_choch_is_reversal():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            event_type="CHoCH",
        )
    )

    assert result.setup_type == SetupType.CHOCH_REVERSAL


def test_missing_swing_uses_atr_fallback():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            swing_low=None,
        )
    )

    assert result.valid is True

    expected_stop = (
        100_000
        - 1_000 * 1.5
        - 1_000 * 0.20
    )

    assert result.stop_loss == expected_stop


def test_missing_required_data_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime=None,
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE
    assert result.setup_type == SetupType.NONE

def test_negative_atr_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            atr=-100,
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE

def test_bullish_regime_with_bearish_event_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            event_type="BOS",
            event_direction="BEARISH",
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE

def test_bearish_regime_with_bullish_event_produces_no_setup():

    engine = SetupEngine()

    result = engine.generate(
        create_row(
            regime=MarketRegime.BEARISH,
            structure_score=-0.8,
            event_type="BOS",
            event_direction="BULLISH",
        )
    )

    assert result.valid is False
    assert result.direction == SetupDirection.NONE