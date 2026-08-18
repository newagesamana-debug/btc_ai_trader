from dataclasses import dataclass
from enum import Enum


class SetupDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    NONE = "none"


class SetupType(str, Enum):
    BOS_CONTINUATION = "bos_continuation"
    CHOCH_REVERSAL = "choch_reversal"
    NONE = "none"


@dataclass(frozen=True)
class TradeSetup:
    direction: SetupDirection
    setup_type: SetupType

    entry: float | None

    stop_loss: float | None
    take_profit: float | None

    risk: float | None
    reward: float | None
    risk_reward: float | None

    confidence: float

    valid: bool