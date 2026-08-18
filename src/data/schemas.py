from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float

    @property
    def is_valid(self) -> bool:
        return (
            self.open > 0
            and self.high > 0
            and self.low > 0
            and self.close > 0
            and self.volume >= 0
            and self.high >= max(self.open, self.close)
            and self.low <= min(self.open, self.close)
        )