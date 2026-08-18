import pytest

from src.backtest.metrics import calculate_metrics
from src.backtest.models import BacktestResult, BacktestTrade
from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


def test_risk_adjusted_metrics():
    trades = (
        BacktestTrade(0, 1, SignalDirection.LONG, 100000, 106600, 1.0, 300.0, 100.0, ExitReason.TAKE_PROFIT, 1),
        BacktestTrade(2, 3, SignalDirection.LONG, 100000, 97800, 1.0, -100.0, 100.0, ExitReason.STOP_LOSS, 1),
        BacktestTrade(4, 5, SignalDirection.SHORT, 100000, 106600, 1.0, -100.0, 100.0, ExitReason.STOP_LOSS, 1),
        BacktestTrade(6, 7, SignalDirection.SHORT, 100000, 98000, 1.0, 200.0, 100.0, ExitReason.TAKE_PROFIT, 1),
    )
    result = BacktestResult(
        initial_balance=10000,
        final_balance=10300,
        total_pnl=300,
        return_pct=3.0,
        max_drawdown_pct=1.0,
        total_trades=4,
        winning_trades=2,
        losing_trades=2,
        win_rate_pct=50.0,
        trades=trades,
        equity_curve=(10000, 10300, 10200, 10100, 10300),
    )

    metrics = calculate_metrics(result)

    assert metrics.median_r == pytest.approx(0.5)
    # Sample standard deviation of R values [3, -1, -1, 2].
    assert metrics.r_stddev == pytest.approx(2.061552813, rel=1e-6)
    assert metrics.recovery_factor == pytest.approx(3.0)
    assert metrics.calmar_ratio == pytest.approx(3.0)
    assert metrics.sharpe_ratio == pytest.approx(0.741005418, rel=1e-6)
