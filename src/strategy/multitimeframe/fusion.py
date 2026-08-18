from datetime import timedelta

import pandas as pd


class MultiTimeframeFeatureFusion:

    FEATURE_COLUMNS = [
        "ema_20",
        "ema_50",
        "ema_200",
        "rsi_14",
        "atr_pct",
        "volume_ratio",
    ]

    TIMEFRAME_DURATIONS = {
        "4h": timedelta(hours=4),
        "1h": timedelta(hours=1),
        "15m": timedelta(minutes=15),
        "5m": timedelta(minutes=5),
    }

    PREFIXES = {
        "4h": "h4",
        "1h": "h1",
        "15m": "m15",
        "5m": "m5",
    }

    def combine(
        self,
        base: pd.DataFrame,
        timeframes: dict[str, pd.DataFrame],
    ) -> pd.DataFrame:

        self._validate_base_dataframe(base)

        result = (
            base.copy()
            .sort_values("timestamp")
            .reset_index(drop=True)
        )

        for timeframe, dataframe in timeframes.items():

            self._validate_timeframe(
                timeframe,
                dataframe,
            )

            features = (
                dataframe[
                    [
                        "timestamp",
                        *self.FEATURE_COLUMNS,
                    ]
                ]
                .copy()
                .sort_values("timestamp")
                .reset_index(drop=True)
            )

            # The source timestamp represents candle OPEN time.
            #
            # Features become available only after
            # that candle has CLOSED.
            #
            # Example:
            #
            # 08:00 4H candle
            # 08:00 ---------------- 12:00
            #                                  ^
            #                             available
            #
            features["timestamp"] = (
                features["timestamp"]
                + self.TIMEFRAME_DURATIONS[timeframe]
            )

            prefix = self.PREFIXES[timeframe]

            rename_map = {
                column: f"{prefix}_{column}"
                for column in self.FEATURE_COLUMNS
            }

            features = features.rename(
                columns=rename_map
            )

            # Only allow the most recent CLOSED candle
            # of this timeframe.
            #
            # We intentionally use the timeframe duration
            # as tolerance instead of an arbitrary large
            # value such as 7 days.

            result = pd.merge_asof(
                result,
                features,
                on="timestamp",
                direction="backward",
                tolerance=self.TIMEFRAME_DURATIONS[
                    timeframe
                ],
            )

        return result

    @staticmethod
    def _validate_base_dataframe(
        dataframe: pd.DataFrame,
    ) -> None:

        required = {
            "timestamp",
        }

        missing = (
            required
            - set(dataframe.columns)
        )

        if missing:
            raise ValueError(
                f"Missing base columns: {missing}"
            )

        if dataframe.empty:
            raise ValueError(
                "Base dataframe is empty"
            )

    def _validate_timeframe(
        self,
        timeframe: str,
        dataframe: pd.DataFrame,
    ) -> None:

        if timeframe not in self.TIMEFRAME_DURATIONS:
            raise ValueError(
                f"Unsupported timeframe: {timeframe}"
            )

        required = {
            "timestamp",
            *self.FEATURE_COLUMNS,
        }

        missing = (
            required
            - set(dataframe.columns)
        )

        if missing:
            raise ValueError(
                f"Missing columns for {timeframe}: "
                f"{missing}"
            )

        if dataframe.empty:
            raise ValueError(
                f"{timeframe} dataframe is empty"
            )