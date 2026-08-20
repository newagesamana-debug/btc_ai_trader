from src.backtest.metrics import calculate_metrics
from src.backtest.models import BacktestResult


def make_result(equity_curve):
    return BacktestResult(
        initial_balance=10_000,
        final_balance=equity_curve[-1],
        total_pnl=equity_curve[-1] - equity_curve[0],
        return_pct=(equity_curve[-1] - equity_curve[0]) / equity_curve[0] * 100.0,
        max_drawdown_pct=0.0,
        total_trades=0,
        winning_trades=0,
        losing_trades=0,
        win_rate_pct=0.0,
        trades=(),
        equity_curve=tuple(equity_curve),
    )


def test_drawdown_duration_and_recovery_periods():
    result = make_result((10_000, 10_300, 10_200, 10_100, 10_300))

    metrics = calculate_metrics(result)

    assert metrics.max_drawdown_duration == 2
    assert metrics.max_recovery_periods == 3


def test_open_drawdown_is_measured_until_end_of_backtest():
    result = make_result((10_000, 10_500, 10_300, 10_100))

    metrics = calculate_metrics(result)

    assert metrics.max_drawdown_duration == 1
    assert metrics.max_recovery_periods == 0


def test_no_drawdown_has_zero_duration_and_recovery():
    result = make_result((10_000, 10_100, 10_200, 10_300))

    metrics = calculate_metrics(result)

    assert metrics.max_drawdown_duration == 0
    assert metrics.max_recovery_periods == 0
