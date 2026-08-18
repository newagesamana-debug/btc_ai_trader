import pandas as pd
import pytest

from src.backtest.engine import BacktestEngine
from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


def create_row(
    close=100_000,
    high=None,
    low=None,
    bullish=True,
):
    if high is None:
        high = close + 500

    if low is None:
        low = close - 500

    if bullish:
        return {
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

    return {
        "h4_ema_20": 95,
        "h4_ema_50": 100,
        "h4_ema_200": 105,
        "h1_ema_20": 96,
        "h1_ema_50": 100,
        "h1_ema_200": 104,
        "h4_rsi": 40,
        "h1_rsi": 42,
        "h4_atr_pct": 1.5,
        "h1_atr_pct": 1.0,
        "m15_atr_pct": 0.6,
        "close": close,
        "high": high,
        "low": low,
        "atr": 1_000,
        "swing_low": 98_000,
        "swing_high": 102_000,
        "structure_label": "LL",
        "event_type": "BOS",
        "event_direction": "BEARISH",
    }


def make_data(*rows):
    return pd.DataFrame(rows)


def test_backtest_takes_long_profit():
    data = make_data(
        create_row(),
        create_row(
            close=101_000,
            high=106_700,
            low=100_500,
        ),
    )

    result = BacktestEngine().run(
        data=data,
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    assert result.total_trades == 1
    assert result.winning_trades == 1
    assert result.losing_trades == 0
    assert result.win_rate_pct == 100.0

    trade = result.trades[0]
    assert trade.direction == SignalDirection.LONG
    assert trade.reason == ExitReason.TAKE_PROFIT
    assert trade.pnl == pytest.approx(300.0)
    assert result.final_balance == pytest.approx(10_300.0)
    assert result.equity_curve == pytest.approx((10_000.0, 10_300.0))
    assert result.max_drawdown_pct == pytest.approx(0.0)


def test_backtest_takes_long_stop_loss():
    data = make_data(
        create_row(),
        create_row(
            close=99_000,
            high=100_000,
            low=97_700,
        ),
    )

    result = BacktestEngine().run(
        data=data,
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    assert result.total_trades == 1
    assert result.trades[0].reason == ExitReason.STOP_LOSS
    assert result.trades[0].pnl == pytest.approx(-100.0)
    assert result.final_balance == pytest.approx(9_900.0)
    assert result.equity_curve == pytest.approx((10_000.0, 9_900.0))
    assert result.max_drawdown_pct == pytest.approx(1.0)


def test_backtest_handles_short_stop_loss():
    data = make_data(
        create_row(bullish=False),
        create_row(
            close=101_000,
            high=102_300,
            low=100_500,
            bullish=False,
        ),
    )

    result = BacktestEngine().run(
        data=data,
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    assert result.total_trades == 1
    assert result.trades[0].direction == SignalDirection.SHORT
    assert result.trades[0].reason == ExitReason.STOP_LOSS
    assert result.trades[0].pnl == pytest.approx(-100.0)
    assert result.final_balance == pytest.approx(9_900.0)


def test_backtest_time_stop():
    data = make_data(
        create_row(),
        create_row(close=100_100, high=100_500, low=99_900),
        create_row(close=100_200, high=100_500, low=99_900),
    )

    result = BacktestEngine().run(
        data=data,
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
        max_candles=2,
    )

    assert result.total_trades == 1
    assert result.trades[0].reason == ExitReason.TIME_STOP
    assert result.trades[0].pnl == pytest.approx(0.0)
    assert result.final_balance == pytest.approx(10_000.0)


def test_backtest_closes_open_position_at_end_of_data():
    data = make_data(
        create_row(),
        create_row(close=101_000, high=101_500, low=100_500),
    )

    result = BacktestEngine().run(
        data=data,
        initial_balance=10_000,
        risk_percent=1.0,
        leverage=1.0,
    )

    assert result.total_trades == 1
    assert result.trades[0].reason == ExitReason.END_OF_DATA
    assert result.trades[0].exit_price == 101_000
    assert result.trades[0].pnl == pytest.approx(100 / 2200 * 1000)
    assert len(result.equity_curve) == 2
    assert result.equity_curve[0] == pytest.approx(10_000.0)
    assert result.equity_curve[-1] == pytest.approx(result.final_balance)


def test_empty_backtest_returns_initial_balance():
    result = BacktestEngine().run(
        data=pd.DataFrame(columns=["high", "low", "close"]),
        initial_balance=10_000,
    )

    assert result.final_balance == 10_000
    assert result.total_trades == 0
    assert result.return_pct == 0.0
    assert result.equity_curve == pytest.approx((10_000.0,))
