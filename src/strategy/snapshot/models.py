from dataclasses import dataclass
from datetime import datetime

from src.strategy.regime.models import (
    MarketRegime,
)


@dataclass(frozen=True)
class PriceState:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class StructureState:
    last_swing_high: float | None
    last_swing_low: float | None

    last_structure_label: str | None

    last_event_type: str | None
    last_event_direction: str | None


@dataclass(frozen=True)
class SnapshotTechnicalState:
    h4_rsi: float | None
    h4_atr_pct: float | None

    h1_rsi: float | None
    h1_atr_pct: float | None

    m15_rsi: float | None
    m15_atr_pct: float | None

    m5_rsi: float | None
    m5_atr_pct: float | None

    m5_volume_ratio: float | None


@dataclass(frozen=True)
class MarketSnapshot:

    timestamp: datetime

    price: PriceState

    structure: StructureState

    technical: SnapshotTechnicalState

    regime: MarketRegime

    regime_confidence: float