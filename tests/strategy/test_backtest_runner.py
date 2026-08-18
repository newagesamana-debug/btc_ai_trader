import pandas as pd
import pytest

from src.backtest.runner import BacktestRunner


def make_data():
    return pd.DataFrame(
        [
            {"open": 100, "high": 101, "low": 99, "close": 100},
            {"open": 100, "high": 102, "low": 98, "close": 101},
        ]
    )


def test_runner_validates_ohlc(tmp_path):
    path = tmp_path / "data.parquet"
    make_data().to_parquet(path)

    result, metrics = BacktestRunner().run_file(
        path=path,
        initial_balance=10_000,
    )

    assert result.initial_balance == 10_000
    assert result.final_balance >= 0
    assert metrics.total_trades == result.total_trades


def test_runner_rejects_missing_ohlc(tmp_path):
    path = tmp_path / "data.parquet"
    pd.DataFrame({"close": [100]}).to_parquet(path)

    with pytest.raises(ValueError, match="Missing OHLC columns"):
        BacktestRunner().run_file(path, initial_balance=10_000)


def test_runner_rejects_invalid_ohlc(tmp_path):
    path = tmp_path / "data.parquet"
    pd.DataFrame(
        [{"open": 100, "high": 90, "low": 95, "close": 100}]
    ).to_parquet(path)

    with pytest.raises(ValueError, match="high < low"):
        BacktestRunner().run_file(path, initial_balance=10_000)
