from dataclasses import dataclass
from enum import Enum


class ExitReason(str, Enum):
    STOP_LOSS = "stop_loss"
    TAKE_PROFIT = "take_profit"
    TIME_STOP = "time_stop"
    SIGNAL_EXIT = "signal_exit"
    END_OF_DATA = "end_of_data"
    NONE = "none"


@dataclass(frozen=True)
class ExitDecision:
    should_exit: bool
    reason: ExitReason
    exit_price: float | None
    pnl_per_unit: float | None
    candles_held: int
