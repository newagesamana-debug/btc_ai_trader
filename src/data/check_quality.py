from pathlib import Path

import pandas as pd

from src.config.loader import load_settings
from src.data.quality import DataQualityChecker


TIMEFRAMES = [
    "1m",
    "5m",
    "15m",
    "1h",
    "4h",
]


def main():

    settings = load_settings()

    symbol = settings["market"]["symbol"]

    checker = DataQualityChecker()

    print("=" * 70)
    print("DATA QUALITY REPORT")
    print("=" * 70)

    for timeframe in TIMEFRAMES:

        if timeframe == "1m":
            directory = Path(
                settings["data"]["raw_path"]
            )
        else:
            directory = Path(
                settings["data"]["processed_path"]
            )

        filename = (
            f"{symbol.replace('/', '_').replace(':', '_')}_"
            f"{timeframe}.parquet"
        )

        path = directory / filename

        if not path.exists():
            print(
                f"{timeframe}: FILE NOT FOUND"
            )
            continue

        dataframe = pd.read_parquet(path)

        report = checker.check(
            dataframe,
            timeframe,
        )

        print()
        print(f"TIMEFRAME: {timeframe}")
        print(f"Candles: {report.total_candles}")
        print(f"Duplicates: {report.duplicate_count}")
        print(f"Gaps: {report.gap_count}")
        print(
            f"Invalid OHLC: "
            f"{report.invalid_ohlc_count}"
        )
        print(
            f"Zero volume: "
            f"{report.zero_volume_count}"
        )
        print(
            f"Future candles: "
            f"{report.future_candle_count}"
        )
        print(
            f"Range: "
            f"{report.first_timestamp} → "
            f"{report.last_timestamp}"
        )
        print(
            f"VALID: {report.is_valid}"
        )

    print()
    print("=" * 70)


if __name__ == "__main__":
    main()