from dataclasses import dataclass

import pandas as pd

from src.strategy.regime.models import MarketRegime


@dataclass(frozen=True)
class RegimeResult:
    regime: MarketRegime
    confidence: float

    trend_score: float
    volatility_score: float

    bullish_alignment: float
    bearish_alignment: float

    structure_score: float


class RegimeClassifier:

    def classify(
            self,
            row: pd.Series,
            structure_label: str | None = None,
            event_type: str | None = None,
            event_direction: str | None = None,
    ) -> RegimeResult:
        has_market_data = any(
            self._value(row, column) is not None
            for column in (
                "h4_ema_20",
                "h4_ema_50",
                "h4_ema_200",
                "h1_ema_20",
                "h1_ema_50",
                "h1_ema_200",
                "h4_rsi",
                "h1_rsi",
            )
        )

        if not has_market_data:
            return RegimeResult(
                regime=MarketRegime.UNKNOWN,
                confidence=0.0,
                trend_score=0.0,
                volatility_score=0.0,
                bullish_alignment=0.0,
                bearish_alignment=0.0,
                structure_score=0.0,
            )

        bullish = 0.0
        bearish = 0.0

        # --------------------------------------------------
        # 1. 4H EMA structure
        # --------------------------------------------------

        h4_ema20 = self._value(row, "h4_ema_20")
        h4_ema50 = self._value(row, "h4_ema_50")
        h4_ema200 = self._value(row, "h4_ema_200")

        if self._all_present(
            h4_ema20,
            h4_ema50,
            h4_ema200,
        ):

            if (
                h4_ema20
                > h4_ema50
                > h4_ema200
            ):
                bullish += 2.0

            elif (
                h4_ema20
                < h4_ema50
                < h4_ema200
            ):
                bearish += 2.0

        # --------------------------------------------------
        # 2. 1H EMA structure
        # --------------------------------------------------

        h1_ema20 = self._value(row, "h1_ema_20")
        h1_ema50 = self._value(row, "h1_ema_50")
        h1_ema200 = self._value(row, "h1_ema_200")

        if self._all_present(
            h1_ema20,
            h1_ema50,
            h1_ema200,
        ):

            if (
                h1_ema20
                > h1_ema50
                > h1_ema200
            ):
                bullish += 1.5

            elif (
                h1_ema20
                < h1_ema50
                < h1_ema200
            ):
                bearish += 1.5

        # --------------------------------------------------
        # 3. RSI confirmation
        # --------------------------------------------------

        h4_rsi = self._value(row, "h4_rsi")
        h1_rsi = self._value(row, "h1_rsi")

        if h4_rsi is not None:

            if h4_rsi >= 55:
                bullish += 0.75

            elif h4_rsi <= 45:
                bearish += 0.75

        if h1_rsi is not None:

            if h1_rsi >= 55:
                bullish += 0.5

            elif h1_rsi <= 45:
                bearish += 0.5

        # --------------------------------------------------
        # 4. Market structure
        # --------------------------------------------------



        # --------------------------------------------------
        # 4. Determine trend
        # --------------------------------------------------

        total_directional_score = (
            bullish + bearish
        )

        if total_directional_score == 0:

            atr_values = []

            for column in (
                    "h4_atr_pct",
                    "h1_atr_pct",
                    "m15_atr_pct",
            ):

                value = self._value(
                    row,
                    column,
                )

                if value is not None:
                    atr_values.append(value)

            if atr_values:

                average_atr = (
                        sum(atr_values)
                        / len(atr_values)
                )

                volatility_score = min(
                    average_atr / 3.0,
                    1.0,
                )

            else:

                volatility_score = 0.0

            return RegimeResult(
                regime=MarketRegime.RANGE,
                confidence=1.0 - volatility_score,
                trend_score=0.0,
                volatility_score=volatility_score,
                bullish_alignment=0.0,
                bearish_alignment=0.0,
                structure_score=0.0,
            )

        bullish_alignment = (
            bullish / total_directional_score
        )

        bearish_alignment = (
            bearish / total_directional_score
        )

        trend_score = abs(
            bullish - bearish
        ) / max(
            total_directional_score,
            1.0,
        )

        # --------------------------------------------------
        # 5. Volatility
        # --------------------------------------------------

        atr_values = []

        for column in (
            "h4_atr_pct",
            "h1_atr_pct",
            "m15_atr_pct",
        ):

            value = self._value(
                row,
                column,
            )

            if value is not None:
                atr_values.append(value)

        if atr_values:

            average_atr = sum(
                atr_values
            ) / len(atr_values)

            volatility_score = min(
                average_atr / 3.0,
                1.0,
            )

        else:

            volatility_score = 0.0

        # --------------------------------------------------
        # 5.5 Market structure score
        # --------------------------------------------------

        structure_score = 0.0

        structure_weights = {
            "HH": 0.40,
            "HL": 0.30,
            "LH": -0.40,
            "LL": -0.50,
        }

        event_weights = {
            "BOS": 0.60,
            "CHOCH": 1.00,
        }

        if structure_label is not None:
            label = str(
                structure_label
            ).upper()

            structure_score += (
                structure_weights.get(
                    label,
                    0.0,
                )
            )

        if event_type is not None:

            event = str(
                event_type
            ).upper()

            event_score = (
                event_weights.get(
                    event,
                    0.0,
                )
            )

            if event_direction is not None:

                direction = str(
                    event_direction
                ).upper()

                if direction == "BEARISH":
                    event_score *= -1.0

                elif direction != "BULLISH":
                    event_score = 0.0

            structure_score += event_score

        structure_score = max(
            -1.0,
            min(
                1.0,
                structure_score,
            ),
        )

        # --------------------------------------------------
        # 6. Final regime
        # --------------------------------------------------

        indicator_direction = (
                bullish_alignment
                - bearish_alignment
        )

        combined_direction = (
                indicator_direction * 0.40
                + structure_score * 0.60
        )

        if trend_score < 0.20:

            regime = MarketRegime.RANGE

        elif combined_direction > 0:

            regime = MarketRegime.BULLISH

        else:

            regime = MarketRegime.BEARISH

        structure_strength = abs(
            structure_score
        )

        confidence = min(
            (
                    trend_score * 0.55
                    + structure_strength * 0.25
                    + volatility_score * 0.20
            ),
            1.0,
        )

        return RegimeResult(
            regime=regime,
            confidence=confidence,
            trend_score=trend_score,
            volatility_score=volatility_score,
            bullish_alignment=bullish_alignment,
            bearish_alignment=bearish_alignment,
            structure_score=structure_score,
        )

    @staticmethod
    def _value(
        row: pd.Series,
        column: str,
    ) -> float | None:

        value = row.get(column)

        if value is None:
            return None

        if pd.isna(value):
            return None

        return float(value)

    @staticmethod
    def _all_present(
        *values,
    ) -> bool:

        return all(
            value is not None
            for value in values
        )