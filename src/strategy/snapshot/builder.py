from src.strategy.regime.models import (
    MarketRegime,
)

from src.strategy.snapshot.models import (
    MarketSnapshot,
    PriceState,
    SnapshotTechnicalState,
    StructureState,
)


class MarketSnapshotBuilder:

    def build(
        self,
        row,
        regime: MarketRegime,
        regime_confidence: float,
        last_swing_high: float | None,
        last_swing_low: float | None,
        last_structure_label: str | None,
        last_event_type: str | None,
        last_event_direction: str | None,
    ) -> MarketSnapshot:

        price = PriceState(
            timestamp=row["timestamp"],
            open=float(row["open"]),
            high=float(row["high"]),
            low=float(row["low"]),
            close=float(row["close"]),
            volume=float(row["volume"]),
        )

        structure = StructureState(
            last_swing_high=last_swing_high,
            last_swing_low=last_swing_low,
            last_structure_label=last_structure_label,
            last_event_type=last_event_type,
            last_event_direction=last_event_direction,
        )

        technical = SnapshotTechnicalState(
            h4_rsi=self._value(
                row,
                "h4_rsi",
            ),
            h4_atr_pct=self._value(
                row,
                "h4_atr_pct",
            ),
            h1_rsi=self._value(
                row,
                "h1_rsi",
            ),
            h1_atr_pct=self._value(
                row,
                "h1_atr_pct",
            ),
            m15_rsi=self._value(
                row,
                "m15_rsi",
            ),
            m15_atr_pct=self._value(
                row,
                "m15_atr_pct",
            ),
            m5_rsi=self._value(
                row,
                "m5_rsi",
            ),
            m5_atr_pct=self._value(
                row,
                "m5_atr_pct",
            ),
            m5_volume_ratio=self._value(
                row,
                "m5_volume_ratio",
            ),
        )

        return MarketSnapshot(
            timestamp=row["timestamp"],
            price=price,
            structure=structure,
            technical=technical,
            regime=regime,
            regime_confidence=float(
                regime_confidence
            ),
        )

    @staticmethod
    def _value(
        row,
        column: str,
    ) -> float | None:

        value = row.get(column)

        if value is None:
            return None

        try:
            if value != value:
                return None
        except TypeError:
            return None

        return float(value)