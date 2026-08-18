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

    total_trades = len(trades)
    expectancy = result.total_pnl / total_trades if total_trades else 0.0

    largest_win = max(wins, default=0.0)
    largest_loss = min(losses, default=0.0)

    risk_units = []
    for trade in trades:
        if trade.direction.value == "long":
            risk_distance = trade.entry_price - trade.exit_price
        else:
            risk_distance = trade.exit_price - trade.entry_price

        if trade.position_size > 0:
            risk_units.append(trade.pnl / (abs(risk_distance) * trade.position_size))

    average_r = sum(risk_units) / len(risk_units) if risk_units else 0.0

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
