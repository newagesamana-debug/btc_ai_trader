import pandas as pd

from src.strategy.regime.models import (
    MarketRegime,
)

from src.strategy.snapshot.builder import (
    MarketSnapshotBuilder,
)


def create_row():

    return pd.Series(
        {
            "timestamp": pd.Timestamp(
                "2026-01-01 12:00",
                tz="UTC",
            ),
            "open": 64000,
            "high": 64500,
            "low": 63800,
            "close": 64300,
            "volume": 1500,

            "h4_rsi": 61,
            "h4_atr_pct": 2.1,

            "h1_rsi": 58,
            "h1_atr_pct": 1.2,

            "m15_rsi": 54,
            "m15_atr_pct": 0.7,

            "m5_rsi": 52,
            "m5_atr_pct": 0.3,

            "m5_volume_ratio": 1.8,
        }
    )


def test_snapshot_builder():

    builder = MarketSnapshotBuilder()

    snapshot = builder.build(
        row=create_row(),
        regime=MarketRegime.BULLISH,
        regime_confidence=0.8,
        last_swing_high=64500,
        last_swing_low=63500,
        last_structure_label="HH",
        last_event_type="BOS",
        last_event_direction="BULLISH",
    )

    assert snapshot.price.close == 64300

    assert (
        snapshot.regime
        == MarketRegime.BULLISH
    )

    assert (
        snapshot.regime_confidence
        == 0.8
    )

    assert (
        snapshot.technical.h4_rsi
        == 61
    )

    assert (
        snapshot.technical.m5_volume_ratio
        == 1.8
    )


def test_snapshot_is_immutable():

    builder = MarketSnapshotBuilder()

    snapshot = builder.build(
        row=create_row(),
        regime=MarketRegime.BULLISH,
        regime_confidence=0.8,
        last_swing_high=64500,
        last_swing_low=63500,
        last_structure_label="HH",
        last_event_type="BOS",
        last_event_direction="BULLISH",
    )

    try:
        snapshot.price.close = 100000
        assert False

    except AttributeError:
        pass