from dataclasses import dataclass
import math

from src.backtest.models import BacktestResult
from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


@dataclass(frozen=True)
class BacktestMetrics:
    """Derived performance metrics for a backtest result."""

    profit_factor: float
    average_win: float
    average_loss: float
    expectancy: float
    largest_win: float
    largest_loss: float
    average_r: float
    max_consecutive_losses: int

    gross_profit: float = 0.0
    gross_loss: float = 0.0
    total_fees: float = 0.0
    total_slippage: float = 0.0
    payoff_ratio: float = 0.0
    max_consecutive_wins: int = 0
    total_trades: int = 0
    long_trades: int = 0
    short_trades: int = 0
    long_win_rate_pct: float = 0.0
    short_win_rate_pct: float = 0.0
    average_candles_held: float = 0.0
    stop_loss_trades: int = 0
    take_profit_trades: int = 0
    time_stop_trades: int = 0
    signal_exit_trades: int = 0
    end_of_data_trades: int = 0

    median_r: float = 0.0
    r_stddev: float = 0.0
    recovery_factor: float = 0.0
    sharpe_ratio: float = 0.0
    calmar_ratio: float = 0.0
    max_drawdown_duration: int = 0
    max_recovery_periods: int = 0


def _drawdown_duration_metrics(equity_curve: tuple[float, ...]) -> tuple[int, int]:
    """Return max underwater duration and max peak-to-recovery duration."""
    if len(equity_curve) < 2:
        return 0, 0

    peak = equity_curve[0]
    peak_index = 0
    trough_index = 0
    max_underwater_duration = 0
    max_recovery_periods = 0

    for index, equity in enumerate(equity_curve[1:], start=1):
        if equity >= peak:
            if trough_index > peak_index:
                max_underwater_duration = max(
                    max_underwater_duration,
                    index - trough_index,
                )
                max_recovery_periods = max(
                    max_recovery_periods,
                    index - peak_index,
                )
            peak = equity
            peak_index = index
            trough_index = index
        elif equity < peak and trough_index == peak_index:
            trough_index = index

    if trough_index > peak_index:
        max_underwater_duration = max(
            max_underwater_duration,
            len(equity_curve) - 1 - trough_index,
        )

    return max_underwater_duration, max_recovery_periods


