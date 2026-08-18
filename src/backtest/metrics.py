from dataclasses import dataclass

from src.backtest.models import BacktestResult
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
    long_trades: int = 0
    short_trades: int = 0
    long_win_rate_pct: float = 0.0
    short_win_rate_pct: float = 0.0


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

    max_consecutive_losses = 0
    consecutive_losses = 0
    max_consecutive_wins = 0
    consecutive_wins = 0

    for trade in trades:
        if trade.pnl < 0:
            consecutive_losses += 1
            consecutive_wins = 0
            max_consecutive_losses = max(
                max_consecutive_losses,
                consecutive_losses,
            )
        elif trade.pnl > 0:
            consecutive_wins += 1
            consecutive_losses = 0
            max_consecutive_wins = max(
                max_consecutive_wins,
                consecutive_wins,
            )
        else:
            consecutive_losses = 0
            consecutive_wins = 0

    long_trades = [
        trade for trade in trades
        if trade.direction == SignalDirection.LONG
    ]
    short_trades = [
        trade for trade in trades
        if trade.direction == SignalDirection.SHORT
    ]

    long_wins = sum(1 for trade in long_trades if trade.pnl > 0)
    short_wins = sum(1 for trade in short_trades if trade.pnl > 0)

    long_win_rate_pct = (
        long_wins / len(long_trades) * 100.0
        if long_trades
        else 0.0
    )
    short_win_rate_pct = (
        short_wins / len(short_trades) * 100.0
        if short_trades
        else 0.0
    )

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
        long_trades=len(long_trades),
        short_trades=len(short_trades),
        long_win_rate_pct=long_win_rate_pct,
        short_win_rate_pct=short_win_rate_pct,
    )
