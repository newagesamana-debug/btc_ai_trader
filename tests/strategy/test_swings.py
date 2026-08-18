import pandas as pd

from src.strategy.structure.models import SwingType
from src.strategy.structure.swings import (
    SwingDetector,
)


def test_detect_swing_high():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=7,
                freq="1min",
                tz="UTC",
            ),
            "high": [
                100,
                101,
                102,
                110,
                103,
                102,
                101,
            ],
            "low": [
                98,
                99,
                100,
                105,
                100,
                99,
                98,
            ],
        }
    )

    detector = SwingDetector(
        left_bars=3,
        right_bars=3,
    )

    swings = detector.detect(dataframe)

    highs = [
        swing
        for swing in swings
        if swing.type == SwingType.HIGH
    ]

    assert len(highs) == 1
    assert highs[0].price == 110
    assert highs[0].index == 3


def test_detect_swing_low():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=7,
                freq="1min",
                tz="UTC",
            ),
            "high": [
                105,
                104,
                103,
                100,
                103,
                104,
                105,
            ],
            "low": [
                100,
                99,
                98,
                90,
                97,
                98,
                99,
            ],
        }
    )

    detector = SwingDetector(
        left_bars=3,
        right_bars=3,
    )

    swings = detector.detect(dataframe)

    lows = [
        swing
        for swing in swings
        if swing.type == SwingType.LOW
    ]

    assert len(lows) == 1
    assert lows[0].price == 90
    assert lows[0].index == 3


def test_no_future_edge_swings():

    dataframe = pd.DataFrame(
        {
            "timestamp": pd.date_range(
                "2026-01-01",
                periods=5,
                freq="1min",
                tz="UTC",
            ),
            "high": [
                100,
                101,
                102,
                103,
                104,
            ],
            "low": [
                90,
                91,
                92,
                93,
                94,
            ],
        }
    )

    detector = SwingDetector(
        left_bars=2,
        right_bars=2,
    )

    swings = detector.detect(dataframe)

    assert swings == []