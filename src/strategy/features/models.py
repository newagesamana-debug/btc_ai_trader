from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TechnicalFeatures:
    timestamp: datetime

    ema_20: float | None
    ema_50: float | None
    ema_200: float | None

    rsi_14: float | None

    atr_14: float | None
    atr_pct: float | None

    roc_10: float | None

    volume_ma_20: float | None
    volume_ratio: float | None