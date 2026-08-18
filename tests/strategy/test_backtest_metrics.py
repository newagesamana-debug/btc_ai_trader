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
            gross_pnl=300.0,
            fees=5.0,
            slippage_cost=2.0,
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
            gross_pnl=-100.0,
            fees=4.0,
            slippage_cost=1.0,
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
            gross_pnl=-100.0,
            fees=3.0,
            slippage_cost=1.0,
        ),
        BacktestTrade(
            entry_index=6,
            exit_index=7,
            direction=SignalDirection.SHORT,
            entry_price=100_000,
            exit_price=98_000,
            position_size=1.0,
            pnl=200.0,
            risk_amount=100.0,
            reason=ExitReason.TAKE_PROFIT,
            candles_held=1,
            gross_pnl=200.0,
            fees=2.0,
            slippage_cost=1.0,
        ),
    )
    return BacktestResult(
        initial_balance=10_000,
        final_balance=10_300,
        total_pnl=300,
        return_pct=3.0,
        max_drawdown_pct=1.0,
        total_trades=4,
        winning_trades=2,
        losing_trades=2,
        win_rate_pct=50.0,
        trades=trades,
    )


def test_calculate_metrics():
    metrics = calculate_metrics(make_result())

    assert metrics.profit_factor == pytest.approx(2.5)
    assert metrics.average_win == pytest.approx(250.0)
    assert metrics.average_loss == pytest.approx(-100.0)
    assert metrics.expectancy == pytest.approx(75.0)
    assert metrics.largest_win == pytest.approx(300.0)
    assert metrics.largest_loss == pytest.approx(-100.0)
    assert metrics.average_r == pytest.approx(0.75)
    assert metrics.max_consecutive_losses == 2
    assert metrics.max_consecutive_wins == 1


def test_calculate_cost_and_direction_metrics():
    metrics = calculate_metrics(make_result())

    assert metrics.gross_profit == pytest.approx(500.0)
    assert metrics.gross_loss == pytest.approx(200.0)
    assert metrics.total_fees == pytest.approx(14.0)
    assert metrics.total_slippage == pytest.approx(5.0)
    assert metrics.payoff_ratio == pytest.approx(3.0)

    assert metrics.long_trades == 2
    assert metrics.short_trades == 2
    assert metrics.long_win_rate_pct == pytest.approx(50.0)
    assert metrics.short_win_rate_pct == pytest.approx(50.0)


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
    assert metrics.max_consecutive_wins == 0
    assert metrics.total_fees == 0.0
    assert metrics.total_slippage == 0.0
    assert metrics.long_trades == 0
    assert metrics.short_trades == 0
