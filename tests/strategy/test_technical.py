import pandas as pd
import pytest

from src.strategy.features.technical import (
    TechnicalFeatureEngine,
)


def create_dataframe(
    rows: int = 250,
) -> pd.DataFrame:

    timestamps = pd.date_range(
        "2026-01-01",
        periods=rows,
        freq="1min",
        tz="UTC",
    )

    close = [
        100 + i * 0.1
        for i in range(rows)
    ]

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": close,
            "high": [
                price + 1
                for price in close
            ],
            "low": [
                price - 1
                for price in close
            ],
            "close": close,
            "volume": [
                1000
                for _ in range(rows)
            ],
        }
    )


def test_technical_features_are_created():

    dataframe = create_dataframe()

    engine = TechnicalFeatureEngine()

    result = engine.calculate(
        dataframe
    )

    expected_columns = {
        "ema_20",
        "ema_50",
        "ema_200",
        "rsi_14",
        "atr_14",
        "atr_pct",
        "roc_10",
        "volume_ma_20",
        "volume_ratio",
    }

    assert expected_columns.issubset(
        result.columns
    )


def test_ema_is_calculated():

    dataframe = create_dataframe()

    engine = TechnicalFeatureEngine()

    result = engine.calculate(
        dataframe
    )

    assert pd.notna(
        result["ema_20"].iloc[-1]
    )

    assert pd.notna(
        result["ema_50"].iloc[-1]
    )

    assert pd.notna(
        result["ema_200"].iloc[-1]
    )


def test_atr_is_positive():

    dataframe = create_dataframe()

    engine = TechnicalFeatureEngine()

    result = engine.calculate(
        dataframe
    )

    atr = result["atr_14"].dropna()

    assert len(atr) > 0
    assert (atr > 0).all()


def test_rsi_range():

    dataframe = create_dataframe()

    engine = TechnicalFeatureEngine()

    result = engine.calculate(
        dataframe
    )

    rsi = result["rsi_14"].dropna()

    assert len(rsi) > 0
    assert (rsi >= 0).all()
    assert (rsi <= 100).all()


def test_rsi_reaches_100_on_continuous_growth():

    dataframe = create_dataframe()

    engine = TechnicalFeatureEngine()

    result = engine.calculate(
        dataframe
    )

    rsi = result["rsi_14"].dropna()

    assert len(rsi) > 0
    assert rsi.iloc[-1] == 100.0

    def test_rsi_reaches_0_on_continuous_decline():
        dataframe = create_dataframe()

        dataframe["close"] = [
            200 - i * 0.1
            for i in range(len(dataframe))
        ]

        dataframe["open"] = dataframe["close"]
        dataframe["high"] = (
                dataframe["close"] + 1
        )
        dataframe["low"] = (
                dataframe["close"] - 1
        )

        engine = TechnicalFeatureEngine()

        result = engine.calculate(
            dataframe
        )

        rsi = result["rsi_14"].dropna()

        assert len(rsi) > 0
        assert rsi.iloc[-1] == 0.0

def test_volume_ratio():

    dataframe = create_dataframe()

    engine = TechnicalFeatureEngine()

    result = engine.calculate(
        dataframe
    )

    ratio = result["volume_ratio"].dropna()

    assert len(ratio) > 0

    assert (
        ratio > 0
    ).all()


def test_missing_column():

    dataframe = create_dataframe()

    dataframe = dataframe.drop(
        columns=["volume"]
    )

    engine = TechnicalFeatureEngine()

    with pytest.raises(ValueError):

        engine.calculate(
            dataframe
        )

        def test_future_candle_does_not_change_past_features():
            dataframe = create_dataframe(300)

            engine = TechnicalFeatureEngine()

            original = engine.calculate(
                dataframe
            )

            modified = dataframe.copy()

            # Меняем только будущую свечу
            future_index = 299

            modified.loc[
                future_index,
                "close"
            ] = 10000

            modified.loc[
                future_index,
                "high"
            ] = 10001

            modified.loc[
                future_index,
                "low"
            ] = 9999

            modified.loc[
                future_index,
                "open"
            ] = 10000

            modified.loc[
                future_index,
                "volume"
            ] = 999999

            changed = engine.calculate(
                modified
            )

            # Проверяем значения ДО изменённой свечи
            columns = [
                "ema_20",
                "ema_50",
                "ema_200",
                "rsi_14",
                "atr_14",
                "atr_pct",
                "roc_10",
                "volume_ma_20",
                "volume_ratio",
            ]

            for column in columns:
                pd.testing.assert_series_equal(
                    original[column].iloc[:299].reset_index(
                        drop=True
                    ),
                    changed[column].iloc[:299].reset_index(
                        drop=True
                    ),
                    check_names=False,
                )