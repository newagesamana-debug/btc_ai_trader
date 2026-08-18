import pandas as pd

from src.strategy.structure.models import (
    SwingPoint,
    SwingType,
)


class SwingDetector:

    def __init__(
        self,
        left_bars: int = 3,
        right_bars: int = 3,
    ):
        if left_bars < 1:
            raise ValueError(
                "left_bars must be >= 1"
            )

        if right_bars < 1:
            raise ValueError(
                "right_bars must be >= 1"
            )

        self.left_bars = left_bars
        self.right_bars = right_bars

    def detect(
        self,
        dataframe: pd.DataFrame,
    ) -> list[SwingPoint]:

        self._validate_dataframe(dataframe)

        highs = dataframe["high"].tolist()
        lows = dataframe["low"].tolist()
        timestamps = dataframe["timestamp"].tolist()

        swings = []

        start = self.left_bars
        end = (
            len(dataframe)
            - self.right_bars
        )

        for i in range(start, end):

            current_high = highs[i]
            current_low = lows[i]

            left_highs = highs[
                i - self.left_bars:i
            ]

            right_highs = highs[
                i + 1:i + 1 + self.right_bars
            ]

            left_lows = lows[
                i - self.left_bars:i
            ]

            right_lows = lows[
                i + 1:i + 1 + self.right_bars
            ]

            is_swing_high = (
                current_high > max(left_highs)
                and current_high > max(right_highs)
            )

            is_swing_low = (
                current_low < min(left_lows)
                and current_low < min(right_lows)
            )

            if is_swing_high:

                swings.append(
                    SwingPoint(
                        timestamp=timestamps[i],
                        price=current_high,
                        index=i,
                        type=SwingType.HIGH,
                        strength=self.right_bars,
                    )
                )

            if is_swing_low:

                swings.append(
                    SwingPoint(
                        timestamp=timestamps[i],
                        price=current_low,
                        index=i,
                        type=SwingType.LOW,
                        strength=self.right_bars,
                    )
                )

        return swings

    @staticmethod
    def _validate_dataframe(
        dataframe: pd.DataFrame,
    ) -> None:

        required = {
            "timestamp",
            "high",
            "low",
        }

        missing = required - set(
            dataframe.columns
        )

        if missing:
            raise ValueError(
                f"Missing columns: {missing}"
            )

        if dataframe.empty:
            raise ValueError(
                "Dataframe is empty"
            )