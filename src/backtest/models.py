from dataclasses import dataclass

from src.strategy.exit.models import ExitReason
from src.strategy.signal.models import SignalDirection


@dataclass(frozen=True)
class BacktestTrade:
    entry_index: int
    exit_index: int

    direction: SignalDirection

    entry_price: float
    exit_price: float
    position_size: float

    pnl: float
    risk_amount: float
    reason: ExitReason
    candles_held: int

    gross_pnl: float = 0.0
    fees: float = 0.0
    slippage_cost: float = 0.0


@dataclass(frozen=True)
class BacktestResult:
    initial_balance: float
    final_balance: float

    total_pnl: float
    return_pct: float
    max_drawdown_pct: float

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float

    trades: tuple[BacktestTrade, ...]
