import pandas as pd

from src.strategy.multitimeframe.fusion import (
    MultiTimeframeFeatureFusion,
)


def create_features(
    timestamps,
    value,
):

    if not isinstance(value, (int, float)):
        value = list(value)

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "ema_20": value,
            "ema_50": value,
            "ema_200": value,
            "rsi_14": value,
            "atr_pct": value,
            "volume_ratio": value,
        }
    )


def test_4h_features_are_not_available_before_close():

    base = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01 08:00",
                periods=6,
                freq="1h",
                tz="UTC",
            )
        }
    )

    h4 = create_features(
        pd.date_range(
            "2026-01-01 08:00",
            periods=2,
            freq="4h",
            tz="UTC",
        ),
        100,
    )

    fusion = MultiTimeframeFeatureFusion()

    result = fusion.combine(
        base,
        {"4h": h4},
    )

    # 08:00, 09:00, 10:00, 11:00
    # must NOT see the 08:00 candle.

    assert pd.isna(
        result.loc[0, "h4_ema_20"]
    )

    assert pd.isna(
        result.loc[3, "h4_ema_20"]
    )

    # 12:00 can use the closed 4H candle.

    assert (
        result.loc[4, "h4_ema_20"]
        == 100
    )


def test_latest_closed_timeframe_value_is_used():

    base = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01 00:00",
                periods=10,
                freq="1h",
                tz="UTC",
            )
        }
    )

    h1 = create_features(
        pd.date_range(
            "2026-01-01 00:00",
            periods=10,
            freq="1h",
            tz="UTC",
        ),
        range(10),
    )

    fusion = MultiTimeframeFeatureFusion()

    result = fusion.combine(
        base,
        {"1h": h1},
    )

    # At 01:00 the 00:00 candle is closed.

    assert (
        result.loc[1, "h1_ema_20"]
        == 0
    )

    # At 05:00 the 04:00 candle is closed.

    assert (
        result.loc[5, "h1_ema_20"]
        == 4
    )

    def test_future_timeframe_candle_is_not_used():
        base = pd.DataFrame(
            {
                "timestamp": pd.date_range(
                    "2026-01-01 08:00",
                    periods=8,
                    freq="1h",
                    tz="UTC",
                )
            }
        )

        h4 = create_features(
            pd.date_range(
                "2026-01-01 08:00",
                periods=2,
                freq="4h",
                tz="UTC",
            ),
            [100, 200],
        )

        fusion = MultiTimeframeFeatureFusion()

        result = fusion.combine(
            base,
            {"4h": h4},
        )

        # 08:00-11:00 -> no closed 4H candle
        assert result.loc[0, "h4_ema_20"] != 100
        assert result.loc[3, "h4_ema_20"] != 100

        # 12:00-15:00 -> first 4H candle is available
        assert result.loc[4, "h4_ema_20"] == 100

        # Second 4H candle closes at 16:00
        assert result.loc[7, "h4_ema_20"] == 100