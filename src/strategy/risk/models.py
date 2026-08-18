from dataclasses import dataclass

from src.strategy.signal.models import SignalDirection


@dataclass(frozen=True)
class PositionPlan:
    direction: SignalDirection

    entry: float | None
    stop_loss: float | None
    take_profit: float | None

    account_balance: float

    risk_percent: float
    risk_amount: float

    position_size: float
    notional_value: float

    leverage: float

    max_loss: float
    potential_profit: float

    risk_reward: float | None

    valid: bool