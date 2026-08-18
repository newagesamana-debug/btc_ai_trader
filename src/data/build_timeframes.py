from pathlib import Path

import pandas as pd

from src.config.loader import load_settings
from src.data.aggregator import TimeframeAggregator


TIMEFRAMES = [
    "5m",
    "15m",
    "1h",
    "4h",
]


def main():

    settings = load_settings()

    symbol = settings["market"]["symbol"]

    raw_path = Path(
        settings["data"]["raw_path"]
    ) / "BTC_USDT_USDT_1m.parquet"

    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw data not found: {raw_path}"
        )

    dataframe = pd.read_parquet(
        raw_path
    )

    aggregator = TimeframeAggregator(
        settings["data"]["processed_path"]
    )

    print("=" * 60)
    print("TIMEFRAME AGGREGATION")
    print("=" * 60)

    print(
        f"Input candles: {len(dataframe)}"
    )

    print()

    for timeframe in TIMEFRAMES:

        result = aggregator.aggregate(
            dataframe,
            timeframe,
        )

        path = aggregator.save(
            result,
            symbol,
            timeframe,
        )

        print(
            f"{timeframe}: "
            f"{len(result)} candles → {path}"
        )

    print("=" * 60)
    print("AGGREGATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()