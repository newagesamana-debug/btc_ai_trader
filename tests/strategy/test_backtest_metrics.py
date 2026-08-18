import pytest

from src.backtest.metrics import calculate_metrics
from src.backtest.models import BacktestResult, BacktestTrade
from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


def make_result():
    trades = (
        BacktestTrade(
            entry_index=0,
            exit_index=1,
            direction=SignalDirection.LONG,
            entry_price=100_000,
            exit_price=106_600,
            position_size=1.0,
            pnl=300.0,
            risk_amount=100.0,
            reason=ExitReason.TAKE_PROFIT,
            candles_held=1,
        ),
        BacktestTrade(
            entry_index=2,
            exit_index=3,
            direction=SignalDirection.LONG,
            entry_price=100_000,
            exit_price=97_800,
            position_size=1.0,
            pnl=-100.0,
            risk_amount=100.0,
            reason=ExitReason.STOP_LOSS,
            candles_held=1,
        ),
        BacktestTrade(
            entry_index=4,
            exit_index=5,
            direction=SignalDirection.SHORT,
            entry_price=100_000,
            exit_price=106_600,
            position_size=1.0,
            pnl=-100.0,
            risk_amount=100.0,
            reason=ExitReason.STOP_LOSS,
            candles_held=1,
        ),
    )
    return BacktestResult(
        initial_balance=10_000,
        final_balance=10_100,
        total_pnl=100,
        return_pct=1.0,
        max_drawdown_pct=1.0,
        total_trades=3,
        winning_trades=1,
        losing_trades=2,
        win_rate_pct=100 / 3,
        trades=trades,
    )


def test_calculate_metrics():
    metrics = calculate_metrics(make_result())

    assert metrics.profit_factor == pytest.approx(1.5)
    assert metrics.average_win == pytest.approx(300.0)
    assert metrics.average_loss == pytest.approx(-100.0)
    assert metrics.expectancy == pytest.approx(100 / 3)
    assert metrics.largest_win == pytest.approx(300.0)
    assert metrics.largest_loss == pytest.approx(-100.0)
    assert metrics.average_r == pytest.approx(1 / 3)
    assert metrics.max_consecutive_losses == 2


def test_empty_metrics_are_zero():
    result = BacktestResult(
        initial_balance=10_000,
        final_balance=10_000,
        total_pnl=0.0,
        return_pct=0.0,
        max_drawdown_pct=0.0,
        total_trades=0,
        winning_trades=0,
        losing_trades=0,
        win_rate_pct=0.0,
        trades=(),
    )

    metrics = calculate_metrics(result)

    assert metrics.profit_factor == 0.0
    assert metrics.expectancy == 0.0
    assert metrics.average_r == 0.0
    assert metrics.max_consecutive_losses == 0