def calculate_metrics(result: BacktestResult) -> BacktestMetrics:
    trades = result.trades
    wins = [trade.pnl for trade in trades if trade.pnl > 0]
    losses = [trade.pnl for trade in trades if trade.pnl < 0]

    gross_profit = sum(wins)
    gross_loss = abs(sum(losses))

    if gross_loss > 0:
        profit_factor = gross_profit / gross_loss
    elif gross_profit > 0:
        profit_factor = float("inf")
    else:
        profit_factor = 0.0

    average_win = gross_profit / len(wins) if wins else 0.0
    average_loss = sum(losses) / len(losses) if losses else 0.0

    total_trades = len(trades)
    expectancy = result.total_pnl / total_trades if total_trades else 0.0

    largest_win = max(wins, default=0.0)
    largest_loss = min(losses, default=0.0)

    if largest_win > 0 and largest_loss < 0:
        payoff_ratio = largest_win / abs(largest_loss)
    elif average_win > 0 and average_loss < 0:
        payoff_ratio = average_win / abs(average_loss)
    else:
        payoff_ratio = 0.0

    r_values = [
        trade.pnl / trade.risk_amount
        for trade in trades
        if trade.risk_amount > 0
    ]
    average_r = sum(r_values) / len(r_values) if r_values else 0.0

    median_r = 0.0
    r_stddev = 0.0
    if r_values:
        ordered_r = sorted(r_values)
        middle = len(ordered_r) // 2
        if len(ordered_r) % 2:
            median_r = ordered_r[middle]
        else:
            median_r = (ordered_r[middle - 1] + ordered_r[middle]) / 2.0
        if len(r_values) > 1:
            mean_r = average_r
            r_stddev = math.sqrt(
                sum((value - mean_r) ** 2 for value in r_values)
                / (len(r_values) - 1)
            )

    max_consecutive_losses = 0
    consecutive_losses = 0
    max_consecutive_wins = 0
    consecutive_wins = 0

    for trade in trades:
        if trade.pnl < 0:
            consecutive_losses += 1
            consecutive_wins = 0
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        elif trade.pnl > 0:
            consecutive_wins += 1
            consecutive_losses = 0
            max_consecutive_wins = max(max_consecutive_wins, consecutive_wins)
        else:
            consecutive_losses = 0
            consecutive_wins = 0

    long_trades = [trade for trade in trades if trade.direction == SignalDirection.LONG]
    short_trades = [trade for trade in trades if trade.direction == SignalDirection.SHORT]

    long_wins = sum(1 for trade in long_trades if trade.pnl > 0)
    short_wins = sum(1 for trade in short_trades if trade.pnl > 0)

    long_win_rate_pct = long_wins / len(long_trades) * 100.0 if long_trades else 0.0
    short_win_rate_pct = short_wins / len(short_trades) * 100.0 if short_trades else 0.0

    average_candles_held = (
        sum(trade.candles_held for trade in trades) / total_trades
        if total_trades else 0.0
    )

    exit_counts = {
        reason: sum(1 for trade in trades if trade.reason == reason)
        for reason in ExitReason
    }

    max_drawdown_pct = result.max_drawdown_pct
    recovery_factor = (
        result.total_pnl / (max_drawdown_pct / 100.0 * result.initial_balance)
        if max_drawdown_pct > 0
        else 0.0
    )

    returns = []
    curve = result.equity_curve
    if len(curve) > 1:
        for previous, current in zip(curve, curve[1:]):
            if previous > 0:
                returns.append((current - previous) / previous)

    sharpe_ratio = 0.0
    if len(returns) > 1:
        mean_return = sum(returns) / len(returns)
        variance = sum((value - mean_return) ** 2 for value in returns) / (len(returns) - 1)
        stddev = math.sqrt(variance)
        if stddev > 0:
            sharpe_ratio = mean_return / stddev * math.sqrt(len(returns))

    calmar_ratio = (
        result.return_pct / max_drawdown_pct
        if max_drawdown_pct > 0
        else 0.0
    )

    max_drawdown_duration, max_recovery_periods = _drawdown_duration_metrics(curve)

    return BacktestMetrics(
        profit_factor=profit_factor,
        average_win=average_win,
        average_loss=average_loss,
        expectancy=expectancy,
        largest_win=largest_win,
        largest_loss=largest_loss,
        average_r=average_r,
        max_consecutive_losses=max_consecutive_losses,
        gross_profit=gross_profit,
        gross_loss=gross_loss,
        total_fees=sum(trade.fees for trade in trades),
        total_slippage=sum(trade.slippage_cost for trade in trades),
        payoff_ratio=payoff_ratio,
        max_consecutive_wins=max_consecutive_wins,
        total_trades=total_trades,
        long_trades=len(long_trades),
        short_trades=len(short_trades),
        long_win_rate_pct=long_win_rate_pct,
        short_win_rate_pct=short_win_rate_pct,
        average_candles_held=average_candles_held,
        stop_loss_trades=exit_counts[ExitReason.STOP_LOSS],
        take_profit_trades=exit_counts[ExitReason.TAKE_PROFIT],
        time_stop_trades=exit_counts[ExitReason.TIME_STOP],
        signal_exit_trades=exit_counts[ExitReason.SIGNAL_EXIT],
        end_of_data_trades=exit_counts[ExitReason.END_OF_DATA],
        median_r=median_r,
        r_stddev=r_stddev,
        recovery_factor=recovery_factor,
        sharpe_ratio=sharpe_ratio,
        calmar_ratio=calmar_ratio,
        max_drawdown_duration=max_drawdown_duration,
        max_recovery_periods=max_recovery_periods,
    )
