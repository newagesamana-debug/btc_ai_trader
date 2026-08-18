from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class SwingType(str, Enum):
    HIGH = "HIGH"
    LOW = "LOW"


class StructureLabel(str, Enum):
    HH = "HH"
    HL = "HL"
    LH = "LH"
    LL = "LL"


class StructureEventType(str, Enum):
    BOS = "BOS"
    CHOCH = "CHOCH"


class MarketDirection(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"


@dataclass(frozen=True)
class SwingPoint:
    timestamp: datetime
    price: float
    index: int
    type: SwingType
    strength: int


@dataclass(frozen=True)
class ClassifiedSwing:
    swing: SwingPoint
    label: StructureLabel


@dataclass(frozen=True)
class StructureEvent:
    timestamp: datetime
    event_type: StructureEventType
    direction: MarketDirection
    broken_level: float
    break_price: float
    swing_index: int
    candle_index: int