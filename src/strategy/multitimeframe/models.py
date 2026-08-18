from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MultiTimeframeFeatures:
    timestamp: datetime

    # 4H
    h4_ema_20: float | None
    h4_ema_50: float | None
    h4_ema_200: float | None
    h4_rsi: float | None
    h4_atr_pct: float | None

    # 1H
    h1_ema_20: float | None
    h1_ema_50: float | None
    h1_ema_200: float | None
    h1_rsi: float | None
    h1_atr_pct: float | None

    # 15M
    m15_ema_20: float | None
    m15_ema_50: float | None
    m15_rsi: float | None
    m15_atr_pct: float | None

    # 5M
    m5_ema_20: float | None
    m5_ema_50: float | None
    m5_rsi: float | None
    m5_atr_pct: float | None
    m5_volume_ratio: float | None