import pandas as pd
import pytest

from src.backtest.walk_forward import WalkForwardRunner


def create_row(close=100_000, high=None, low=None):
    if high is None:
        high = close + 500
    if low is None:
        low = close - 500

    return {
        "open": close,
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
        "close": close,
        "high": high,
        "low": low,
        "atr": 1_000,
        "swing_low": 98_000,
        "swing_high": 102_000,
        "structure_label": "HH",
        "event_type": "BOS",
        "event_direction": "BULLISH",
    }


def make_data(rows=8):
    return pd.DataFrame(create_row() for _ in range(rows))


def test_walk_forward_creates_sequential_oos_folds():
    result = WalkForwardRunner().run(
        data=make_data(10),
        initial_balance=10_000,
        train_size=4,
        test_size=2,
    )

    assert result.total_folds == 3
    assert [(f.test_start, f.test_end) for f in result.folds] == [
        (4, 6),
        (6, 8),
        (8, 10),
    ]
    assert all(f.train_end == f.test_start for f in result.folds)


def test_walk_forward_combines_fold_trades():
    result = WalkForwardRunner().run(
        data=make_data(8),
        initial_balance=10_000,
        train_size=2,
        test_size=2,
    )

    assert result.total_folds == 3
    assert result.combined_result.total_trades == sum(
        fold.result.total_trades for fold in result.folds
    )
    assert result.combined_metrics.total_trades == result.combined_result.total_trades


def test_walk_forward_rejects_insufficient_data():
    with pytest.raises(ValueError, match="Not enough data"):
        WalkForwardRunner().run(
            data=make_data(5),
            initial_balance=10_000,
            train_size=4,
            test_size=2,
        )


def test_walk_forward_validates_window_arguments():
    data = make_data(10)

    with pytest.raises(ValueError, match="train_size must be positive"):
        WalkForwardRunner().run(data, 10_000, train_size=0, test_size=2)

    with pytest.raises(ValueError, match="test_size must be positive"):
        WalkForwardRunner().run(data, 10_000, train_size=2, test_size=0)

    with pytest.raises(ValueError, match="step_size must be positive"):
        WalkForwardRunner().run(
            data,
            10_000,
            train_size=2,
            test_size=2,
            step_size=0,
        )
