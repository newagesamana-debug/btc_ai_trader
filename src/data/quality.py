from dataclasses import dataclass
from datetime import datetime, timedelta

import pandas as pd


TIMEFRAME_MINUTES = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
}


@dataclass
class QualityReport:
    timeframe: str
    total_candles: int
    duplicate_count: int
    gap_count: int
    invalid_ohlc_count: int
    zero_volume_count: int
    future_candle_count: int
    first_timestamp: datetime | None
    last_timestamp: datetime | None

    @property
    def is_valid(self) -> bool:
        return (
            self.duplicate_count == 0
            and self.invalid_ohlc_count == 0
            and self.future_candle_count == 0
        )


class DataQualityChecker:

    def check(
        self,
        dataframe: pd.DataFrame,
        timeframe: str,
        now: datetime | None = None,
    ) -> QualityReport:

        if timeframe not in TIMEFRAME_MINUTES:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        required_columns = {
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
        }

        missing = required_columns - set(
            dataframe.columns
        )

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        if dataframe.empty:
            raise ValueError(
                "Cannot validate empty dataframe"
            )

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
        )

        df = df.sort_values(
            "timestamp"
        ).reset_index(drop=True)

        duplicate_count = int(
            df["timestamp"].duplicated().sum()
        )

        invalid_ohlc_count = int(
            (
                (df["high"] < df["open"])
                | (df["high"] < df["close"])
                | (df["low"] > df["open"])
                | (df["low"] > df["close"])
                | (df["open"] <= 0)
                | (df["high"] <= 0)
                | (df["low"] <= 0)
                | (df["close"] <= 0)
            ).sum()
        )

        zero_volume_count = int(
            (df["volume"] <= 0).sum()
        )

        interval = timedelta(
            minutes=TIMEFRAME_MINUTES[timeframe]
        )

        timestamps = df["timestamp"].tolist()

        gap_count = 0

        for previous, current in zip(
            timestamps,
            timestamps[1:],
        ):
            if current - previous != interval:
                gap_count += 1

        if now is None:
            now = datetime.now(
                df["timestamp"].iloc[0].tzinfo
            )

        future_candle_count = int(
            (df["timestamp"] > now).sum()
        )

        return QualityReport(
            timeframe=timeframe,
            total_candles=len(df),
            duplicate_count=duplicate_count,
            gap_count=gap_count,
            invalid_ohlc_count=invalid_ohlc_count,
            zero_volume_count=zero_volume_count,
            future_candle_count=future_candle_count,
            first_timestamp=df["timestamp"].iloc[0],
            last_timestamp=df["timestamp"].iloc[-1],
        )