import pytest

from src.backtest.metrics import calculate_metrics
from src.backtest.models import BacktestResult, BacktestTrade
from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


def make_result():
    trades = (
        BacktestTrade(0, 1, SignalDirection.LONG, 100_000, 106_600, 1.0, 300.0, 100.0, ExitReason.TAKE_PROFIT, 1),
        BacktestTrade(2, 3, SignalDirection.LONG, 100_000, 97_800, 1.0, -100.0, 100.0, ExitReason.STOP_LOSS, 2),
        BacktestTrade(4, 5, SignalDirection.SHORT, 100_000, 106_600, 1.0, -100.0, 100.0, ExitReason.STOP_LOSS, 3),
        BacktestTrade(6, 7, SignalDirection.SHORT, 100_000, 98_000, 1.0, 200.0, 100.0, ExitReason.TAKE_PROFIT, 2),
    )
    return BacktestResult(
        initial_balance=10_000,
        final_balance=10_300,
        total_pnl=300.0,
        return_pct=3.0,
        max_drawdown_pct=1.0,
        total_trades=4,
        winning_trades=2,
        losing_trades=2,
        win_rate_pct=50.0,
        trades=trades,
    )


def test_exit_reason_and_holding_metrics():
    metrics = calculate_metrics(make_result())

    assert metrics.average_candles_held == pytest.approx(2.0)
    assert metrics.stop_loss_trades == 2
    assert metrics.take_profit_trades == 2
    assert metrics.time_stop_trades == 0
    assert metrics.signal_exit_trades == 0
    assert metrics.end_of_data_trades == 0
