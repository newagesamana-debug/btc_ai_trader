import pytest

from src.backtest.models import BacktestResult, BacktestTrade
from src.backtest.monte_carlo import run_monte_carlo
from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


def make_result() -> BacktestResult:
    trades = (
        BacktestTrade(0, 1, SignalDirection.LONG, 100_000, 106_600, 1.0, 300.0, 100.0, ExitReason.TAKE_PROFIT, 1),
        BacktestTrade(2, 3, SignalDirection.LONG, 100_000, 97_800, 1.0, -100.0, 100.0, ExitReason.STOP_LOSS, 1),
        BacktestTrade(4, 5, SignalDirection.SHORT, 100_000, 106_600, 1.0, -100.0, 100.0, ExitReason.STOP_LOSS, 1),
        BacktestTrade(6, 7, SignalDirection.SHORT, 100_000, 98_000, 1.0, 200.0, 100.0, ExitReason.TAKE_PROFIT, 1),
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


def test_monte_carlo_is_deterministic_with_seed():
    first = run_monte_carlo(make_result(), simulations=500, seed=42)
    second = run_monte_carlo(make_result(), simulations=500, seed=42)

    assert first == second
    assert first.p05_final_balance <= first.median_final_balance <= first.p95_final_balance
    assert 0.0 <= first.probability_of_loss_pct <= 100.0
    assert 0.0 <= first.probability_of_ruin_pct <= 100.0


def test_monte_carlo_empty_result():
    result = BacktestResult(
        initial_balance=10_000,
        final_balance=10_000,
        total_pnl=0,
        return_pct=0,
        max_drawdown_pct=0,
        total_trades=0,
        winning_trades=0,
        losing_trades=0,
        win_rate_pct=0,
        trades=(),
    )

    metrics = run_monte_carlo(result, simulations=10)

    assert metrics.median_final_balance == 10_000
    assert metrics.p05_final_balance == 10_000
    assert metrics.p95_final_balance == 10_000
    assert metrics.probability_of_loss_pct == 0
    assert metrics.probability_of_ruin_pct == 0


def test_monte_carlo_validates_arguments():
    with pytest.raises(ValueError):
        run_monte_carlo(make_result(), simulations=0)

    with pytest.raises(ValueError):
        run_monte_carlo(make_result(), ruin_threshold_pct=100)
