import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.data.exchange import ExchangeClient
from src.data.validator import (
    find_gaps,
    timestamp_to_datetime,
)


class HistoricalDataDownloader:

    def __init__(
        self,
        exchange: ExchangeClient,
        output_directory: str = "data/raw",
        batch_size: int = 1000,
        request_delay: float = 0.1,
    ):
        self.exchange = exchange
        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.batch_size = batch_size
        self.request_delay = request_delay

    def download(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime | None = None,
    ) -> pd.DataFrame:

        if start.tzinfo is None:
            raise ValueError(
                "Start datetime must be timezone-aware"
            )

        if end is not None and end.tzinfo is None:
            raise ValueError(
                "End datetime must be timezone-aware"
            )

        since = int(start.timestamp() * 1000)

        end_timestamp = (
            int(end.timestamp() * 1000)
            if end
            else None
        )

        all_rows = []

        while True:

            rows = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                since=since,
                limit=self.batch_size,
            )

            if not rows:
                break

            all_rows.extend(rows)

            last_timestamp = rows[-1][0]

            print(
                f"Downloaded {len(all_rows)} candles | "
                f"last={timestamp_to_datetime(last_timestamp)}"
            )

            if end_timestamp is not None:
                if last_timestamp >= end_timestamp:
                    break

            next_since = last_timestamp + 1

            if next_since <= since:
                raise RuntimeError(
                    "Pagination did not advance"
                )

            since = next_since

            time.sleep(self.request_delay)

            if len(rows) < self.batch_size:
                break

        if not all_rows:
            raise RuntimeError(
                "No historical data received"
            )

        dataframe = pd.DataFrame(
            all_rows,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ],
        )

        dataframe["timestamp"] = dataframe[
            "timestamp"
        ].apply(timestamp_to_datetime)

        numeric_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]

        dataframe[numeric_columns] = (
            dataframe[numeric_columns].astype(float)
        )

        dataframe = (
            dataframe
            .drop_duplicates(subset=["timestamp"])
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        if end is not None:
            dataframe = dataframe[
                dataframe["timestamp"] < end
                ]

        gaps = find_gaps(
            dataframe["timestamp"].tolist(),
            timeframe,
        )

        if gaps:
            print()
            print(
                f"WARNING: detected {len(gaps)} gaps"
            )

            for previous, current in gaps[:10]:
                print(
                    f"  {previous} -> {current}"
                )

        filename = (
            f"{symbol.replace('/', '_').replace(':', '_')}_"
            f"{timeframe}.parquet"
        )

        output_path = (
            self.output_directory / filename
        )

        dataframe.to_parquet(
            output_path,
            index=False,
        )

        print()
        print(f"Saved: {output_path}")
        print(f"Rows: {len(dataframe)}")

        return dataframe