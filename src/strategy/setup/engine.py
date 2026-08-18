import pandas as pd

from src.strategy.regime.models import MarketRegime
from src.strategy.setup.models import (
    SetupDirection,
    SetupType,
    TradeSetup,
)


class SetupEngine:

    MIN_CONFIDENCE = 0.65
    MIN_RISK_REWARD = 2.5

    ATR_BUFFER = 0.20

    def generate(
        self,
        row: pd.Series,
    ) -> TradeSetup:

        regime = row.get("regime")

        confidence = self._value(
            row,
            "regime_confidence",
        )

        close = self._value(
            row,
            "close",
        )

        atr = self._value(
            row,
            "atr",
        )

        structure_score = self._value(
            row,
            "structure_score",
        )

        event_type = self._string(
            row,
            "event_type",
        )

        event_direction = self._string(
            row,
            "event_direction",
        )

        if (
            regime is None
            or confidence is None
            or close is None
            or atr is None
            or structure_score is None
        ):
            return self._no_setup()

        if confidence < self.MIN_CONFIDENCE:
            return self._no_setup()

        if atr <= 0:
            return self._no_setup()

        # --------------------------------------------------
        # LONG
        # --------------------------------------------------

        if regime == MarketRegime.BULLISH:

            if structure_score <= 0:
                return self._no_setup()

            if event_direction not in (
                None,
                "BULLISH",
            ):
                return self._no_setup()

            return self._build_long(
                row=row,
                close=close,
                atr=atr,
                confidence=confidence,
                event_type=event_type,
            )

        # --------------------------------------------------
        # SHORT
        # --------------------------------------------------

        if regime == MarketRegime.BEARISH:

            if structure_score >= 0:
                return self._no_setup()

            if event_direction not in (
                None,
                "BEARISH",
            ):
                return self._no_setup()

            return self._build_short(
                row=row,
                close=close,
                atr=atr,
                confidence=confidence,
                event_type=event_type,
            )

        return self._no_setup()

    # ======================================================
    # LONG
    # ======================================================

    def _build_long(
        self,
        row: pd.Series,
        close: float,
        atr: float,
        confidence: float,
        event_type: str | None,
    ) -> TradeSetup:

        swing_low = self._value(
            row,
            "swing_low",
        )

        if swing_low is None:
            swing_low = close - atr * 1.5

        stop_loss = (
            swing_low
            - atr * self.ATR_BUFFER
        )

        risk = close - stop_loss

        if risk <= 0:
            return self._no_setup()

        take_profit = (
            close
            + risk * 3.0
        )

        reward = (
            take_profit
            - close
        )

        risk_reward = reward / risk

        if risk_reward < self.MIN_RISK_REWARD:
            return self._no_setup()

        setup_type = self._setup_type(
            event_type,
            bullish=True,
        )

        return TradeSetup(
            direction=SetupDirection.LONG,
            setup_type=setup_type,
            entry=close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk=risk,
            reward=reward,
            risk_reward=risk_reward,
            confidence=confidence,
            valid=True,
        )

    # ======================================================
    # SHORT
    # ======================================================

    def _build_short(
        self,
        row: pd.Series,
        close: float,
        atr: float,
        confidence: float,
        event_type: str | None,
    ) -> TradeSetup:

        swing_high = self._value(
            row,
            "swing_high",
        )

        if swing_high is None:
            swing_high = close + atr * 1.5

        stop_loss = (
            swing_high
            + atr * self.ATR_BUFFER
        )

        risk = stop_loss - close

        if risk <= 0:
            return self._no_setup()

        take_profit = (
            close
            - risk * 3.0
        )

        reward = (
            close
            - take_profit
        )

        risk_reward = reward / risk

        if risk_reward < self.MIN_RISK_REWARD:
            return self._no_setup()

        setup_type = self._setup_type(
            event_type,
            bullish=False,
        )

        return TradeSetup(
            direction=SetupDirection.SHORT,
            setup_type=setup_type,
            entry=close,
            stop_loss=stop_loss,
            take_profit=take_profit,
            risk=risk,
            reward=reward,
            risk_reward=risk_reward,
            confidence=confidence,
            valid=True,
        )

    # ======================================================
    # Helpers
    # ======================================================

    @staticmethod
    def _setup_type(
        event_type: str | None,
        bullish: bool,
    ) -> SetupType:

        if event_type == "CHOCH":
            return SetupType.CHOCH_REVERSAL

        if event_type == "BOS":
            return SetupType.BOS_CONTINUATION

        return SetupType.BOS_CONTINUATION

    @staticmethod
    def _no_setup() -> TradeSetup:

        return TradeSetup(
            direction=SetupDirection.NONE,
            setup_type=SetupType.NONE,
            entry=None,
            stop_loss=None,
            take_profit=None,
            risk=None,
            reward=None,
            risk_reward=None,
            confidence=0.0,
            valid=False,
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
    def _string(
        row: pd.Series,
        column: str,
    ) -> str | None:

        value = row.get(column)

        if value is None:
            return None

        if pd.isna(value):
            return None

        return str(value).upper()
