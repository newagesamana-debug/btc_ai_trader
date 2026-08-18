from datetime import datetime, timedelta, timezone

from src.data.schemas import Candle


TIMEFRAME_MINUTES = {
    "1m": 1,
    "5m": 5,
    "15m": 15,
    "1h": 60,
    "4h": 240,
}


def validate_candle(candle: Candle) -> None:
    if not candle.is_valid:
        raise ValueError(f"Invalid candle: {candle}")


def validate_candles(candles: list[Candle]) -> None:
    if not candles:
        raise ValueError("Candle list is empty")

    previous_timestamp = None

    for candle in candles:
        validate_candle(candle)

        if previous_timestamp is not None:
            if candle.timestamp <= previous_timestamp:
                raise ValueError(
                    "Candles are not strictly chronological"
                )

        previous_timestamp = candle.timestamp


def timestamp_to_datetime(timestamp_ms: int) -> datetime:
    return datetime.fromtimestamp(
        timestamp_ms / 1000,
        tz=timezone.utc,
    )


def find_gaps(
    timestamps: list[datetime],
    timeframe: str,
) -> list[tuple[datetime, datetime]]:

    if timeframe not in TIMEFRAME_MINUTES:
        raise ValueError(
            f"Unsupported timeframe: {timeframe}"
        )

    if len(timestamps) < 2:
        return []

    interval = timedelta(
        minutes=TIMEFRAME_MINUTES[timeframe]
    )

    gaps = []

    for previous, current in zip(
        timestamps,
        timestamps[1:],
    ):
        expected = previous + interval

        if current != expected:
            gaps.append((previous, current))

    return gaps