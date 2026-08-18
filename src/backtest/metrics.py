from dataclasses import dataclass

from src.backtest.models import BacktestResult


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
    expectancy = result.total_pnl / len(trades) if trades else 0.0
    largest_win = max(wins, default=0.0)
    largest_loss = min(losses, default=0.0)

    r_values = [
        trade.pnl / trade.risk_amount
        for trade in trades
        if trade.risk_amount > 0
    ]
    average_r = sum(r_values) / len(r_values) if r_values else 0.0

    max_consecutive_losses = 0
    consecutive_losses = 0
    for trade in trades:
        if trade.pnl < 0:
            consecutive_losses += 1
            max_consecutive_losses = max(max_consecutive_losses, consecutive_losses)
        else:
            consecutive_losses = 0

    return BacktestMetrics(
        profit_factor=profit_factor,
        average_win=average_win,
        average_loss=average_loss,
        expectancy=expectancy,
        largest_win=largest_win,
        largest_loss=largest_loss,
        average_r=average_r,
        max_consecutive_losses=max_consecutive_losses,
    )
