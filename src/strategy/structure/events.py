import pandas as pd

from src.strategy.structure.models import (
    ClassifiedSwing,
    MarketDirection,
    StructureEvent,
    StructureEventType,
    StructureLabel,
    SwingType,
)


class StructureEventDetector:

    def detect(
        self,
        dataframe: pd.DataFrame,
        classified_swings: list[ClassifiedSwing],
    ) -> list[StructureEvent]:

        self._validate_dataframe(dataframe)

        if not classified_swings:
            return []

        swings = sorted(
            classified_swings,
            key=lambda item: item.swing.index,
        )

        events: list[StructureEvent] = []

        broken_high_indices: set[int] = set()
        broken_low_indices: set[int] = set()

        current_direction: MarketDirection | None = None

        for candle_index in range(len(dataframe)):

            close = float(
                dataframe.iloc[candle_index]["close"]
            )

            eligible_swings = [
                item
                for item in swings
                if item.swing.index < candle_index
            ]

            if not eligible_swings:
                continue

            # --------------------------------------------------
            # Most recent eligible HIGH
            # --------------------------------------------------

            high_candidates = [
                item
                for item in eligible_swings
                if item.swing.type == SwingType.HIGH
                and item.swing.index
                not in broken_high_indices
            ]

            if high_candidates:

                high = high_candidates[-1]

                if (
                    high.label
                    in (
                        StructureLabel.HH,
                        StructureLabel.LH,
                    )
                    and close > high.swing.price
                ):

                    if high.label == StructureLabel.HH:
                        event_type = (
                            StructureEventType.BOS
                        )
                    else:
                        event_type = (
                            StructureEventType.CHOCH
                        )

                    direction = (
                        MarketDirection.BULLISH
                    )

                    events.append(
                        StructureEvent(
                            timestamp=dataframe.iloc[
                                candle_index
                            ]["timestamp"],
                            event_type=event_type,
                            direction=direction,
                            broken_level=high.swing.price,
                            break_price=close,
                            swing_index=high.swing.index,
                            candle_index=candle_index,
                        )
                    )

                    broken_high_indices.add(
                        high.swing.index
                    )

                    current_direction = direction

            # --------------------------------------------------
            # Most recent eligible LOW
            # --------------------------------------------------

            low_candidates = [
                item
                for item in eligible_swings
                if item.swing.type == SwingType.LOW
                and item.swing.index
                not in broken_low_indices
            ]

            if low_candidates:

                low = low_candidates[-1]

                if (
                    low.label
                    in (
                        StructureLabel.HL,
                        StructureLabel.LL,
                    )
                    and close < low.swing.price
                ):

                    if low.label == StructureLabel.LL:
                        event_type = (
                            StructureEventType.BOS
                        )
                    else:
                        event_type = (
                            StructureEventType.CHOCH
                        )

                    direction = (
                        MarketDirection.BEARISH
                    )

                    events.append(
                        StructureEvent(
                            timestamp=dataframe.iloc[
                                candle_index
                            ]["timestamp"],
                            event_type=event_type,
                            direction=direction,
                            broken_level=low.swing.price,
                            break_price=close,
                            swing_index=low.swing.index,
                            candle_index=candle_index,
                        )
                    )

                    broken_low_indices.add(
                        low.swing.index
                    )

                    current_direction = direction

        events.sort(
            key=lambda event: (
                event.candle_index,
                event.swing_index,
            )
        )

        return events

    @staticmethod
    def _validate_dataframe(
        dataframe: pd.DataFrame,
    ) -> None:

        required = {
            "timestamp",
            "close",
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