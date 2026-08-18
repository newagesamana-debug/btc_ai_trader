from dataclasses import dataclass
from enum import Enum


class SignalDirection(str, Enum):
    LONG = "long"
    SHORT = "short"
    NONE = "none"


class SignalReason(str, Enum):
    TREND_CONTINUATION = "trend_continuation"
    BULLISH_CHOCH = "bullish_choch"
    BEARISH_CHOCH = "bearish_choch"
    BULLISH_BOS = "bullish_bos"
    BEARISH_BOS = "bearish_bos"
    NO_SETUP = "no_setup"


@dataclass(frozen=True)
class TradeSignal:
    direction: SignalDirection

    entry: float | None
    stop_loss: float | None
    take_profit: float | None

    risk_reward: float | None

    confidence: float

    reason: SignalReason

    valid: bool