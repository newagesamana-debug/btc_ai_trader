import pandas as pd

from src.data.aggregator import TimeframeAggregator


def create_test_data():

    timestamps = pd.date_range(
        start="2026-01-01 00:00:00",
        periods=10,
        freq="1min",
        tz="UTC",
    )

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": [
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
            ],
            "high": [
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
                111,
            ],
            "low": [
                99,
                100,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
            ],
            "close": [
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                110,
            ],
            "volume": [
                10,
                20,
                30,
                40,
                50,
                60,
                70,
                80,
                90,
                100,
            ],
        }
    )


def test_5m_aggregation():

    df = create_test_data()

    aggregator = TimeframeAggregator()

    result = aggregator.aggregate(
        df,
        "5m",
    )

    assert len(result) == 2

    first = result.iloc[0]

    assert first["open"] == 100
    assert first["high"] == 106
    assert first["low"] == 99
    assert first["close"] == 105
    assert first["volume"] == 150


def test_15m_aggregation():

    df = create_test_data()

    aggregator = TimeframeAggregator()

    result = aggregator.aggregate(
        df,
        "15m",
    )

    assert len(result) == 1

    candle = result.iloc[0]

    assert candle["open"] == 100
    assert candle["high"] == 111
    assert candle["low"] == 99
    assert candle["close"] == 110
    assert candle["volume"] == 550