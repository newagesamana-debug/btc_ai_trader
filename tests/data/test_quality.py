import pandas as pd

from src.data.quality import DataQualityChecker


def create_dataframe():

    timestamps = pd.date_range(
        start="2026-01-01 00:00:00",
        periods=5,
        freq="1min",
        tz="UTC",
    )

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": [100, 101, 102, 103, 104],
            "high": [102, 103, 104, 105, 106],
            "low": [99, 100, 101, 102, 103],
            "close": [101, 102, 103, 104, 105],
            "volume": [10, 20, 30, 40, 50],
        }
    )


def test_valid_data():

    df = create_dataframe()

    checker = DataQualityChecker()

    report = checker.check(
        df,
        "1m",
        now=pd.Timestamp(
            "2026-01-01 01:00:00",
            tz="UTC",
        ).to_pydatetime(),
    )

    assert report.total_candles == 5
    assert report.duplicate_count == 0
    assert report.gap_count == 0
    assert report.invalid_ohlc_count == 0
    assert report.future_candle_count == 0
    assert report.is_valid


def test_duplicate_detection():

    df = create_dataframe()

    df = pd.concat(
        [df, df.iloc[[0]]],
        ignore_index=True,
    )

    checker = DataQualityChecker()

    report = checker.check(
        df,
        "1m",
        now=pd.Timestamp(
            "2026-01-01 01:00:00",
            tz="UTC",
        ).to_pydatetime(),
    )

    assert report.duplicate_count == 1
    assert not report.is_valid


def test_gap_detection():

    df = create_dataframe()

    df = df.drop(index=2).reset_index(
        drop=True
    )

    checker = DataQualityChecker()

    report = checker.check(
        df,
        "1m",
        now=pd.Timestamp(
            "2026-01-01 01:00:00",
            tz="UTC",
        ).to_pydatetime(),
    )

    assert report.gap_count == 1


def test_invalid_ohlc_detection():

    df = create_dataframe()

    df.loc[2, "high"] = 90

    checker = DataQualityChecker()

    report = checker.check(
        df,
        "1m",
        now=pd.Timestamp(
            "2026-01-01 01:00:00",
            tz="UTC",
        ).to_pydatetime(),
    )

    assert report.invalid_ohlc_count == 1
    assert not report.is_valid