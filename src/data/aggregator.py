from pathlib import Path

import pandas as pd


TIMEFRAME_RULES = {
    "5m": "5min",
    "15m": "15min",
    "1h": "1h",
    "4h": "4h",
}


REQUIRED_COLUMNS = [
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


class TimeframeAggregator:

    def __init__(self, output_directory: str = "data/processed"):
        self.output_directory = Path(output_directory)

        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def aggregate(
        self,
        dataframe: pd.DataFrame,
        timeframe: str,
    ) -> pd.DataFrame:

        if timeframe not in TIMEFRAME_RULES:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        self._validate_input(dataframe)

        df = dataframe.copy()

        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            utc=True,
        )

        df = (
            df
            .sort_values("timestamp")
            .drop_duplicates("timestamp")
            .set_index("timestamp")
        )

        rule = TIMEFRAME_RULES[timeframe]

        aggregated = (
            df.resample(
                rule,
                label="left",
                closed="left",
            )
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
        )

        aggregated = aggregated.dropna()

        aggregated = aggregated.reset_index()

        self._validate_output(
            aggregated,
            timeframe,
        )

        return aggregated

    def save(
        self,
        dataframe: pd.DataFrame,
        symbol: str,
        timeframe: str,
    ) -> Path:

        filename = (
            f"{symbol.replace('/', '_').replace(':', '_')}_"
            f"{timeframe}.parquet"
        )

        path = self.output_directory / filename

        dataframe.to_parquet(
            path,
            index=False,
        )

        return path

    @staticmethod
    def _validate_input(
        dataframe: pd.DataFrame,
    ) -> None:

        missing = [
            column
            for column in REQUIRED_COLUMNS
            if column not in dataframe.columns
        ]

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        if dataframe.empty:
            raise ValueError(
                "Input dataframe is empty"
            )

    @staticmethod
    def _validate_output(
        dataframe: pd.DataFrame,
        timeframe: str,
    ) -> None:

        if dataframe.empty:
            raise ValueError(
                f"Aggregation produced no data for {timeframe}"
            )

        if dataframe[
            "timestamp"
        ].duplicated().any():

            raise ValueError(
                f"Duplicate timestamps in {timeframe}"
            )

        invalid_ohlc = (
            (dataframe["high"] < dataframe["open"])
            | (dataframe["high"] < dataframe["close"])
            | (dataframe["low"] > dataframe["open"])
            | (dataframe["low"] > dataframe["close"])
        )

        if invalid_ohlc.any():
            raise ValueError(
                f"Invalid OHLC data in {timeframe}"
            )